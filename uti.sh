#!/bin/bash
#
# uti.sh — side-by-side pairing of synthetic and real results
#
# PURPOSE
#   Reads the last 50 lines from ~/synthethic_results and ~/all_results in
#   parallel (using separate file descriptors) and prints each corresponding
#   pair on one line.  Used for quick ad-hoc comparison of synthetic vs real
#   run data without a full join.
#
# USAGE
#   ./uti.sh          (no arguments; paths are hardcoded)
#
# OUTPUT
#   One line per pair: <synthethic_results_line> <all_results_line (col5 only)>

while IFS= read -r line1 <&3 && IFS= read -r line2 <&4; do
    echo "$line1 $line2"
done 3< <(cat ~/synthethic_results | tail -n 50) 4< <(cat ~/all_results | awk '{print $5}' | tail -n 50)