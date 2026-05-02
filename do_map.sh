#!/bin/bash
#
# do_map.sh — PC-level MLP and stall ranking from perf traces
#
# PURPOSE
#   Reads a perf trace file containing per-PC MLP and stall records (fields
#   separated by '*'), aggregates them by PC address, and ranks each PC using
#   log2-bucketed average MLP level.
#
# USAGE
#   ./do_map.sh <trace_file> <output_name>
#   Output is written to ~/latencymaps/<output_name>
#
# INPUT FORMAT  (fields in each record, '*' as separator)
#   $1  = PC address (hex)
#   $12 = stall count
#   $16 = MLP count
#   Records must include the literal token "MLP" to be processed.
#
# OUTPUT COLUMNS (space-separated, one row per PC)
#   addr  avg_stalls  avg_mlp  log2_mlp_rank  rank_relative  log2_mlp
#   stalls_div16  mlp_div32  mlp_div64  log2_stalls  half_mlp_rank  half_mlp
#
# NOTES
#   - PCs with average MLP ≤ 1 (log2 ≤ 0) are omitted from the ranking output.
#   - rank_relative normalises the MLP rank against the smallest non-zero rank
#     seen across all PCs, so the output is relative rather than absolute.
#   - The smallest_s variable is initialised to 9999 but the stall baseline
#     (smallest_s) is not currently updated in the loop; stall-relative ranks
#     therefore use a fixed offset.

cat $1 | tr '*' '\n' | sort | awk '
/MLP/ {
    i = strtonum("0x" $1)
    stalls[i] += $12
    mlp[i] += $16
    c[i] += 1
}
END {
    n = 0
    for (k in stalls) n++
    print n " " n " " n " " n " " n " "

    PROCINFO["sorted_in"] = "@ind_str_asc"
    smallest = 9999
	smallest_s = 0009999

    for (k in stalls) {
        long_rank = int(log(int(mlp[k] / c[k])) / log(2))
        if (long_rank <= 0) {
            continue
        }
        if (long_rank != 0 && long_rank < smallest) {
            smallest = long_rank
        }
    }

    for (k in stalls) {
        long_rank = int(log(int(mlp[k] / c[k])) / log(2))
		long_stalls = int(log(int(stalls[k] / c[k]))/log(2))
        if (long_rank <= 0) { long_rank = 0 }
		if(long_stalls <= 0) { long_stalls = 0  }
        if (long_rank > 0) { long_rank_smaller = long_rank - (smallest) }
        if (long_stalls > 0) { long_stalls_smaller = long_stalls - (smallest_s -1) }
        print k " " int(stalls[k] / c[k]) " " int(mlp[k] / c[k]) " " long_rank " " long_rank_smaller " " int(log(int(mlp[k] / c[k])) / log(2))  " " int(stalls[k] / c[k] / 16) " " int(mlp[k] / c[k] / 32) " " int(mlp[k] / c[k] / 64) " " long_stalls " " int((2**long_rank_smaller)/2) " " int(mlp[k] / (2*c[k]) )
    }
}
' | tee ~/latencymaps/$2
