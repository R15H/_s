#!/bin/bash
#
# predicated_count.sh — count conditional-move instructions in a binary
#
# PURPOSE
#   Disassembles a binary with objdump and counts x86 CMOV (integer) and
#   FCMOV (floating-point) instructions.  Used to characterise benchmarks for
#   branch-prediction / predication sensitivity analysis.
#
# USAGE
#   ./predicated_count.sh <binary_file>
#
# OUTPUT (to stdout)
#   CMOV (integer): N
#   FCMOV (float):  N
#   Total:          N
#
# ROLE IN PIPELINE
#   Benchmark characterisation step.  Run once per binary to understand whether
#   a workload is branch-heavy vs predicated, which influences memory-access
#   pattern assumptions in the memory-tiering analysis.

# Simple script to count predicated move instructions
# Usage: ./simple_predicated_count.sh <binary_file>

if [[ $# -eq 0 ]]; then
    echo "Usage: $0 <binary_file>"
    exit 1
fi

BINARY="$1"

if [[ ! -f "$BINARY" ]]; then
    echo "Error: File '$BINARY' not found"
    exit 1
fi

echo "Analyzing predicated moves in: $BINARY"
echo "======================================"

# Disassemble and count CMOV instructions
echo "Counting x86/x86_64 conditional moves (CMOV)..."
CMOV_COUNT=$(objdump -d "$BINARY" | awk '
    /^[ 	]*[0-9a-f]+:/ {
        # Extract instruction part
        split($0, parts, "	")
        if (length(parts) >= 3) {
            instr = parts[3]
            split(instr, instr_parts, " ")
            # Check if instruction starts with cmov
            if (instr_parts[1] ~ /^cmov/) {
                count++
            }
        }
    }
    END { 
        print "Total CMOV instructions: " (count + 0) > "/dev/stderr"
        print count + 0 
    }
')

# Count FCMOV instructions  
echo ""
echo "Counting floating-point conditional moves (FCMOV)..."
FCMOV_COUNT=$(objdump -d "$BINARY" | awk '
    /^[ 	]*[0-9a-f]+:/ {
        split($0, parts, "	")
        if (length(parts) >= 3) {
            instr = parts[3]
            split(instr, instr_parts, " ")
            if (instr_parts[1] ~ /^fcmov/) {
                count++
            }
        }
    }
    END { 
        print "Total FCMOV instructions: " (count + 0) > "/dev/stderr"
        print count + 0 
    }
')

TOTAL=$((CMOV_COUNT + FCMOV_COUNT))

echo ""
echo "SUMMARY:"
echo "========="
echo "CMOV (integer): $CMOV_COUNT"
echo "FCMOV (float):  $FCMOV_COUNT"
echo "Total:          $TOTAL"

      