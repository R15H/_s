#!/bin/bash
#
# real_analysis.sh — per-run metric extraction for memory-tiering experiments
#
# PURPOSE
#   Extracts and aggregates performance metrics from detailed per-run log files
#   produced by the HTMM/ASMEM/MEMTIS/TPP benchmark harness.  The canonical
#   entry point is `desired_metrics`, which produces the file `super_desired`
#   used by downstream Python plotting scripts.
#
# KEY GLOBALS
#   BASE    — memory-system variant tag embedded in log file names
#             (e.g. ASMEM, MEMTIS-1, TPP, MEMTIS-NULL-299)
#   runID   — Unix-timestamp run identifier, also used as a file-name suffix
#   mempath — root of per-run log tree
#             (~/nas/latency_benchmark/tests_syn/plot_time_math)
#   sourceF — aggregated results file  (~/nas/all_results  or  ~/nas/bad_alto_res)
#
# LOG FILE LAYOUT  ($mempath/detailed/<dim>-<BASE>-<runID>)
#   taskclock      — perf-stat CPU-clock samples (used to compute wall/cpu time)
#   perf           — perf-stat hardware counters  (e.g. stalls_l3_miss, INST)
#   vmstat         — periodic /proc/vmstat snapshots  (htmm_nr_promoted/demoted)
#   journal        — HTMM daemon log  (hit ratio, nr_sampled, total runtime …)
#   ratio_over_time— hit-ratio time series
#
# UTILITY FUNCTIONS
#   average          — awk: arithmetic mean of $1
#   sum              — awk: sum of $1
#   numeralize       — replace non-numeric tokens with 0
#   remove_comma     — strip thousands-separator commas
#   delta_over_time  — awk: consecutive differences of $2 (timestamped series)
#   delta_first_last — awk: last $2 minus first $2 (total delta)
#   get_dim <d>      — cat $mempath/detailed/<d>-$BASE-$runID
#   echo_dim <d>     — print the path (no read)
#   get_clock        — shorthand: get_dim taskclock
#
# DESIRED_METRICS / super_desired  (see detailed note below)
#   Iterates every run in ~/nas/all_results, collects six metrics per run, and
#   appends complete rows to the file `super_desired`.  Rows with any missing
#   metric are skipped and reported to stderr.
#
# OTHER TOP-LEVEL FUNCTIONS
#   get_over_time_all  — extract all time-series metrics for one (BASE, runID)
#   s / sp / first_synth — run get_over_time_all for hardcoded run sets
#   gett               — sampling overhead stats for one run
#   generate_cost      — sampling CPU cost for a list of runs
#   gen_cost_plots     — perf-stack cost pipeline → plot_costs.py
#   bc_sampler / mg_sampler / set_bench — populate per-system run-ID lists
#   compare            — percent diff ASMEM vs MEMTIS on an awk expression
#
# EXECUTION
#   The script ends with `$@; exit`, so pass a function name as an argument:
#     ./real_analysis.sh desired_metrics
#     ./real_analysis.sh s
#   Everything after the exit is dead/historical code kept for reference.
#
# OUTPUT FILES (written to the working directory)
#   super_desired            — see desired_metrics section below
#   _<BASE>_<metric>-overtime — per-system time-series vectors for plotting
#   over_time_files          — manifest of overtime vector files
#   used_over_time_files     — log of log paths actually read
#
# ─── desired_metrics / super_desired ──────────────────────────────────────────
#
#   `desired_metrics` builds a compact, analysis-ready summary of every run in
#   ~/nas/all_results.  For each (BASE, runID) pair it reads five sources:
#
#     promotions   — total HTMM page promotions   (vmstat htmm_nr_promoted,
#                    delta from first to last sample)
#     demotions    — total HTMM page demotions     (vmstat htmm_nr_demoted,
#                    same method)
#     stalls       — total L3-miss stall cycles    (perf stalls_l3_miss, summed
#                    across all intervals)
#     access_ratio — DRAM hit ratio in %           (journal: dram_hits*100/
#                    (dram_hits+dram_misses))
#     time         — net CPU-time in ms            (taskclock: sum(cpu_time *
#                    cpu_count) − wall_time)
#
#   A row is written to `super_desired` only if ALL six fields are non-empty.
#   Incomplete rows are skipped with a stderr report listing which fields are
#   absent.  A running "Processed / Skipped" counter is printed on stderr.
#
#   super_desired column layout:
#     BASE  runID  promotions  demotions  stalls  access_ratio  time
# ──────────────────────────────────────────────────────────────────────────────

average(){
    awk -v OFMT='%.10f'  '{a+=$1; b+=1;  } END {print a/b}'
}


