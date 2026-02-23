#!/bin/bash

results_folder="/mnt/nas/inesc/ist196723/osdi26/results_gem5"
gem5_pids_folder=$results_folder

parse_gem5_output(){
	echo hii?
    pid=$1
    # confirm there is only 1 file for each pid
    r=$(ls $results_folder/compressed/global_$pid* 2>/dev/null | wc -l) # >> conflicts
    echo $r
    #zstd -k $results_folder/compressed/global_$pid* -d -o  "$results_folder/$(basename $results_folder/compressed/global_$pid*)"

    #return
    gf=$results_folder/global_$pid*
    iif=$results_folder/inst_$pid*
    af=$results_folder/aggregate_$pid*
    echo --------START---------
    echo $gf
    echo $iif
    echo $af
    echo -----------------
    
    ls $results_folder/global_$pid* 2>/dev/null | wc -l  >> conflicts
    ok=0
    for f in $gf $iif $af; do
        if [ -L "$f" ];then
            ok=1;
            break
        fi
    done

    targets="$(ls $results_folder/global_$pid* )"
    targets="$(ls $results_folder/inst_$pid* )"
    echo "new pid $pid"
    if [  $ok -eq 0 ]; then
	    echo not okay..
       # return # skip runs that are all local. that is repeated! 
    fi



    
    i=0
    for t in $targets; do 
	    i=$((i+1))
	    t=$(basename $t)

	    pid=$(echo $t | cut -d_ -f 2)
	    machine=$(echo $t | cut -d_ -f 3)
    mkdir -p $results_folder/$pid-$machine
	    echo $pid $machine $t
	    if [ $i -gt 1 ];then
		    echo conflict count $i $pid-$pid for $machine
	    fi

    ls $results_folder/global_$pid*  >/dev/null
    if [ ! $? -eq "0" ]; then
	    echo $pid >> must_review
    fi

    ls $results_folder/inst_$pid\_$machine* | wc -l
    ls $results_folder/inst_$pid*  >/dev/null
    if [ ! $? -eq "0" ]; then
	    echo $pid >> must_review
    fi
    ls $results_folder/aggregate_$pid* | wc -l


    echo $i doing..
    du -h $results_folder/global_$pid\_$machine* $results_folder/inst_$pid\_$machine* $results_folder/aggregate_$pid\_$machine*
    ./sample_parser $results_folder/global_$pid\_$machine* $results_folder/inst_$pid\_$machine* $results_folder/aggregate_$pid\_$machine* # && echo "yes" | rm $results_folder/inst_$pid\_$machine*

    echo - 
    #grep $pid $results_folder/gem5_pids.txt
    done
}

export -f parse_gem5_output
go(){
gcc sample_parser.c -O3 -o sample_parser || exit 
#grep npb_result-iter | grep cg.D | 
##grep df4777   | 
	tac $results_folder/gem5_pids.txt | head -n  1700 | grep synth |  awk '{print $2}' | uniq | xargs -I {} -P 10 /mnt/nas/inesc/ist196723/osdi26/bin/parse.sh parse_gem5_output {} # while read pid; do parse_gem5_output $pid; done
}

gop(){
gcc sample_parser.c -O3 -o sample_parser
#grep npb_result-iter | grep cg.D | 
results_folder=$1
	cat $gem5_pids_folder/gem5_pids.txt | grep cg.D |  awk '{print $2}' | uniq | xargs -I {} -P 5 /mnt/nas/inesc/ist196723/osdi26/bin/parse.sh parse_gem5_output {} # while read pid; do parse_gem5_output $pid; done
}

"$@"


