# CS3001 Assignment 2: GBN and Selective Repeat

Name: Abdullah
Roll No: 24K-0859
Demo Video: [\[Google Drive link\]](https://drive.google.com/file/d/1wcIuNaYJ5lBUs48r9ZHdRMK7FiuT47pT/view?usp=drive_link)

## Files
- `reliable_transfer.py`: GBN and SR sender/receiver and the simulated unreliable channel
- `task4.py`: runs experiments A, B and C for both protocols
- `results.csv`: results table from `task4.py`
- `gbn_vs_sr.png`: GBN vs SR graph
- `CN-A2-[24K-0859]-Report.pdf`: Report (approach, traces, results, analysis)

## How to run
You need Python 3. Only `task4.py` needs an extra package: `pip install matplotlib`.

Sample command (SR, 20 packets, window 4, 3-bit sequence numbers, 5% loss, 5% corruption, 10% delay):

```
python3 reliable_transfer.py --protocol sr --packets 20 --window 4 --seqbits 3 --loss 0.05 --corrupt 0.05 --delay 0.1 --seed 859
```

The program prints one log line for every send, receive, ACK, loss, corruption, delay, timeout and retransmission, then a summary at the end.

To repeat the three experiments (200 packets, N = 4, k = 3):

```
python3 experiments.py --seed 859
```

This prints the results table and saves `results.csv` and `gbn_vs_sr.png`.

## Parameters
| Flag | Meaning | Default |
|---|---|---|
| `--protocol` | `gbn` or `sr` | gbn |
| `--packets` | number of packets to send | 20 |
| `--window` | window size N | 4 |
| `--seqbits` | sequence number bits k (numbers wrap modulo 2^k) | 3 |
| `--loss` | loss probability (packets and ACKs) | 0.0 |
| `--corrupt` | corruption probability (caught by the checksum) | 0.0 |
| `--delay` | probability that a packet or ACK gets extra delay | 0.0 |
| `--timeout` | retransmission timeout in ms | 900 |
| `--seed` | random seed, last 4 digits of roll number | 859 |
| `--quiet` | print only the summary | off |

## Notes
- Keep the timeout above the worst-case round trip (about 800 ms in this simulation). A shorter timeout causes early retransmissions and old duplicate packets can be mistaken for new ones after the sequence numbers wrap.
- The program prints a warning if the window is larger than the safe limit (GBN: 2^k - 1, SR: 2^(k-1)).