# 230 instructions
#cat ~/nas/all_results | grep -E "bck|kron"  | grep ASMEM  
#cat ~/nas/all_results | grep -E "bck|kron"  | grep "MEMTIS "

BASE="ASMEM"
bench_regex="bck|kron"
bench_regex="mg"
set -ex
sourceF=~/nas/all_results
sourceF=~/nas/bad_alto_res
bc_sampler(){
    sourceF=~/nas/bad_alto_res
    bench_regex="bck|kron"
    BASE="ASMEM"
    cat  $sourceF | grep -E "$bench_regex"  | grep $BASE | awk '$6 ~ /17/ {print $6 }' > _$BASE\_bc # $3 is DRAM
    echo "cat  $sourceF | grep -E \"$bench_regex\"  | grep \"$BASE \" | awk '\$6 ~ /17/ {print $6 }'"
    BASE="MEMTIS"
    cat $sourceF | grep -E "$bench_regex"  | grep "$BASE " | awk '$6 ~ /17/ {print $6 }' > _$BASE\_bc # $3 is DRAM

}
mg_sampler(){
    bench_regex="mg"
    sourceF=~/nas/bad_alto_res
    BASE="ASMEM"
    cat  /home/ist196723/nas/bad_alto_res | grep -E "mg"  | grep "$BASE "  | awk ' / 176/ {print $7 }' > _$BASE\_bc
    BASE="MEMTIS"
    cat  /home/ist196723/nas/bad_alto_res | grep -E "mg"  | grep "$BASE "  | awk ' / 176/ {print $7 }' > _$BASE\_bc
}

#cat  /home/ist196723/nas/bad_alto_res | grep -E "mg"  | grep "$BASE "  | awk ' / 176/ {print $7 }' > _$BASE\_bc
#cat  /home/ist196723/nas/bad_alto_res | grep -E "mg"  | grep "$BASE "  | awk ' / 176/ {print $7 }' > _$BASE\_bc
#cat _$BASE\_bc
set_bench(){
mg_sampler
bc_sampler
}


echo_dim(){
    dim=$1
    echo $mempath/detailed/$dim-$BASE-$runID 
}
get_dim(){
    dim=$1
    echo  $mempath/detailed/$dim-$BASE-$runID  >> used_over_time_files
    cat $mempath/detailed/$dim-$BASE-$runID 
}
get_clock(){
    get_dim taskclock
     #echo $mempath/detailed/-$BASE-$now_in_seconds 
}


get_dim_soar(){
    dim=$1; runID=$2;
    tpp_path="/home/ist196723/nas/tools/SoarAlto/run/bc-urand/rst/"
    file="$tpp_path/rst-$BASE/$dim-th0-$runID.log"
}

delta_over_time(){
 awk 'NR==1 { prev = $2; next } { elapsed=($2-prev); prev=$2; print elapsed}' 
}
delta_first_last(){
    #delta_over_time

    awk 'NR==1 { first = $2; next } { prev=$2;} END { print prev - first}' 
    

}
# 400
save_to_time(){
    echo - 

}
mempath=~/nas/latency_benchmark/tests_syn/plot_time_math
get_most_recent(){
    BASE=$1
    BENCH=$2
    #runID=$(ls -t $mempath/detailed | grep $BASE | tail -n1)
    id=$(cat ~/nas/all_results   | grep "$BENCH" | grep "2000" | grep "$BASE" | tail -n1 | head -n1 | tr ' ' '\n' | awk '/176/{print $1}')
    id=$(cat ~/nas/all_results   | grep "$BENCH" | grep "2000" | grep "$BASE" | tail -n1 | head -n1 | tr ' ' '\n' | awk '/176/{print $1}')
    echo "FOUND RUN ID FOR $BASE $id" 1>&2
    echo $id
}

samp_cost(){
    get_dim "journal" $runID | grep htmm_promote | delta_over_time  > _$BASE\_htmm_promote-overtime
    
}


remove_comma(){
    sed "s/,//g" 
}

save_output(){
    file=$1
    shift 1
    $@ > $file
}
ensure_non_null_output(){
    # if stdin is empty then echo -
    if [ -z "$(cat -)" ]; then
        echo "BIG_MISTAKE"
    fi
}
numeralize(){
    awk '{if ($1 ~ /[0-9]+/) {print $1; } else { print 0; }} '
}

