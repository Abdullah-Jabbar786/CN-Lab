"""
Reliable data transfer simulator: Go-Back-N (GBN) and Selective Repeat (SR).
seed = 859 (my nu id is 24k-0859) is used as the default random seed.
Time unit: milliseconds.
"""

import argparse
import copy
import heapq
import random
import time

PACKET_BYTES = 1000

def compute_checksum(kind, seq, payload):
    """16-bit one's complement sum (Internet checksum style)."""
    data = bytes([1 if kind == "DATA" else 2]) + seq.to_bytes(2, "big") + payload
    if len(data) % 2:
        data += b"\x00"
    total = 0
    for i in range(0, len(data), 2):
        total += (data[i] << 8) | data[i+1]
        total = (total & 0xFFFF) + (total >> 16)
    return (~total) & 0xFFFF

class Packet:
    def __init__(self, kind, seq, payload=b""):
        self.kind = kind
        self.seq = seq
        self.payload = payload
        self.checksum = compute_checksum(kind, seq, payload)

    def is_corrupt(self):
        return self.checksum != compute_checksum(self.kind, self.seq, self.payload)
    def label(self):
        return f"{self.kind} seq={self.seq}"

class Simulation:
    def __init__(self, cfg):
        self.cfg = cfg
        self.now = 0.0
        self.queue = []
        self.counter = 0
        self.rng = random.Random(cfg["seed"])
        self.stats = {"data_sent": 0, "retransmissions": 0, "acks_sent": 0,
                      "lost": 0, "corrupted": 0, "delayed": 0, "timeouts": 0}
        self.link_free = 0.0
        self.tx_time = PACKET_BYTES * 8 / cfg["rate_mbps"] / 1000.0
        self.prop = cfg["rtt"] / 2.0

    def log(self, who, msg):
        if not self.cfg["quiet"]:
            print(f"[t={self.now:9.1f} ms] {who:<8} {msg}")

    def schedule(self, when, fn, *args):
        self.counter += 1
        heapq.heappush(self.queue, (when, self.counter, fn, args))

    def transmit(self, pkt, receiver_fn, who):
        """Unreliable channel: may lose, corrupt or delay the packet."""
        cfg = self.cfg
        if pkt.kind == "DATA":
            depart = max(self.now, self.link_free)
            self.link_free = depart + self.tx_time
            arrive = depart + self.tx_time + self.prop
        else:
            arrive = self.now + self.prop

        if self.rng.random() < cfg["loss"]:
            self.stats["lost"] += 1
            self.log("CHANNEL", f"{pkt.label()} LOST")
            return

        pkt = copy.copy(pkt)
        if self.rng.random() < cfg["corrupt"]:
            self.stats["corrupted"] += 1
            self.log("CHANNEL", f"{pkt.label()} CORRUPTED")
            if pkt.kind == "DATA" and pkt.payload:
                pkt.payload = bytes([pkt.payload[0] ^ 0x01]) + pkt.payload[1:]
            else:
                pkt.checksum ^= 0x00FF

        if self.rng.random() < cfg["delay"]:
            extra = self.rng.uniform(0, cfg["max_extra_delay"])
            arrive += extra
            self.stats["delayed"] += 1
            self.log("CHANNEL", f"{pkt.label()} DELAYED by {extra:.1f} ms")

        self.schedule(arrive, receiver_fn, pkt)

    def run(self, sender, max_time=5_000_000):
        sender.start()
        while self.queue and not sender.done() and self.now < max_time:
            when, _, fn, args = heapq.heappop(self.queue)
            self.now = when
            fn(*args)

class TimerMixin:
    """Timers are events in the queue; stopping a timer just invalidates it."""
    def start_timer(self, key):
        self.timer_ids[key] = self.timer_ids.get(key, 0) + 1
        tid = self.timer_ids[key]
        self.sim.schedule(self.sim.now + self.sim.cfg["timeout"],
                          self.on_timer_event, key, tid)

    def stop_timer(self, key):
        if key in self.timer_ids:
            self.timer_ids[key] += 1
    def on_timer_event(self, key, tid):
        if self.timer_ids.get(key) == tid:
            self.on_timeout(key)

