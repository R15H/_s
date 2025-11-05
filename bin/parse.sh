#!/bin/bash

results_folder="/mnt/nas/inesc/ist196723/osdi26/results_gem5"

parse_gem5_output(){
    pid=$1
    mkdir -p $results_folder/$pid
    # confirm there is only 1 file for each pid
    ls $results_folder/global_$pid* | wc -l
    ls $results_folder/inst_$pid* | wc -l
    ls $results_folder/aggregate_$pid* | wc -l


    ./sample_parser $results_folder/global_$pid* $results_folder/inst_$pid* $results_folder/aggregate_$pid*
    echo - 
    grep $pid $results_folder/gem5_pids.txt
}
export -f parse_gem5_output
go(){
gcc sample_parser.c -O3 -o sample_parser
	cat $results_folder/gem5_pids.txt | awk '{print $2}' | uniq | xargs -I {} -P 20 /mnt/nas/inesc/ist196723/osdi26/bin/parse.sh parse_gem5_output {} # while read pid; do parse_gem5_output $pid; done
}
"$@"


