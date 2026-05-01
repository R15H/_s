#!/bin/bash
VMTOUCH="/usr/bin/vmtouch"
nas="/mnt/nas/inesc/ist196723"
folder="/mnt/nas/inesc/ist196723/osdi26/"

#set -x 
#set -e

HUGE_SPLIT=""

# Track the maximum resident set size (RSS) of a process until it exits.
# Usage: max_memory <pid> [poll_interval]
#   <pid>           PID of the target process
#   [poll_interval] How often to sample memory in seconds (default: 0.1)
max_memory() {
  local pid="$1"
  local interval="${2:-0.1}"
  local max_rss=0
  local current_rss

  if [[ -z "$pid" || ! -d "/proc/$pid" ]]; then
    echo "Usage: max_memory <pid> [poll_interval]"
    return 1
  fi

  set +xe
  # Poll until the process exits
  while kill -0 "$pid" 2>/dev/null; do
    # Read current RSS from /proc/[pid]/status this is in KiB
    current_rss=$(awk '/VmRSS:/ {print $2}' /proc/"$pid"/status 2>/dev/null)
    # Update maximum if this sample is greater
    echo $current_rss
    if (( current_rss > max_rss )); then
      max_rss=$current_rss
    fi
    sleep "$interval"
  done

  # Print the peak RSS in KiB
  echo "$max_rss"
}









##################
removeeeee_question_mark(){
rm benchmarks_todo
~/run_commands.sh
}
total_runs=0


prep(){
    sudo /home/ist196723/memtis/memtis-userspace/scripts/set_uncore_freq.sh on
    sudo cpupower frequency-set -g performance
    numactl --membind 0 $VMTOUCH -e $BINARY -m 64G
    echo "BOUT TO RUN $BINARY $ARGS $(date '+%Y-%m-%d_%H-%M-%S')"
}

prepare(){
    set +xe
    sudo /home/ist196723/memtis/memtis-userspace/scripts/set_uncore_freq.sh on > /dev/null
    sudo cpupower frequency-set -g performance

    numactl --membind 0 $VMTOUCH -e $BINARY -m 64G
    for a in $ARGS; do
        if [ -f "$a" ]; then
            numactl --membind 1 $VMTOUCH -e $a -m 64G
        fi
    done
    set -xe
}
LOCAL_RUN="numactl  --membind 0"
REMOTE_RUN="numactl  --membind 1"

export OMP_NUM_THREADS=1



generate_window_results(){
    cat $1 | {
        declare -A workload_list
    total_runs=0
        while read -r line; do
            eval "$line"
            echo "$line"
            total_runs=$((total_runs+1))

            global_file=~/nas/osdi26/perf/global_$total_runs
            trace_file=~/nas/osdi26/perf/trace_$total_runs
            rss_file=~/nas/osdi26/perf/rss_$total_runs
            output_file=~/nas/osdi26/perf/output_$total_runs

            # decompress trace file
            zcat $trace_file > $trace_file.unzipped
            generate_weights $trace_file.unzipped $global_file 

            rm $trace_file.unzipped
        done
    }


}
_execute_gem5(){
    # ssh into remote machine and execute gem5
    name=$(basename $BINARY)
    current_bench=$1 #$total_runs

    echo "CONNECTING TO REMOTE NODE - $bench_file $current_bench"
    #srun --nodelist=proteina07--pty 
    #bash -c "cd /mnt/nas/inesc/ist196723/osdi26/infra/; source docker.sh; restore $bench_file $current_bench"



}
short_executions(){
    awk '/STARTED/ {a[$1$2$3$4$5$6$7$8$9$10] = $14;  next; } /TERMINATED/{if( ($15 -  a[$1$2$3$4$5$6$7$8$9$10]) <= 120) {print $0}; print $0 ; delete a[$1$2$3$4$5$6$7$8$9$10]; next;   } ' results_gem5/gem5_pids.txt 
    awk '/STARTED/ {a[$1$2$3$4$5$6$7$8$9$10] = $14;  next; } /TERMINATED/{if( ($15 -  a[$1$2$3$4$5$6$7$8$9$10]) >= 3600) {print $0}; print $0 ; delete a[$1$2$3$4$5$6$7$8$9$10]; next;   } ' results_gem5/gem5_pids.txt 
     awk '/STARTED/ {a[$1$2$3$4$5$6$7$8$9$10] = $14;  next; } /TERMINATED/{if( ($15 -  a[$1$2$3$4$5$6$7$8$9$10]) >= 10) {print $0};  delete a[$1$2$3$4$5$6$7$8$9$10]; next;   } {print "RUNNING " $0 } ' results_gem5/gem5_pids.txt

     awk '/STARTED/ {a[$1$2$3$4$5$6$7$8$9$10] = $14;  next; } /TERMINATED/{print $10 " " $15 -  a[$1$2$3$4$5$6$7$8$9$10];  next;   } END {   for (key in a) {
        print "Unmatched STARTED for key '" key "': " a[key] " (no TERMINATED found)"
    } } ' results_gem5/gem5_pids.txt

    awk '/STARTED/ {b[$1$2$3$4$5$6$7$8$9$10]= $0; a[$1$2$3$4$5$6$7$8$9$10] = $14;  next; } /TERMINATED/{if($15 -  a[$1$2$3$4$5$6$7$8$9$10] > 10) {print $0 } ;  next;   } END {   for (key in a) {
    print b[key]
    } } ' results_gem5/gem5_pids.txt > _
    cat _ >results_gem5/gem5_pids.txt 
    # one_more_gem5

}

current_runs(){
gpids="/mnt/nas/inesc/ist196723/osdi26/results_gem5/gem5_pids.txt" 
# +2382
tail -n +1644 $gpids 
}



wait_for_space(){
    while true; do 
        # sleep random number of seconds between 1 and 60
        #sleep $((RANDOM % 6 + 1))
        echo "busy"
        # how many gem5 processes are currently running?
        gpids="/mnt/nas/inesc/ist196723/osdi26/results_gem5/gem5_pids.txt"
        gem5_done=$(current_runs | grep $(hostname) | grep TERMINATED | wc -l)
        gem5_started=$(current_runs | grep $(hostname) | grep STARTED | wc -l)
        gem5_count=$(($gem5_started - $gem5_done))
        echo "on going: $gem5_count done: $gem5_done started: $gem5_started"
        # get NR of GBs of dram this server has
        if [ $gem5_count -lt 13 ]; then
            #sleep $((RANDOM % 2 + 1))
            break
        fi
        sleep $((RANDOM % 1 + 1))
    done
}
slout(){ # see last outputs
 ls -t results_gem5/out* | xargs -n1  less
}
slerr(){ # see last errors
 ls -t results_gem5/err* | xargs -n1  less
}

