"""
Task 4 runner: GBN vs SR under three channel conditions.
seed = 859 (my nu id is 24k-0859)
Writes results.csv and gbn_vs_sr.png, and prints the results table.
"""

import argparse
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reliable_transfer import simulate  

PACKETS = 200
WINDOW = 4
SEQBITS = 3

SCENARIOS = [
    ("A: Reliable", dict(loss=0.0, corrupt=0.0, delay=0.0)),
    ("B: Loss 0.10", dict(loss=0.10, corrupt=0.0, delay=0.0)),
    ("C: Mixed (L0.05, C0.05, D0.10)", dict(loss=0.05, corrupt=0.05, delay=0.10)),
]

def run_one(protocol, channel, seed, runs):
    """Average over `runs` consecutive seeds (runs=1 means a single run)."""
    keys = ["data_sent", "retransmissions", "delivered", "sim_time_ms", "throughput_kbps"]
    totals = {k: 0.0 for k in keys}
    for i in range(runs):
        r = simulate(protocol, packets=PACKETS, window=WINDOW, seqbits=SEQBITS,
                     quiet=True, seed=seed + i, **channel)
        if not r["in_order_and_correct"]:
            raise RuntimeError(f"{protocol} failed to deliver correctly (seed {seed + i})")
        for k in keys:
            totals[k] += r[k]
    return {k: totals[k] / runs for k in keys}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=859, help="last 3 digits of roll number since first is 0 so 859 is used as the default random seed")
    ap.add_argument("--runs", type=int, default=1, help="average over this many seeds")
    a = ap.parse_args()

    rows = []
    for name, channel in SCENARIOS:
        for proto in ("gbn", "sr"):
            res = run_one(proto, channel, a.seed, a.runs)
            rows.append(dict(scenario=name, protocol=proto.upper(), **res))

    with open("results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f"Seed {a.seed}, runs averaged: {a.runs}, {PACKETS} packets, N={WINDOW}, k={SEQBITS}\n")
    print("| Scenario | Protocol | Transmitted | Retransmissions | Delivered | Time (s) | Throughput (kbps) |")
    print("|---|---|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['scenario']} | {r['protocol']} | {r['data_sent']:.0f} | "
              f"{r['retransmissions']:.0f} | {r['delivered']:.0f} | "
              f"{r['sim_time_ms'] / 1000:.1f} | {r['throughput_kbps']:.1f} |")

    labels = ["A: Reliable", "B: Loss 0.10", "C: Mixed"]
    gbn = [r for r in rows if r["protocol"] == "GBN"]
    sr = [r for r in rows if r["protocol"] == "SR"]
    x = range(len(labels))
    width = 0.38

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    panels = [("retransmissions", "Retransmissions (packets)", "Retransmissions"),
              ("throughput_kbps", "Throughput (kbps)", "Throughput")]
    for ax, (key, ylabel, title) in zip(axes, panels):
        b1 = ax.bar([i - width / 2 for i in x], [r[key] for r in gbn], width, label="GBN", color="#d9534f")
        b2 = ax.bar([i + width / 2 for i in x], [r[key] for r in sr], width, label="SR", color="#337ab7")
        ax.set_xticks(list(x))
        ax.set_xticklabels(labels)
        ax.set_xlabel("Channel scenario")
        ax.set_ylabel(ylabel)
        ax.set_title(f"{title}: GBN vs SR (200 packets, N=4, k=3)")
        ax.legend()
        for bars in (b1, b2):
            for bar in bars:
                ax.annotate(f"{bar.get_height():.0f}", (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                            ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    plt.savefig("gbn_vs_sr.png", dpi=150)
    print("\nSaved results.csv and gbn_vs_sr.png")

if __name__ == "__main__":
    main()