allo(){
        awk 'BEGING{r=0;l=0} /Runtime/ {r=$2; } /Lookups/ {l=$2} /Average Time:/ {r=$3 } /Time in seconds/ {r=$5; } /Mop/ {l=$4} /Time taken/{r=$3} /TIME_STATS/{if(!r){ r=$2;} } END {print r " " l}'
}
get_over_time_all(){
    echo ----------
    echo $BASE
    #get_dim "taskclock" $runID |  awk '{print $2}'  | remove_comma | average
    #return
    file=_$BASE\_taskclock-overtimeTOTAL
    get_dim "taskclock" $runID | awk '/CPU/ {print $2 " " $1}' |  remove_comma | awk '{a+=$1; b+=$2; if($4 > max_cpus) {max_cpus=4}} END {print a*int(max_cpus)-b}' > $file
    cat $mempath/detailed/$runID  | allo > _$BASE\_time
    

    file=_$BASE\_taskclock-overtime
    get_dim "taskclock" $runID | awk '/CPU/ {print $2}' |  remove_comma > $file

    echo $file >> over_time_files
    get_dim "ratio_over_time" $runID | awk '/HIT_RATIOO/ {print $5;  }' |  numeralize >  _$BASE\_hit_ratio-overtimeY # '{print $2 " " ($1 + $4) }' 
    echo _$BASE\_hit_ratio-overtimeY >> over_time_files
    get_dim "ratio_over_time" $runID  | awk '/HIT_RATIOO/ {print $6 + $7;  }'  | numeralize | cut -d '.' -f 1 |  tee >(ensure_non_null_output)  _$BASE\_reads_done-overtimeX 1 > /dev/null # timestamps 
    get_dim "ratio_over_time" $runID  | awk '/HIT_RATIOO/ {print $1;  }'  | numeralize | cut -d '.' -f 1 |  tee >(ensure_non_null_output)  _$BASE\_hit_ratio-overtimeX 1 > /dev/null # timestamps

    get_dim "journal" $runID  | awk '/hit ratio/ {print $7*100/($7+$12)  }'   >   _$BASE\_hit_ratioTOTAL 
    
    echo _$BASE\_hit_ratio-overtimeX >> over_time_files
    get_dim "perf" $runID |  awk ' /stalls_l3_miss/ {print $2 } ' | numeralize | remove_comma  > _$BASE\_stalls_l3_miss-overtime
    echo _$BASE\_stalls_l3_miss-overtime >> over_time_files
    get_dim "perf" $runID   |  awk ' /INST/ {print $2 } '   | numeralize | remove_comma  > _$BASE\_instructions-overtime
    echo _$BASE\_instructions-overtime >> over_time_files
    target=htmm_nr_promoted
    get_dim "vmstat" $runID | grep $target | delta_over_time  > _$BASE\_$target-overtime
    echo _$BASE\_$target-overtime >> over_time_files
    echo "prom " $( get_dim "vmstat"  $runID | grep $target | delta_first_last )
    target=htmm_nr_demoted
    get_dim "vmstat"  $runID| grep $target | delta_over_time  > _$BASE\_$target-overtime

    echo _$BASE\_$target-overtime >> over_time_files
    echo "demo " $( get_dim "vmstat"  $runID | grep $target | delta_first_last )

}

desired_metrics(){
    cat ~/nas/all_results | awk '{print $5 " " $6 " " $1}' | {
    skipped=0
    processed=0
    echo "" > super_desired
    while read -r line; do
    {
        BASE="$(echo $line | awk  '{ print $1 }')"
        runID="$(echo $line | awk  '{ print $2 }')"
        #time="$(echo $line | awk  '{ print $3 }')"
        promotions=$(get_dim "vmstat" $runID | grep htmm_nr_promoted | delta_first_last)
        demotions=$(get_dim "vmstat"  $runID | grep htmm_nr_demoted  | delta_first_last)
        stalls=$(get_dim "perf" $runID   |  awk ' /stalls_l3_miss/ {print $2 } ' | numeralize | remove_comma | sum)
        access_ratio=$(get_dim "journal" $runID | awk '/dram_hits/ {print $7*100/$12}' )
        time=$(get_dim "taskclock" $runID | awk '/CPU/ {print $2 " " $1}' |  remove_comma | awk '{a+=$1; b+=$2; if($4 > max_cpus) {max_cpus=4}} END {print a*int(max_cpus)-b}')
        #echo "$BASE" "$runID" "$promotions" "$demotions" "$stalls" "$access_ratio" $time
    } 2>/dev/null
        if [[ -n "$BASE" && -n "$runID" && -n "$time" && -n "$promotions" && -n "$demotions" && -n "$stalls" && -n "$access_ratio" ]]; then
            echo "$BASE" "$runID" "$promotions" "$demotions" "$stalls" "$access_ratio" $time >> super_desired
            processed=$((processed + 1))
        else
            missing=""
            [[ -z "$BASE" ]] && missing+="BASE "
            [[ -z "$runID" ]] && missing+="runID "
            [[ -z "$time" ]] && missing+="time "
            [[ -z "$promotions" ]] && missing+="promotions "
            [[ -z "$demotions" ]] && missing+="demotions "
            [[ -z "$stalls" ]] && missing+="stalls "
            [[ -z "$access_ratio" ]] && missing+="access_ratio "
            printf "\r\e[KFailed on BASE=%s runID=%s. Missing: %s\n" "$BASE" "$runID" "$missing" >&2
            skipped=$((skipped + 1))
        fi
        printf "\r\e[KProcessed: %d, Skipped: %d" "$processed" "$skipped" >&2
    done 
    echo >&2
}
}