make_table_readable(){
        awk -v BINARY="$BINARY" -v SHARED_LIBS="$shared_libs"  'BEGIN{print "addr, weights...,source"} {
        hex = sprintf("%x", $1);
        cmd = "addr2line " "-e " BINARY " " hex;
        cmd | getline source_code_location;
        print $0 " " source_code_location;
        close(cmd); }' "$file" 
}
#        if (source_code_location ~ "?") {
#            for (i = 1; i <= SHARED_LIBS; i++) {
#                cmd = "addr2line " "-e " SHARED_LIBS[i] " " hex;
#                cmd | getline source_code_location;
#                if (source_code_location !~ "?") {
#                    break;
#                }
#            }
#        }
glatTable(){ 
    #set +x
    #set +e
    i=0
    ls ~/nas/osdi26/final_data/maps/* | while read -r file; do
    i=$((i+1))

        #shared_libs="$(objdump -p  /mnt/nas/inesc/ist196723/gapbs/sssp | grep NEEDED | cut -d ' ' -f 2)"
        #echo "$(basename $file) $file"
        bin="$(basename "$file" | cut -d ' ' -f 1)"
        eval "$(cat benches_final | grep "/mnt/nas/inesc.*$bin\""  |  head -n1 )" # define BINARY 
        #echo "$file"
        make_table_readable > ~/nas/osdi26/final_data/maps_human/"$(basename "$file")"  # QUOTED ~ WILL NOT EXPAND!!!
        #echo $i
    done
}


get_gem5_cmd_line(){
                GEM5=$nas/gem5.end
                GEM5=/bench/userspace/benchmarks/gemm5/gem5/buildO/build/X86/gem5.fast
                GEM5=/mnt/nas/inesc/ist196723/gem5.end
                GEM5=/mnt/nas/inesc/ist196723/gem5.endGOOD
                GEM5=/mnt/nas/inesc/ist196723/gem5.fast
                #bench/userspace/benchmarks/gemm5/gem5/buildO/build/X86/gem5.fast

                CONFIG=/bench/copyyy_bento.py
                CONFIG_SKIP=$nas/config.end.py
                CONFIG=$nas/copyyy_bento.py
                increase=0
                 cmd_line_filled=$(cat <<EOF
    $GEM5 $CONFIG "$BINARY" --latency-increase $increase --bargs "$ARGS" --cpu-start KVM --dramsize=${DRAM}GiB --bstdin "$STDIN"
EOF
    )
                cmd_line_to_expand='$GEM5 $CONFIG "$BINARY" --latency-increase $increase --bargs "$ARGS" --cpu-start KVM --dramsize=${DRAM}GiB --bstdin "$STDIN"'
                echo ${cmd_line_to_expand@Q}
}

rungem5_with_report(){
      {
                benchset=$1
                benchnr=$2
                increase=$3
                
                # Validate that increase is a positive integer
                if ! [[ "$increase" =~ ^[0-9]+$ ]]; then
                    echo "Error: 'increase' must be a positive integer, got '$increase'" >&2
                    return 1
                fi
                shift 3
                echo hi
                now_time=$(date +%s)
                    errfile="$nas/osdi26/results_gem5/err_${benchset}_${benchnr}_${increase}_"
                    outfile="$nas/osdi26/results_gem5/output_${benchset}_${benchnr}_${increase}_"
                    $@ 2> "$errfile" > "$outfile" &
                    pid=$!
                    echo "pid: $pid benchset: $benchset benchnr: $benchnr bench: $BINARY increase: $increase host: $(hostname) STARTED $now_time" >> $nas/osdi26/results_gem5/gem5_pids.txt
                    wait $pid
                    gem5_exit=$?
                    if [[ $gem5_exit -ne 0 ]]; then
                        echo "ERROR: GEM5 exited with code $gem5_exit — bench=$BINARY benchset=$benchset benchnr=$benchnr increase=$increase" >&2
                        echo "--- last 30 lines of $errfile ---" >&2
                        tail -30 "$errfile" >&2
                    fi
                    echo "pid: $pid benchset: $benchset benchnr: $benchnr bench: $BINARY increase: $increase host: $(hostname) TERMINATED $gem5_exit $now_time" >> $nas/osdi26/results_gem5/gem5_pids.txt
    } 
}

synthethics_all_80(){

    DRAM=1
    source $nas/latency_benchmark/tests_syn/plot_time_math/plot2.sh


        owo
        update_program_variables
    benchnr=41000
                for reds in  10 1 100; do
        for ratio in 0 5 1 2 4 8 16 32 64; do # 32 100; do
                        #loops=$((3000*)) # 3 million reads of each
                        aptr=$reds
                        arand=$((reds*ratio))
                        looops=10000000000
                        loops=1000000000
                        OUTA_FILE=$BINARY
                        exec=$BINARY
                        WORKDIR="$nas/latency_benchmark/tests_syn/plot_time_math"
                        BINARY="$WORKDIR/outa"  ########################################################################################

                        benchset="synthethic_extended-$arand-$aptr-"
                        ARGS="$args"; STDIN=""; WORKDIR="$WORKDIR"; # size=simsmall
                        SKIP_SECONDS=50
                        TIMEOUT_SECONDS=60 # 1 minutes 
                        update_program_variables
                    _do_gem5_skip 0 &  ########################################################################################
                    #_do_gem5_skip 80
                    #exit

                    #exit

        benchnr=$(($benchnr+1))
                done
                wait
                done
                continue

                for reds in  1 2 4 8 16 32 64 128 256 512; do
                        #loops=$((3000*)) # 3 million reads of each
                        aptr=0
                        arand=$((reds))
                        looops=10000000000
                        loops=1000000000
                        update_program_variables
                        exec=$BINARY
                        WORKDIR="$nas/latency_benchmark/tests_syn/plot_time_math"
                        BINARY="$WORKDIR/outa"  ########################################################################################

                        benchset="synthethic_extended-$arand-$aptr-"
                        ARGS="$args"; STDIN=""; WORKDIR="$WORKDIR"; # size=simsmall
                        SKIP_SECONDS=50
                        TIMEOUT_SECONDS=60 # 1 minutes 
                   _do_gem5_skip 0  ########################################################################################
                    _do_gem5_skip 80
                    #exit

                    #exit

        benchnr=$(($benchnr+1))
                done

                for reds in  1 2 4 8 16 32 64 128 256 512; do
                        #loops=$((3000*)) # 3 million reads of each
                        aptr=$((reds))
                        arand=$((reds))
                        looops=10000000000
                        loops=1000000000
                        update_program_variables
                        exec=$BINARY
                        WORKDIR="$nas/latency_benchmark/tests_syn/plot_time_math"
                        BINARY="$WORKDIR/outa"  ########################################################################################

                        benchset="synthethic_extended-$arand-$aptr-"
                        ARGS="$args"; STDIN=""; WORKDIR="$WORKDIR"; # size=simsmall
                        SKIP_SECONDS=50
                        TIMEOUT_SECONDS=60 # 1 minutes 
                    _do_gem5_skip 0  ########################################################################################
                    _do_gem5_skip 80
                    #exit

                    #exit

        benchnr=$(($benchnr+1))
                done







                sleep 120
}
__core_synthethic_all(){
                        aptr=$reds
                        arand=$((reds*ratio))
                        looops=10000000000
                        loops=1000000000
                        OUTA_FILE=$BINARY
                        update_program_variables
                        exec=$BINARY
                        WORKDIR="$nas/latency_benchmark/tests_syn/plot_time_math"
                        BINARY="$WORKDIR/outa"
                        #continue

                        benchset="synthethic_extended-$arand-$aptr-"
                        ARGS="$args"; STDIN=""; WORKDIR="$WORKDIR"; # size=simsmall
                        SKIP_SECONDS=80
                        TIMEOUT_SECONDS=60 # 2 minutes 
                    _do_gem5_skip 

}
synthethics_all(){
    DRAM=1
    source $nas/latency_benchmark/tests_syn/plot_time_math/plot.sh


        owo
        update_program_variables
    benchnr=41000
    WARMUP=4
    memory=4
                for reds in 1 10; do # 10 100 200; do
                
        for ratio in  {0..30..2}; do #19  23 29 2 6 10 14 18 22 26 30; do
                    __core_synthethic_all &
        benchnr=$(($benchnr+1))
        #sleep 10 &
                done
                wait
        for ratio in  {1..30..2}; do #19  23 29 2 6 10 14 18 22 26 30; do
                    __core_synthethic_all &
        benchnr=$(($benchnr+1))
        #sleep 10 &
                done

                wait
done




}

setup_big(){
    DRAM=16
    SKIP_SECONDS=200
    benchnr='78000000'
    TIMEOUT_SECONDS=8640000 # 100 days

}
# TODO

machine_learn(){

BINARY="/mnt/nas/inesc/ist196723/benchmarks/liblinear-multicore-2.47/datasets/../train"; ARGS="-s 0 -c 1 -e 0.01  /mnt/nas/inesc/ist196723/benchmarks/liblinear-multicore-2.47/datasets/webspam_wc_normalized_unigram.svm"; STDIN=""; WORKDIR="/"; # size=simsmall
    benchset='liblinear'
    SKIP_SECONDS=0
    DRAM=2
setup_big
    benchnr='7000001'
_do_gem5_skip
    SKIP_SECONDS=50
_do_gem5_skip
    benchnr='7000002'
    SKIP_SECONDS=100
_do_gem5_skip
    benchnr='7000003'
    SKIP_SECONDS=200
_do_gem5_skip


}


over_math(){
    DRAM=1
    id=1000
    #$dock create_container gem5
    #for bench in "${synthethic_benches[@]}"; do
    benchset="THE_syntehthic-STATMATH"
    SKIP_SECONDS=15
    TIMEOUT_SECONDS=60000 #86400000 # 100 da
    mm=0
    benchnr="777000$mm"
    for mm in 1 2 4 8 16 32 64; do
        ARGS="$mm 0 4 100 0 100 100 200 099999900 2 0 0 0 000000 0 splitted_math optimal" STDIN="" WORKDIR="/" # size=simsmall    64
        BINARY="/mnt/nas/inesc/ist196723/latency_benchmark/tests_syn/plot_time_math/outa-$mm" 
        #_do_gem5_skip
        _do_gem5_skip $1
        benchnr=$(($benchnr+1))
    done
    return
    benchset="THE_syntehthic-DYNMATH"
    BINARY="/mnt/nas/inesc/ist196723/latency_benchmark/tests_syn/plot_time_math/outa-DYN" 
    mm=0
    for mm in 1 2 4 8 16 32 64; do
        ARGS="$mm 0 4 100 0 100 100 200 099999900 2 0 0 0 000000 0 splitted_math optimal" STDIN="" WORKDIR="/" # size=simsmall    64
        benchnr="777000$mm"
        _do_gem5_skip
        #_do_gem5_skip 80
        benchnr=$(($benchnr+1))
    done

}

over_latency(){

 DRAM=1
    id=1000
    #$dock create_container gem5
    #for bench in "${synthethic_benches[@]}"; do
    benchset="THE_syntehthic"
    benchnr="2099"
    BINARY="/mnt/nas/inesc/ist196723/latency_benchmark/tests_syn/plot_time_math/outa" 
    ARGS="0 0 4 100 0 10 100 200 032250000 2 0 0 0 000000 0 splitted optimal" STDIN="" WORKDIR="/" # size=simsmall    64
    ARGS="0 0 4 100 0 5 20 200 032250000 2 0 0 0 000000 0 splitted optimal"
        #get_plot_run $bench
        i=88888
        for i in 0 80; do
        echo -
        done

special_ptr_chase
math 

}

graphy(){

    DRAM=4
    benchset='1GB_GRAPH'
    SKIP_SECONDS=60
    benchnr='97000'
    TIMEOUT_SECONDS=86400000 # 100 days
    #kron23
    g="kron23"
BINARY="/mnt/nas/inesc/ist196723/gapbs/bc"; ARGS="-f /mnt/nas/inesc/ist196723/gapbs/$g.sg -n 40000"; STDIN=""; WORKDIR="/"; # size=simsmall
#_do_gem5_skip
#_do_gem5_skip 80
SKIP_SECONDS=61
benchnr=$(($benchnr+1))
BINARY="/mnt/nas/inesc/ist196723/gapbs/bfs"; ARGS="-f /mnt/nas/inesc/ist196723/gapbs/$g.sg -n 40000"; STDIN=""; WORKDIR="/"; # size=simsmall
#_do_gem5_skip
#_do_gem5_skip 80
SKIP_SECONDS=62
benchnr=$(($benchnr+1))
BINARY="/mnt/nas/inesc/ist196723/gapbs/bc"; ARGS="-f /mnt/nas/inesc/ist196723/gapbs/$g.sg -n 4000"; STDIN=""; WORKDIR="/"; # size=simsmall
#_do_gem5_skip
#_do_gem5_skip 80
SKIP_SECONDS=63
benchnr=$(($benchnr+1))
BINARY="/mnt/nas/inesc/ist196723/gapbs/bc"; ARGS="-f /mnt/nas/inesc/ist196723/gapbs/$g.sg -n 4000"; STDIN=""; WORKDIR="/"; # size=simsmall
#_do_gem5_skip
#_do_gem5_skip 80
SKIP_SECONDS=64
benchnr=$(($benchnr+1))
BINARY="/mnt/nas/inesc/ist196723/gapbs/bc"; ARGS="-f /mnt/nas/inesc/ist196723/gapbs/$g.sg -n 4000"; STDIN=""; WORKDIR="/"; # size=simsmall
#_do_gem5_skip
#_do_gem5_skip 80
SKIP_SECONDS=65
benchnr=$(($benchnr+1))
BINARY="/mnt/nas/inesc/ist196723/gapbs/bc"; ARGS="-f /mnt/nas/inesc/ist196723/gapbs/$g.sg -n 4000"; STDIN=""; WORKDIR="/"; # size=simsmall
#_do_gem5_skip
#_do_gem5_skip 80
SKIP_SECONDS=66
benchnr=$(($benchnr+1))
BINARY="/mnt/nas/inesc/ist196723/gapbs/bc"; ARGS="-f /mnt/nas/inesc/ist196723/gapbs/$g.sg -n 4000"; STDIN=""; WORKDIR="/"; # size=simsmall
#_do_gem5_skip
#_do_gem5_skip 80
for SKIP_SECONDS in 70 81 92 103 113; do # 124 135 146; do
	benchnr=$(($benchnr+1))
	_do_gem5_skip
	_do_gem5_skip 80
done



}

npb_final1(){
    skip="$1"
    DRAM=10
    benchnr=1880002
    benchnr='10'
    TIMEOUT_SECONDS=10 # 100 days
    for SKIP_SECONDS in $skip; do
        benchnr=$(($benchnr+1))
        BINARY="/mnt/nas/inesc/ist196723/benchmarks/NPB-CPP/NPB-OMP/bin/cg.D"; ARGS=""; STDIN=""; WORKDIR="/"; # size=simsmall
        _do_gem5_skip
    done

}

np1(){
npb_final1 "0 30 50 60 80 90"
}
np2(){
npb_final1 "100 110 120  140 150 160 170 180 190" # 130
}
echo hiiiiiiuuuiuiui
np5(){
npb_final1 "512 543 587" # 5\90 5\60"  5\30
}
np4(){
npb_final1 "400 420 450 470 490"
}
np3(){
npb_final1 "200 210 220  240 250  270 280 290"
}



npb_final(){

    DRAM=4
    benchset='npb_result-iter'
    SKIP_SECONDS=50
    benchnr='15333'
    TIMEOUT_SECONDS=8640000 # 100 days
    BINARY="/mnt/nas/inesc/ist196723/benchmarks/NPB-CPP/NPB-OMP/bin/ft.D"; ARGS=""; STDIN=""; WORKDIR="/"; # size=simsmall
#_do_gem5_skip
#exit

    BINARY="/mnt/nas/inesc/ist196723/benchmarks/NPB-CPP/NPB-OMP/bin/sp.D"; ARGS=""; STDIN=""; WORKDIR="/"; # size=simsmall
#_do_gem5_skip
BINARY="/mnt/nas/inesc/ist196723/benchmarks/NPB-CPP/NPB-OMP/bin/lu.D"; ARGS=""; STDIN=""; WORKDIR="/"; # size=simsmall
benchnr=$(($benchnr+1))
#_do_gem5_skip
BINARY="/mnt/nas/inesc/ist196723/benchmarks/NPB-CPP/NPB-OMP/bin/ep.C"; ARGS=""; STDIN=""; WORKDIR="/"; # size=simsmall
benchnr=$(($benchnr+1))
#_do_gem5_skip
BINARY="/mnt/nas/inesc/ist196723/benchmarks/NPB-CPP/NPB-OMP/bin/bt.D"; ARGS=""; STDIN=""; WORKDIR="/"; # size=simsmall
benchnr=$(($benchnr+1))
#_do_gem5_skip
BINARY="/mnt/nas/inesc/ist196723/benchmarks/NPB-CPP/NPB-OMP/bin/is.D"; ARGS=""; STDIN=""; WORKDIR="/"; # size=simsmall
benchnr=$(($benchnr+1))
#_do_gem5_skip
BINARY="/mnt/nas/inesc/ist196723/benchmarks/NPB-CPP/NPB-OMP/bin/mg.C"; ARGS=""; STDIN=""; WORKDIR="/"; # size=simsmall
benchnr=$(($benchnr+1))
#_do_gem5_skip
BINARY="/mnt/nas/inesc/ist196723/benchmarks/NPB-CPP/NPB-OMP/bin/cg.D"; ARGS=""; STDIN=""; WORKDIR="/"; # size=simsmall
benchnr=$(($benchnr+1))
#_do_gem5_skip
BINARY="/mnt/nas/inesc/ist196723/benchmarks/NPB-CPP/NPB-OMP/bin/sp.D"; ARGS=""; STDIN=""; WORKDIR="/"; # size=simsmall
benchnr=$(($benchnr+1))
#_do_gem5_skip
benchnr=1600000
SKIP_SECONDS=1
#_do_gem5_skip
BINARY="/mnt/nas/inesc/ist196723/benchmarks/NPB-CPP/NPB-OMP/bin/cg.D"; ARGS=""; STDIN=""; WORKDIR="/"; # size=simsmall
benchnr=1600001
SKIP_SECONDS=1000
#_do_gem5_skip
benchnr=1600002
SKIP_SECONDS=500
BINARY="/mnt/nas/inesc/ist196723/benchmarks/NPB-CPP/NPB-OMP/bin/cg.D"; ARGS=""; STDIN=""; WORKDIR="/"; # size=simsmall
#_do_gem5_skip


BINARY="/mnt/nas/inesc/ist196723/benchmarks/NPB-CPP/NPB-OMP/bin/mg.C"; ARGS=""; STDIN=""; WORKDIR="/"; # size=simsmall
SKIP_SECONDS=50
benchnr=1920000
#_do_gem5_skip 80
#_do_gem5_skip 
SKIP_SECONDS=51
benchnr=$(($benchnr+1))
#_do_gem5_skip 80
#_do_gem5_skip 
SKIP_SECONDS=52
benchnr=$(($benchnr+1))
#_do_gem5_skip 80
#_do_gem5_skip 
SKIP_SECONDS=53
benchnr=$(($benchnr+1))
#_do_gem5_skip 80
#_do_gem5_skip 
SKIP_SECONDS=54
benchnr=$(($benchnr+1))
#_do_gem5_skip 80
#_do_gem5_skip 
SKIP_SECONDS=55
benchnr=$(($benchnr+1))
#_do_gem5_skip 80
#_do_gem5_skip 
SKIP_SECONDS=56
benchnr=$(($benchnr+1))
#_do_gem5_skip 80
#_do_gem5_skip 
SKIP_SECONDS=57
benchnr=$(($benchnr+1))
#_do_gem5_skip 80
#_do_gem5_skip 
SKIP_SECONDS=58
benchnr=$(($benchnr+1))
#_do_gem5_skip 80
#_do_gem5_skip 
SKIP_SECONDS=59
benchnr=1920000
#_do_gem5_skip 80
#_do_gem5_skip 
SKIP_SECONDS=60
benchnr=$(($benchnr+1))
#_do_gem5_skip 80
#_do_gem5_skip 
SKIP_SECONDS=62
benchnr=$(($benchnr+1))
#_do_gem5_skip 80
#_do_gem5_skip 
SKIP_SECONDS=63
benchnr=$(($benchnr+1))
#_do_gem5_skip 80
#_do_gem5_skip 
SKIP_SECONDS=64
benchnr=$(($benchnr+1))
#_do_gem5_skip 80
#_do_gem5_skip 
SKIP_SECONDS=65
benchnr=$(($benchnr+1))
#_do_gem5_skip 80
#_do_gem5_skip 
SKIP_SECONDS=66
benchnr=$(($benchnr+1))
#_do_gem5_skip 80
#_do_gem5_skip 
SKIP_SECONDS=67
benchnr=$(($benchnr+1))
#_do_gem5_skip 80
#_do_gem5_skip 
SKIP_SECONDS=68
benchnr=$(($benchnr+1))
#_do_gem5_skip 80
DRAM=10
BINARY="/mnt/nas/inesc/ist196723/benchmarks/NPB-CPP/NPB-OMP/bin/cg.D"; ARGS=""; STDIN=""; WORKDIR="/"; # size=simsmall
for SKIP_SECONDS in  200 300 500 600 700 800 900 1000; do 
benchnr=$(($benchnr+1))
	_do_gem5_skip 
done

}

DRAM=8
final_attempt(){
BINARY="/mnt/nas/inesc/ist196723/benchmarks/XSBench/openmp-threading/XSBench"; ARGS="-t 1 -p 500000 -G hash -h 1000000 -s XL -b read"; STDIN=""; WORKDIR="/mnt/nas/inesc/ist196723/latency_benchmark/tests_syn/plot_time_math"; 
benchset='hand_made_final'
benchnr='10088'
_do_gem5
return



BINARY="/mnt/nas/inesc/ist196723/benchmarks/XSBench/openmp-threading/XSBench"; ARGS="-t 1 -p 100000 -G hash -l 10 -b read"; STDIN=""; WORKDIR="/mnt/nas/inesc/ist196723/experiments"; 
benchset='hand_made_final'
benchnr='10000'
_do_gem5

benchnr='10001'
BINARY="/mnt/nas/inesc/ist196723/benchmarks/XSBench/openmp-threading/XSBench"; ARGS="-t 1 -p 100000 -G hash -l 34 -b read"; STDIN=""; WORKDIR="/mnt/nas/inesc/ist196723/experiments"; 
_do_gem5


#bench_nr='10001'
#BINARY="/mnt/nas/inesc/ist196723/benchmarks/XSBench/openmp-threading/XSBench"; ARGS=" -t 1 -p 100000 -G hash  -l 34 -b read"; STDIN=""; WORKDIR="/mnt/nas/inesc/ist196723/experiments"; 
#_do_gem5

}

DRAM=8
_do_gem5_skip(){
    increase=$1
                #if [[ "x$1" -eq "x80" ]]; then
                #increase=80
                #return

                #else
                #increase=0
                #exit
                #fi
                GEM5=$nas/gem5.end
                GEM5=/bench/userspace/benchmarks/gemm5/gem5/buildO/build/X86/gem5.fast
                GEM5=/mnt/nas/inesc/ist196723/gem5.end
                GEM5=/mnt/nas/inesc/ist196723/gem5.endGOOD
                GEM5=/mnt/nas/inesc/ist196723/gem5.fastWELL
                #bench/userspace/benchmarks/gemm5/gem5/buildO/build/X86/gem5.fast
                GEM5=/mnt/nas/inesc/ist196723/gem5.fast

                CONFIG=/bench/copyyy_bento.py
                CONFIG=$nas/copyyy_bento.py
                CONFIG_SKIP=$nas/config.end.py
                CONFIG=$nas/config.end.py
                #GEM5="gdb -x $nas/osdi26/bin/flush.gdb --args $GEM5"

                # Validate required files and variables before launching
                if [[ ! -x "$GEM5" ]]; then
                    echo "ERROR: GEM5 binary not found or not executable: $GEM5" >&2; return 1
                fi
                if [[ ! -f "$CONFIG" ]]; then
                    echo "ERROR: GEM5 config not found: $CONFIG" >&2; return 1
                fi
                if [[ ! -f "$BINARY" ]]; then
                    echo "ERROR: benchmark binary not found: $BINARY" >&2; return 1
                fi
                for _var in benchset benchnr DRAM SKIP_SECONDS TIMEOUT_SECONDS; do
                    if [[ -z "${!_var}" ]]; then
                        echo "ERROR: required variable \$$_var is empty" >&2; return 1
                    fi
                done

                increase=0
                echo "launching gem5 for $BINARY with args $ARGS and stdin $STDIN OR $WORKDIR" 1>&2
#        set -x
        #set -e

    {
                now_time=$(date +%s)
                    errfile="$nas/osdi26/results_gem5/err_${benchset}_${benchnr}_${increase}_"
                    outfile="$nas/osdi26/results_gem5/output_${benchset}_${benchnr}_${increase}_"
                    echo "$errfile ERRRRRRRRRRRRRRR"
                    echo "$outfile OOOOOOOOOOOOOOUU"
                    $GEM5 $CONFIG "$BINARY" --latency-increase $increase --bargs "$ARGS" --cpu-start KVM --dramsize=${DRAM}GiB --bstdin "$STDIN" --skip_start_duration $SKIP_SECONDS --exec_timeout $TIMEOUT_SECONDS 2> "$errfile" 1> "$outfile" 
                    pid=$!
                    echo "pid: $pid benchset: $benchset benchnr: $benchnr bench: $BINARY increase: $increase host: $(hostname) STARTED $now_time" >> $nas/osdi26/results_gem5/gem5_pids.txt
                    wait $pid
                    gem5_exit=$?
                    if [[ $gem5_exit -ne 0 ]]; then
                        echo "ERROR: GEM5 exited with code $gem5_exit — bench=$BINARY benchset=$benchset benchnr=$benchnr increase=$increase" >&2
                        echo "--- last 30 lines of $errfile ---" >&2
                        tail -30 "$errfile" >&2
                    fi
                    echo "pid: $pid benchset: $benchset benchnr: $benchnr bench: $BINARY increase: $increase host: $(hostname) TERMINATED $gem5_exit $now_time" >> $nas/osdi26/results_gem5/gem5_pids.txt
    } 
    #sleep 1 # give time to write to the gem5 file...
    #disown #keep it running even if the shell dies
    #return
                    increase=80
    {
                now_time=$(date +%s)
                    errfile="$nas/osdi26/results_gem5/err_${benchset}_${benchnr}_${increase}_"
                    outfile="$nas/osdi26/results_gem5/output_${benchset}_${benchnr}_${increase}_"
                    echo "$errfile"
                    echo "$outfile"
                    $GEM5 $CONFIG "$BINARY" --latency-increase $increase --bargs "$ARGS" --cpu-start KVM --dramsize=8GiB --bstdin "$STDIN" --skip_start_duration $SKIP_SECONDS --exec_timeout $TIMEOUT_SECONDS 2> "$errfile" 1> "$outfile" &
                    pid=$!
                    echo "pid: $pid benchset: $benchset benchnr: $benchnr bench: $BINARY increase: $increase host: $(hostname) STARTED $now_time" >> $nas/osdi26/results_gem5/gem5_pids.txt
                    wait $pid
                    gem5_exit=$?
                    if [[ $gem5_exit -ne 0 ]]; then
                        echo "ERROR: GEM5 exited with code $gem5_exit — bench=$BINARY benchset=$benchset benchnr=$benchnr increase=$increase" >&2
                        echo "--- last 30 lines of $errfile ---" >&2
                        tail -30 "$errfile" >&2
                    fi
                    echo "pid: $pid benchset: $benchset benchnr: $benchnr bench: $BINARY increase: $increase host: $(hostname) TERMINATED $gem5_exit $now_time" >> $nas/osdi26/results_gem5/gem5_pids.txt
    } 
    #disown

}
_do_gem5(){
    set +ex
    DRAM=8
                GEM5=$nas/gem5.end
                GEM5=/bench/userspace/benchmarks/gemm5/gem5/buildO/build/X86/gem5.fast
                GEM5=/mnt/nas/inesc/ist196723/gem5.end
                GEM5=/mnt/nas/inesc/ist196723/gem5.endGOOD
                GEM5=/mnt/nas/inesc/ist196723/gem5.fastWELL
                GEM5=/mnt/nas/inesc/ist196723/gem5.fast
                #bench/userspace/benchmarks/gemm5/gem5/buildO/build/X86/gem5.fast

                CONFIG=/bench/copyyy_bento.py
                CONFIG=$nas/config.end.py
                CONFIG=$nas/copyyy_bento.py
                increase=0
                echo "launching gem5 for $BINARY with args $ARGS and stdin $STDIN OR $WORKDIR" 1>&2
#        set -x
        #set -e

    {
                now_time=$(date +%s)
                    echo $nas/osdi26/results_gem5/err_$benchset\_$benchnr\_$increase\_ 
                    echo $nas/osdi26/results_gem5/output_$benchset\_$benchnr\_$increase\_ 
                    $GEM5 $CONFIG "$BINARY" --latency-increase $increase --bargs "$ARGS" --cpu-start KVM --dramsize=${DRAM}GiB --bstdin "$STDIN" 2> $nas/osdi26/results_gem5/err_$benchset\_$benchnr\_$increase\_ 1>$nas/osdi26/results_gem5/output_$benchset\_$benchnr\_$increase\_ & 
                    pid=$!
                    echo "pid: $pid benchset: $benchset benchnr: $benchnr bench: $BINARY increase: $increase host: $(hostname) STARTED $now_time" >> $nas/osdi26/results_gem5/gem5_pids.txt
                    echo "pid: $pid benchset: $benchset benchnr: $benchnr bench: $BINARY increase: $increase host: $(hostname) STARTED $now_time" >> ~/gem5_pids.txt
                    wait $pid
                    echo "pid: $pid benchset: $benchset benchnr: $benchnr bench: $BINARY increase: $increase host: $(hostname) TERMINATED $? $now_time" >> $nas/osdi26/results_gem5/gem5_pids.txt
                    echo "STILL ALIVE"
    } &
    disown #keep it running even if the shell dies
    #return
                    increase=80
    {
        set +xe
                now_time=$(date +%s)
                    echo $nas/osdi26/results_gem5/err_$benchset\_$benchnr\_$increase\_ 
                    echo $nas/osdi26/results_gem5/output_$benchset\_$benchnr\_$increase\_ 
                    $GEM5 $CONFIG "$BINARY" --latency-increase $increase --bargs "$ARGS" --cpu-start KVM --dramsize=8GiB --bstdin "$STDIN" 2> $nas/osdi26/results_gem5/err_$benchset\_$benchnr\_$increase\_ 1>$nas/osdi26/results_gem5/output_$benchset\_$benchnr\_$increase\_ & 
                    pid=$!
                    echo "pid: $pid benchset: $benchset benchnr: $benchnr bench: $BINARY increase: $increase host: $(hostname) STARTED $now_time" >> $nas/osdi26/results_gem5/gem5_pids.txt
                    echo "pid: $pid benchset: $benchset benchnr: $benchnr bench: $BINARY increase: $increase host: $(hostname) STARTED $now_time" >> ~/gem5_pids.txt
                    wait $pid 
                    echo "pid: $pid benchset: $benchset benchnr: $benchnr bench: $BINARY increase: $increase host: $(hostname) TERMINATED $? $now_time" >> $nas/osdi26/results_gem5/gem5_pids.txt
                    echo "STILL ALIVEOO"
    } &
    disown
    echo "Done launching..."

}

do_one_gem5(){
benchset=$1
benchnr=$2
increase=$3
total_runs=0
set -x
set -e
cat $1 | {
        declare -A workload_list
        while read -r line; do
            echo $line
            eval "$line"
            #echo "$line"
            benchset=$(basename $benchset)
            
            pushd $WORKDIR
            if (( total_runs == benchnr )); then

                _do_gem5
                break
            fi
            total_runs=$((total_runs+1))
            popd
        done
    }
}



_execute(){
                if [ -z "$STDIN" ]; then
                    $r $BINARY $ARGS & > /mnt/nas/inesc/ist196723/osdi26/perf/output_$total_runs
                    # execute perf to sample LLC misses with very high precision and frequency
                else
                    $r $BINARY $ARGS < $STDIN & > /mnt/nas/inesc/ist196723/osdi26/perf/output_$total_runs
                fi
                pid=$!
                #sudo  perf stat -e '{cycle_activity.stalls_l3_miss:u,INST_RETIRED.ANY:u,offcore_requests_outstanding.cycles_with_demand_data_rd:u,OFFCORE_REQUESTS.demand_data_rd:u}' -I 250  -o /mnt/nas/inesc/ist196723/osdi26/perf/global-$name-$total_runs -p $pid &  
                #sudo perf record -T -e MEM_LOAD_RETIRED.L3_MISS:uppp -z=6 -c 100 -p $pid -o /mnt/nas/inesc/ist196723/osdi26/perf/trace_$total_runs &
                max_memory $pid 1 > /mnt/nas/inesc/ist196723/osdi26/perf/rss_$total_runs & 
                echo waiting for it all
                wait
}

get_l3_stall_over_time(){
    cat /mnt/nas/inesc/ist196723/osdi26/perf/global-$name-$this_run | awk '$NF == "cycle_activity.stalls_l3_miss:u" {gsub(/,/, "", $2); print $2+0;}' 
}
get_global_l3_stall(){
    name=$1
    this_run=$2
    cat /mnt/nas/inesc/ist196723/osdi26/perf/global-$name-$this_run | awk '$NF == "cycle_activity.stalls_l3_miss:u" {gsub(/,/, "", $2); total+=$2+0; END {print $total}' 
}
get_exec_time(){
    name=$1
    this_run=$2
    cat /mnt/nas/inesc/ist196723/osdi26/perf/global-$name-$this_run | tail -n 1 | awk '{print $1}'
}
get_rss(){
    name=$1
    this_run=$2
    rss=$(cat /mnt/nas/inesc/ist196723/osdi26/perf/rss-$name-$this_run)
    rss=$((rss / 1024))
    echo $rss
}
get_run_type(){
    input_size="-"
    if [[ "$WORKDIR" == *"test"* ]]; then
        input_size="test"
    elif [[ "$WORKDIR" == *"ref"* ]]; then
        input_size="ref"
    elif [[ "$WORKDIR" == *"train"* ]]; then
        input_size="train"
    fi
    echo $input_size
}

report_benchmark(){
    this_run=$(($total_runs)) # STARTS AT 0. ERROR
    name="dram"
    json_obj="{"
    rss=$(get_rss $name $this_run)
    json_obj="$json_obj\"rss\": $rss,"

    json_obj="$json_obj}"

    exec_time=$(get_exec_time $name $this_run)
    name="ecxl"
    slow_time=$(get_exec_time $name $this_run)


    l3_stall_fast=$(get_global_l3_stall $name $this_run)
    l3_stall_slow=$(get_global_l3_stall $name $this_run)

    input_size=$(get_run_type)

# is there test/ref or train in $BINARY?

    #######  Future fields
    # total LLC misses on each of the runs
    #

    # /mnt/nas/inesc/ist196723/osdi26/perf/rss_$total_runs
    #echo $json_obj

    # multiply by 2 to get the column we want
    echo "1-total: $total_runs 2-bin: $(basename $BINARY) 3-rss: $rss 4-exec_time: $exec_time 5-ecxl_time: $slow_time 6-input_size: $input_size"
}



echo_run(){
    echo "$line" "  " $total_runs
    #echo "1-BINARY: $(basename $BINARY) 2-ARGS: $ARGS 3-STDIN: $STDIN 4-WORDIR: $WORKDIR"
}
rebuild_benches(){
    rm ~/benchmarks_todo ~/natives_todo
    cp benches_final "backups/benches_final_$(date)"
    cp  benchmarks_native_todo_final "backups/benchmarks_native_todo_final_$(date)"
    ~/run_commands.sh
    cp ~/benchmarks_todo benches_final
    cp ~/natives_todo benchmarks_native_todo_final
}

set -x 
set -e

iterate_benches(){
    bench_file=$1
    benchset=$1
    exec=$2
    bench_nr=$3
    benchnr=$3
    if [ ! -z "$bench_nr" ]; then
        echo "lOoking for $bench_nr" 1>&2
    fi
    #set +x
    cat $nas/osdi26/$bench_file | {
        declare -A workload_list
        total_runs=-1
        while read -r line; do
            eval "$line"
            #echo "$line"
            pushd $WORKDIR 1>/dev/null
    # if bench nr is not null, check if we are in the right run
            total_runs=$((total_runs+1))
            echo "ITERATING $total_runs" 1>&2

            if [ ! -z "$bench_nr" ]; then
                if (( total_runs < bench_nr )); then
                    continue
                fi
                $exec $total_runs
                break;
            fi

            $exec $total_runs
            popd 1>/dev/null
        done
    }
}

getr(){
    total_runs=0
    name=0
    file=$1
    # extract the right most number
    bench_nr=$2 #$(echo $file | grep -oP "\d+$")
    iterate_benches benches_final  echo_run $bench_nr
}

if [ "$1" == "gem5" ]; then
    bench_nr=$2
    echo $@
    iterate_benches benches_final _execute_gem5 $bench_nr
    exit
fi

do_real_bench(){
            prepare
            r="$REMOTE_RUN"; name="ecxl"; _execute; r="$LOCAL_RUN"; name="dram"; _execute
}

real_execute(){
    benches=${1:-$nas/osdi26/benches_final}
    filter_reg=${2:-".*"}
    total_runs=0
    cat $benches | grep "$filter_reg" | {
        declare -A workload_list
        while read -r line; do
            eval "$line"
            echo "$line"
            pushd $WORKDIR
            do_real_bench
            popd
            total_runs=$((total_runs+1))
        done
    }
}


failed_workload(){
    grep 'unmapped' 
}


stats_execute(){
cat $1 | {
    declare -A workload_list
    while read -r line; do
        echo "$line"
        if [ -z "$line" ]; then
        continue
        fi

        eval "$line"
        #echo B $BINARY; echo A $ARGS; echo S $STDIN; echo W $WORDIR; echo ---;
         
        # if apps in BINARY extract .../apps/{NAME}/...
        if [[ "$BINARY" == *"apps"* ]]; then
            BINARY_NAME=$(echo "$BINARY" | grep -oP "apps/\K[^/]+")
            bs=$(basename "$BINARY")
            if [ "$bs" == "run.sh" ]; then
                #BINARY="${BINARY/"run.sh"/"$BINARY_NAME"}"
                echo -
            fi
        else 
            BINARY_NAME=$(basename "$BINARY")
        fi
        echo $BINARY_NAME
        total_runs=$((total_runs+1))


        # BINARY variable has been filled, count nr of different args for each binary observed
        workload_list["$BINARY_NAME"]=$((workload_list["$BINARY_NAME"]+1)) # STALL: ERROR WAS COMMING FROM THIS LINE
    done
    # print nr of BINARIES 

    gem5_runs=$((total_runs*2))
    real_runs=$((total_runs*2)) 


    echo "Number of binaries: ${#workload_list[@]} and total runs: $total_runs (gem5: $gem5_runs)."
    # print nr of different args for each binary
    for binary in "${!workload_list[@]}"; do
        echo "Binary: $binary, Args: ${workload_list[$binary]}"
    done
}
}

report(){
    bench_file=./benches_final
    iterate_benches $bench_file report_benchmark
}
report_natives(){
    bench_file=./benchmarks_native_todo_final 
    iterate_benches $bench_file report_benchmark
}
execute_and_gather_stats_real(){
    real_execute  ./benchmarks_native_todo_final 
}

#30 per machine
#382 runs 
#382/30 = 12.73

# if its "stats" then call stats_execute

if [ "$1" == "real" ]; then
    real_execute 
    exit
fi
if [ "$1" == "stats" ]; then
    stats_execute ~/nas/osdi26/benches_final
fi
if [ "$1" == "report" ]; then
    report
fi
if [ "$1" == "rebuild" ]; then
    rebuild_benches
fi
#if [ "$1" == "getr" ]; then
#    getr $2
#    exit
#fi


###################
last_out(){
cat results_gem5/gem5_pids.txt | tail -n 1 | awk '{ print $4 "_" $6 "_" $10 "_" }' | xargs -I {} cat ./results_gem5/output_{}
}
all_terminated_err(){
cat results_gem5/gem5_pids.txt | awk '/TERMINATED/ { print $4 "_" $6 "_" $10 "_" }' | xargs -I {} cat ./results_gem5/err_{}
}
all_terminated__out(){
cat results_gem5/gem5_pids.txt | awk '/TERMINATED/ { print $4 "_" $6 "_" $10 "_" }' | xargs -I {} cat ./results_gem5/output_{}
}
last_out(){
    cat results_gem5/gem5_pids.txt | tail -n 1 | awk '{ print $4 "_" $6 "_" $10 "_" }' | xargs -I {} cat ./results_gem5/output_{}
}
last_err(){
    cat results_gem5/gem5_pids.txt | tail -n 1 | awk '{ print $4 "_" $6 "_" $10 "_" }' | xargs -I {} cat ./results_gem5/err_{}
}

parsec_small(){
$nas/osdi26/controller.sh getr 2>/dev/null | grep -v 20.sg | grep parsec | grep 'simsmall' | awk '{print $NF}'
}

check_status() {
    parsec_small | while read -r line; do
        cat $nas/osdi26/results_gem5/gem5_pids.txt | grep "benchnr: $line"
    done
}


lockfile="$nas/osdi26/lock"
launch_or_skip_one(){
    bench_nr=$1

    #must_do="$(cat $nas/osdi26/must_do | head -n 5)"
    # remove the first line
    #sed -i '5d' $nas/osdi26/must_do
    #for b in $must_do; do
    #    $nas/osdi26/controller.sh iterate_benches benches_final _do_gem5 $b  &
    #done
    ##sleep $((RANDOM % 5 + 1))
    #return



    #DRAM=4
    
    set +ex
    if current_runs | grep "benchnr: $bench_nr"; then #cat results_gem5/gem5_pids.txt
        echo "skipping $bench_nr"
        return
    fi
    echo SLEEPING
    sleep 1
    echo HUMM
    sleep $((RANDOM % 21 + 1))
    echo DONE_SLEEP?
    if current_runs | grep "benchnr: $bench_nr"; then
        echo "skipping $bench_nr"
        return
    fi
    $nas/osdi26/controller.sh iterate_benches benches_final _do_gem5 $bench_nr  &
    echo ALIVOOO?
    return 0
}

do_all_big(){
    #cp $nas/osdi26/big_benches $nas/osdi26/benches_final
    $nas/osdi26/controller.sh getr 2>/dev/null  | awk '{print $NF}' | while read -r line; do
        bench_nr=$line
        wait_for_space # only select the bench after we are reading to compute! otherwise its a race condition!
        $nas/osdi26/controller.sh  launch_or_skip_one $bench_nr &
        sleep 2 
        
    done

}

l3(){

    $nas/osdi26/controller.sh iterate_benches benches_finalNATIVE test_l3_events
}

stall_cycles(){
    $nas/osdi26/controller.sh iterate_benches benches_finalNATIVE test_stalls_many #1 0009 # do all file
    #$nas/osdi26/controller.sh iterate_benches benches_finalNATIVE test_stalls #1 0 # do all non file

    #$nas/osdi26/controller.sh iterate_benches benches_finalNATIVE test_stalls #16 1
    #$nas/osdi26/controller.sh iterate_benches benches_finalNATIVE test_stalls 8 1
    #$nas/osdi26/controller.sh iterate_benches benches_finalNATIVE test_stalls #16 0009
    #$nas/osdi26/controller.sh iterate_benches benches_finalNATIVE test_stalls 8 0009

    #$nas/osdi26/controller.sh iterate_benches benches_finalNATIVE test_stalls 4
}

# remove last line of all the specified files
remove_last_line(){
    for f in $(ls .); do
        tail -n +2 "$f" > "$f.tmp" && mv "$f.tmp" "$f"
    done
}
# wc -l ./*  




######## SEGMENT A JOB BY TYPES...
_do_test_(){
    b=0
    check=$2
    #for a in $ARGS; do
    #numactl --membind 1 ${VMTOUCH} -m 60G -f -t $a  
    #    b=0009
    #done
    #if [[ $b == $check ]]; then
    #    return
    #fi
    sleep 1
    echo "RUNNING $threads $TIER $benchnr" 
    # 1 min = single thread  initialization! 
    sudo perf stat -e $evts -o $nas/osdi26/bin/real_stalls/$benchset\_$benchnr\_$TIER.log -- numactl --membind=$TIER_ --physcpubind=0,15 env OMP_NUM_THREADS=$threads   $BINARY $ARGS  < $STDIN
    echo "Ran!"
    cat $nas/osdi26/bin/real_stalls/$benchset\_$benchnr\_$TIER.log | grep stalls_l3_miss >> $nas/osdi26/bin/real_stalls/count
    cat $nas/osdi26/bin/real_stalls/$benchset\_$benchnr\_$TIER.log | grep bound_on_stores  >> $nas/osdi26/bin/real_stalls/countANY
    cat $nas/osdi26/bin/real_stalls/$benchset\_$benchnr\_$TIER.log | grep stalls_total  >> $nas/osdi26/bin/real_stalls/countTOTAL
    cat $nas/osdi26/bin/real_stalls/$benchset\_$benchnr\_$TIER.log | grep "seconds time elapsed"  | awk '{print $1}' >> $nas/osdi26/bin/real_stalls/countTIME
    cat $nas/osdi26/bin/real_stalls/$benchset\_$benchnr\_$TIER.log | grep cycles >> $nas/osdi26/bin/real_stalls/countCYCLES
    echo $benchset >> $nas/osdi26/bin/real_stalls/benchset
    echo $benchnr >> $nas/osdi26/bin/real_stalls/benchnr
    echo $BINARY >> $nas/osdi26/bin/real_stalls/binary
    echo "$ARGS $STDIN" >> $nas/osdi26/bin/real_stalls/ARGS
    echo "$TIER" >> $nas/osdi26/bin/real_stalls/mode
    echo "$threads" >> $nas/osdi26/bin/real_stalls/threads 
}

test_stalls_many(){

    #test_stalls 8 0

    test_stalls 1 0009
    test_stalls 16 0009
    #test_stalls 8 0009
    #test_stalls 1 0
    #test_stalls 16 0
    #test_stalls 8 0009
    #test_stalls 8 0
}
test_stalls(){
    threads=$1
    set +xe
    sudo /home/ist196723/memtis/memtis-userspace/scripts/set_uncore_freq.sh on
    touch ho
    #echo oooooooooooo $BINARY
    #return
    if [[ -z $STDIN ]]; then
        STDIN=ho
    fi
    

    pushd $WORKDIR
    #now=$(date +%s)
    evts="cycle_activity.stalls_l3_miss,exe_activity.bound_on_stores,cycle_activity.stalls_total,cycles"
    TIER=FAST
    TIER_=0
    _do_test_ $2
    TIER=SLOW
    TIER_=1
    _do_test_ $2

    if [ -f ~/stop ]; then
        echo "STOPPING"
        exit
    fi
    return 

    #sudo perf stat -e $evts -o $nas/osdi26/bin/real_stalls/$benchset\_$benchnr\_SLOW.log -- numactl --membind=1 --physcpubind=0,15 env OMP_NUM_THREADS=$threads   $BINARY $ARGS  < $STDIN
    #cycle_activity.stalls_total

    echo $benchset >> $nas/osdi26/bin/real_stalls/benchset
    echo $benchnr >> $nas/osdi26/bin/real_stalls/benchnr
    echo $BINARY >> $nas/osdi26/bin/real_stalls/binary
    echo "$ARGS $STDIN" >> $nas/osdi26/bin/real_stalls/ARGS
    echo "SLOW" >> $nas/osdi26/bin/real_stalls/mode
    echo "$threads" >> $nas/osdi26/bin/real_stalls/threads 
    cat $nas/osdi26/bin/real_stalls/$benchset\_$benchnr\_SLOW.log | grep stalls_l3_miss >> $nas/osdi26/bin/real_stalls/count
    cat $nas/osdi26/bin/real_stalls/$benchset\_$benchnr\_SLOW.log | grep stalls_any >> $nas/osdi26/bin/real_stalls/countANY
    cat $nas/osdi26/bin/real_stalls/$benchset\_$benchnr\_SLOW.log | grep cycles >> $nas/osdi26/bin/real_stalls/countCYCLES
    # GREP TIME
    #cat $nas/osdi26/bin/real_stalls/$benchset\_$benchnr\_SLOW.log | grep stalls_l3_miss >> $nas/osdi26/bin/real_stalls/count

    if [ -f ~/stop ]; then
        echo "STOPPING"
        exit
    fi
    


}

test_l3_events(){
    # STDIN
    set +xe
    sudo /home/ist196723/memtis/memtis-userspace/scripts/set_uncore_freq.sh on
    touch ho
    #echo oooooooooooo $BINARY
    #return
    if [[ -z $STDIN ]]; then
        STDIN=ho
    fi
    

    pushd $WORKDIR
    sudo perf stat -e mem_load_retired.l3_miss -o $nas/osdi26/bin/real/$benchset\_$benchnr\_FAST.log -- numactl --membind=0 --cpunodebind=0 env OMP_NUM_THREADS=1   $BINARY $ARGS  < $STDIN
    cat $nas/osdi26/bin/real/$benchset\_$benchnr\_FAST.log | grep mem_ >> $nas/osdi26/bin/real/count
    echo $benchset >> $nas/osdi26/bin/real/benchset
    echo $benchnr >> $nas/osdi26/bin/real/benchnr
    echo $BINARY >> $nas/osdi26/bin/real/binary
    echo "$ARGS $STDIN" >> $nas/osdi26/bin/real/ARGS
    echo "FAST" >> $nas/osdi26/bin/real/mode
    sudo perf stat -e mem_load_retired.l3_miss -o $nas/osdi26/bin/real/$benchset\_$benchnr\_SLOW.log -- numactl --membind=1 --cpunodebind=0 env OMP_NUM_THREADS=1   $BINARY $ARGS  < $STDIN


    echo $benchset >> $nas/osdi26/bin/real/benchset
    echo $benchnr >> $nas/osdi26/bin/real/benchnr
    echo $BINARY >> $nas/osdi26/bin/real/binary
    echo "$ARGS $STDIN" >> $nas/osdi26/bin/real/ARGS
    echo "SLOW" >> $nas/osdi26/bin/real/mode
    cat $nas/osdi26/bin/real/$benchset\_$benchnr\_SLOW.log | grep mem_ >> $nas/osdi26/bin/real/count

    if [ -f ~/stop ]; then
        echo "STOPPING"
        exit
    fi

    #$nas/osdi26/controller.sh getr 2>/dev/null  | awk '{print $NF}' | while read -r line; do

}

do_all(){
    #cp $nas/osdi26/benches_final_backup $nas/osdi26/benches_final
    #| grep -v 20.sg | grep -E 'lulesh|btree|XSBench|NPB|liblinear' 
    #$nas/osdi26/controller.sh getr 2>/dev/null  | awk '{print $NF}' | 
    while read -r line; do
    echo " ---------------"
    echo "$line"
        bench_nr=$line
        echo $bench_nr
    echo " ---------------"
        echo $bench_nr
        echo $bench_nr
        echo $bench_nr
        wait_for_space # only select the bench after we are reading to compute! otherwise its a race condition!
        #echo DISOWNED IT
        echo DISOWNED IT
        echo DISOWNED IT
        #edisown
        set +xe

#        {
#            #disown
{
            sleep 1
            echo BEFORE LAUNCH
                $nas/osdi26/controller.sh  launch_or_skip_one $bench_nr    2>/dev/null 1>/dev/null  < /dev/null
}
#                echo Launched it
#        } 
        #disown
        echo DISOWNED IT
        echo DISOWNED IT
        echo DISOWNED IT
        echo DISOWNED IT
        echo DISOWNED IT
        echo DISOWNED IT
        echo DISOWNED IT
        #sleep 30
        echo DISOWNED IT
        echo DISOWNED IT
        echo DISOWNED IT
        echo DISOWNED IT
        echo DISOWNED IT
        echo DISOWNED IT
        echo DISOWNED IT
        echo DISOWNED IT
        echo DISOWNED IT
        echo STILL_ITERATING_THROUGH_BENCHES
        echo $bench_nr
        sleep 2 
        echo "humm"
    #    $nas/osdi26/controller.sh getr
    #    echo "this is what you get"
    done < <($nas/osdi26/controller.sh getr 2>/dev/null  | awk '{print $NF}' )
}


launch_or_skip_oneREPEAT(){
    bench_nr=$1
    # SPACE between bench_nr and the rest!! otherwise we will catch more numbers!!
    number_of_starts=$(cat results_gem5/gem5_pids.txt | grep -E "benchnr: $bench_nr .*STARTED" | wc -l)
    if [ $number_of_starts -gt 3 ]; then # 2 is the normal, cuz of increase 80/0, 3 indicates that a rerun was launched
        echo "skipping $bench_nr"
        return
    fi
    $nas/osdi26/controller.sh iterate_benches benches_final _do_gem5 $bench_nr  &
}

repeat_gem5(){
    file=$1
    cat $file | while read linenr; do
        # get the line nr 
        #line="$(cat $nas/osdi26/benches_final | head -n $linenr | tail -n 1 )"
        #eval "$line"
        wait_for_space
        $nas/osdi26/controller.sh  launch_or_skip_oneREPEAT $linenr &
    done
}




reset_ALL(){
    yes | rm -r results_gem5/*
    yes | rm final_data/**/.png
}
best_gapbs(){
    $nas/osdi26/controller.sh getr | grep 20.sg | awk '{print $NF}' | xargs -I {} $nas/osdi26/controller.sh iterate_benches benches_final _do_gem5 {}
}
do_parsec(){
    $nas/osdi26/controller.sh getr | grep parsec | awk '{print $NF}' | xargs -I {} $nas/osdi26/controller.sh iterate_benches benches_final _do_gem5 {}
}
do_sss(){
    $nas/osdi26/controller.sh getr | grep WEIGHT | awk '{print $NF}' | xargs -I {} $nas/osdi26/controller.sh iterate_benches benches_final _do_gem5 {}
}

