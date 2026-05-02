#!/usr/bin/env python3
"""
plot_costs.py — bar chart of HTMM sampling function cycle costs vs weight-map size

PURPOSE
  Reads the output of real_analysis.sh:gen_cost_plots from stdin and produces a
  grouped bar chart comparing the cycle cost of find_ip_weight (cost1) and
  update_pginfo (cost2) across different weight-map sizes and data structure
  types (struct 1 vs struct 5).  Multiple runs for the same (struct, add_limit)
  are averaged.

ROLE IN PIPELINE  (step 4 of 4 — visualisation)
  gen_cost_plots in real_analysis.sh → stdout → plot_costs.py → SVG/PDF

INPUT FORMAT  (stdin, space-separated tokens on one line or multiple lines)
  struct: <N>  add_limt: <M>  costs: <cost1> <cost2> <samples>  -  [...]

OUTPUT FILES
  costs_plot[_normalized][_mapped][_no_struct5].svg   (default)
  costs_plot_*_paper.pdf                              (with --paper)
  costs_proportion_plot[_paper].{svg,pdf}             (with --proportion)
  costs_per_sample_plot[_paper].{svg,pdf}             (with --sample-proportion)

KEY FLAGS
  --proportion        plot cost1/cost2 ratio instead of absolute costs
  --sample-proportion plot costs divided by sample count
  --map-x-axis        replace add_limit with mapped value from hardcoded bcBALA_ table
  --normalize-x-axis  express X-axis as multiples of the smallest value (e.g. 1x, 2x)
  --ignore-struct-5   exclude struct-5 bars from the plot
  --paper             compact 3.5×2.5" figure with small fonts, saved as PDF

Usage:
    echo "struct: 1 add_limt: 16 costs: 559 13943 1000 - ..." | python plot_costs.py
    cat data.txt | python plot_costs.py
    python plot_costs.py --proportion  # Plot cost1/cost2 proportion instead of individual costs
    python plot_costs.py --sample-proportion  # Plot costs per sample instead of absolute costs
    python plot_costs.py --map-x-axis  # Map X-axis values from file paths instead of using add_limit
"""

import sys
import re
import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections import defaultdict

# ── Parse arguments ─────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description='Plot costs or cost proportions')
parser.add_argument('--proportion', action='store_true', 
                    help='Plot cost1/cost2 proportion instead of individual costs')
parser.add_argument('--sample-proportion', action='store_true', 
                    help='Plot costs per sample instead of absolute costs')
parser.add_argument('--map-x-axis', action='store_true',
                    help='Map X-axis values from file paths instead of using add_limit')
parser.add_argument('--ignore-struct-5', action='store_true',
                    help='Ignore struct 5 from plotting')
parser.add_argument('--normalize-x-axis', action='store_true',
                    help='Normalize X-axis values as multipliers of the smallest value')
parser.add_argument('--paper', action='store_true',
                    help='Paper-ready output: compact size, small fonts, PDF')
args = parser.parse_args()

# ── Parse stdin ──────────────────────────────────────────────────────────────
raw = sys.stdin.read()
#maybe I can just specify a list of files (where you will do wc -l ) instead of me passing the output of wc -l from the terminal 
mappp="""
      432 /home/ist196723/nas/bcBALA_1
    89410 /home/ist196723/nas/bcBALA_1_1000
   502332 /home/ist196723/nas/bcBALA_1_10000
  3550398 /home/ist196723/nas/bcBALA_1_1000000
     3155 /home/ist196723/nas/bcBALA_1_16
      645 /home/ist196723/nas/bcBALA_1_2
   153491 /home/ist196723/nas/bcBALA_1_2000
    25085 /home/ist196723/nas/bcBALA_1_208
     6262 /home/ist196723/nas/bcBALA_1_38
   255211 /home/ist196723/nas/bcBALA_1_4000
    50356 /home/ist196723/nas/bcBALA_1_490
   299233 /home/ist196723/nas/bcBALA_1_5000
  2550398 /home/ist196723/nas/bcBALA_1_500000
     1450 /home/ist196723/nas/bcBALA_1_6
     3155 /home/ist196723/nas/bcBALA_16
 11762315 /home/ist196723/nas/bcBALA_1_6000000
    12551 /home/ist196723/nas/bcBALA_1_90
      645 /home/ist196723/nas/bcBALA_2
   156323 /home/ist196723/nas/bcBALA_2048
    25085 /home/ist196723/nas/bcBALA_208
     6262 /home/ist196723/nas/bcBALA_38
    50356 /home/ist196723/nas/bcBALA_490
     1450 /home/ist196723/nas/bcBALA_6
    12551 /home/ist196723/nas/bcBALA_90
    85711 /home/ist196723/nas/bcBALA_950
"""