s(){
    echo "" > used_over_time_files
    echo "" > over_time_files
    while read -r col1 col2 col3 col4 BASE runID col7; do
        get_over_time_all
    done << "EOF" 
155.827160 0 185 0 ASMEM 1764604115 outa
156.969742 0 185 0 MEMTIS-1 1764604322 outa
169.683775 0 185 0 ASMEM 1764604528 outa
169.577488 0 185 0 MEMTIS-1 1764604745 outa
187.800194 0 185 0 ASMEM 1764604963 outa
186.920663 0 185 0 MEMTIS-1 1764605198 outa
298.992354 0 185 0 ASMEM 1764605432 outa
296.825983 0 185 0 MEMTIS-1 1764605780 outa
812.696846 0 185 0 ASMEM 1764606127 outa
811.608676 0 185 0 MEMTIS-1 1764606989 outa
EOF

}
sum(){
    awk '{a+=$1} END {print a}'
}

#BASE=MEMTIS-1-299 
#runID=1770474259 


sp(){
     BASE=MEMTIS-1-299 
     runID=1770474259 

    echo "" > used_over_time_files
    echo "" > over_time_files
    get_over_time_all


    BASE=ASMEM-F10-5000nostore-299
    runID=1770484861 

    get_over_time_all
}

# 200 ptr chase reads 
first_synth(){
runID="1764604115"
runID="1764611953"
    BASE="ASMEM"

    echo "" > used_over_time_files
    echo "" > over_time_files
    get_over_time_all
    # perf stat -C 0 -a uncore_imc_0/cas_count_read/,uncore_imc_0/cas_count_write/ -I 1000

    BASE="MEMTIS-1"
runID="1764604322"
runID="1764612106"
    get_over_time_all

# it migrates less pages! less memory trahsing (migration does nto cause stalls..)
    runID=1764765206 
    BASE="MEMTIS-1"
    get_over_time_all
    runID=1764764987
    BASE="ASMEM"
    get_over_time_all

    BASE="ASMEM"
    #14.765981 0 185 0 ASMEM 1764761052 outa
#19.857155 0 185 0 MEMTIS-1 1764761113 outa
    runID="1764761052"
    get_over_time_all
    BASE="MEMTIS-1"
    runID="1764761113"
    get_over_time_all

}
gett(){


    #nr_sampled / total time 

nr_sampled=$(get_dim "journal" $runID |  awk '/nr_sampled/  {print $7 }') # $22/$23; }' 
total_time_sampling=$(get_dim "journal" $runID |  awk '/total runtime:/  {print $22 }') # $22/$23; }' 
echo time per sample $(echo $nr_sampled $total_time_sampling | awk '{print $2/$1}')
nr_lost="$(get_dim "journal" $runID | awk '/nr_lost/ {print $11}')"

#get_dim "journal" $runID 

get_dim "journal" $runID |  awk '/total runtime:/ {print $0}' # '{print $22/$23; }' 
get_dim "journal" $runID |  awk '/sampled/  {print $0 }' # $22/$23; }' 
    echo total_samlpe_time/run_Time
    get_dim "journal" $runID |  awk '/total runtime:/ {print $22/$23; }' 
    echo  average time per sample '(usefull)'
    get_dim "journal" $runID | awk '/total runtime:/ {print $22/$8; }' # '{print $2 " " ($1 + $4) }' 
    echo  average time per sample '(total)'
    get_dim "journal" $runID | awk '/total runtime:/ {print $23/$8; }' # '{print $2 " " ($1 + $4) }' 


}
set +xe
echo SAD .. 

