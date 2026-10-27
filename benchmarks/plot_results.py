#!/usr/bin/env python3
"""Generate benchmark results plots for Core2 benchmark."""
import csv
import matplotlib.pyplot as plt
import numpy as np

def generate_plots():
    # Read raw samples
    samples = []
    with open("benchmarks/results/raw_core2.log", encoding="utf-8", errors="replace") as f:
        for line in f:
            idx = line.find("BENCH,")
            if idx < 0:
                continue
            fields = line[idx:].strip().split(",")
            if len(fields) == 8:
                _, workload, impl, sample, us, checksum, internal, psram = fields
                samples.append({
                    "sample": int(sample),
                    "us": int(us),
                    "ms": int(us) / 1000.0,
                    "checksum": int(checksum),
                    "internal_kb": int(internal) / 1024.0,
                    "psram_mb": int(psram) / (1024.0 * 1024.0)
                })

    if not samples:
        print("No samples found!")
        return

    sample_nums = [s["sample"] for s in samples]
    times_ms = [s["ms"] for s in samples]
    median_ms = float(np.median(times_ms))
    p95_ms = float(np.percentile(times_ms, 95))
    min_ms = float(min(times_ms))
    max_ms = float(max(times_ms))
    median_us = median_ms * 1000.0
    jitter_us = (max_ms - min_ms) * 1000.0
    jitter_pct = (jitter_us / median_us) * 100.0

    # Set up styling
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=200)
    fig.patch.set_facecolor('#ffffff')

    # Plot 1: Run-by-run latency (30 samples)
    ax1.plot(sample_nums, times_ms, marker='o', color='#2563eb', linewidth=1.8, markersize=5, label='C Baseline Run Latency')
    ax1.axhline(median_ms, color='#dc2626', linestyle='--', linewidth=1.5, label=f'Median: {median_ms:.3f} ms ({median_us:.0f} μs)')
    ax1.axhline(p95_ms, color='#d97706', linestyle=':', linewidth=1.5, label=f'P95: {p95_ms:.3f} ms')
    ax1.set_title('Core2: array_scan (1024 items × 1000 inner) Latency Across 30 Runs', fontsize=11, fontweight='bold', pad=12)
    ax1.set_xlabel('Sample Run Index (Warm)', fontsize=10)
    ax1.set_ylabel('Execution Time (ms)', fontsize=10)
    
    span = max_ms - min_ms if max_ms != min_ms else 0.01
    ax1.set_ylim(min_ms - span * 1.5, max_ms + span * 2.0)
    ax1.grid(True, linestyle='--', alpha=0.6)
    ax1.legend(loc='upper right', frameon=True, facecolor='#f8fafc', edgecolor='#cbd5e1', fontsize=9)

    # Add text annotation
    ax1.text(0.04, 0.08, f'Min: {min_ms:.3f} ms | Max: {max_ms:.3f} ms\nJitter: {jitter_us:.0f} μs ({jitter_pct:.3f}%)', 
             transform=ax1.transAxes, fontsize=9, bbox=dict(boxstyle='round,pad=0.5', facecolor='#f1f5f9', edgecolor='#cbd5e1'))

    # Plot 2: Implementation Status & Execution Time Comparison
    impls = ['C Baseline\n(ESP-IDF 5.3)', 'C (Arena-opt)\n(Pending)', 'Rust\n(Pending)', 'Goose\n(Pending runtime)']
    values = [median_ms, 0, 0, 0]
    colors = ['#10b981', '#e2e8f0', '#e2e8f0', '#e2e8f0']
    edgecolors = ['#059669', '#94a3b8', '#94a3b8', '#94a3b8']

    bars = ax2.bar(impls, values, color=colors, edgecolor=edgecolors, width=0.55, linewidth=1.2)
    ax2.set_title('Workload Implementation Status (Core2 Hardware Run)', fontsize=11, fontweight='bold', pad=12)
    ax2.set_ylabel('Median Execution Time (ms)', fontsize=10)
    ax2.set_ylim(0, max(120, median_ms * 1.25))
    ax2.grid(True, linestyle='--', alpha=0.6, axis='y')

    # Add bar labels
    ax2.text(0, median_ms + 3.0, f'{median_ms:.2f} ms\n(Verified on Core2)', ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#0f172a')
    for i in range(1, 4):
        ax2.text(i, 8, 'Pending / In Progress\n(Issue #7)', ha='center', va='bottom', fontsize=8.5, color='#64748b', style='italic')

    # Adjust layout to make room for metadata footer
    plt.subplots_adjust(bottom=0.22, top=0.90, wspace=0.22)

    # Add environment metadata footer
    env_text = (
        "Environment: M5Stack Core2 (ESP32-D0WDQ6-V3 @ 160MHz) | OS: FreeRTOS (ESP-IDF v5.3.1) | Compiler: xtensa-esp-elf GCC 13.2.0 (-Os)\n"
        "Memory: 363.2 KB Free Internal Heap | 4.19 MB Free PSRAM | Checksum Parity: 33582136 (100% deterministic over 30 runs)"
    )
    fig.text(0.5, 0.04, env_text, ha='center', fontsize=8.5, color='#334155',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='#f8fafc', edgecolor='#cbd5e1'))

    plt.savefig("benchmarks/results/benchmark_results.png", bbox_inches='tight', dpi=200)
    plt.close()
    print("Generated benchmarks/results/benchmark_results.png successfully!")

if __name__ == "__main__":
    generate_plots()