# Function to extract add_limit from file path
def extract_add_limit_from_path(path):
    """Extract the last number from a file path."""
    # Split by underscore and take the last part
    parts = path.split('_')
    if parts:
        last_part = parts[-1]
        # Extract any digits from the last part
        match = re.search(r'\d+', last_part)
        if match:
            return int(match.group())
    return None

# Parse both the original format and file path format
pattern = re.compile(r"struct:\s*(\d+)\s+add_limt:\s*(\d+)\s+costs:\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)")
path_pattern = re.compile(r"^(\s*\d+)\s+(/home/ist196723/nas/bcBALA_[^\s]+)")

# Accumulate multiple runs → average them
buckets = defaultdict(list)   # (struct, add_limit) -> [(c1, c2, samples), ...]
path_mappings = {}  # add_limit -> mapped_value

# First, check if we have path format data and extract mappings
if args.map_x_axis:
    for line in mappp.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        match = path_pattern.match(line)
        if match:
            value = int(match.group(1).strip())
            path = match.group(2)
            mapped_value = extract_add_limit_from_path(path)
            if mapped_value is not None:
                path_mappings[value] = mapped_value

def invert_keys_to_values(d):
    return {v: k for k, v in d.items()}

# Parse the main data format
path_mappings= invert_keys_to_values(path_mappings)
for m in pattern.finditer(raw):
    struct     = int(m.group(1))
    add_limit  = int(m.group(2))
    cost1      = int(m.group(3))
    cost2      = int(m.group(4))
    lock_cost  = int(m.group(5))
    samples    = int(m.group(6))

    # Apply mapping if requested and available

    print(add_limit, "JJJ")
    print(path_mappings.values())
    if args.map_x_axis and int(add_limit) in path_mappings:
        mapped_limit = path_mappings[int(add_limit)]
        print("MAPPED LIMIT", mapped_limit)
    else:
        mapped_limit = add_limit
        print("NORMAL LIMIT", mapped_limit)

    buckets[(struct, mapped_limit)].append((cost1, cost2, lock_cost, samples))

if not buckets:
    sys.exit("No data parsed — check that input matches expected format.")

# Average repeated (struct, add_limit) pairs
averaged = {}
for (struct, add_limit), runs in buckets.items():
    c1      = np.mean([r[0] for r in runs])
    c2      = np.mean([r[1] for r in runs])
    lock    = np.mean([r[2] for r in runs])
    samples = np.mean([r[3] for r in runs])
    averaged[(struct, add_limit)] = (c1, c2, lock, samples)

# ── Organise for plotting ────────────────────────────────────────────────────
# Filter out struct 5 if requested
if args.ignore_struct_5:
    filtered_keys = [k for k in averaged.keys() if k[0] != 5]
    filtered_averaged = {k: v for k, v in averaged.items() if k[0] != 5}
else:
    filtered_keys = averaged.keys()
    filtered_averaged = averaged

structs     = sorted({k[0] for k in filtered_keys})
x_values    = sorted({k[1] for k in filtered_keys})

# Determine what to show on X-axis
if args.normalize_x_axis and x_values:
    # Normalize as multipliers of the smallest value
    min_value = min(x_values)
    print("MINIMOOOO", min_value) # 432
    x_labels = [f"{val/min_value:.1f}x" for val in x_values]
    x_label_name = "normalized_add_limit"