generate_cost(){
    while read -r line; do
        BASE="$(echo $line | awk  '{ print $5 }')"
        runID="$(echo $line | awk  '{ print $6 }')"
        intensity=$(echo $line | awk  '{ print $5 }' |   cut -d'_' -f 3 | cut -d '-' -f 1 )
        cost=$(get_dim "journal" $runID | awk '/total cputime:/{ print $12 }')
        #
        percentAwake=$(get_dim "journal" $runID  | awk '/total runtime:/ { print  $12/$16*100*1000; }') # 1>&2
        cost=$(get_dim "journal" $runID  | awk '/total runtime:/ { print  $22; }') # 1>&2
        totcputime=$(get_dim "journal" $runID  | awk '/total runtime:/ { print  $22; }') # 1>&2

	#echo $totrtime  $totcputime "GETTING " 1>&2
	echo $percentAwake "GETTING " 1>&2
	echo 

        #continue
	echo $( get_dim "journal" $runID  | awk '/total runtime:/ { print  $0 }') 1>&2
        if [ -z "$cost" ] ; then
            continue
        fi
        echo  $intensity  $cost
        done
}

_gperf_samples(){
	sudo perf report -i $mempath/detailed/perf-stack-$BASE-$ID --stdio  -g none -n --stdio |  awk -v total="$nr_samples" '
  /^\s*[0-9]/ {
    children_pct = $1
    self_pct     = $2
    symbol       = $NF
    gsub(/%/, "", children_pct)
    gsub(/%/, "", self_pct)
    children_samples = int(children_pct * total / 100)
    self_samples     = int(self_pct     * total / 100)
    #printf "%s  children=%-8d self=%-8d %s\n", $0, children_samples, self_samples, symbol
	print children_samples, $0
  } ' | tee ~/nas/perfro/perf-stack-$BASE-$ID   1>&2

}
get_fun_cost(){
	BASE=$1
	ID=$2
	#perf script -i $mempath/detailed/perf-stack-$BASE-$ID --stdio
	pfile="$mempath/detailed/perf-stack-$BASE-$ID"
	##--no-children
	fnr_samples="$(realpath ~/nas/perfro/perf-stack-$BASE-$ID-samples)"
	nr_samples="$(cat $fnr_samples)"  ####### MIXED FILE W/ RESULT OF FILE
#_gperf_samples
#continue

	echo $pfile 1>&2
	#sudo perf script -i $pfile   
	echo --- 1>&2
	#sudo perf report -i $pfile   --stdio -n -g none | awk ' !/#/ {a+= $3; } END { print a } ' | tee  $nr_samples  1>&2
	# awk '/# Samples/ { print $3 }' | cut -f1 -dK | 


	echo --- 1>&2

    lock_cost="$(grep -E '_raw_spin_lock|read_trylock|rcu.*lock|queued_spin_lock_slowpath' ~/nas/perfro/perf-stack-$BASE-$ID | awk '{sum += $1} END {print sum+0}')"
	echo $(cat ~/nas/perfro/perf-stack-$BASE-$ID  | grep find_sample_weight  | awk '{ a+= $1 } END {print a } ') $(cat ~/nas/perfro/perf-stack-$BASE-$ID  | grep update_pg | awk '{ a+= $1 } END {print a } ') $lock_cost $nr_samples

}
gen_cost_plots(){
	# Complete this function such that the commented data pipeline is completed. assume get_sample_cost exists. 
    # /STO/ { exit }
    tac ~/nas/all_results | grep BALA  | awk '
        /STOPY/ { exit }
        {
            # $5 = "5-MEMTIS-1-true-def_bcBALA_1_1000000-299"

            # Extract leading number before first "-"  →  5
            split($5, parts, "-")
            struct = parts[1]
	

            # Extract the number immediately after "MEMTIS-"  →  1
            match($5, /bcBALA_1_([0-9]+)/, m)
            add_limit = m[1]
if(! add_limit){
            match($5, /bcBALA_([0-9]+)/, m)
            add_limit = m[1]

}

            print $5, $6,  struct, add_limit, $6, $5, $0    # carry full line through
        }
    ' \
    | while read -r BASE time_ID struct add_limit rest; do
#echo "$struct"A "$add_limit"A "$time_ID"A $BASE\A "$rest"\A #sudo perf report -i $mempath/detailed/perf-stack-$BASE-$time_ID # --stdio --no-children -g none -n --stdio > ~/nas/perfro/perf-stack-$BASE-$ID continue #echo BELOW $rest
        cost="$(get_fun_cost  $BASE $time_ID "$struct" "$add_limit" 2>/dev/null)"
        #echo bro
        if [ -z "$cost" ]; then continue; fi
	_B=$BASE
	runID=$time_ID
	#echo $time_ID TIMO #BASE="MEMTIS-1-true-def_bcBALA_1_6000000-299" #S="$(get_dim "journal" | awk '/nr_sampled/  {print $0 }')"
	BASE=$_B
	#echo $S #printf "%s\t%s\t%s\t%s\n" "$struct" "$add_limit" "$cost" - # "$rest"
        printf "%s\t%s\t%s\t%s\n" "struct: $struct" "add_limt: $add_limit" "costs: $cost" - # "$rest"
        #echo baila
    done  | tr '\n' ' '   | tee >(python3 plot_costs.py --paper --sample-proportion    --map-x-axis   --normalize-x-axis --ignore-struct-5  ) PLOT_COSTS_DATA # --ignore-struct-5  --proportion

	#tac ~/nas/all_results | awk  ' ST { exit; } /{ print $6; }'
exit

	
	#82.65781 0 562 0 5-MEMTIS-1-true-def_bcBALA_1_1000000-299 1773775863 bcu

	# extact the number 5 from the string programatically in awk 
	# extract  the last number of MEMTIS .... programatidaclly in awk. 
	# print each to the output 
	# run bash function get_sample_cost, for each line outputted, and add the result as a column  


}

