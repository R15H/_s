# bin/SY.py — synthetic benchmark result plotter (pointer-chasing vs streaming)
#
# PURPOSE
#   Reads synthetic memory-access benchmark results from a flat text file and
#   plots runtime vs DRAM size broken down by system (ASMEM, MEMTIS, TPP) and
#   the random/pointer-access mix (arand/aptr ratio).
#
# ENTRY POINT
#   plot_r()  — reads the file configured via the `file` variable (currently
#               "sinn_all" under ~/nas/inesc/ist196723/) and calls do_plot()
#               to generate matplotlib figures
#
# ROLE IN PIPELINE  (step 4 of 4 — synthetic result path)
#   ~/nas/synthethic_results or ~/nas/sinn_all
#     → SY.py:plot_r() → matplotlib figures
#   Counterpart to bin/pyplots.py (which reads the same format but is the
#   newer version used for publication figures).

import matplotlib.pyplot as plt
import os
import numpy as np

def plot_r():
    global time, system, arand, aptr, ratio, dram
    # real results of sy
    folder="/mnt/nas/inesc/ist196723/" # latency_benchmark/tests_syn/plot_time_math"
    #file="TIREDbig_final_results"
    file="final_synthethic_tiering"
    file="syn_ftw"
    file="N" #synthethic_results_now"
    file="sinos" #synthethic_results_now"
    file="sinn" #synthethic_results_now"
    file="sinn_all" #synthethic_results_now"

    LAST_SYN = True
    def do_plot(bench_file, nr_args, bench_name, other_bench=False):
        global time, system, arand, aptr, ratio, dram, benched 
        system = []
        time = []
        arand = []
        aptr = []
        ratio = []
        dram = []
        benched = []

        def parse_all_results(line_array):
            if len(line_array ) < 5:
                return
            
        with open(os.path.join(folder, bench_file), 'r') as f:
            lines = f.readlines()
            sy_results = {}
            TIME=0
            ARAND=2
            APTR=1
            RATIO=3
            DRAM=4
            SYSTEM=6

            

            SYSTEM=-1
            DRAM=3
            for line in lines:
                v = line.split(" ")
                print(v)
                #if "outa" not in line: continue
                if len(v) == 3:
                    continue
                if "ALL_" in line:
                    SYSTEM=-1
                    DRAM=-3
                elif len(v) < 3:
                    continue
                if len(v) < 6:
                    continue
                t = float(v[TIME])
                s = v[SYSTEM].strip()
                d = v[DRAM].strip()
                if float(v[ARAND]) < 1:
                    continue
                dram.append(int(d))
                system.append(s.upper())
                time.append(float(t))
                arand.append(int(v[ARAND]))
                aptr.append(int(v[APTR]))
                
                ratio.append( arand[-1]/aptr[-1]) # float(v[RATIO]))
                continue
        ratio = np.array(ratio)
        arand = np.array(arand)
        aptr = np.array(aptr)
        time = np.array(time)
        system = np.array(system)
        dram = np.array(dram)
        print("DRAM as ", np.unique(dram))
        print("APTR as ", np.unique(aptr))
        print("ARAND as ", np.unique(arand))
        print("RATIO as ", np.unique(ratio))
        print("SYSTEM as ", np.unique(system))
        #exit(0)
    nr_args=7
    bench = "syn"
    do_plot(file, nr_args, bench, False)
    for r in np.unique(aptr):
        idx = aptr == r
        print("Doing aptr R",r)
        plt.figure()
        print(time[idx])
        plt.title(f"Performance by pointer chasins {r}")
        plt.xlabel("Number of streaming reads")
        plt.ylabel("Average execution time")
        print(system[idx])
        #print(time[idx])
        # one idx per aptr
        # half index per system
        arands = np.unique(arand[idx])
        idx_sort = np.argsort(arands)
        #aptrs = np.sort(aptrs)
        #print("ARAND", current_arand)

        xticks = []
        xticks_labels = []
        for i in range(len(arands)):
            current_arand = arands[idx_sort][i]
            
            DRAM_USED=185
            #print(dram, idx)
            idx_mem = (arand[idx] == current_arand) & (system[idx] == "MEMTIS-1") & (dram[idx] == DRAM_USED) #(dram[idx] == 320)
            idx_scaled = (arand[idx] == current_arand) & (system[idx] == "MEMTIS-SCALED") & (dram[idx] == DRAM_USED) #(dram[idx] == 320)
            idx_stock = (arand[idx] == current_arand) & (system[idx] == "MEMTIS-STOCK") & (dram[idx] == DRAM_USED) #(dram[idx] == 320)
            idx_asm = (arand[idx] == current_arand) & (system[idx] == "ASMEM") & (dram[idx] == DRAM_USED) #(dram[idx] == 320)
            print(idx_asm, "asmmm")

            idx_all_fast = (aptr[idx] == r) & ( arand[idx] == current_arand) & ((system[idx] == "ALL_FAST") | (system[idx] == "ALL_FAST"))
            idx_all_slow = (aptr[idx] == r) & ( arand[idx] == current_arand) & (((system[idx] == "ALL_SLOW") | (system[idx] == "ALL_SLOW"))) 

            baseline_fast =  np.mean(time[idx][idx_all_fast])
            baseline_slow =  np.mean(time[idx][idx_all_slow])
            baseline_fast =  1 # np.mean(time[idx][idx_asm])  # baseline_slow
            #baseline_fast = np.mean(time[idx][idx_asm])
            o = i*2 # *1.1

            print("----------")
            print(len(time[idx][idx_mem]))
            print(len(time[idx][idx_asm]))
            if (len(time[idx][idx_mem]) < 5 or len(time[idx][idx_asm]) < 5):
                pass
                #continue
            print("----------")
            plt.bar(i+o, np.mean(time[idx][idx_mem])/baseline_fast, width=0.5, color="blue")
            plt.bar(i+o+0.5, np.mean(time[idx][idx_asm])/baseline_fast, width=0.5, color="orange")
            plt.bar(i+o+1, np.mean(time[idx][idx_stock])/baseline_fast, width=0.5, color="green")
            plt.bar(i+o+1.5, np.mean(time[idx][idx_scaled])/baseline_fast, width=0.5, color="magenta")
            xticks.append(i+o+0.25)
            xticks_labels.append(str(current_arand))

            print(time[idx][idx_all_fast])
            v = np.mean(time[idx][idx_all_fast])/baseline_fast
            print(v)
            plt.bar(i+o+1, v, width=0.5, color="purple")
            v = np.mean(time[idx][idx_all_slow])/baseline_fast
            print(v)
            plt.bar(i+o+1.5, v, width=0.5, color="yellow")
            print('cry')
        plt.xticks(xticks, xticks_labels)
            #plt.bar(i+0.25, 0, width=0, bottom=str(aptrs[i]))

            #plt.bar(system[idx][i] + aptr[idx][i], time[idx][i], label="Time")
            #plt.bar(system[idx][i], aptr[idx][i], bottom=time[idx][i], label="Ptr")

        from matplotlib.lines import Line2D

        # Color legend handles
        color_handles = [
            Line2D([0], [0],  color='blue', label='MEMTIS'),
            Line2D([0], [0],  color='orange', label='AsMem'),
            Line2D([0], [0],  color='green', label='Stock'),
            Line2D([0], [0],  color='magenta', label='Scaled'),
            Line2D([0], [0],  color='yellow', label='Fast'),
            Line2D([0], [0],  color='purple', label='Slow'),
        ]


        # Combine marker and color handles
        all_handles =  color_handles

        # Show legend with all handles
        plt.legend(handles=all_handles, loc='best')
        plt.title(f"Performance with {r} pointer chasings")
        FIGS_FOLDER = "/mnt/nas/inesc/ist196723/osdi26/infra/"
        plt.savefig(f"{FIGS_FOLDER}/../report/happyaptr_{r}.png")
    
    return
    print(ratio)
    for r in np.unique(ratio):
        idx = ratio == r
        print("Doing ratio R",r)
        plt.figure()
        plt.title(f"Performance by ratio {r}")
        plt.xlabel("Number of pointer chase reads")
        plt.ylabel("Average execution time")
        print(system[idx])
        print(time[idx])
        # one idx per aptr
        # half index per system
        aptrs = np.unique(aptr[idx])
        idx_sort = np.argsort(aptrs)
        #aptrs = np.sort(aptrs)

        print('be happy')
        #exit(0)
        xticks = []
        xticks_labels = []
        for i in range(len(aptrs)):
            current_aptr = aptrs[idx_sort][i]
            
            print(dram, idx)
            idx_mem = (aptr[idx] == current_aptr) & (system[idx] == "MEMTIS\n") & (dram[idx] == 230) #(dram[idx] == 320)
            idx_asm = (aptr[idx] == current_aptr) & (system[idx] != "MEMTIS\n") & (dram[idx] == 230) #(dram[idx] == 320)
            o = i*0.1

            print("----------")
            print(len(time[idx][idx_mem]))
            print(len(time[idx][idx_asm]))
            print("----------")
            plt.bar(i+o, np.mean(time[idx][idx_mem]), width=0.5, color="blue")
            plt.bar(i+o+0.5, np.mean(time[idx][idx_asm]), width=0.5, color="orange")
            xticks.append(i+o+0.25)
            xticks_labels.append(str(current_aptr))

            idx_all_fast = (((system[idx] == "ALL_FAST\n") | (system[idx] == "ALL_FAST")) & dram[idx] == 230)
            idx_all_slow = (((system[idx] == "ALL_SLOW\n") | (system[idx] == "ALL_SLOW")) & dram[idx] == 230)
            plt.bar(i+o+0.5, np.minimum(500, np.mean(time[idx][idx_all_fast])), width=0.5, color="purple")
            plt.bar(i+o+0.75, np.minimum(500, np.mean(time[idx][idx_all_slow])), width=0.5, color="yellow")
            #i+= 0.75
            

        plt.xticks(xticks, xticks_labels)
            #plt.bar(i+0.25, 0, width=0, bottom=str(aptrs[i]))

            #plt.bar(system[idx][i] + aptr[idx][i], time[idx][i], label="Time")
            #plt.bar(system[idx][i], aptr[idx][i], bottom=time[idx][i], label="Ptr")

        from matplotlib.lines import Line2D

        # Color legend handles
        color_handles = [
            Line2D([0], [0],  color='blue', label='MEMTIS'),
            Line2D([0], [0],  color='orange', label='AsMem'),
        ]

        # Combine marker and color handles
        all_handles =  color_handles

        # Show legend with all handles
        plt.legend(handles=all_handles, loc='best')
        plt.title(f"Performance with {r}x more sequential reads")
        plt.savefig(f"{FIGS_FOLDER}/../report/HAPPYratio_{r}.png")
    
plot_r()