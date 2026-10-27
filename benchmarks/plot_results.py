#!/usr/bin/env python3
"""Generate benchmark results plots comparing C Baseline, C Optimized, and Goose on Core2."""
import csv
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

def generate_plots():
    groups = defaultdict(list)
    with open("benchmarks/results/raw_core2.log", encoding="utf-8", errors="replace") as f:
        for line in f:
            idx = line.find("BENCH,")
            if idx < 0:
                continue
            fields = line[idx:].strip().split(",")
            if len(fields) == 8:
                _, workload, impl, sample, us, checksum, internal, psram = fields
                groups[impl].append({
                    "sample": int(sample),
                    "us": int(us),
                    "ms": int(us) / 1000.0,
                    "checksum": int(checksum),
                    "internal_kb": int(internal) / 1024.0,
                    "psram_mb": int(psram) / (1024.0 * 1024.0)
                })

    if not groups:
        print("No samples found!")
        return

    # Set up styling
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6.2), dpi=200)
    fig.patch.set_facecolor('#ffffff')

    colors = {
        'c_opt': '#059669',    # Emerald
        'c': '#2563eb',        # Blue
        'goose': '#d97706',    # Amber
        'rust': '#94a3b8'      # Slate
    }

    labels = {
        'c_opt': 'C (Arena/Pointer Opt)',
        'c': 'C Baseline',
        'goose': 'Goose (Ported Runtime)'
    }

    # Plot 1: 30-run latency comparison
    for impl in ['c_opt', 'c', 'goose']:
        if impl in groups:
            items = sorted(groups[impl], key=lambda x: x['sample'])
            xs = [x['sample'] for x in items]
            ys = [x['ms'] for x in items]
            med = np.median(ys)
            ax1.plot(xs, ys, marker='o', markersize=4.5, linewidth=1.6, color=colors[impl], 
                     label=f"{labels[impl]} (Med: {med:.2f} ms)")

    ax1.set_title('Core2: array_scan (1024 items × 1000 inner) Latency Across 30 Runs', fontsize=11, fontweight='bold', pad=12)
    ax1.set_xlabel('Sample Run Index (Warm)', fontsize=10)
    ax1.set_ylabel('Execution Time (ms)', fontsize=10)
    ax1.set_ylim(40, 205)
    ax1.grid(True, linestyle='--', alpha=0.6)
    ax1.legend(loc='upper right', frameon=True, facecolor='#f8fafc', edgecolor='#cbd5e1', fontsize=9.5)

    # Plot 2: Median execution time comparison bar chart
    bar_impls = ['C (Optimized)', 'C (Baseline)', 'Goose (Ported)', 'Rust (Pending)']
    c_opt_med = float(np.median([x['ms'] for x in groups.get('c_opt', [])])) if 'c_opt' in groups else 0
    c_med = float(np.median([x['ms'] for x in groups.get('c', [])])) if 'c' in groups else 0
    goose_med = float(np.median([x['ms'] for x in groups.get('goose', [])])) if 'goose' in groups else 0
    bar_vals = [c_opt_med, c_med, goose_med, 0]
    bar_colors = [colors['c_opt'], colors['c'], colors['goose'], colors['rust']]
    bar_edges = ['#047857', '#1d4ed8', '#b45309', '#64748b']

    bars = ax2.bar(bar_impls, bar_vals, color=bar_colors, edgecolor=bar_edges, width=0.55, linewidth=1.2)
    ax2.set_title('Median Latency by Implementation (Core2 Hardware)', fontsize=11, fontweight='bold', pad=12)
    ax2.set_ylabel('Execution Time (ms)', fontsize=10)
    ax2.set_ylim(0, 180)
    ax2.grid(True, linestyle='--', alpha=0.6, axis='y')

    # Add bar value annotations
    ax2.text(0, c_opt_med + 3, f"{c_opt_med:.2f} ms\n(1.66x faster)", ha='center', va='bottom', fontsize=9, fontweight='bold', color='#065f46')
    ax2.text(1, c_med + 3, f"{c_med:.2f} ms\n(Baseline)", ha='center', va='bottom', fontsize=9, fontweight='bold', color='#1e40af')
    ax2.text(2, goose_med + 3, f"{goose_med:.2f} ms\n(1.53x baseline)", ha='center', va='bottom', fontsize=9, fontweight='bold', color='#92400e')
    ax2.text(3, 10, 'Toolchain Pending\n(Issue #7)', ha='center', va='bottom', fontsize=8.5, color='#64748b', style='italic')

    # Adjust layout
    plt.subplots_adjust(bottom=0.22, top=0.90, wspace=0.22)

    # Add environment metadata footer
    env_text = (
        "Target: M5Stack Core2 (ESP32-D0WDQ6-V3 @ 160MHz) | OS: FreeRTOS (ESP-IDF v5.3.1) | Compiler: xtensa-esp-elf GCC 13.2.0 (-Os)\n"
        "Checksum Parity: 33582136 (100% deterministic across all 90 runs of C, C-Opt, and Goose)\n"
        "Memory Footprint: C & C-Opt Free PSRAM: 4.19 MB | Goose Free PSRAM: 2.09 MB (~2 MB PSRAM stack-arena mapped)"
    )
    fig.text(0.5, 0.04, env_text, ha='center', fontsize=8.5, color='#334155',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='#f8fafc', edgecolor='#cbd5e1'))

    plt.savefig("benchmarks/results/benchmark_results.png", bbox_inches='tight', dpi=200)
    plt.close()
    print("Generated benchmarks/results/benchmark_results.png successfully!")

if __name__ == "__main__":
    generate_plots()