class GBNSender(TimerMixin):
    def __init__(self, sim, payloads, receiver):
        self.sim, self.payloads, self.receiver = sim, payloads, receiver
        self.N = sim.cfg["window"]
        self.M = 2 ** sim.cfg["seqbits"]
        self.base = 0
        self.nextseqnum = 0
        self.timer_ids = {}

    def done(self):
        return self.base == len(self.payloads)
    def start(self):
        self.send_available()
    def send_available(self):
        while self.nextseqnum < self.base + self.N and self.nextseqnum < len(self.payloads):
            self.send(self.nextseqnum, retransmit=False)
            if self.base == self.nextseqnum:
                self.start_timer("gbn")   # oldest unACKed packet
            self.nextseqnum += 1

    def send(self, idx, retransmit):
        pkt = Packet("DATA", idx % self.M, self.payloads[idx])
        tag = "RETRANSMIT" if retransmit else "send"
        self.sim.stats["data_sent"] += 1
        if retransmit:
            self.sim.stats["retransmissions"] += 1
        self.sim.log("SENDER", f"{tag} {pkt.label()} (pkt #{idx}) "
                               f"[base={self.base}, nextseqnum={self.nextseqnum}]")
        self.sim.transmit(pkt, self.receiver.on_data, "SENDER")

    def on_ack(self, pkt):
        if pkt.is_corrupt():
            self.sim.log("SENDER", f"received corrupted ACK, ignored")
            return
        d = (pkt.seq - self.base % self.M) % self.M
        if d < self.nextseqnum - self.base:           # cumulative: acks base..base+d
            self.base += d + 1
            self.sim.log("SENDER", f"received {pkt.label()} (cumulative), base -> {self.base}")
            if self.base == self.nextseqnum:
                self.stop_timer("gbn")
            else:
                self.start_timer("gbn")
            self.send_available()
        else:
            self.sim.log("SENDER", f"received duplicate {pkt.label()}, ignored")

    def on_timeout(self, key):
        self.sim.stats["timeouts"] += 1
        self.sim.log("SENDER", f"TIMEOUT: resend pkts {self.base}..{self.nextseqnum - 1}")
        self.start_timer("gbn")
        for idx in range(self.base, self.nextseqnum):   # go back N
            self.send(idx, retransmit=True)

class GBNReceiver:
    def __init__(self, sim):
        self.sim = sim
        self.M = 2 ** sim.cfg["seqbits"]
        self.expectedseqnum = 0
        self.delivered = []
        self.sender = None

    def send_ack(self, idx):
        ack = Packet("ACK", idx % self.M)
        self.sim.stats["acks_sent"] += 1
        self.sim.log("RECEIVER", f"send {ack.label()}")
        self.sim.transmit(ack, self.sender.on_ack, "RECEIVER")

    def on_data(self, pkt):
        if pkt.is_corrupt():
            self.sim.log("RECEIVER", "received corrupted DATA, discarded")
            if self.expectedseqnum > 0:
                self.send_ack(self.expectedseqnum - 1)
            return
        if pkt.seq == self.expectedseqnum % self.M:
            self.sim.log("RECEIVER", f"received {pkt.label()} in order, delivered")
            self.delivered.append(pkt.payload)
            self.send_ack(self.expectedseqnum)
            self.expectedseqnum += 1
        else:
            self.sim.log("RECEIVER", f"received {pkt.label()} out of order "
                                     f"(expected {self.expectedseqnum % self.M}), discarded")
            if self.expectedseqnum > 0:
                self.send_ack(self.expectedseqnum - 1)

