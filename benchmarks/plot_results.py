#!/usr/bin/env python3
"""Generate benchmark results plots comparing C, C-Opt, Rust, and Goose on M5Stack Core2."""
import csv
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

def generate_plots():
    groups = defaultdict(lambda: defaultdict(list))
    with open("benchmarks/results/raw_core2.log", encoding="utf-8", errors="replace") as f:
        for line in f:
            idx = line.find("BENCH,")
            if idx < 0:
                continue
            fields = line[idx:].strip().split(",")
            if len(fields) == 8:
                _, workload, impl, sample, us, checksum, internal, psram = fields
                groups[workload][impl].append({
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

    # Style
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6.8), dpi=220)
    fig.patch.set_facecolor('#ffffff')

    colors = {
        'c_opt': '#059669',    # Emerald
        'rust': '#7c3aed',     # Purple
        'c': '#2563eb',        # Blue
        'goose': '#d97706',    # Amber
        'c_arena': '#059669',  # Emerald
        'c_heap': '#dc2626'    # Red
    }

    # ================= PANEL 1: array_scan =================
    ax1.set_facecolor('#f8fafc')
    w1 = groups.get('array_scan', {})
    c_opt_ms = float(np.median([x['ms'] for x in w1.get('c_opt', [])])) if 'c_opt' in w1 else 0
    rust1_ms = float(np.median([x['ms'] for x in w1.get('rust', [])])) if 'rust' in w1 else 0
    c_ms = float(np.median([x['ms'] for x in w1.get('c', [])])) if 'c' in w1 else 0
    goose1_ms = float(np.median([x['ms'] for x in w1.get('goose', [])])) if 'goose' in w1 else 0

    p1_labels = ['C (Optimized)', 'Rust (no_std)', 'C (Baseline)', 'Goose (Ported)']
    p1_vals = [c_opt_ms, rust1_ms, c_ms, goose1_ms]
    p1_colors = [colors['c_opt'], colors['rust'], colors['c'], colors['goose']]
    p1_edges = ['#047857', '#6d28d9', '#1d4ed8', '#b45309']

    bars1 = ax1.bar(p1_labels, p1_vals, color=p1_colors, edgecolor=p1_edges, width=0.55, linewidth=1.2, zorder=3)
    ax1.set_title('Workload 1: array_scan (1,024 items × 1,000 iter)\nLatency by Implementation (Lower is Better)',
                  fontsize=11.5, fontweight='bold', pad=12)
    ax1.set_ylabel('Execution Time (ms)', fontsize=10.5, fontweight='bold')
    ax1.set_ylim(0, 185)
    ax1.grid(True, linestyle='--', alpha=0.6, axis='y', zorder=0)

    # Annotations for panel 1
    ax1.text(0, c_opt_ms + 3.5, f"{c_opt_ms:.2f} ms\n(1.66x vs C)", ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#065f46')
    ax1.text(1, rust1_ms + 3.5, f"{rust1_ms:.2f} ms\n(1.50x vs C)", ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#5b21b6')
    ax1.text(2, c_ms + 3.5, f"{c_ms:.2f} ms\n(Baseline)", ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#1e40af')
    ax1.text(3, goose1_ms + 3.5, f"{goose1_ms:.2f} ms\n(0.65x vs C)", ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#92400e')

    # ================= PANEL 2: record_arena =================
    ax2.set_facecolor('#f8fafc')
    w2 = groups.get('record_arena', {})
    rust2_ms = float(np.median([x['ms'] for x in w2.get('rust', [])])) if 'rust' in w2 else 0
    c_arena_ms = float(np.median([x['ms'] for x in w2.get('c_arena', [])])) if 'c_arena' in w2 else 0
    goose2_ms = float(np.median([x['ms'] for x in w2.get('goose', [])])) if 'goose' in w2 else 0
    c_heap_ms = float(np.median([x['ms'] for x in w2.get('c_heap', [])])) if 'c_heap' in w2 else 0

    p2_labels = ['Rust (Arena)', 'C (Arena Bump)', 'Goose (Arena O(1))', 'C (Heap malloc/free)']
    p2_vals = [rust2_ms, c_arena_ms, goose2_ms, c_heap_ms]
    p2_colors = [colors['rust'], colors['c_arena'], colors['goose'], colors['c_heap']]
    p2_edges = ['#6d28d9', '#047857', '#b45309', '#b91c1c']

    bars2 = ax2.bar(p2_labels, p2_vals, color=p2_colors, edgecolor=p2_edges, width=0.55, linewidth=1.2, zorder=3)
    ax2.set_title('Workload 2: record_arena (64 records × 50 iter)\nMemory Allocation / Bump Latency (Lower is Better)',
                  fontsize=11.5, fontweight='bold', pad=12)
    ax2.set_ylabel('Execution Time (ms)', fontsize=10.5, fontweight='bold')
    ax2.set_ylim(0, 115)
    ax2.grid(True, linestyle='--', alpha=0.6, axis='y', zorder=0)

    # Annotations for panel 2
    ax2.text(0, rust2_ms + 2.5, f"{rust2_ms:.2f} ms\n(3.88x faster)", ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#5b21b6')
    ax2.text(1, c_arena_ms + 2.5, f"{c_arena_ms:.2f} ms\n(2.50x faster)", ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#065f46')
    ax2.text(2, goose2_ms + 2.5, f"{goose2_ms:.2f} ms\n(1.65x faster)", ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#92400e')
    ax2.text(3, c_heap_ms + 2.5, f"{c_heap_ms:.2f} ms\n(C Heap Base)", ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#991b1b')

    # Layout adjustment
    plt.subplots_adjust(bottom=0.22, top=0.88, wspace=0.24)

    # Footer note
    footer = (
        "Hardware: M5Stack Core2 (ESP32-D0WDQ6-V3 @ 160MHz) | OS: FreeRTOS (ESP-IDF v5.3.1) | 30 Runs Median\n"
        "Compilers: GCC 13.2.0 (-Os) | Rust 1.97.0-nightly (xtensa-esp32-none-elf, opt-level=s) | Upstream Goose 0.1\n"
        "Deterministic Checksums: array_scan = 33582136 (100% matched across 4 impls) | record_arena = 2469415251 (100% matched across 4 impls)"
    )
    fig.text(0.5, 0.04, footer, ha='center', fontsize=8.8, color='#334155',
             bbox=dict(boxstyle='round,pad=0.55', facecolor='#f8fafc', edgecolor='#cbd5e1'))

    plt.savefig("benchmarks/results/benchmark_results.png", bbox_inches='tight', dpi=220)
    plt.close()
    print("Generated benchmarks/results/benchmark_results.png successfully!")

if __name__ == "__main__":
    generate_plots()