$@
exit
gen_cost_plots

analyse_samp_cost_synthethic(){
     #MEMTIS-NULL-true-def-299
     
     
     #grep NULL | grep -E "bcu$" | grep true | grep 7050 | tail -n 10 |  
      
    #cat ~/nas/all_results | grep MEMTIS-1-true-def_bcBALA_1_1000000-299 | tail -n 1 |  generate_cost | awk '{ print $2 }' | average  #| tee ~/nas/stock_cost

    cat ~/nas/all_results | grep  5-MEMTIS-1-true-def_bcBALA_1_1000000-299 | tail -n 1 |  generate_cost | awk '{ print $2 }' | average  #| tee ~/nas/stock_cost
     
    				
      
    echo ----

    #cat ~/nas/all_results | grep BALA | generate_cost | tee ~/nas/samp_costCPU
}
analyse_samp_cost_synthethic 
exit

runID="1764611953"
BASE="ASMEM" 
get_over_time_all
runID="1764612106"
BASE="MEMTIS-1" 
get_over_time_all
#jecho "" > over_time_files Qfirst_synth
#sp
#MAKER LAST
exit
 #ASMEM-299 1768048731
  #./real_analysis.sh
  #  python3 bin/python_parserFTW.py "all_over_time_real()" 
  BASE="ASMEM-299"
  runID=1768149745
  for s in $(ls $mempath/detailed/vmstat*);  do
    #echo $s ... 

    runID="${s##*-}"
    # Remove everything from the last - to the end
    temp="${s%-*}"

    # Remove up to and including the first -
    BASE="${temp#*-}"
    #echo $runID $BASE $s
    #BASE=
    #runID=
    get_dim "journal" | awk '/dram_hits/ {print 100*$7/($12+$7);}'
done


 #echo bla
 #exit
  echo "MEMTIS-STOCK"
  gett
  get_over_time_all

  echo "ASMEM"

  BASE="MEMTIS-STOCK-299"
  runID="1768177551" 
  gett

  exit
  # 22269995
  
  exit

 BASE=ASMEM-299 
 runID=1768064135
 runID=1768149745  # small speed up prsmv, using stores
 runID=1768147984  # stores not used, slowdown
get_over_time_all
 BASE=MEMTIS-1-299 
 runID=1768064372
 runID=1768150185
 runID=1768148429 
get_over_time_all
exit


BASE=MEMTIS-STOCK-299 
runID=1764993150
 #36904307

  BASE=MEMTIS-STOCK-299-10000 
runID=1764995709 
runID=1765006865 

#41141883


bck_big_run(){
    BASE=ASMEM-299 
    runID=1764942158 
    BASE=ASMEM-11
    runID="1766747217"
    gett

    exit
    BASE=MEMTIS-NULL-299 
    runID=1764974951
    gett
    # 0.0953769/0.0615962 = 1.55 more time spend processing

}

 #ASMEM-11 1766848098
BASE="MEMTIS-NULL-11"
runID=1766854867 
runID="1766859028"
runID="1766946953" #224095758
gett
exit
#                   264338117
BASE="ASMEM-11" 
runID=1766854576 #  264849699
runID="1766858734"
runID=1766946682 #  241786244
gett
exit

BASE=MEMTIS-NULL-11 
runID=1766853148 # 356932276
gett
exit
runID="1766850309"
BASE="ASMEM-11"
#                   388618594
gett
exit



BASE="ASMEM49"
runID="1766741828"
gett;
#         227664821
exit

BASE=ASMEM-11 
runID=1766748612
#         689491
gett
exit


# cat ~/all_results | grep high | grep MEMTIS |  awk '{print $6 }'
BASE="ASMEM49"
runID="1766741828"
gett;
exit