class SRSender(TimerMixin):
    def __init__(self, sim, payloads, receiver):
        self.sim, self.payloads, self.receiver = sim, payloads, receiver
        self.N = sim.cfg["window"]
        self.M = 2 ** sim.cfg["seqbits"]
        self.base = 0
        self.nextseqnum = 0
        self.acked = {}
        self.timer_ids = {}

    def done(self):
        return self.base == len(self.payloads)
    def start(self):
        self.send_available()

    def send_available(self):
        while self.nextseqnum < self.base + self.N and self.nextseqnum < len(self.payloads):
            self.acked[self.nextseqnum] = False
            self.send(self.nextseqnum, retransmit=False)
            self.start_timer(self.nextseqnum) # one timer per packet
            self.nextseqnum += 1

    def send(self, idx, retransmit):
        pkt = Packet("DATA", idx % self.M, self.payloads[idx])
        tag = "RETRANSMIT" if retransmit else "send"
        self.sim.stats["data_sent"] += 1
        if retransmit:
            self.sim.stats["retransmissions"] += 1
        self.sim.log("SENDER", f"{tag} {pkt.label()} (pkt #{idx}) "
                               f"[send_base={self.base}, nextseqnum={self.nextseqnum}]")
        self.sim.transmit(pkt, self.receiver.on_data, "SENDER")

    def on_ack(self, pkt):
        if pkt.is_corrupt():
            self.sim.log("SENDER", "received corrupted ACK, ignored")
            return
        d = (pkt.seq - self.base % self.M) % self.M
        idx = self.base + d
        if d < self.nextseqnum - self.base and not self.acked[idx]:
            self.acked[idx] = True   # individual ACK
            self.stop_timer(idx)
            self.sim.log("SENDER", f"received {pkt.label()} (pkt #{idx}) individually ACKed")
            while self.base < self.nextseqnum and self.acked[self.base]:
                self.base += 1 
            self.sim.log("SENDER", f"send window now [{self.base}, {self.base + self.N - 1}]")
            self.send_available()
        else:
            self.sim.log("SENDER", f"received duplicate {pkt.label()}, ignored")

    def on_timeout(self, idx):
        self.sim.stats["timeouts"] += 1
        self.sim.log("SENDER", f"TIMEOUT for pkt #{idx}: resend only this packet")
        self.send(idx, retransmit=True)
        self.start_timer(idx)

class SRReceiver:
    def __init__(self, sim):
        self.sim = sim
        self.N = sim.cfg["window"]
        self.M = 2 ** sim.cfg["seqbits"]
        self.rcv_base = 0
        self.buffer = {}
        self.delivered = []
        self.sender = None

    def send_ack(self, seq):
        ack = Packet("ACK", seq)
        self.sim.stats["acks_sent"] += 1
        self.sim.log("RECEIVER", f"send {ack.label()}")
        self.sim.transmit(ack, self.sender.on_ack, "RECEIVER")

    def on_data(self, pkt):
        if pkt.is_corrupt():
            self.sim.log("RECEIVER", "received corrupted DATA, discarded (no ACK)")
            return
        d = (pkt.seq - self.rcv_base % self.M) % self.M
        if d < self.N:
            idx = self.rcv_base + d
            self.send_ack(pkt.seq)                 #individual ACK
            if idx not in self.buffer:
                self.buffer[idx] = pkt.payload
                if idx == self.rcv_base:
                    self.sim.log("RECEIVER", f"received {pkt.label()} (rcv_base), accepted")
                else:
                    self.sim.log("RECEIVER", f"received {pkt.label()} out of order, BUFFERED")
            while self.rcv_base in self.buffer: 
                self.delivered.append(self.buffer.pop(self.rcv_base))
                self.sim.log("RECEIVER", f"delivered pkt #{self.rcv_base} to application")
                self.rcv_base += 1
        elif d >= self.M - self.N:  #old packet, its ACK was lost
            self.sim.log("RECEIVER", f"received old {pkt.label()}, re-ACK")
            self.send_ack(pkt.seq)
        else:
            self.sim.log("RECEIVER", f"received {pkt.label()} outside window, ignored")