lulesh(){
    $nas/osdi26/controller.sh getr 2>/dev/null | grep lulesh | grep "\-s 10" | awk '{print $NF}' | {
        while read -r line; do
            bench_nr=$line
            DRAM=1
            $nas/osdi26/controller.sh iterate_benches benches_final _do_gem5 $bench_nr
        done
    } 

}

cat_memtis_config(){
    for file in /sys/kernel/mm/htmm/*; do
        echo "$(basename $file): $(cat $file)"
    done
}

posfix=""
memtis_config="memtis"
run_memtis(){
    repeats=$3
    dram=$1
    exec=$2
    shift 3
    sudo sh -c "echo 3 > /sys/kernel/mm/htmm/htmm_event_precision"
    cat_memtis_config
    for i in $(seq 1 $repeats); do
        echo "------- START"
        python3 ~/nas/latency_benchmark/main.py exec runner_memtis $exec "$*"  --device="ecxl" --dram=$dram  # | tee -a "results/$memtis_config\_$(basename $out)-$i-"
        echo "------- END"
    done
}
MODE="NONE"

run_memtis_field(){
    source_map="$2"
    {
    echo "FILED $1"
    if [ ! -f "$source_map" ]; then
        echo "ERROR: Source map $source_map not found"
        exit
    fi
    cp "$source_map"  ~/latencymaps/$(basename $source_map| awk '{print $1}')
    #0.58
    #disable skipcooling
    #sudo sh -c "echo disabled > /sys/kernel/mm/htmm/htmm_skip_cooling"

    # memory mode = 1
    sudo sh -c "echo 1 > /sys/kernel/mm/htmm/htmm_mode"
    sudo sh -c "echo enabled > /sys/kernel/mm/htmm/htmm_weighted_sampling"
    sudo sh -c "echo $1 > /sys/kernel/mm/htmm/htmm_weight_field"
    run_memtis $FAST_DRAM $BINARY 1 $ARGS | tee memtis_outputs_field_$1  

    } | add_column "MEMTIS++-$1-$benchnr"
}

waitf(){
	while [ ! -e $(realpath $1)  ]; do
	  sleep 1
	done

}

run_memtis_no_migweighted(){
    # runs on the slow tier so that we experience the full overhead of the extra LLC misses
    column="MEMTIS-NO_MIG-$benchnr"
    {
        dram=$1
        if [ -z "$dram" ]; then
            dram=0
        fi
        FAST_DRAM=$dram
        prep
        echo "DRAM: $FAST_DRAM"
        sudo sh -c "echo 0 > /sys/kernel/mm/htmm/htmm_mode"
        sudo sh -c "echo enabled > /sys/kernel/mm/htmm/htmm_weighted_sampling"
        run_memtis $FAST_DRAM $BINARY 1 $ARGS
        sudo sh -c "echo 1 > /sys/kernel/mm/htmm/htmm_mode"
    } |  add_column "$column"
}
run_memtis_all_fast(){
    column="MEMTIS-ALL_FAST-$benchnr"
	echo "MODE: ALL FAST"
	run_memtis_optimal_static_allocation "$1" 0 60000
}
run_memtis_all_slow(){
    column="MEMTIS-ALL_SLOW-$benchnr"
	echo "MODE: ALL SLOW"
	run_memtis_optimal_static_allocation "$1" 1 0
}
run_memtis_heap_fast(){
    files=$1
    dram=$2
    if [ -z "$dram" ]; then
        dram=5000
    fi
    echo "MODE: HEAP FAST ($dram)"
    column="MEMTIS-HEAP_FAST-$dram-$benchnr"
	run_memtis_optimal_static_allocation "$files" 1 $dram
}


add_column(){
	sed "s/^/$1 /" 
}


run_numactl_heap_fast(){
    {
    prep
    # dropcacches
    sudo sh -c "echo 3 > /proc/sys/vm/drop_caches"
    start_hold_files 1 $files
    numactl --membind 1 $BINARY $ARGS
    stop_hold_files
    } | add_column "NUMACTL-HEAP_FAST-$benchnr"
}
run_numactl_all_slow(){
    {
    prep
    sudo sh -c "echo 3 > /proc/sys/vm/drop_caches"
  #  start_hold_files 1 $files
    numactl --membind 1 $BINARY $ARGS
  #  stop_hold_files
    } | add_column "NUMACTL-ALL_SLOW-$benchnr"
}
run_numactl_all_fast(){
    {
    prep
    sudo sh -c "echo 3 > /proc/sys/vm/drop_caches"
#    start_hold_files 0 $files
    numactl --membind 0 $BINARY $ARGS
#    stop_hold_files
    } | add_column "NUMACTL-ALL_FAST-$benchnr"
}

start_hold_files(){
    numactl --membind $1 ${VMTOUCH} -m 60G -L -f -P vmtouchpid -t $2  &
    vmpid=$!
    waitf vmtouchpid
}
stop_hold_files(){
    kill -15 $vmpid
}

run_memtis_optimal_static_allocation(){
	{
		files="$1"    #############  ARGS MUST RELIGIOSLY BE AT THE START
		tier="$2"
		dram="$3"
    FAST_DRAM=60000 # 60GB.. basically no limit
		if [ -z $2 ]; then
			tier=1
		fi
		if [ ! -z $dram ]; then
			
			FAST_DRAM=$dram
			
		fi
    sudo  sh -c "echo 3 > /proc/sys/vm/drop_caches"
    # TODO - read all files in the current dir (which is the running dir!) numactl --membind 1 ${VMTOUCH} -f -t $local_graph  -m 60G
    start_hold_files $tier $files
    echo "BOUT TO RUN $BINARY $ARGS $(date '+%Y-%m-%d_%H-%M-%S')"
    sudo sh -c "echo 0 > /sys/kernel/mm/htmm/htmm_mode"
    #numactl --membind 0 --cpubind 0 $BINARY $ARGS
    run_memtis $FAST_DRAM $BINARY 1 $ARGS 
    stop_hold_files
    
}|  add_column "$column" | tee -a memtis_outputs_field_static 


}


wipeout_bench(){
    host=$1
    # if not host then use localhost
    if [ -z "$host" ]; then
        host="$(hostname)"
    fi
    now=$(date +%s)
    cp $nas/osdi26/results_gem5/gem5_pids.txt "$nas/osdi26/backups/gem5_pids.txt.$now"
    sed -i "/sssp/d" $nas/osdi26/results_gem5/gem5_pids.txt
}

wipeout_host(){
    host=$1
    # if not host then use localhost
    if [ -z "$host" ]; then
        host="$(hostname)"
    fi
    now=$(date +%s)
    cp $nas/osdi26/results_gem5/gem5_pids.txt "$nas/osdi26/backups/gem5_pids.txt.$now"
    sed -i "/$host/d" $nas/osdi26/results_gem5/gem5_pids.txt
}
disable_migration(){
    sudo sh -c "echo 0 > /sys/kernel/mm/htmm/htmm_mode"
}
kill_sampler(){
    ~/memtis/memtis-userspace/bin/kill_ksampled
}

ablock_time(){
    f=$1
    output=$2
    type=("asm_exc_page_fault" "gomp_barrier") 
    header="SYSTEM "
    row="$MODE "
    #accepted_types=$(printf "%s," "${type[@]}")
    #accepted_types=${accepted_types%,}  # Remove trailing comma

# where faults happen? 
{
    echo "${type[@]} %"
    awk '/page_fault/ {a["mig"]+= $NF;} /gomp/ {a['omp']+= $NF;} END{print a["mig"] " " a['omp']}' $f  
}| tee $output 
    exit
    #>(awk '{
    #echo "${type[@]} %" 
    #awk -v accepted_lines="${accepted_types}" 'BEGIN{split(accepted_lines, accepted_array, ",")}{if ($1 in accepted_array) a[$1]+= $NF;}END{
    #n = asorti(a,sorted_keys)
    #for (i=1;i<=n;i++) printf "%s ", a[sorted_keys[i]];
    #print ""}' $f | 
    #awk '{ 
    #sum=0; for (i=1;i<=NF;i++) sum+=$i;   
    #for (i=1;i<=NF;i++) printf "%s ", $i/sum;
    #print ""}'
    #} | tee $output
    ## do a stacked bar plot of the data in python
    ##ython3 -c "import matplotlib.pyplot as plt; import numpy as np; import pandas as pd; df = pd.read_csv('$(realpath $outputfile)'); df.plot(kind='bar', stacked=True); plt.show()"
}
#block_time offcpu_loading
#block_time offcpu_loading_++
bo(){


    disable_migration
    kill_sampler
    run_memtis $FAST_DRAM $BINARY 1 $ARGS
    # measure the number of stall cycles experienced 
    # perf stat -e INST_RETIRED.STALL_CYCLES -p $BINARY $ARGS
}

collect_overheads_data(){
    output="$1"
    prefix=real_data/gen/overheads
    i=0
    bench_pip=$(pgrep $(basename "$BINARY"))
    trials=0
    memory_tiering_state="full"
    while read -r line; do
        bench_pip=$(pgrep $(basename "$BINARY")) # if the process ceases to exist, this will make the loop read all and exit
        if [ -z "$bench_pip" ]; then
            continue # did not initialize yet....
        fi

        if [$trials -eq 100]; then
            #echo disabling migration
            memory_tiering_state="migration_disabled"
            disable_migration
        fi

        if [$trials -eq 100]; then
            echo disabling sampler
            memory_tiering_state="sampler_disabled"
            kill_sampler
        fi
        if [$trials -lt 300]; then
            continue
        fi
        if [ "$line" == "Trial Time:" ]; then
            trials=$(($trials+1))
            echo $line >> $prefix/$output-RAW-$memory_tiering_state
        fi
    done
}


collect_blocked_time_data(){
    output="$1"
    prefix=real_data/gen/offcpu_loading
    i=0
    bench_pip=$(pgrep $(basename "$BINARY"))
    while read -r line; do
        bench_pip=$(pgrep $(basename "$BINARY")) # if the process ceases to exist, this will make the loop read all and exit
        if [ -z "$bench_pip" ]; then
            continue # did not initialize yet....
        fi
        ablock_time <(sudo python3 $nas/osdi26/infra/real/offcpu.py   -p $bench_pip -f -d $MEASURING_TIME | tee $prefix/$output-RAW-$i ) $prefix/$output-$i | add_column "BLOCKED_OUTPUT-$i" 
        i=$(($i+1))
    done

}

# grep -A 9999999 Average Time

break_down_overheads(){
    set +x
    set +e
    MEASURING_TIME=5
    FAST_DRAM=100
    #block_time offcpu_loading

    # the blocked time is greater in memtis++??
    GLOBAL_MODIFICATION="10000cooling"
    BASE_SYSTEM="NORMAL"

    sudo sh -c "echo 2 > /sys/kernel/mm/htmm/htmm_mode"
    # 250 000 us = 250 ms (during a 5 second run = 5% )
    MODE="MEMTIS_$BASE_SYSTEM-$GLOBAL_MODIFICATION"
    sudo sh -c "echo disabled > /sys/kernel/mm/htmm/htmm_weighted_sampling"

    default_memtis_settings
    run_memtis $FAST_DRAM $BINARY 1 $ARGS  | tee >(collect_blocked_time_data "$MODE") 
    run_memtis $FAST_DRAM $BINARY 1 $ARGS  | tee >(collect_overheads_data "$MODE")

    for field in 1, 7; do 
        BASE_SYSTEM="++$field"
        MODE="MEMTIS_$BASE_SYSTEM-$GLOBAL_MODIFICATION"
        echo "$MODE"
        sudo sh -c "echo enabled > /sys/kernel/mm/htmm/htmm_weighted_sampling"
        sudo sh -c "echo 2 > /sys/kernel/mm/htmm/htmm_mode"
        sudo sh -c "echo 3 > /sys/kernel/mm/htmm/htmm_event_precision"
        run_memtis_field $field | tee >(collect_blocked_time_data "$MODE")
        run_memtis_field $field | tee >(collect_overheads_data "$MODE")
    done
    #run_memtis $FAST_DRAM $BINARY 1 $ARGS 
}





default_memtis_settings(){
    sudo sh -c "echo disabled > /sys/kernel/mm/htmm/htmm_weighted_sampling"
    sudo sh -c "echo disabled > /sys/kernel/mm/htmm/htmm_skip_cooling"            # REMOVE IT 
     echo 1500 | sudo tee /sys/kernel/mm/htmm/htmm_sample_period
    echo 100007 |sudo  tee /sys/kernel/mm/htmm/htmm_inst_sample_period
    echo 1 | sudo tee /sys/kernel/mm/htmm/htmm_thres_hot
    echo 2 | sudo tee /sys/kernel/mm/htmm/htmm_split_period
    #    100000 
    echo 100000 | sudo tee /sys/kernel/mm/htmm/htmm_adaptation_period
    echo 2000000 | sudo tee /sys/kernel/mm/htmm/htmm_cooling_period
    # CHAAAAAAAAAANGE
    
    if [ "$HUGE_SPLIT" = "NO-SPLIT" ]; then
        echo 1 | sudo tee /sys/kernel/mm/htmm/htmm_mode
    else 
        echo 2 | sudo tee /sys/kernel/mm/htmm/htmm_mode
    fi
    

    echo 500 | sudo tee /sys/kernel/mm/htmm/htmm_demotion_period_in_ms
    echo 500 | sudo tee /sys/kernel/mm/htmm/htmm_promotion_period_in_ms
    echo 4 | sudo tee /sys/kernel/mm/htmm/htmm_gamma
    ###  cpu cap (per mille) for ksampled
    echo 0 | sudo tee /sys/kernel/mm/htmm/ksampled_soft_cpu_quota
}


run_stats(){

awk '/Average Time/ {
a+=1
  data[a] = $NF
}
function percentile(p) {
    i = int(p * n)
    if (i < 1) i = 1
    if (i > n) i = n
    return data[i]
  }
END {
  n = a
  for (i = 1; i <= n; i++) {
    for (j = i + 1; j <= n; j++) {
      if (data[i] > data[j]) {
        temp = data[i]; data[i] = data[j]; data[j] = temp
      }
    }
  }


  sum = 0
  for (i = 1; i <= n; i++) sum += data[i]
  avg = sum / n
  
  p99 = percentile(0.99)
  p50 = percentile(0.50)
  best = data[1]
  worst = data[n]
  
  print "p99:", p99
  print "p50:", p50
  print "average:", avg
  print "worst:", worst
  print "best:", best
}' $1


}

choose_weight_field(){

#Acost_inst_stall_time  1
#Bcost_inst_L3stall_time 2
#Ccost_inst_L3MLP 
#Dcost_inst_MLP
#Ecost_inst_MLP/stall
#Fcost_inst_MLP/total
#Gcost_inst_stall*cost_inst_MLP
#Hcost_inst_stall*cost_inst_MLP'

#cg.C L3MLP
#cg.B (any except L3MLP)
#bt.A (L3stalled)
#is.C (totalStall)
#lu.A (L3Stalled)
#mc.G L3MLPStalled
#sp.B (L3stalled)
if [[ $binary == *mcf* ]]; then
    FIELD=3
fi

if [[ $binary == *LULESH* ]]; then
    FIELD=2
fi
if [[ $binary == *lbm* ]]; then
    FIELD=2
fi

if [[ $binary == *cg.C ]]; then
    FIELD=3
fi
if [[ $binary == *cg.B ]]; then
    FIELD=2        # same benchmark! but its very small!!! 
fi
if [[ $binary == *bt.A ]]; then
    FIELD=2
fi
if [[ $binary == *is.C ]]; then
    FIELD=1
fi
if [[ $binary == *lu.A ]]; then
    FIELD=2
fi
if [[ $binary == *mc.G ]]; then
    FIELD=3
fi
if [[ $binary == *sp.B ]]; then
    FIELD=2
fi

FIELD="1"

}

echo "" > /home/ist196723/nas/osdi26/real_data/numpy/bin
echo "" > /home/ist196723/nas/osdi26/real_data/numpy/migs
echo "" > /home/ist196723/nas/osdi26/real_data/numpy/time
echo "" > /home/ist196723/nas/osdi26/real_data/numpy/mode

results_to_numpy(){
    # time per benchmark
    # total migs per benchmark
    # the name of the system


        folder="/mnt/nas/inesc/ist196723/osdi26/real_data/clean_try"
        cat benchmarks_native_todo_final | while read -r line; do
            export OMP_NUM_THREADS=8
            eval "$line"

            set +xe
            binary=$(basename $BINARY)
            for mode in  "MEMTIS-NORMAL-0" "MEMTIS-NORMAL-90000" "MEMTIS-MAIS_MAIS" 'MEMTIS-NORMAL-(?!90000|0)[0-9]+'; do
                
            f=/home/ist196723/nas/osdi26/real_data/clean_try/real_data/batch/
            for file in $(ls $f  | grep -P "$binary.*$mode"); do
                base=$(basename $file)
                case $base in
                    PERF*)
                        echo "PERF file: $file"
                        ;;
                    STATS*)
                        echo "STATS file: $file"
                        ;;
                    *)
                        echo "Other file: $file"
                        if grep -q "Total Threads.*=.*8" $f$base ; then
                            continue
                        fi
                        #if ! grep -q "NAS Parallel" $f$base ; then
                            #continue
                        #fi
                        
                        time=$(cat $f$base  | grep "Time in seconds" | awk '{print $NF}')
                        #htmm_nr_promoted
                        pgmigrate_success=$(grep  "htmm_migrate" $f$base | head -n 1 | awk '{print $NF}')
                        pgmigrate_end=$(grep  "pgmigrate_success" $f$base | tail -n 1 | awk '{print $NF}')
                        #htmm_nr_promoted
                        #htmm_nr_demoted
                        pgmigrate_success=$(grep  "pgmigrate_success" $f$base | head -n 1 | awk '{print $NF}')
                        pgmigrate_end=$(grep  "pgmigrate_success" $f$base | tail -n 1 | awk '{print $NF}')
                        total_migs="$(($pgmigrate_end-$pgmigrate_success))"
                        echo $binary >> /home/ist196723/nas/osdi26/real_data/numpy/bin
                        echo $total_migs >> /home/ist196723/nas/osdi26/real_data/numpy/migs
                        echo $time >> /home/ist196723/nas/osdi26/real_data/numpy/time
                        echo $mode >> /home/ist196723/nas/osdi26/real_data/numpy/mode
                        ;;
                esac

            done
            done

            for mode in "MEMTIS-numactl-0" "MEMTIS-numactl-90000"; do 
                total_migs=0
                f="/home/ist196723/nas/osdi26/real_data/clean_try/"
                for file in $(ls $f  | grep -P "output_$binary.*$mode"); do
                    base=$(basename $file)
                    case $base in
                        PERF*)
                            echo "PERF file: $file"
                            ;;
                        STATS*)
                            echo "STATS file: $file"
                            ;;
                        *)

                            echo "Other file: $file"
                            if grep -q "Total Threads.*=.*8" $f$base ; then
                                continue
                            fi
                            if ! grep -q "NAS Parallel" $f$base ; then
                                continue
                            fi
                            
                            time=$(cat $f$base  | grep "Time in seconds" | awk '{print $NF}')
                            echo $binary >> /home/ist196723/nas/osdi26/real_data/numpy/bin
                            echo $total_migs >> /home/ist196723/nas/osdi26/real_data/numpy/migs
                            echo $time >> /home/ist196723/nas/osdi26/real_data/numpy/time
                            echo $mode >> /home/ist196723/nas/osdi26/real_data/numpy/mode
                        esac
                done

            done
            continue


            pushd $WORKDIR
            benchid=$(echo "$line" | md5sum)
            # all files that DO NOT starts with PERF/STATS that are in $folder/
            files=$(find "$folder" ! -name "PERF*" ! -name "STATS*" -type f -exec readlink -f {} \; )
            echo $files
            grep "$benchid" $files | {
                while read -r file; do
                    execution_id=$(awk -F- '{print $NF}' <<<"$file")
                    echo $execution_id

                    # Is NAS PB in output
                    #
                    #echo $file
                done
            }
            
            
            break
            popd
            done
}
do_numpy(){
    results_to_numpy
    python3 bin/python_parser.py
}

choose_dram(){
        FAST_DRAM=1000
        if [[ $binary == *mcf* ]]; then
            FAST_DRAM=2000
        fi
        if [[ $binary == *.B ]]; then
            FAST_DRAM=100
            DRAM=100
        fi
        if [[ $binary == *.C ]]; then
            FAST_DRAM=400
            DRAM=400
        fi
        if [[ $binary == *.A ]]; then
            FAST_DRAM=20
            DRAM=20
        fi
        DRAM=$FAST_DRAM
}
choose_weight_file(){


        source_map_dir="/home/ist196723/nas/osdi26/final_data/maps"
        if [[ $binary == *mcf* ]]; then
            source_map="$(ls /home/ist196723/nas/osdi26/final_data/maps/$(basename $BINARY)* | tail -n 1)"
        else
            source_map="$(ls /home/ist196723/nas/osdi26/final_data/maps/$(basename $BINARY)* | head -n 1)"
        fi

        #source_map_dir="/home/ist196723/nas/osdi26/final_data/maps"
        #source_map="$(ls /home/ist196723/nas/osdi26/final_data/maps/$(basename $BINARY)* | head -n 1)"
}
do_native_memtis(){
        binary=$(basename $BINARY)
        choose_dram
        choose_weight_field
        if [[ -z "$FIELD" ]]; then
            return # field not found == benchmark not supported!
        fi 
        set_mode
        
        choose_weight_file
        echo $source_map
        set_mode
        pp_run
}
do_lat_map_evt(){
    OMP_NUM_THREADS=32

    local_graph="/mnt/nas/inesc/ist196723/gapbs/benchmark/graphs/kron.sg"

    BINARY="/mnt/nas/inesc/ist196723/gapbs/bc"; ARGS="-f $local_graph -n 100"; STDIN=""; WORKDIR="/"; # size=simsmall    64
    sudo perf record -o bc.perf -c 100 -e  mem_load_retired.l3_miss:pppu -- $BINARY $ARGS
    exit

    BINARY="/mnt/nas/inesc/ist196723/gapbs/bfs"; ARGS="-f $local_graph -n 100"; STDIN=""; WORKDIR="/"; # size=simsmall    64
    source_map="/home/ist196723/nas/osdi26/final_data/maps_human/best/bc 64.txt"
    sudo perf record -o bfs.perf -c 100 -e  mem_load_retired.l3_miss:pppu -- $BINARY $ARGS

BINARY="/mnt/nas/inesc/ist196723/benchmarks/cpu2017/benchspec/CPU/623.xalancbmk_s/exe/xalancbmk_s_base.NOavxprota-m64"; ARGS="-v t5.xml xalanc.xsl"; STDIN=""; WORKDIR="/home/ist196723/nas/benchmarks/cpu2017/benchspec/CPU/623.xalancbmk_s/run/run_base_refspeed_NOavxprota-m64.0000"; # size=
    pushd $WORKDIR
    sudo perf record -o xal.perf -c 100 -e  mem_load_retired.l3_miss:pppu -- $BINARY $ARGS
    popd
ls /mnt/nas/inesc/ist196723/benchmarks/binaries/* | xargs -I {} bash -c "readelf -S '{}' | grep .text | awk -F'[[:space:]]+' '{ printf \"%d\n\", strtonum(\"0x\" \$6) }' > ~/vmaoffsets/\$(basename {})"
}
# ./controller.sh do_lat_map_evt

#readelf -S /mnt/nas/inesc/ist196723/gapbs/bfs | grep .text | awk -F'[[:space:]]+' '{ printf \"%d 1\\n\", strtonum(\"0x\"$1) }'

create_lat_map(){
    # awk '!/^#/ {printf "%d 1\n", strtonum("0x"$1)}' BC_SYNTH | sort -n | uniq > bfs_MANUAL

    #sudo perf script -i bfs.perf -F ip | awk '!/^#/ {printf "%d 1\n", strtonum("0x"$1)}' | sort -n | uniq | tee ~/latencymaps/bfs
    sudo perf script -i bfs.perf -F ip | gawk '
  !/^#/ {
    ip = strtonum("0x"$1);
    arr[ip]++;
  }
  END {
    PROCINFO["sorted_in"] = "@ind_num_asc"
    for (ip in arr) {
      print ip, "1"
    }
  }
' > ~/latencymaps/bfs
# !/^#/ {printf "%d 1\n", strtonum("0x"$1)}' | sort -n | uniq | tee ~/latencymaps/xalancbmk_s_base.NOavxprota-m64
    #sudo perf script -i bc.perf -F ip | awk '!/^#/ {printf \"%d 1\\n\", strtonum(\"0x\"$1)}' | sort -n | uniq > BFS_MANUAL #latencymaps/bfs
    sudo perf script -i xal.perf -F ip | gawk ' 
  !/^#/ {
    ip = strtonum("0x"$1);
    arr[ip]++;
  }
  END {
  PROCINFO["sorted_in"] = "@ind_num_asc"
        for (ip in arr) {
      print ip, "1"
    }
  }'  > ~/latencymaps/xalancbmk_s_base.NOavxprota-m64

# size=$(cat ~/latencymaps/bfs | wc -l)

}

lk(){

        echo 32  > /tmp/omp_num_threads
        default_memtis_settings
        sudo sh -c "echo $quota > /sys/kernel/mm/htmm/ksampled_soft_cpu_quota"
          
        pushd $WORKDIR
        #$BINARY $ARGS
        (echo "QUOTA $quota DS $i BIN $BINARY";  sudo journalctl -f & PID=$!; run_memtis $FAST_DRAM "$BINARY" 1 $ARGS; sudo kill $PID) | tee -a /home/ist196723/nas/osdi26/real_data/lookup/$(basename $BINARY)-$quota-$i-$(date +%s)-$extra.log
        popd
}
HASHTABLE=4
test_lookup(){
    compressed_array=1
    hashtable=4
    naive_array=5

# ./controller.sh test_lookup

    #mv ~/nas/osdi26/real_data/lookup/*  ~/nas/osdi26/real_data/lookup/old/
    local_graph="/mnt/nas/inesc/ist196723/gapbs/kron23.sg"
    #local_graph="/mnt/nas/inesc/ist196723/gapbs/benchmark/graphs/kron20.sg"
    BINARY="/mnt/nas/inesc/ist196723/gapbs/bfs"; ARGS="-f $local_graph -n 50"; STDIN=""; WORKDIR="/"; # size=simsmall    64
    OMP_NUM_THREADS=32


    cp  bfs_MANUAL ~/latencymaps/bfs
    #cp  bfs_MANUAL ~/latencymaps/bfs
    FAST_DRAM=20000
    BINARY="/mnt/nas/inesc/ist196723/benchmarks/cpu2017/benchspec/CPU/623.xalancbmk_s/exe/xalancbmk_s_base.NOavxprota-m64"; ARGS="-v t5.xml xalanc.xsl"; STDIN=""; WORKDIR="/home/ist196723/nas/benchmarks/cpu2017/benchspec/CPU/623.xalancbmk_s/run/run_base_refspeed_NOavxprota-m64.0000"; # size=
    for reps in 0 1 2 3 ; do # 4 5 6 7 8 9; do
        quota=0
        i=$hashtable
        extra="hashtable"
        sudo sh -c "echo enabled > /sys/kernel/mm/htmm/htmm_weighted_sampling"
        lk 
        exit


        i=9999
        extra="normal_no_cap"
        sudo sh -c "echo disabled > /sys/kernel/mm/htmm/htmm_weighted_sampling"
        lk
        extra="normal_default_cap"
        quota=10
        lk 
        quota=0
        extra="asmem_no_cap"
        sudo sh -c "echo enabled > /sys/kernel/mm/htmm/htmm_weighted_sampling"
        i=$compressed_array
        lk
        exit


        for quota in 0; do
        for i in $compressed_array $hashtable $naive_array; do
            sudo sh -c "echo $i > /sys/kernel/mm/htmm/htmm_weighted_sampling_struct"
            cat /sys/kernel/mm/htmm/htmm_weighted_sampling_struct
            FIELD=1
            default_memtis_settings
            sudo sh -c "echo enabled > /sys/kernel/mm/htmm/htmm_weighted_sampling"
            ############ THE FIELD IS NOT COUNTING WITH THE INSTRUCTION!
            sudo sh -c "echo $FIELD > /sys/kernel/mm/htmm/htmm_weight_field"
            sudo sh -c "echo $quota > /sys/kernel/mm/htmm/ksampled_soft_cpu_quota"
            pushd $WORKDIR
            #$BINARY $ARGS
            (echo "QUOTA $quota DS $i BIN $BINARY";  sudo journalctl -f & PID=$!; run_memtis $FAST_DRAM "$BINARY" 1 $ARGS; sudo kill $PID) | tee -a /home/ist196723/nas/osdi26/real_data/lookup/$(basename $BINARY)-$quota-$i-$(date +%s).log
            popd
        done

    done
    done
}

get_lookup(){
    compressed_array=1
    hashtable=4
    naive_array=5
        for quota in 0 10 50; do
        for i in $compressed_array $hashtable $naive_array; do
        for f in  /home/ist196723/nas/osdi26/real_data/lookup/$(basename $BINARY)-$quota-$i-*.log; do
            avg_time_per_sample=$(awk '/TIME_STATS/ {print $2}' $f )
            avg_busy_wait_time=$(awk '/TIME_STATS/ {print $3}' $f )
            nr_of_samples=$(awk '/TIME_STATS/ {print $3}' $f )
            #nr_of_samples_per_second=$()
            

            
        done
    done
    done
}



ee_lookup(){
    do_lat_map_evt
    create_lat_map
    test_lookup
}


# 1759624040 delee this 
do_native(){
    set +xe
    FAST_DRAMS=(90000 0)
    i=0
    prepare
    now_in_seconds="$(date +%s)"
    binary=$(basename "$BINARY")
    folder=/mnt/nas/inesc/ist196723/osdi26/real_data/clean_try # first put the dir wrong to catch errors?
    ##OMP_NUM_THREADS=8
    echo $OMP_NUM_THREADS > /tmp/omp_num_threads
    export OMP_NUM_THREADS
    sudo sh -c "echo 100 > /proc/sys/kernel/perf_event_max_sample_rate"
    # nm_run 
    # if linux version is 6
    set +xe
    if echo $line | grep -v "XSBench"; then
        return
    fi
    i=0
    if [ $(uname -r | cut -d. -f1) -ge 6 ]; then
        echo "Linux version is 6 or higher"
        memtis-userspace/scripts/set_mem_size.sh $FAST_DRAM
        # VERIFY THAT VERSION 6 HAS NO WEIRD TIERING! 
    else
        echo "Linux version is lower than 6"
    fi 
    #set_bc
    do_native_memtis
    #set_bfs
    do_native_memtis
    do_native_memtis
    nm_run # 2 runs for reliable results!
    nm_run # 2 runs for reliable results!
    exit
    set_bfs
    nm_run # 2 runs for reliable results!
    set_bc
    nm_run # 2 runs for reliable results!
    exit
    
    for r in "0" "1"; do
        FAST_DRAM=${FAST_DRAMS[$i]}
        SYSTEM="numactl"
        echo $now_in_seconds
        set_mode
        #for i in {1..10}; do
        bash_c="$r" 
        /usr/bin/time -f "TIME_STATS %e %S %U %F" numactl --membind=$r --cpubind=0 $BINARY $ARGS  > $folder/output_"$MODE" 2>&1 & 
        pid=$!
        max_memory $pid 1 > $folder/rss_"$MODE" & 
        sudo  perf stat -e '{cycle_activity.stalls_l3_miss:u,INST_RETIRED.ANY:u}' -I 1000  -o $folder/perf_"$MODE" -p $pid 
        # U user cpu time 
        # S kernel cpu time 
        # e wall clock 
        # F major page faults (we will have less pg faults in single thread (because there is more time for migration?))
          
        i=$(($i+1))
        echo $benchid | sudo tee -a  $folder/time_"$MODE" $folder/output_"$MODE" $folder/rss_"$MODE" $folder/perf_"$MODE"
    done
    for DRAM in 90000 0 ; do
        FAST_DRAM=$DRAM
        set_mode
        nm_run # 2 runs for reliable results!
    done

}




llc_perf_natives(){
    #for ola in 1 2 3 4 5 6; do
        set +xe
        IFS=
        cat benchmarks_native_todo_final | while read -r line; do
        set +xe
            export OMP_NUM_THREADS=8
            echo "$line"
            eval "$line"
            pushd $WORKDIR
            set +xe
            benchid=$(echo "$line" | md5sum)
            binary_name=$(basename $BINARY)
            sudo perf record -o $binary_name.perf -c 500 -e  mem_load_retired.l3_miss -- $BINARY "$ARGS" 
            popd
        done
}
# sudo perf script -i l3_a.perf  | awk '{print $5}' | sort | uniq -c | wc -l


do_natives(){
    for ola in 1 2 3 4 5 6; do
        set +xe
        IFS=
        cat benchmarks_native_todo_final | while read -r line; do
        set +xe
            export OMP_NUM_THREADS=8
            echo "$line"
            eval "$line"
            pushd $WORKDIR
            benchid=$(echo "$line" | md5sum)
            do_native
            popd
        done
        cat benchmarks_native_todo_final | while read -r line; do
            export OMP_NUM_THREADS=8
            eval "$line"
            benchid=$(echo "$line" | md5sum)
            do_native
        done
        cat benchmarks_native_todo_final | while read -r line; do
            export OMP_NUM_THREADS=8
            eval "$line"
            benchid=$(echo "$line" | md5sum)
            do_native
        done
        cat benchmarks_native_todo_final | while read -r line; do
            export OMP_NUM_THREADS=8
            eval "$line"
            benchid=$(echo "$line" | md5sum)
            do_native
        done
    done
}


pp_run(){
    default_memtis_settings
    #cat
    #source_map_dir="$(dirname "$source_map")" 
    canon_name="$(basename "$source_map" | cut -f1 -d" " )"
    #dest_source_map="$source_map_dir/$(basename "$source_map" | cut -f1 -d" " )"
    #cp "$source_map" $dest_source_map #bfs 64.txt" 
    #cp "$source_map" /home/ist196723/latencymaps/$canon_name 
    #sudo sh -c "echo enabled > /sys/kernel/mm/htmm/htmm_skip_cooling"            # REMOVE IT 
    sudo sh -c "echo enabled > /sys/kernel/mm/htmm/htmm_weighted_sampling"
    ############ THE FIELD IS NOT COUNTING WITH THE INSTRUCTION!
    sudo sh -c "echo $FIELD > /sys/kernel/mm/htmm/htmm_weight_field"
    sudo  sh -c "echo 3 > /proc/sys/vm/drop_caches"
    sudo  sh -c "echo 3 > /proc/sys/vm/drop_caches"
    #100000
    #echo 99 | sudo tee /sys/kernel/mm/htmm/ksampled_soft_cpu_quota

    #           echo 50000 | sudo tee /sys/kernel/mm/htmm/htmm_adaptation_period
    #sudo sh -c "echo 5000000000 >  /sys/kernel/mm/htmm/htmm_cooling_period" #4x more coold owns
    #sudo sh -c "echo  5000 >  /sys/kernel/mm/htmm/htmm_adaptation_period" # 10x more adaptation period
          #2000000 
    #echo 2000000 | sudo tee /sys/kernel/mm/htmm/htmm_cooling_period
    #echo 2 | sudo tee /sys/kernel/mm/htmm/htmm_thres_hot
    # 63 
    set -x 
    set -e 
    SYSTEM="MAIS_MAIS-$FIELD-"
    if [ $FIELD -eq 5 ]; then
        echo "FIELD 5 HOT = 2"
        sudo sh -c "echo 2 > /sys/kernel/mm/htmm/htmm_thres_hot"
    else 
        echo "FIELD 5 HOT = 1"
        sudo sh -c "echo 1 > /sys/kernel/mm/htmm/htmm_thres_hot"
    fi

    #numactl --membind 1 ${VMTOUCH} -f -t $local_graph  -m 60G
    to_file_run
}

set_mode(){
    binary=$(basename "$BINARY")
    echo $now_in_seconds
    MODE="$binary-MEMTIS-$SYSTEM$HUGE_SPLIT-$FAST_DRAM-$now_in_seconds"
}

    

to_file_run_call(){
    binary="$1"
    MODE="$2"
    folder="$3"
    FAST_DRAM="$4"
    ARGS="$5"
    to_file_run
}

to_file_run(){
    now_in_seconds=$(date +%s)
    binary=$(basename "$BINARY")
    # if FAST_DRAM or DRAM is not defined blow up
    if [ -z "$FAST_DRAM" ] ; then
        echo "FAST_DRAM or DRAM is not defined"
        exit 1
    fi
    # if FAST DRAM = 8 exit
    if [ $FAST_DRAM -eq 8 ]; then
        exit 1
    fi
    #if [ -z "$FAST_DRAM" ]; then
    #fi
    echo "Writing output to $folder/real_data/batch/$MODE "  1>&2 

    set_mode
    {
        echo "_----------"
        echo "BENCHID: $benchid"
        echo "TIME: $(date)"
        echo "FIELD: $FIELD"
        echo "FAST_DRAM: $FAST_DRAM"
        echo "SOURCE_MAP: $source_map"
        echo "BINARY: $BINARY"
        echo "GRAPH: $local_graph"
        echo "ARGS: $ARGS"
        echo "STDIN: $STDIN"
        echo "WORKDIR: $WORKDIR"
    cat /proc/vmstat
    promoted=$(cat /proc/vmstat | grep htmm_nr_promoted | awk '{print $2}')
    demoted=$(cat /proc/vmstat | grep htmm_nr_demoted | awk '{print $2}')
    run_memtis $FAST_DRAM "$BINARY" 1 $ARGS   #| tee >(collect_blocked_time_data "$MODE") 

    cat /proc/vmstat
    # delta promoted and delta demoted
    promoted2=$(cat /proc/vmstat | grep htmm_nr_promoted | awk '{print $2}')
    demoted2=$(cat /proc/vmstat | grep htmm_nr_demoted | awk '{print $2}')
    echo "TOTAL_PROMOTIONS: $(($promoted2 - $promoted)) TOTAL_DEMOTIONS: $(($demoted2 - $demoted))" 
  #prorun_memtis $FAST_DRAM $BINARY 1 $ARGS  #| tee >(collect_overheads_data "$MODE")
    really_now_in_seconds=$(date +%s)
    echo "Elapsed time from shell: $(($really_now_in_seconds - $now_in_seconds))" 
    } >> $folder/real_data/batch/"$MODE" &
    bench_pid=$!
    {

    set +xe
    while :
        do
        {
        cat /proc/vmstat >> $folder/real_data/batch/STATS-"$MODE"
        cat  /sys/fs/cgroup/htmm/memory.numa_stat >> $folder/real_data/batch/STATS-"$MODE"
        cat /sys/fs/cgroup/htmm/memory.hotness_stat >> $folder/real_data/batch/STATS-"$MODE"
        } 
        sleep 2
        done
    } &

    monitor_pid=$!
    ############## the kmigrated thread may run on the other core! and may allocate cache entries on the second core!!! --> more mig = more performance for that!
    ##perf stat -e mem_load_l3_miss_retired.local_dram,mem_load_l3_miss_retired.remote_dram  -p $bench_pid -o "real_data/batch/PERF-$MODE" 
    # perf already waits for the process to finish
    sleep 2
    sudo  perf stat -e '{cycle_activity.stalls_l3_miss:u,INST_RETIRED.ANY:u,ocr.all_data_rd.l3_miss_local_dram.any_snoop,ocr.all_data_rd.l3_miss_remote_dram.any_snoop}' -I 1000  -o $folder/perf_"$MODE" -p $bench_pid  
    #wait $bench_pid
    echo "DONE"
    kill $monitor_pid
    sudo journalctl  -n 100 >> $folder/real_data/batch/STATS-"$MODE"
    echo $benchid | sudo tee -a $folder/real_data/batch/STATS-"$MODE"  $folder/real_data/batch/PERF-"$MODE" 
}
nm_run(){
    SYSTEM="NORMAL"
    sudo  sh -c "echo 3 > /proc/sys/vm/drop_caches"
    if [ ! -z "$local_graph" ]; then
        numactl --membind 1 ${VMTOUCH} -f -t $local_graph  -m 60G
    fi
    default_memtis_settings
    to_file_run
}

out_result(){

                    pgmigrate_success=$(grep  "pgmigrate_success" real_data/batch/$MODE* | head -n 1 | awk '{print $NF}')
                    pgmigrate_end=$(grep  "pgmigrate_success" real_data/batch/$MODE* | tail -n 1 | awk '{print $NF}')
                    echo "$SYSTEM Average Time: $time  $FAST_DRAM $(($pgmigrate_end-$pgmigrate_success))  $local_graph " 
}
gb(){
    set +x
    set +e

       for local_graph in  "/mnt/nas/inesc/ist196723/gapbs/benchmark/graphs/twitterU.sg" "/mnt/nas/inesc/ist196723/gapbs/benchmark/graphs/kron.sg" "/mnt/nas/inesc/ist196723/gapbs/benchmark/graphs/urand.sg"; do
            for FAST_DRAM in 0  1000 5000 2500 10000 50000; do
                # group all results by FAST_DRAM, FIELD, and LOCAL_GRAFPH
                results=0
                for FIELD in 5 6 7 8 9; do
                    set_bfs
                    SYSTEM="NORMAL"
                    set_mode
                    #echo "FIELD $FIELD DRAM $FAST_DRAM SYSTEM $SYSTEM"
                    time=$(grep -A1000 "$local_graph" real_data/batch/$MODE*  | grep "Average Time" | awk '{print $NF}')
                    if [ -z "$time" ]; then
                        continue
                    fi
                    #results=$( echo "$results + $time " | bc )
                    # to rpoperly sum
                    results=$(echo "scale=2; $results + $time" | bc)
                    #echo "bfs-MEMTIS-MAIS_MAIS-$FIELD-$DRAM" | tee -a run_files.txt
                    out_result
                done
                #average_time=$(echo "$results / 5" | bc)
            done
            for FAST_DRAM in 0  5000 2500 10000 50000; do
                # group all results by FAST_DRAM, FIELD, and LOCAL_GRAFPH
                results=0
                for FIELD in 5 6 7 8 9; do
                    set_bfs
                    SYSTEM="MAIS_MAIS-$FIELD-"
                    set_mode
                    time=$(grep -A1000 "$local_graph" real_data/batch/$MODE*  | grep "Average Time" | awk '{print $NF}')
                    if [ -z "$time" ]; then
                        continue
                    fi
                    pgmigrate_success=$(grep  "pgmigrate_success" real_data/batch/$MODE* | head -n 1 | awk '{print $NF}')
                    pgmigrate_end=$(grep  "pgmigrate_fail" real_data/batch/$MODE* | tail -n 1 | awk '{print $NF}')
                    #results=$( echo "$results + $time " | bc )
                    # to rpoperly sum
                    results=$(echo "scale=2; $results + $time" | bc)
                    out_result
            done
            done

    done
}

set_bfs(){
    
    local_graph="/mnt/nas/inesc/ist196723/gapbs/benchmark/graphs/kron.sg"
    BINARY="/mnt/nas/inesc/ist196723/gapbs/bfs"; ARGS="-f $local_graph -n 50"; STDIN=""; WORKDIR="/"; # size=simsmall    64
    source_map="/home/ist196723/nas/osdi26/final_data/maps_human/best/bfs 64.txt"
}
set_bc(){
    local_graph="/mnt/nas/inesc/ist196723/gapbs/benchmark/graphs/kron.sg"
    BINARY="/mnt/nas/inesc/ist196723/gapbs/bc"; ARGS="-f $local_graph -n 50"; STDIN=""; WORKDIR="/"; # size=simsmall    64
    source_map="/home/ist196723/latencymaps/bc" # /home/ist196723/latencymaps/bc" #nas/osdi26/final_data/maps_human/best/bc 64.txt"
}
set_mode__(){
    binary=$(basename "$BINARY")
    MODE="$binary-MEMTIS-$SYSTEM-$FAST_DRAM-"
}

analyse_results(){
       set_bfs
       for local_graph in  "/mnt/nas/inesc/ist196723/gapbs/benchmark/graphs/twitterU.sg" "/mnt/nas/inesc/ist196723/gapbs/benchmark/graphs/kron.sg" "/mnt/nas/inesc/ist196723/gapbs/benchmark/graphs/urand.sg"; do
        for FAST_DRAM in 0 5000 2500 10000 50000; do
            for FIELD in 6 5 7 8 9; do
                set_mode
                grep real_data/batch/"$MODE-*"  Average Time
            done
            done
            done

}


run_speedups(){

#"XSBench " "cg.B " "xalac " "bt.A"
#cat benchmarks_native_todo_final | grep "
#cat benchmarks_native_todo_final | grep "cg.B"

echo --

}

HASHTABLE=1
hand_soar(){
    #/home/ist196723/nas/tools/SoarAlto/me/process.sh 


    # TO DOS

    # 1) give weights such that the score is equal to every single one, regardless of frequency; 2) adjust weights for cost proportion
    # 
    # use naive_set instead (and set all others to 0) 


    cp ~/nas/bc_map_2_all ~/latencymaps/bc
    set_bc
    BINARY="/mnt/nas/inesc/ist196723/gapbs_changed/gapbs/bc";
    source_map="$(realpath ~/nas/bc_map_2)"
    LOOKUP_DS=1
    DRAM=1100 # 1072 +  200 mb of headroom
    FAST_DRAM=$DRAM
    FIELD=1
    sudo sh -c "echo 3 > /proc/sys/vm/drop_caches"
    sudo sh -c "echo $LOOKUP_DS > /sys/kernel/mm/htmm/htmm_weighted_sampling_struct"
    OMP_NUM_THREADS=9
    export OMP_NUM_THREADS
    #run_numactl_all_slow | tee ~/nine_core_all
    run_numactl_all_fast | tee ~/nine_core_fast
    exit

    pp_run
    pp_run
    pp_run
    pp_run
    pp_run
    pp_run
    nm_run
    nm_run
    nm_run
    nm_run
    nm_run
    nm_run
    
#set_bc(){
#    local_graph="/mnt/nas/inesc/ist196723/gapbs/benchmark/graphs/kron.sg"
#    BINARY="/mnt/nas/inesc/ist196723/gapbs/bfs"; ARGS="-f $local_graph -n 50"; STDIN=""; WORKDIR="/"; # size=simsmall    64
#    source_map="/home/ist196723/nas/osdi26/final_data/maps_human/best/bc 64.txt"
#}

}

tw(){
    #4294967294
    #2000000


    # column 6      0 if < 10 else 1
    # column 7      0 if < 10 else 1
    # column 10     0-10 granularity  
    graph="/mnt/nas/inesc/ist196723/gapbs/kron20.sg"
    local_graph="$graph"
    wow=0 #"/mnt/nas/inesc/ist196723/gapbs/benchmark/graphs/kron20.sg"; do #

    for o in 1 2 3 4 5 6 7 8 9 10 11; do
    {
        for local_graph in "/mnt/nas/inesc/ist196723/gapbs/benchmark/graphs/twitterU.sg" "/mnt/nas/inesc/ist196723/gapbs/benchmark/graphs/kron.sg" "/mnt/nas/inesc/ist196723/gapbs/benchmark/graphs/urand.sg"; do
        graph="$local_graph"
        set_bfs
        set_bc
        for FAST_DRAM in 0 1000 5000 2500 10000 50000; do
            for FIELD in 4; do #6 5 7 8 9
                pp_run
            done
            nm_run
            # run all in cxl
            #cxl_run
        done
        continue
            now_in_seconds=$(date +%s)
            SYSTEM="NUMACTL_SLOW-$now_in_seconds"
            set_mode
            run_numactl_all_slow > real_data/batch/"$MODE"

            now_in_seconds=$(date +%s)
            SYSTEM="NUMACTL_FAST-$now_in_seconds"
            set_mode
            run_numactl_all_fast > real_data/batch/"$MODE"
    done
        echo "DONE $o" >> dooooooooooooooo
    } |  tee -a one_big_out_$wow
    done
    exit 
    wow=1
    {
        for local_graph in  "/mnt/nas/inesc/ist196723/gapbs/benchmark/graphs/twitterU.sg" "/mnt/nas/inesc/ist196723/gapbs/benchmark/graphs/kron.sg" "/mnt/nas/inesc/ist196723/gapbs/benchmark/graphs/urand.sg"; do
        for FAST_DRAM in 0 5000 2500 10000 50000; do
            for FIELD in 6 5 7 8 9; do
                pp_run
            done
            nm_run
        done
    done
    } | tee one_big_out_$wow
    wow=2
    {
        for local_graph in  "/mnt/nas/inesc/ist196723/gapbs/benchmark/graphs/twitterU.sg" "/mnt/nas/inesc/ist196723/gapbs/benchmark/graphs/kron.sg" "/mnt/nas/inesc/ist196723/gapbs/benchmark/graphs/urand.sg"; do
        for DRAM in 0 5000 2500 10000 50000; do
            for FIELD in 6 5 7 8 9; do
                pp_run
            done
            nm_run
        done
    done
    } | tee one_big_out_$wow






    # disable compeltly cooling
    set -x 
    set -e 
    sudo sh -c "echo 10000 >  /sys/kernel/mm/htmm/htmm_cooling_period"
    sudo sh -c "echo 4294967294 >  /sys/kernel/mm/htmm/htmm_cooling_period"
    #sudo sh -c "echo enabled > /sys/kernel/mm/htmm/htmm_"
    # REMOVE IT 

    # adaptation period can be very low, as all weights are all ways increase
    #sudo sh -c "echo 1000 >  /sys/kernel/mm/htmm/htmm_adaptation_period"

    sudo sh -c "echo disabled > /sys/kernel/mm/htmm/htmm_weighted_sampling"
    sudo sh -c "echo 3 > /sys/kernel/mm/htmm/htmm_event_precision"
    export OMP_NUM_THREADS=1

    VMTOUCH="vmtouch"
    graph="/mnt/nas/inesc/ist196723/gapbs/kron23.sg"
    graph="/mnt/nas/inesc/ist196723/gapbs/kron23.sg"
    graph="/mnt/nas/inesc/ist196723/gapbs/benchmark/graphs/twitterU.sg"
    local_graph="$(realpath ~/$(basename $graph))"
    local_graph="/mnt/nas/inesc/ist196723/gapbs/kron20.sg"
    local_graph="/mnt/nas/inesc/ist196723/gapbs/benchmark/graphs/twitterU.sg"
    local_graph="/mnt/nas/inesc/ist196723/gapbs/benchmark/graphs/kron.sg"

    sudo  sh -c "echo 3 > /proc/sys/vm/drop_caches"

    BINARY="/mnt/nas/inesc/ist196723/gapbs/bfs"; ARGS="-f $local_graph -n 50"; STDIN=""; WORKDIR="/"; # size=simsmall    64
    files="$BINARY $local_graph"
    #run_numactl_all_slow
    #exit
    echo "MEMTIS_NORMAL"


    ########
    # cooling or no cooling is indiferrent. showing that page's sensitivness is constant for this workload
    {
        for local_graph in "/mnt/nas/inesc/ist196723/gapbs/benchmark/graphs/kron20.sg"  "/mnt/nas/inesc/ist196723/gapbs/benchmark/graphs/twitterU.sg" "/mnt/nas/inesc/ist196723/gapbs/benchmark/graphs/kron.sg" "/mnt/nas/inesc/ist196723/gapbs/benchmark/graphs/urand.sg"; do
                for BINARY in "/mnt/nas/inesc/ist196723/gapbs/bfs" "/mnt/nas/inesc/ist196723/gapbs/bc" "/mnt/nas/inesc/ist196723/gapbs/cc_sv" "/mnt/nas/inesc/ist196723/gapbs/cc_sv" "/mnt/nas/inesc/ist196723/gapbs/pr" ; do
            for FAST_DRAM in 0 313 625 1250 2500 5000 10000 50000; do 
                bin=$(basename $BINARY)
                #source_maps="$(ls /mnt/nas/inesc/ist196723/osdi26/final_data/maps/maps_fixed_bu_no_fast/$bin*.txt)"

                for source_map in /mnt/nas/inesc/ist196723/osdi26/final_data/maps/maps_fixed_bu_no_fast/"$bin"*.txt; do
                    echo "Processing file: '$source_map'"
                # files have spaces to handle that 

    #FAST_DRAM=500  # 1.1GB of memory 
    # at 0% it seems like its faster??
    #numactl --membind 1 ${VMTOUCH} -f -t $local_graph  -m 10G


        #source_map="/mnt/nas/inesc/ist196723/osdi26/final_data/maps/hand_made/bc.txt" #maps_fixed_bu_no_fast/bc 63.txt"  
        #source_map="/mnt/nas/inesc/ist196723/osdi26/final_data/maps/maps_fixed_bu_no_fast/bc 63.txt" #maps_fixed_bu_no_fast/bc 63.txt"  
        # get the folder path of the source map
                source_map_dir=$(dirname "$source_map") # 15 seconds BC with wrong source map
                FIELD=1
                pp_run
                FIELD=2
                pp_run
                nm_run
    done
    done
    done
    done

    exit

# 209.19584 (both had huge spike!)
# 

    exit
    #run_memtis $FAST_DRAM $BINARY 1 $ARGS #  0.90716
    # index 8

    FAST_DRAM=100  # 1.1GB of memory 
    # at 0% it seems like its faster??
    #numactl --membind 1 ${VMTOUCH} -f -t $local_graph  -m 10G



    sudo  sh -c "echo 3 > /proc/sys/vm/drop_caches"
    numactl --membind 1 ${VMTOUCH} -f -t $local_graph  -m 60G
    sudo sh -c "echo disabled > /sys/kernel/mm/htmm/htmm_weighted_sampling"
    sudo sh -c "echo disabled > /sys/kernel/mm/htmm/htmm_skip_cooling"            # REMOVE IT 
    default_memtis_settings
    MODE="BFS-MEMTIS_NORMIAL$FAST_DRAM"
    {
    run_memtis $FAST_DRAM $BINARY 1 $ARGS  #| tee >(collect_blocked_time_data "$MODE") 
    #run_memtis $FAST_DRAM $BINARY 1 $ARGS  #| tee >(collect_overheads_data "$MODE")
    } | tee $MODE
    #run_memtis $FAST_DRAM $BINARY 1 $ARGS #  0.90716
    # index 8

    source_map="/mnt/nas/inesc/ist196723/osdi26/final_data/maps/bfs 64.txt"  
    cp "$source_map" ~/latencymaps/bfs  #bfs 64.txt" 
    default_memtis_settings
    sudo sh -c "echo enabled > /sys/kernel/mm/htmm/htmm_skip_cooling"            # REMOVE IT 
    sudo sh -c "echo enabled > /sys/kernel/mm/htmm/htmm_weighted_sampling"
    sudo sh -c "echo 7 > /sys/kernel/mm/htmm/htmm_weight_field"
    sudo  sh -c "echo 3 > /proc/sys/vm/drop_caches"
    # 63 
    #run_memtis $FAST_DRAM $BINARY 1 $ARGS
    {
    MODE="BFS-MEMTIS_MAIS_MAIS$FAST_DRAM"
    numactl --membind 1 ${VMTOUCH} -f -t $local_graph  -m 60G
    run_memtis $FAST_DRAM $BINARY 1 $ARGS  #| tee <(collect_blocked_time_data "$MODE") 
    #run_memtis $FAST_DRAM $BINARY 1 $ARGS  #| tee collect_overheads_data "$MODE")
    } | tee $MODE
    exit

    FAST_DRAM=10000  # 1.1GB of memory 
    source_map="/mnt/nas/inesc/ist196723/osdi26/final_data/maps/bc 63.txt"  
    cp "$source_map" ~/latencymaps/bc  #bfs 64.txt" 
    sudo  sh -c "echo 3 > /proc/sys/vm/drop_caches"
    sudo sh -c "echo disabled > /sys/kernel/mm/htmm/htmm_weighted_sampling"
    sudo sh -c "echo disabled > /sys/kernel/mm/htmm/htmm_skip_cooling"            # REMOVE IT 
    numactl --membind 1 ${VMTOUCH} -f -t $local_graph  -m 60G
    default_memtis_settings
    MODE="MEMTIS_NORMIAL$FAST_DRAM"
    {
    run_memtis $FAST_DRAM $BINARY 1 $ARGS  #| tee >(collect_blocked_time_data "$MODE") 
     run_memtis $FAST_DRAM $BINARY 1 $ARGS  #| tee >(collect_overheads_data "$MODE")
    } | tee $MODE



    default_memtis_settings
    sudo sh -c "echo enabled > /sys/kernel/mm/htmm/htmm_skip_cooling"            # REMOVE IT 
    sudo sh -c "echo enabled > /sys/kernel/mm/htmm/htmm_weighted_sampling"
    sudo sh -c "echo 7 > /sys/kernel/mm/htmm/htmm_weight_field"
    sudo  sh -c "echo 3 > /proc/sys/vm/drop_caches"
    numactl --membind 1 ${VMTOUCH} -f -t $local_graph  -m 60G
    # 63 
    #run_memtis $FAST_DRAM $BINARY 1 $ARGS
    MODE="MEMTIS_MAIS_MAIS$FAST_DRAM"
    {
    run_memtis $FAST_DRAM $BINARY 1 $ARGS  #| tee >(collect_blocked_time_data "$MODE") 
    #run_memtis $FAST_DRAM $BINARY 1 $ARGS  #| tee >(collect_overheads_data "$MODE")
    } | tee $MODE



} 




    exit
    
    #cp $graph $local_graph
    #numactl --membind 1 ${VMTOUCH} -f -t $local_graph  -m 60G
    {

    BINARY="/mnt/nas/inesc/ist196723/gapbs/bfs"; ARGS="-f $local_graph -n 100"; STDIN=""; WORKDIR="/"; # size=simsmall    64
    echo "MEMTIS++: BFS 64"
    sudo sh -c "echo 1 > /sys/kernel/mm/htmm/htmm_weight_field"
    cp "/mnt/nas/inesc/ist196723/osdi26/final_data/maps/bfs 70.txt"  ~/latencymaps/bfs
    cp "/mnt/nas/inesc/ist196723/osdi26/final_data/maps/bfs 64.txt"  ~/latencymaps/bfs
    #numactl --membind 1 ${VMTOUCH} -f -t $local_graph  -m 60G
    #run_memtis $FAST_DRAM $BINARY 1 $ARGS
    # if the index can fit in the cache .. we will see no change in DRAM/Slow
    files=$local_graph
    FAST_DRAM=200
    source_map="/mnt/nas/inesc/ist196723/osdi26/final_data/maps/bfs 70.txt"
    # memtis overhead (without migration)

    # itereate over fast dram for fast heap
    benchnr="bfs"
    source_map="/mnt/nas/inesc/ist196723/osdi26/final_data/maps/bfs 64.txt"
    break_down_overheads

    exit
    benchnr="bfs"
    cat /proc/vmstat  | grep -E "prom|demo|mig" >> vmstat_0.txt
    run_memtis_no_migweighted 0| tee -a plus_out &           # 0.98990   # THIS IS BECAUSE.. (confirm there are 0 migrations)
    sleep 10  # is nto doing any migs.. 
    echo "" >> vmstat_0.txt
    cat /proc/vmstat  | grep -E "prom|demo|mig" >> vmstat_0.txt
    wait
    echo "" >> vmstat_0.txt
    cat /proc/vmstat  | grep -E "prom|demo|mig" >> vmstat_0.txt
    exit

    run_memtis_no_migweighted 60000 | tee -a plus_out       # 0.46586   # when all on fast there is no overhead
    run_memtis_all_fast $local_graph                        # 0.46556   # when all on fast there is no overhead periodically there is a 0.71 dude...
    run_memtis_all_slow $local_graph                        # 0.89471 
    exit


    # itereate over fast dram for every field

    {
    run_memtis_field 4 "$source_map"
    run_memtis_field 1 "$source_map"
    run_memtis_field 7 "$source_map"
    run_memtis_field 8 "$source_map"
    run_memtis_field 9 "$source_map"
    source_map="/mnt/nas/inesc/ist196723/osdi26/final_data/maps/bfs 64.txt"
    echo 644444444
    run_memtis_field 4 "$source_map"
    run_memtis_field 1 "$source_map"
    run_memtis_field 7 "$source_map"
    run_memtis_field 8 "$source_map"
    run_memtis_field 9 "$source_map"
    } > whyyyyyyyyyy
    exit
    benchnr="bfs-64"
    {
        run_numactl_all_slow
        run_numactl_all_fast
        run_numactl_heap_fast
    } | tee -a real_output_data
    exit
    run_memtis_heap_fast $local_graph 100
    run_memtis_heap_fast $local_graph 50000
    exit 
    run_memtis_heap_fast $local_graph 1000
    run_memtis_heap_fast $local_graph 2000
    run_memtis_heap_fast $local_graph 10000
    exit
    run_memtis_all_fast $local_graph
    run_memtis_all_slow $local_graph
    #run_memtis_optimal_static_allocation $local_graph
    exit
    # iterate over DRAM SIZE for each  
    run_memtis_field 3
    run_memtis_field 4
    exit
    run_memtis_field 2
    run_memtis_field 7
    run_memtis_field 8
    run_memtis_field 9
    exit

    #BINARY="/mnt/nas/inesc/ist196723/gapbs/pr"; ARGS="-f $local_graph -n 200"; STDIN=""; WORKDIR="/"; # size=simsmall    64
    #time numactl --membind 0 --cpubind 0 $BINARY $ARGS
    #exit
    # 1m15.423s                  0.37370

    echo "MEMTIS_NORMAL"
    sudo sh -c "echo disabled > /sys/kernel/mm/htmm/htmm_weighted_sampling"
    run_memtis $FAST_DRAM $BINARY 1 $ARGS
    # index 8

    echo "MEMTIS++: BFS 70"
    numactl --membind 1 ${VMTOUCH} -f -t $local_graph  -m 10G
    cp "/mnt/nas/inesc/ist196723/osdi26/final_data/maps/bfs 70.txt"  ~/latencymaps/bfs
    run_memtis $FAST_DRAM $BINARY 1 $ARGS

    #bwaves  3 cost_inst_L3MLP
    



    } | tee memtis_outputs




    #sudo sh -c "echo enabled > /sys/kernel/mm/htmm/htmm_weighted_sampling"

BINARY="/mnt/nas/inesc/ist196723/gapbs/bfs"; ARGS="-f /mnt/nas/inesc/ist196723/gapbs/urand23.sg -n 2"; STDIN=""; WORKDIR="/"; # size=simsmall    70
# TODO if the index fit in the cache... we are screwed...


    #./controller.sh report #| grep bfs 
}


cg(){
        #exec="/mnt/nas/inesc/ist196723/benchmarks/XSBench/openmp-threading/XSBench"
        #args="-t 1 -p 500000 -G hash -h 1000000 -s XL -b read
        #exec="/mnt/nas/inesc/ist196723/benchmarks/XSBench/openmp-threading/XSBench"
        args=""
        echo 8 > /tmp/omp_num_threads
     bench="cg.D"
        bench="mg.C"
        exec="/mnt/nas/inesc/ist196723/benchmarks/NPB-CPP/NPB-OMP/bin/$bench"
    sudo ~/memtis/memtis-userspace/scripts/set_uncore_freq.sh on # FORGOT that changed "on" to "off"!  1h!


     # cp ~/nas/osdi26/final_data/maps/* ~/latencymaps/
      #cp ~/nas/osdi26/final_data/multi/npb_result-cg.D ~/latencymaps/cg.D
      cp ~/nas/osdi26/final_data/multi/npb_result-mg.C ~/latencymaps/mg.C
     #
     for i in 1 2 3 4 5 6 7 8 9 0; do 

        #5000 4000 1500 6000 7000
          DRAMS="1000 2000 3000"
          for DRAM in  $DRAMS; do # 1500 3000 2000 2500; do
          FAST_DRAM=$DRAM
          binary="$exec"
          #to_file_run | 
          default_memtis_settings
          #        FIELD=0
                 echo "8" > /tmp/omp_num_threads

            THREAD_MODE="NO_HT"
            BASE="32_bit"
            COOL="DECAY_new_map"
            MODE="$THREAD_MODE-$BASE-$COOL-$DRAM-$i-0"
            #run_time=$(run_memtis $DRAM "$exec" 1 $args |  awk ' /Time in seconds/ {r=$5; } /Mop/ {l=$4} END {print r " " l}')
            #echo $run_time $DRAM $memory $bench $FIELD $THREAD_MODE $BASE $COOL noll | tee -a promising_results
            #memtis_weighted
            for FIELD in  4; do
            #sudo sh -c "echo 3 > /proc/sys/vm/drop_caches"
            #echo $FIELD
            sudo sh -c "echo $FIELD > /sys/kernel/mm/htmm/htmm_weight_field"
            sudo sh -c "echo enabled > /sys/kernel/mm/htmm/htmm_weighted_sampling"
            args=""
                run_time=$( to_file_run "$binary" "$MODE" "$folder" "$FAST_DRAM" "$args" |  awk ' /Time in seconds/ {r=$5; } /Mop/ {l=$4} END {print r " " l}')
                echo $run_time $DRAM $memory $bench $FIELD $THREAD_MODE $BASE $COOL noll | tee -a /mnt/nas/inesc/ist196723/osdi26/promising_results
            default_memtis_settings
            FIELD=0
            MODE="$THREAD_MODE-$BASE-$COOL-$DRAM-$i-4"

                run_time=$( to_file_run "$binary" "$MODE" "$folder" "$FAST_DRAM" "$args" |  awk ' /Time in seconds/ {r=$5; } /Mop/ {l=$4} END {print r " " l}')

            echo $run_time $DRAM $memory $bench $FIELD $THREAD_MODE $BASE $COOL noll | tee -a /mnt/nas/inesc/ist196723/osdi26/promising_results
          done
  done
  done
}



if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
  #echo "Script is being sourced"
  echo "" > /dev/null
else
  #echo "Script is being executed"
 "$@"
fi

#./controller.sh getr | grep 20.sg | awk '{print $NF}' | xargs -I {} ./controller.sh iterate_benches benches_final do_real_bench {}   # get bench ids that match a criteria
#./controller.sh getr | grep 20.sg | awk '{print $NF}' | xargs -I {} ./controller.sh iterate_benches benches_final do_one_gem5 {}   # get bench ids that match a criteria


#worksplit(){
#    hostname=$(hostname)
#    if [ "$hostname" == "proteina07" ]; then
#        ./controller.sh getr | grep 20.sg | awk '{print $NF}' | xargs -I {} ./controller.sh iterate_benches benches_final _do_gem5 {}
#    fi


#ssh --nodelist=proteina02 /bin/bash -c "docker exec -it gem5 /bin/bash -c 'srun  "    
#srun --nodelist=vitamina02 /bin/bash -c "docker exec -it gem5 /bin/bash -c 'srun  "    
#        ./controller.sh getr | grep -v 20.sg | awk '{print $NF}' | head -n 10 xargs -I {} ./controller.sh iterate_benches benches_final _do_gem5 {}
#    elif [ "$hostname" == "proteina06" ]; then
#        ./controller.sh getr | grep 20.sg | awk '{print $NF}' | xargs -I {} ./controller.sh iterate_benches benches_final _do_gem5 {}
#        ./controller.sh getr | grep -v 20.sg | awk '{print $NF}' | head -n 10 xargs -I {} ./controller.sh iterate_benches benches_final _do_gem5 {}
#    fi

#srun --nodelist=proteina07 /bin/bash -c "docker exec -it gem5 /bin/bash -c 'srun  "    
    
#}
    

# iterate_benches benches_final do_real_bench 

#
#