BASE="MEMTIS-149"
for runID in 1766689956 1766691456; do 

gett; 
done

BASE="ASMEM49"
runID=1766692436
for runID in 1766689539 1766691078; do
gett; 

done
exit


bck_big_run
exit

bfsk_run(){
    # matches what is execpted
    echo "---------- BO "
    BASE="MEMTIS-NULL"
    runID="1765968749"
    gett
    BASE="ASMEM"
    runID="1765968552"
    gett
}
exit


 BASE=MEMTIS-1-299 
 runID=1764974584 
 gett


BASE=MEMTIS-NULL-299 
runID=1764974951 
gett
 exit


 22074686
 85296822




BASE="ASMEM-299"
runID=1764942158
BASE="MEMTIS-NULL-299"
runID=1764943285
get_dim "journal" $runID |  awk '/total runtime:/ {print $0 }' # $22/$23; }' 
get_dim "journal" $runID |  awk '/sampled/  {print $0 }' # $22/$23; }' 
    echo total_samlpe_time/run_Time
    get_dim "journal" $runID |  awk '/total runtime:/ {print $22/$23; }' 
    echo  average time per sample '(usefull)'
    get_dim "journal" $runID | awk '/total runtime:/ {print $22/$8; }' # '{print $2 " " ($1 + $4) }' 
    echo  average time per sample '(total)'
    get_dim "journal" $runID | awk '/total runtime:/ {print $23/$8; }' # '{print $2 " " ($1 + $4) }' 


    # 22074686
    # 22074686
    # 55925658 <--  asmem! 
    # 54789329 <--- MEMTIS-NULL-299-10000     (i.e. )

exit

###### bck analysis by time 
    runID=1764465087
    set +xe
    BASE="MEMTIS"
    # ASmem bck
    # total sample  time/runtime.. 
    echo total_samlpe_time/run_Time
    get_dim "journal" $runID |  awk '/total runtime:/ {print $22/$23; }' 
    echo  average time per sample '(usefull)'
    get_dim "journal" $runID | awk '/total runtime:/ {print $22/$8; }' # '{print $2 " " ($1 + $4) }' 
    echo  average time per sample '(total)'
    get_dim "journal" $runID | awk '/total runtime:/ {print $23/$8; }' # '{print $2 " " ($1 + $4) }' 

echo --------
    runID=1764409351 
    BASE="ASMEM"
    get_dim "journal" $runID |  awk '/total runtime:/ {print $22/$23; }' 
    echo  average time per sample '(usefull)'
    get_dim "journal" $runID | awk '/total runtime:/ {print $22/$8; }' # '{print $2 " " ($1 + $4) }' 
    echo  average time per sample '(total)'
    get_dim "journal" $runID | awk '/total runtime:/ {print $23/$8; }' # '{print $2 " " ($1 + $4) }' 

    # MEMTIS IS ALREADY EXPENSIVE, DUE TO MIGRATION ETC

    exit



#106.052326 0 185 0 ASMEM 1764611953 outa
#154.933468 0 185 0 MEMTIS-1 1764612106 outa




#first_synth
exit