def simulate(protocol="gbn", packets=20, window=4, seqbits=3, loss=0.0,
             corrupt=0.0, delay=0.0, timeout=900.0, seed=859, rtt=500.0,
             rate_mbps=2.0, max_extra_delay=150.0, quiet=False):
    cfg = dict(protocol=protocol, packets=packets, window=window, seqbits=seqbits,
               loss=loss, corrupt=corrupt, delay=delay, timeout=timeout, seed=seed,
               rtt=rtt, rate_mbps=rate_mbps, max_extra_delay=max_extra_delay,
               quiet=quiet)
    M = 2 ** seqbits
    limit = M - 1 if protocol == "gbn" else M // 2
    if window > limit and not quiet:
        print(f"WARNING: window {window} exceeds the safe limit {limit} for "
              f"{protocol.upper()} with {seqbits}-bit sequence numbers.")

    payloads = [f"MSG-{i:04d}".encode() for i in range(packets)]
    sim = Simulation(cfg)
    if protocol == "gbn":
        receiver = GBNReceiver(sim)
        sender = GBNSender(sim, payloads, receiver)
    else:
        receiver = SRReceiver(sim)
        sender = SRSender(sim, payloads, receiver)
    receiver.sender = sender

    wall_start = time.time()
    sim.run(sender)
    wall = time.time() - wall_start

    ok = receiver.delivered == payloads[:len(receiver.delivered)]
    delivered = len(receiver.delivered) if ok else 0
    elapsed_s = max(sim.now, 1e-9) / 1000.0
    result = dict(sim.stats)
    result.update(protocol=protocol.upper(), delivered=delivered,
                  in_order_and_correct=ok and delivered == packets,
                  sim_time_ms=round(sim.now, 1),
                  throughput_kbps=round(delivered * PACKET_BYTES * 8 / elapsed_s / 1000.0, 2),
                  wall_time_s=round(wall, 4))
    return result

def print_summary(r):
    print("\n=== SUMMARY ===")
    print(f"Protocol                 : {r['protocol']}")
    print(f"Data packets transmitted : {r['data_sent']}")
    print(f"Retransmissions          : {r['retransmissions']}")
    print(f"ACKs sent                : {r['acks_sent']}")
    print(f"Lost / corrupted / delayed: {r['lost']} / {r['corrupted']} / {r['delayed']}")
    print(f"Timeouts                 : {r['timeouts']}")
    print(f"Packets delivered        : {r['delivered']} (in order and correct: {r['in_order_and_correct']})")
    print(f"Simulated time           : {r['sim_time_ms']} ms")
    print(f"Throughput               : {r['throughput_kbps']} kbps")
    print(f"Execution time           : {r['wall_time_s']} s")

def main():
    p = argparse.ArgumentParser(description="GBN / SR reliable transfer simulator")
    p.add_argument("--protocol", choices=["gbn", "sr"], default="gbn")
    p.add_argument("--packets", type=int, default=20)
    p.add_argument("--window", type=int, default=4)
    p.add_argument("--seqbits", type=int, default=3)
    p.add_argument("--loss", type=float, default=0.0)
    p.add_argument("--corrupt", type=float, default=0.0)
    p.add_argument("--delay", type=float, default=0.0, help="probability of extra delay")
    p.add_argument("--timeout", type=float, default=900.0, help="ms, keep above worst-case RTT")
    p.add_argument("--seed", type=int, default=859, help="use last 3 digits of roll number since my roll number has forst digit 0 so 859 is used as the default random seed")
    p.add_argument("--quiet", action="store_true", help="suppress per-event log")
    a = p.parse_args()
    r = simulate(a.protocol, a.packets, a.window, a.seqbits, a.loss, a.corrupt,
                 a.delay, a.timeout, a.seed, quiet=a.quiet)
    print_summary(r)

if __name__ == "__main__":
    main()