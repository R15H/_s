#!/bin/bash
VMTOUCH="/usr/bin/vmtouch"
nas="/mnt/nas/inesc/ist196723"

set -x 
set -e


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

  # Poll until the process exits
  while kill -0 "$pid" 2>/dev/null; do
    # Read current RSS from /proc/[pid]/status
    current_rss=$(awk '/VmRSS:/ {print $2}' /proc/"$pid"/status 2>/dev/null)
    # Update maximum if this sample is greater
    if (( current_rss > max_rss )); then
      max_rss=$current_rss
    fi
    sleep "$interval"
  done

  # Print the peak RSS in KiB
  echo "$max_rss"
}









##################
r(){
rm benchmarks_todo
~/run_commands.sh
}
total_runs=0



prepare(){
    sudo /home/ist196723/memtis/memtis-userspace/scripts/set_uncore_freq.sh on
    sudo cpupower frequency-set -g performance

    numactl --membind 0 $VMTOUCH -e $BINARY -m 64G
    for a in $ARGS; do
        if [ -f "$a" ]; then
            numactl --membind 1 $VMTOUCH -e $a -m 64G
        fi
    done
}
LOCAL_RUN="numactl --membind 0"
REMOTE_RUN="numactl --membind 1"

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

_do_gem5(){
                GEM5=$nas/gem5.end
                GEM5=/bench/userspace/benchmarks/gemm5/gem5/buildO/build/X86/gem5.fast

                CONFIG=/bench/copyyy_bento.py
                CONFIG=$nas/config.end.py
                CONFIG=$nas/copyyy_bento.py
                increase=0

                $GEM5 $CONFIG "$BINARY" --latency-increase $increase --bargs "$ARGS" --cpu-start KVM --dramsize=8GiB --bstdin "$STDIN" 2> $nas/osdi26/results_gem5/err_$benchset\_$benchnr\_$increase\_ 1>$nas/osdi26/results_gem5/output_$benchset\_$benchnr\_$increase\_ & 
                pid=$!
                echo "pid: $pid benchset: $benchset benchnr: $benchnr bench: $BINARY increase: $increase host: $(hostname)" >> $nas/osdi26/results_gem5/gem5_pids.txt

                increase=80

                $GEM5 $CONFIG "$BINARY" --latency-increase $increase --bargs "$ARGS" --cpu-start KVM --dramsize=8GiB --bstdin "$STDIN" 2> $nas/osdi26/results_gem5/err_$benchset\_$benchnr\_$increase\_ 1>$nas/osdi26/results_gem5/output_$benchset\_$benchnr\_$increase\_ & 
                pid=$!
                echo "pid: $pid benchset: $benchset benchnr: $benchnr bench: $BINARY increase: $increase host: $(hostname)" >> $nas/osdi26/results_gem5/gem5_pids.txt
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
                

                sudo  perf stat -e '{cycle_activity.stalls_l3_miss:u,INST_RETIRED.ANY:u,offcore_requests_outstanding.cycles_with_demand_data_rd:u,OFFCORE_REQUESTS.demand_data_rd:u}' -I 250  -o /mnt/nas/inesc/ist196723/osdi26/perf/global-$name-$total_runs -p $pid &  
                sudo perf record -T -e MEM_LOAD_RETIRED.L3_MISS:uppp -z=6 -c 100 -p $pid -o /mnt/nas/inesc/ist196723/osdi26/perf/trace_$total_runs &
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


iterate_benches(){
    bench_file=$1
    benchset=$1
    exec=$2
    bench_nr=$3
    benchnr=$3
    if [ ! -z "$bench_nr" ]; then
        echo "lOoking for $bench_nr"
    fi
    cat $bench_file | {
        declare -A workload_list
        total_runs=-1
        while read -r line; do
            eval "$line"
            #echo "$line"
            pushd $WORKDIR
    # if bench nr is not null, check if we are in the right run
            total_runs=$((total_runs+1))
            echo "ITERATING $total_runs"

            if [ ! -z "$bench_nr" ]; then
                if (( total_runs < bench_nr )); then
                    continue
                fi
                $exec $total_runs
                break;
            fi

            $exec $total_runs
            popd
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
    total_runs=0
    cat $benches | {
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

#if $1 is "real" then call real_execute
if [ "$1" == "real" ]; then
    real_execute ~/nas/osdi26/benches_final
    
fi



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

#30 per machine
#382 runs 
#382/30 = 12.73

# if its "stats" then call stats_execute

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

"$@"

#./controller.sh getr | grep 20.sg | awk '{print $NF}' | xargs -I {} ./controller.sh iterate_benches benches_final do_real_bench {}   # get bench ids that match a criteria
#./controller.sh getr | grep 20.sg | awk '{print $NF}' | xargs -I {} ./controller.sh iterate_benches benches_final do_one_gem5 {}   # get bench ids that match a criteria

    
# ./controller.sh getr | grep 20.sg | awk '{print $NF}' | xargs -I {} ./controller.sh iterate_benches benches_final _do_gem5 {}    
# iterate_benches benches_final do_real_bench 

#
#