stalls_over_time(){
    # plot  over time 
    #       stall latency 
    #       nr of promotions / demotoions
    #       hit rate! 
    #asmemID=1763441946 
    #cat detailed/perf-ASMEM-1763441946 | awk ' $1 > 80 && /stalls_l3_miss/ {print $0 } '
    #runID=1763216159
    #BASE="ASMEM"
    #runID="$asmemID"
    #cat $mempath/detailed/perf-$BASE-$runID
    #cat $mempath/detailed/perf-$BASE-$runID

    bench="mg"
    bench="bcu"
    bench="bck"
    asmemRunID=$(get_most_recent "ASMEM" "$bench")
    memtisRunID=$(get_most_recent "MEMTIS-1" "$bench")
    tppRunID=$(get_most_recent "TPP" "$bench")
    tppAltoRunID=$(get_most_recent "TPP-ALTO" "$bench")

#73.77052 0 1536 0 ASMEM 1764582276 bck
#73.85107 0 1536 0 MEMTIS-1 1764582375 bck
    asmemRunID=1764582276
    memtisRunID=1764582375
    # $(get_most_recent "MEMTIS-1" "$bench")


    #cat $mempath/detailed/$asmemRunID
    #cat $mempath/detailed/$memtisRunID

    runID=$asmemRunID
    BASE="ASMEM"
    echo_dim "journal"
    BASE="MEMTIS-1"
    runID=$memtisRunID
    echo_dim "journal"
    #exit
    runID=$asmemRunID
    BASE="ASMEM"

    echo "" > over_time_files
    get_over_time_all
    # perf stat -C 0 -a uncore_imc_0/cas_count_read/,uncore_imc_0/cas_count_write/ -I 1000

    BASE="MEMTIS-1"
    runID=$memtisRunID
    get_over_time_all
    exit






    get_dim "perf" $memtisRunID |  awk ' /stalls_l3_miss/ {print $1 } '  > _$BASE\_stalls_l3_miss-overtime
    #get_dim_soar "pgstat" "$memtisRunID" | awk ' /stalls_l3_miss/ {print $1 } ' > _$BASE\_stalls_l3_miss_soar-overtime

    #get_dim "vmstat" 
    target=htmm_promote
    get_dim "vmstat" | grep $target | delta_over_time  > _$BASE\_$target-overtime
    target=htmm_demote
    get_dim "vmstat" | grep htmm_demote | delta_over_time  > _$BASE\_$target-overtime

    target=pgpromote_anon
    get_dim_soar "pgstat" "$runID" | grep $target | delta_over_time > _$BASE\_$target-overtime
    target=pgdemote_anon
    get_dim_soar "pgstat" "$runID" | grep $target   | delta_over_time > _$BASE\_$target-overtime



    #get_dim "vmstat" | grep htmm_demote | awk '{ elapsed=$1-prev; prev=elapsed; print elapsed}'


    #/home/ist196723/nas/tools/SoarAlto/run/bc-urand/rst/rst-TPP/pgstat-th0-1763216159.log
    #pgdemote_anon pgpromote_anon 
    # awk '$1 > 80 && /stalls_l3_miss/ {print $0 } '
}
stalls_over_time



migs_over_time(){


echo -

}

# mg_sampler_performance
# 18% less samples COMPARE nr_sampled bc  (12% more busy)
# mg --> same ammount echo -1 COMPARE nr_sampled
# for 2500 sample period.. | sudo tee /sys/kernel/mm/htmm/htmm_sample_period

path=~/nas/latency_benchmark/tests_syn/plot_time_math/detailed
BASE=ASMEM
#cat _asmem_bc | xargs -I {} cat $path/hit_rate-$BASE-{} | awk '{print $0}' # '{print $2 " " ($1 + $4) }' 

get_hit_ratio(){
    cat _asmem_bc | xargs -I {} cat $path/journal-$BASE-{} | awk '/HIT_RIGHT/ {print $0; print NR; exit }' # '{print $2 " " ($1 + $4) }' 
}
get_sample_cost(){
    echo -
}
# % time processing samples
get_journal(){
    cat _$BASE\_bc | xargs -I {} cat $path/journal-$BASE-{} | awk  -v OFMT='%.10f'    "$1"
}

___show(){
    #MEMTIS bck

    echo % time usefull


    get_journal '/total runtime:/ {print $22/$23; }' # '{print $2 " " ($1 + $4) }' 
    echo  average time per sample '(usefull)'
    get_journal '/total runtime:/ {print $22/$8; }' # '{print $2 " " ($1 + $4) }' 
    echo  average time per sample '(total)'
    get_journal '/total runtime:/ {print $23/$8; }' # '{print $2 " " ($1 + $4) }' 
}
echo hi

compare(){
    BASE="ASMEM"
    cmd="$1"
    tag="$2"
    a=$(get_journal "$cmd"  | average)
    BASE="MEMTIS"
    b=$(get_journal "$cmd" | average)
    echo "$(echo "scale=0; (($a-$b)*100)/$b" | bc)"  COMPARE $tag
}
echo "usefull"
compare ' /hit ratio/ {split($14, a, ","); print a[1]; }' "nr_sampled"
exit
compare '/total runtime:/ {print $22/$8; }'  "usefull"
echo "total"
compare '/total runtime:/ {print $23/$8; }'  "total"
echo "percentage busy"
compare '/total runtime:/ {print $22/$23; }'  "percentage busy"
exit



exit
get_journal | average 
exit
a=$()
BASE="MEMTIS"
b=$(get_journal '/total runtime:/ {print $22/$8; }' | average )
echo $a $b "COMPARE"
exit

BASE="MEMTIS"
echo % time usefull
get_journal '/total runtime:/ {print $22/$23; }' # '{print $2 " " ($1 + $4) }' 
echo  average time per sample '(usefull)'
get_journal '/total runtime:/ {print $22/$8; }' # '{print $2 " " ($1 + $4) }' 
echo  average time per sample '(total)'
get_journal '/total runtime:/ {print $23/$8; }' # '{print $2 " " ($1 + $4) }' 



# 31

#  > _asmem_bc_hit_rate