else:
    x_labels = [str(val) for val in x_values]
    x_label_name = "mapped_add_limit" if args.map_x_axis else "add_limit"

x = np.arange(len(x_values))

if args.proportion:
    n_bars = len(structs)       # one bar per struct
else:
    n_bars = len(structs) * 3   # 3 bars per struct: find_ip_weight, update_pginfo, processing loop

bar_w    = 0.8 / n_bars
offsets  = np.linspace(-(n_bars - 1) / 2, (n_bars - 1) / 2, n_bars) * bar_w

# Colour palette
if args.proportion:
    palette = {
        1: "#4C9BE8",   # struct 1
        5: "#F4845F",   # struct 5
    }
else:
    palette = {
        (1, 0): "#4C9BE8",   # struct 1 – find_ip_weight
        (1, 1): "#1A5FA8",   # struct 1 – update_pginfo (non-lock)
        (1, 2): "#7B3FB8",   # struct 1 – lock overhead
        (1, 3): "#2CA02C",   # struct 1 – processing loop
        (5, 0): "#F4845F",   # struct 5 – find_ip_weight
        (5, 1): "#B83A10",   # struct 5 – update_pginfo (non-lock)
        (5, 2): "#4B1080",   # struct 5 – lock overhead
        (5, 3): "#1A7A1A",   # struct 5 – processing loop
    }

# ── Draw ─────────────────────────────────────────────────────────────────────
if args.paper:
    figsize = (3.5, 2.5)
    fs_base, fs_tick, fs_legend = 7, 6, 6
    plt.rcParams.update({'font.size': fs_base, 'axes.labelsize': fs_base,
                         'xtick.labelsize': fs_tick, 'ytick.labelsize': fs_tick})
else:
    figsize = (max(10, len(x_values) * 1.2), 6)
    fs_base, fs_tick, fs_legend = 12, 9, 11

fig, ax = plt.subplots(figsize=figsize)

bar_idx = 0
legend_handles = []

if args.proportion:
    # Plot proportions
    for struct in structs:
        color = palette.get(struct, f"C{bar_idx}")
        values = [filtered_averaged.get((struct, x_val), (np.nan, np.nan, np.nan))[0] / 
                  filtered_averaged.get((struct, x_val), (np.nan, np.nan, np.nan))[1]
                  for x_val in x_values]
        values = np.array(values) *100

        bars = ax.bar(
            x + offsets[bar_idx],
            values,
            width=bar_w * 0.92,
            color=color,
            edgecolor="white",
            linewidth=0.5,
            label=f"struct {struct} – cost1/cost2",
        )
        legend_handles.append(mpatches.Patch(color=color,
                                              label=f"struct {struct} – cost1/cost2"))
        bar_idx += 1
