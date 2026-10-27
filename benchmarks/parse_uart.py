#!/usr/bin/env python3
"""Summarize Core2 BENCH UART records from a captured serial log."""
import argparse
import csv
import statistics
from collections import defaultdict

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("log", help="Captured UART text log")
    ap.add_argument("--csv", default="benchmark-summary.csv")
    args = ap.parse_args()
    groups = defaultdict(list)
    with open(args.log, encoding="utf-8", errors="replace") as f:
        for line in f:
            idx = line.find("BENCH,")
            if idx < 0:
                continue
            fields = line[idx:].strip().split(",")
            if len(fields) != 7:
                continue
            _, workload, impl, sample, us, checksum, internal, psram = fields
            try:
                groups[(workload, impl)].append((int(sample), int(us), int(checksum), int(internal), int(psram)))
            except ValueError:
                continue
    rows = []
    for (workload, impl), samples in sorted(groups.items()):
        samples.sort()
        times = [r[1] for r in samples]
        checksums = {r[2] for r in samples}
        if len(checksums) != 1:
            raise SystemExit(f"Inconsistent checksums for {workload}/{impl}")
        p95 = sorted(times)[max(0, (95 * len(times) + 99) // 100 - 1)]
        rows.append(dict(workload=workload, implementation=impl, samples=len(times),
                         median_us=statistics.median(times), p95_us=p95,
                         min_us=min(times), max_us=max(times), checksum=next(iter(checksums)),
                         min_free_internal_bytes=min(r[3] for r in samples),
                         min_free_psram_bytes=min(r[4] for r in samples)))
    if not rows:
        raise SystemExit("No BENCH records found")
    with open(args.csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    for row in rows:
        print(row)
    print("Saved:", args.csv)

if __name__ == "__main__":
    main()