else:
    # Plot 3 bars per struct: find_ip_weight | update_pginfo (lock@bottom) | processing loop
    nan4 = (np.nan, np.nan, np.nan, np.nan)
    label_suffix = " per sample" if args.sample_proportion else ""
    seen_labels = set()

    def _get(struct, x_val, idx):
        v = filtered_averaged.get((struct, x_val), nan4)[idx]
        if args.sample_proportion:
            s = filtered_averaged.get((struct, x_val), nan4)[3]
            return v / s * 100 if s else np.nan
        return v

    for struct in structs:
        struct_label = f" (struct {struct})" if len(structs) > 1 else ""

        # ── bar 0: find_ip_weight ───────────────────────────────────────────
        color = palette.get((struct, 0), f"C{bar_idx}")
        values = [_get(struct, xv, 0) for xv in x_values]
        ax.bar(x + offsets[bar_idx], values, width=bar_w * 0.92,
               color=color, edgecolor="white", linewidth=0.5)
        lbl = f"Weight lookup\n($\\mathtt{{find\\_ip\\_weight}})${struct_label}"
        if lbl not in seen_labels:
            legend_handles.append(mpatches.Patch(color=color, label=lbl))
            seen_labels.add(lbl)
        bar_idx += 1

        # ── bar 1: update_pginfo with lock overhead at bottom ───────────────
        c2_color   = palette.get((struct, 1), f"C{bar_idx}")
        lock_color = palette.get((struct, 2), "#7B3FB8")
        c2_vals    = [_get(struct, xv, 1) for xv in x_values]
        lock_vals  = [_get(struct, xv, 2) for xv in x_values]
        non_lock   = [max(0, c2 - lv) for c2, lv in zip(c2_vals, lock_vals)]
        # lock at the very bottom (bottom=0)
        ax.bar(x + offsets[bar_idx], lock_vals, width=bar_w * 0.92,
               color=lock_color, edgecolor="white", linewidth=0.5)
        # non-lock portion stacked on top of lock
        ax.bar(x + offsets[bar_idx], non_lock, bottom=lock_vals, width=bar_w * 0.92,
               color=c2_color, edgecolor="white", linewidth=0.5)
        for lbl, col in [(f"Lock overhead{struct_label}", lock_color),
                         (f"Page info update\n$(\\mathtt{{update\\_pginfo}})${struct_label}", c2_color)]:
            if lbl not in seen_labels:
                legend_handles.append(mpatches.Patch(color=col, label=lbl))
                seen_labels.add(lbl)
        bar_idx += 1

        # ── bar 2: processing loop (samples − cost1 − cost2) ────────────────
        proc_color = palette.get((struct, 3), "#2CA02C")
        if args.sample_proportion:
            proc_vals = [max(0, 100.0 - _get(struct, xv, 0) - _get(struct, xv, 1))
                         for xv in x_values]
        else:
            proc_vals = [max(0, _get(struct, xv, 3) - _get(struct, xv, 0) - _get(struct, xv, 1))
                         for xv in x_values]
        ax.bar(x + offsets[bar_idx], proc_vals, width=bar_w * 0.92,
               color=proc_color, edgecolor="white", linewidth=0.5)
        lbl = f"Processing loop{struct_label}"
        if lbl not in seen_labels:
            legend_handles.append(mpatches.Patch(color=proc_color, label=lbl))
            seen_labels.add(lbl)
        bar_idx += 1

# ── Labels & formatting ──────────────────────────────────────────────────────
ax.set_xticks(x)
ax.set_xticklabels(x_labels, rotation=45, ha="right", fontsize=fs_tick)
x_label_name = "Weight Map Size (relative to baseline)"
ax.set_xlabel(x_label_name, fontsize=fs_base)

if not args.paper:
    if args.proportion:
        ax.set_title(f"Cost1/Cost2 Proportion by {x_label_name} and struct", fontsize=13, fontweight="bold")
    elif args.sample_proportion:
        ax.set_title(f"Cost per Sample by {x_label_name} and struct", fontsize=13, fontweight="bold")
    else:
        ax.set_title("Cycle cost of update_pginfo and find_ip_weight vs. map size", fontweight="none", fontsize=13)

if args.proportion:
    ax.set_ylabel("Cost1/Cost2 Proportion", fontsize=fs_base)
elif args.sample_proportion:
    ax.set_ylabel("CPU usage (%)", fontsize=fs_base)
else:
    ax.set_ylabel("Fraction of total cycles (%)", fontsize=fs_base)

ax.legend(handles=legend_handles, framealpha=0.9, fontsize=fs_legend, loc='center right')
ax.yaxis.grid(True, linestyle="--", alpha=0.5)
ax.set_axisbelow(True)

plt.tight_layout()
if args.proportion:
    base = "costs_proportion_plot"
elif args.sample_proportion:
    base = "costs_per_sample_plot"
else:
    suffix = "_normalized" if args.normalize_x_axis else ""
    suffix += "_mapped" if args.map_x_axis else ""
    suffix += "_no_struct5" if args.ignore_struct_5 else ""
    base = f"costs_plot{suffix}"

if args.paper:
    output_file = f"{base}_paper.pdf"
    plt.savefig(output_file, bbox_inches='tight', dpi=600)
else:
    output_file = f"{base}.svg"
    plt.savefig(output_file, dpi=150)
print(f"Saved → {output_file}")
plt.show()
