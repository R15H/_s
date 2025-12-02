from ctypes  import *
import collections
global_only = False
success_run = 0
MLP_PRECISION_FACTOR = 1024

from scipy import stats

OLD_V4 = True

def all_over_time_real():
    master_file="over_time_files"
    # check if master exists, if not call 
    if not os.path.exists(master_file):
        os.system("/home/ist196723/nas/osdi26/real_analysis.sh")
    systems = {'MEMTIS': [], 'ASMEM':  [], 'MEMTIS-1':[]}
    with open(master_file) as f:
        lines = f.readlines()
        print(lines)
        for line in lines:
            line = line.strip()
            if "ASMEM" in line:
                systems['ASMEM'].append(line)
            if "MEMTIS-1" in line:
                systems['MEMTIS-1'].append(line)
                continue
            if "MEMTIS" in line:
                systems['MEMTIS'].append(line)
    system_data = {'MEMTIS': {}, 'ASMEM':  {}, 'MEMTIS-1':{}}
    # max_len set here -> time adjusted to match both systems 
    max_len_sys = {}
    def get_partial(partial_key, dict):
        for key in dict:
            if partial_key in key:
                return dict[key]
        return None
        
    for system in systems:
        if system == "MEMTIS":
            continue
        max_len = 0
        for file in systems[system]:
            print(file)
            if "hit_ratio" in file:
                print("speciall...", file)
                if "X" in file:
                    nfile = "hit_ratio_X"
                    system_data[system][nfile] = np.loadtxt(file, dtype=np.float64) 
                    print("------lool")
                    print(system_data[system][nfile], len(system_data[system][nfile]))
                    file = nfile
                else:
                    nfile = "hit_ratio_Y"
                    system_data[system][nfile] = np.loadtxt(file, dtype=np.float64)
                    # convolve with window of 3, keep the same number of entries
                    if len(system_data[system][nfile]) < 10:
                        print("WARNING...")
                        continue
                    window=10
                    system_data[system][nfile] = np.convolve(system_data[system][nfile], np.ones(window)/window, mode='same')

                    print("------lool")
                    print(system_data[system][nfile], len(system_data[system][nfile]))
                    file = nfile
            else:
                system_data[system][file] = np.loadtxt(file, dtype=np.float64)
                def remove_outliers(y):
                    mean = np.mean(y)
                    y = y[np.where(y > 0.05*mean)]
                    return y
                if 'instructions' in file:
                    system_data[system]['instructions'] = system_data[system][file]
                if "stalls" in file:
                    # remove the first entries that are below the 5% of the mean value
                    #system_data[system][file] = remove_outliers(system_data[system][file])
                    system_data[system]['stalls'] = (system_data[system][file])
                    window=3
                    #system_data[system][file] = np.convolve(system_data[system][file], np.ones(window)/window, mode='same')
                    #system_data[system][file] = np.cumsum(system_data[system][file]) #, np.ones(window)/window, mode='same')
                if "demote" in file or "promote" in file:
                    #system_data[system][file] = np.cumsum(system_data[system][file])

                    window=8
                    system_data[system][file] = system_data[system][file] #np.convolve(system_data[system][file], np.ones(window)/window, mode='same')
                    # remove values that are above 500 000, replace them by 500 000
                    system_data[system][file] = np.cumsum( 
                                                          np.where(system_data[system][file] > 500000, 00000, system_data[system][file])
                    )


                    pass
                if "clock" in file:
                    print("CLOCKINGGGGGG", file, system_data[system][file])
                    system_data[system][file] = (8000 - system_data[system][file]) / 8000 # remove_outliers(system_data[system][file])
                    # remove 10 first entries
                    #system_data[system][file] = system_data[system][file][15:]
                    system_data[system][file] = np.concatenate((np.cumsum(system_data[system][file][0:15]), system_data[system][file][15:]))
                    #N = 10
                    #system_data[system][file] = np.array([np.sum(system_data[system][file][i:i+N]) for i in range(0, len(system_data[system][file]), N)])
                    # total lost of CPU time should be equal to the nr of stalls increase

                    #
                    
            flen = len(system_data[system][file])
            if "promote" in file or "demote" in file:
                max_len = max(max_len,flen)
            print(max_len,  flen, file, "len setting...", system) # we have more LLC misses w/AsMEM... why?? 
        max_len_sys[system] = max_len
        _ = system_data[system]['hit_ratio_X']
        _ = _ - _[0]
        _ = _ *  (max_len/_[-1])
        system_data[system]['hit_ratio_X'] =  _ 

    # scale the X axis to be in the range between 0 and, max_len 
    print("why", system_data['ASMEM']['hit_ratio_Y'])
    print(_)
    #for system in system_data:
    #    for file in system_data[system]:
    print(_)
    print("_[-1]", _[-1])
    print(len(system_data['ASMEM']['hit_ratio_X']))
    print(len(_), "new leno!")
    #print(np.diff(system_data['ASMEM']['_ASMEM_htmm_nr_promoted-overtime'] - system_data['ASMEM']['_ASMEM_htmm_nr_demoted-overtime'])) 
    def plot_interpol(ax, y, line, color,max_len):
        #time_x = [i for i in range(0, max_len, int(max_len/len(y)))]
        time_x = np.linspace(0, max_len, len(y))
        #y_interpolated = np.interp(time_x, np.arange(len(y)), y)
        y_interpolated =  y
        ax.plot(time_x, y_interpolated, label=file, color=color, linestyle=line)
        #y_interpolated = y
        #plt.plot(time_x, system_data[system][ftotalAccessTimeSummedile], label=file)
        
        # dashed line

    def plot_by_metrics():
        # 72% of hit rate on both
        pairs = { 'Migrations over time' : ['prom','demo', 'clock'] , 'Performance over time' : ['hit_', 'stalls','clock'] } 
        for p in pairs.keys():
            plt.figure()
            clock = plt.twinx()
            if 'Performance' in p:
                hit = plt.twinx()
                stalls = plt.twinx()
                # disable x axis for ticks
            for system in system_data:
                linestyle = "--" if "ASMEM" in system else "-"
                for file in system_data[system]:
                    def def_color():
                        if "hit_ratio" in file:
                            return 'blue'
                        if "stalls" in file:
                            return 'orange'
                        if "prom" in file:
                            return 'green'
                        if "demo" in file:
                            return 'red'
                        return 'black'
                    color = def_color()
                    if any( [ True if  pp in file else False for pp in pairs[p]]):
                        a = clock if "clock" in  file else plt
                        print("plotting", file, system, system_data[system][file])
                        if 'Migra' in p:
                            if  "dem" in file:
                            # set a axis to be the maximum of the last N poitns
                                #m = max(remove_outliers(system_data[system][file]))
                                pass
                                #a.ylim(0,500000)


                            

                        if 'Performance' in p:
                            """
                            if "hit_ratio_X" in file:
                                try:
                                    color = 'red' if 'ASMEM' in system else 'blue'
                                    print("MEAN FOR ", system, np.mean(system_data[system]['hit_ratio_Y']))

                                    # interpolate hit ratio such that we have max_len * 2 poitns
                                    hit.scatter(system_data[system]['hit_ratio_X'], 
                                                (system_data[system]['hit_ratio_Y']), 
                                                label=file, color=color, s=0.1)
                                    # many migrations provide little benefit, since they correspond to not only latency insensitive pages, but withg low reuse
                                    # The most latency sensitive pages are also globally the most frequentlly accessed. 
                                    # these data structures are easily identifable my tiering systems, specially due to their short sizes. 
                                    # however, other pages are also heavily accessed, and can compete with them. 
                                    # memtis migrates pages w/low reuse or too late. increasing the sample rate, will allow it to improve perf.
                                    # 
                                    # an increased ammount of migrations = more LLC misses (unless you consider the page is moved w/a cpu thread.. then we have trashing)

                                    # we have a higher hit ratio, but more LLC misses
                                    # 

                                    print("did hit")
                                except Exception as e:
                                    print("FAiled to do hit raito", e)
                                continue
                            if "hit_ratio_Y" in file:
                                continue
                            """
                            if "stall" in file:
                                a = stalls
                                v = system_data[system]['stalls']/system_data[system]['instructions']
                                # np cumsum 
                                v = np.cumsum(v)
                                plot_interpol(a, v, linestyle,color,max_len_sys[system])
                            plot_interpol(a, system_data[system][file], linestyle,color,max_len_sys[system])
                            print("did a plot!")
                        else:
                            plot_interpol(a, system_data[system][file], linestyle,color,max_len_sys[system])

            plt.title(p)
            plt.xlabel("Time")
            plt.ylabel("Metric")
            if "Perf" in p: 
                # legend, black, dashed line is AsMem, - is Memtis
                plt.legend(["ASMEM", "MEMTIS"], loc="upper left")
                # red is demotions, green is promotions, blue is stalls
                plt.legend(["demotions", "promotions", "stalls"], loc="upper right")
                #        hit.set_xticks([])
                #stalls.set_xticks([])

            #clock.set_xticks([])


            # starts at 0 and goes up to max_len_sys[system]
            def get_elapsed_time():
                max  = 0
                max_v = []
                for s in system_data:
                    for k in system_data[s]:
                        if "hit_ratio_X" in k:
                            l= len(system_data[s][k])

                            if l > max:
                                max = l
                                max_v = system_data[s][k]

                a =  max_v - max_v[0]


                xlabels  = a[(a  % 50) == 0]
                # the place is the indexes where the value is true
                fith_seconds = (np.asarray(a, dtype=int)  % 5) # == 0
                # select only the first of each 
                fith_seconds = np.diff(fith_seconds) #!= 0
                # add one more entry to keep the size
                fith_seconds = np.append(fith_seconds, True)
                xlabels  = a[fith_seconds !=0]
                indexes_where_is_true = np.where(fith_seconds != 0)[0]
                return indexes_where_is_true, xlabels
                #for i in range(len(fith_seconds)):
                    #print(fith_seconds[i], a[i])
                #print(fith_seconds, )


                """
                xticks = np.where((
                    == 0)[0]
                print(xticks, "ticos", np.where((a  % 5) == 0), a % 5)
                """
                return xticks, xlabels


            plt.xticks(get_elapsed_time()[0], get_elapsed_time()[1])
            plt.legend()
            plt.savefig("over_time_" + p + ".png")
            plt.close()
            print("done figure of p ", p)
    plot_by_metrics()

    def plot_all_together():
        plt.figure()
        plt.title("Suff over time")
        #ax = plt.gca()
        # create an Y axis for promotions/demotions, another for stall cycles, another for hit ratio
        promotion_axis = plt.twinx()
        hit_ratio_axis = plt.twinx()
        stall_axis = plt.twinx()
        for system in system_data:
            for file in system_data[system]:
                color="blue"
                print(file)
                if "stalls" in file:
                    ax = stall_axis
                    color="red"

                if "nr_promoted" in file or "nr_demoted" in file:
                    ax = promotion_axis
                if "nr_promoted" in file:
                    color="orange"
                    #continue
                if "nr_demoted" in file:
                    color="brown"
                    #continue
                print(color)
                

                # make each datapoint equivalently spaced up to max_len
                #   np.linspace(0, max_len, len(system_data[system][file])), 

                if "hit_ratio_Y" in file:
                    continue
                if "hit_ratio_X" in file:
                    try:
                        ax = hit_ratio_axis
                        ax.plot(system_data[system]['hit_ratio_X'], system_data[system]['hit_ratio_Y'], label=file, color="green")
                    except:
                        print("FAiled to do hit raito")
                else:
                    try:
                        time_x = np.linspace(0, max_len, len(system_data[system][file]))
                        y_interpolated = np.interp(time_x,
                            np.arange(len(system_data[system][file])), system_data[system][file])
                        #plt.plot(time_x, system_data[system][file], label=file)
                        ax.plot(time_x, y_interpolated, label=file, color=color)

                        print("done")
                    except Exception as e:
                        print("whhh", e)
    plt.legend()
    plt.xlabel("Time")
    plt.ylabel("Stuff")
    plt.savefig("over_time.png")
    plt.close()

        
        
    


def cdf_inst():
    RESULT_FOLDER="multi"
    for MODE in "": # "-freq_weighted" "":
        fname=f"{FIGS_FOLDER}/{RESULT_FOLDER}/"
        # for file in fname
        for file in os.listdir(fname):
            try:
                if "png" in file:
                    print("whhh")
                    continue
                print("99")
                print(os.path.join(fname, file))
                with open(os.path.join(fname, file), 'r') as f:

                    lines = f.readlines()[1:]
                    d = {
                        'address' : [],
                        'Access time' : [],
                        'Stall Cycles' : [],
                        'Stall Cycles/MLP' : [],
                        'Frequency': []
                    }
                    for line in lines:
                        v = line.split(" ")
                        d['address'].append(v[0])
                        d['Access time'].append(int(v[1]))
                        d['Stall Cycles'].append(int(v[2]))
                        d['Stall Cycles/MLP'].append(int(v[4]))
                        d['Frequency'].append(int(v[5]))
            except Exception as e:
                print(e) ########### WILL PRINT THE KEY MISSINGF IF ITS A NOT FOUND ERROR!
                continue
        # do CDF of stall cycles, access time, totalTime
            plt.figure()
            plt.scatter(d['Stall Cycles/MLP'], d['Frequency'])
            plt.title("Stall Cycles/MLP vs Frequency")
            plt.xlabel("Stall Cycles/MLP")
            plt.ylabel("Frequency")
            plt.savefig(f"{FIGS_FOLDER}/{RESULT_FOLDER}/{file}_stallsmlp_freq.png")
            plt.close()

            

            plt.title("CDF of instruction metrics for " + file.split("-")[-1])
            plt.xlabel("Metric")
            for i in ['Stall Cycles', 'Access time','Stall Cycles/MLP']:
                sorted_data, cdf = get_cdf_array(d[i])
                plt.plot(sorted_data, cdf, label=i)
            plt.ylabel("CDF")
            plt.legend()
            plt.savefig(f"{FIGS_FOLDER}/{RESULT_FOLDER}/{file}{MODE}.png")
            plt.close()
        """
        plt.figure()
        plt.title("CDF of average MLP")
        plt.xlabel("Metric")
        for i in ['Stall Cycles/MLP']:
            sorted_data, cdf = get_cdf_array(d[i])
            plt.plot(sorted_data, cdf, label=i)
        plt.ylabel("CDF")
        plt.legend()
        plt.savefig(f"{FIGS_FOLDER}/{RESULT_FOLDER}/{file}.png")
        plt.close()
        """
def correspond(): 
    import glob
    files = glob.glob("/home/ist196723/nas/tools/SoarAlto/run/bc-urand/rst/rst-TPP/out-th0-*")
    # sort files by date
    files.sort(key=lambda x: os.path.getmtime(x))
    for f in files:
        print(f)
        o = f.split("th0-")[-1].split(".")[0]
        mem = "/home/ist196723/nas/tools/SoarAlto/run/bc-urand/rst/rst-TPP/mem-th0-" +o + ".log"
        out = "/home/ist196723/nas/tools/SoarAlto/run/bc-urand/rst/rst-TPP/out-th0-" +o + ".log"
        try:
            with open(mem) as g:
                with open(out) as o:
                    lines = g.readlines()
                    lo = o.readlines()
                    print("".join(lines))
                    print("".join(lo))
        except:
            continue

                

def orphan():
    result_files = os.listdir("results_gem5")
    f = {}
    for r in result_files:
        try:
            pid = r.split("_")[1] 
            machine = r.split("_")[2]
        except:
            continue
        f[pid+machine] = True
    pid_machines_registed = {}
    i =0
    ghosts = 0
    with open("results_gem5/gem5_pids.txt") as f:
        lines = f.readlines()
        for l in lines:
            if "pid: " in l:
                if len(l.split(" ")) < 3:
                    continue
                pid = l.split("pid: ")[1].split(' ')[0]
                machine = l.split("host: ")[1].split(' ')[0]
                pid_machines_registed[pid+machine] = True
                if pid+machine not in f:
                    print("ghost gem5 pid!", pid+machine, l)
                    ghosts+=1
    for r in result_files:
        try:
            pid = r.split("_")[1] 
            machine = r.split("_")[2]
            if pid +machine not in pid_machines_registed:
                print("orphan gem5 result!", pid+machine)
                
                i+=1
        except:
            continue
    print("ghosts", ghosts)
    print("orphans", i)

                

def missing_gem5():
    not_done = 0
    benches_done = {}
    with open("results_gem5/gem5_pids.txt") as f:
        lines = f.readlines()
        for l in lines:
            if "benchnr" not in l:
                #print(l, "no benchnr")
                continue
            benchnr = l.split("benchnr")[1].split(' ')[0]
            benches_done[benchnr] = True

        with open("benches_final") as todo:
            todo_lines = todo.readlines()
            l = 0
            for line in todo_lines:
                l += 1
                if str(l) not in  benches_done:
                    not_done +=1
                    print(line)

    print("Not done", not_done)
        


"""
AsMem/MEMtis  promising_results_16_LAST_FINAL

"""
def fino():
    folder="/mnt/nas/inesc/ist196723"
    #BENCH="bck"
    BENCH="mg"
    if BENCH == "mg":
        file="hurt_mg"
        max_usage = 3400
    if BENCH == "bck":
        file="osdi26/hurt_bck"
        file="hu_bck"
        max_usage = 22000
    #obj_sizes = { "bc48": 1, }


    # read as csv seperated by spaces
    # its seperated by spaces , but has mixed tabs
    data = [[],[],[],[], []]
    def filter_empty_entries(vector):
        return [v for v in vector if v]
    def split_by_blanks(line):
        l = line.split("\t")
        l = [li.split(" ") for li in l]
        l = [ entry for entry_list in l for entry in entry_list]
        return l
    with open(os.path.join(folder, file), 'r') as f:
        lines = f.readlines()
        for line in lines:
            v = split_by_blanks(line)
            v = filter_empty_entries(v)
            print(v)

            if not v[4].strip():
                continue
            data[0].append(v[0])
            data[1].append(v[1])
            data[2].append(v[2])
            data[3].append(v[3])
            data[4].append(v[4].strip())
        
    TIME = 0
    DRAM = 2
    SYSTEM = 4
    times = np.array(data[TIME], dtype=float)
    drams = np.array(data[DRAM], dtype=int)
    systems = np.array(data[SYSTEM], dtype=str)
    print("drams are", drams)
    # scatter plot
    # color by system
    # blue=asmem, orange=Memtis, red =Soar
    colors = {
        "ASMEM": "blue",
        "MEMTIS": "orange",
        "MEMTIS-1": "orange",
        "SOAR": "red",
        "ALL_FAST": "green",
        "ALL_SLOW": "black",
        'TPP': 'cyan',
        'TPP-ALTO': 'brown',

    }
    baseline_fast =np.mean(times[systems == "ALL_FAST"])
    baseline_slow =np.mean(times[systems == "ALL_SLOW"])
    
    print(systems)
    # plot horizontal line at baseline_slow
    plt.axhline(y=baseline_slow/baseline_fast, color='grey', linestyle='-')
    
    xticks = []
    xticks_str = []
    print()

    i = 0

    dones = {}
    sys_plots = {}
    for d in np.unique(drams[systems == "SOAR"]): # np.unique(drams):
        i+=2
        for system in np.unique(systems):
            if "ALL" in system:
                continue
            if "MEMTIS" == system:
                continue
            if system != "SOAR":
                # find the nearest dram that is greater
                v = drams[(systems == system) & (drams <= d)]
                if len(v) != 0:
                    nearest_dram = np.max(v)
                    if system + str(nearest_dram) in dones:
                        continue
                    dones[system + str(nearest_dram)] = True
            else:
                nearest_dram = d
            nr_of_trials = np.sum((systems == system) & (drams == nearest_dram))
            if nr_of_trials < 2:
                continue
            #i += 50
            i += 2
            #if len(times[(systems == system) & (drams == d)]) < 3:
            #continue

            #dram_percent = 100*(d+i)/max_usage
            if system in sys_plots:
                sys_plots[system] = True
                plt.bar(i, np.mean(times[(systems == system) & (drams == nearest_dram)])/baseline_fast, width=2, color=colors[system])
            else:
                plt.bar(i, np.mean(times[(systems == system) & (drams == nearest_dram)])/baseline_fast, width=2, color=colors[system])
        xticks.append(i)
        xticks_str.append(str(int(100*(d)/max_usage)))
    plt.xticks(xticks, xticks_str)

    #plt.scatter(drams, times/baseline_fast, c=[colors[s] for s in systems])
    #plt.xlim(0,100*7000/max_usage)
    plt.xlabel("Fast tier (%)")
    plt.ylabel("Performance degradation")
    plt.title("GAPBs bc-kron.sg performance")
    # do legend 
    plt.legend(
        [sys for sys in sys_plots],
        [colors[sys] for sys in sys_plots],
        loc="upper left",
        bbox_to_anchor=(1,1)
    )

    plt.savefig("hurt_bckk" + bench + ".png")
    print(data)
def clean_try():
    folder="/mnt/nas/inesc/ist196723"
    file ="all_results"
    file="osdi26/hurt_bck"
    OBJ_NR_DRAM_MAPS = { "bck": 
        [0, 512, 1536, 2560, 3072, 3584, 4096, 20480, 2200, 2200, 2200]
                        }
    def get_bench(bench):
        if "kron" in bench and "bc" in bench or "bck":
            return "bck"
        if "mg" in bench:
            return "mg"
        if "cg.D"  in bench:
            return "cg.D"
        
    systems = []
    benches = []
    times = []
    drams = []
    def is_system(entry):
        return "ALL" in entry or "ASMEM" in entry or "MEMTIS" in entry
    with open(os.path.join(folder, file), 'r') as f:
        lines = f.readlines()
        for line in lines:
            v = line.split(" ")
            TIME = 0
            if "SOAR" in line:
                if len(v) < 3 or "SOAR" != v[2]:
                    print(v)
                    print("BAD SOAR")
                    continue
                SYSTEM=3
                BENCH=get_bench(v[0])
                OBJ_NR=6
                print(int(v[OBJ_NR]))
                dram=OBJ_NR_DRAM_MAPS[BENCH][int(v[OBJ_NR])]
                drams.append(dram)
            else:
                SYSTEM=5
                DRAM=3
                if len(v) < 8:
                    print(v)
                    continue
                if not is_system(line):
                    print("BAD system", line)
                    continue

                BENCH=get_bench(v[7])
                dram=OBJ_NR_DRAM_MAPS[BENCH][DRAM]
                drams.append(dram)
            systems.append(v[SYSTEM])
            benches.append(BENCH)
            times.append(v[TIME])
    print("DRAM", drams)

                
            

                
        
def plot_r():
    global time, system, arand, aptr, ratio, dram
    # real results of sy
    folder="/mnt/nas/inesc/ist196723/latency_benchmark/tests_syn/plot_time_math"
    #file="TIREDbig_final_results"
    file="final_synthethic_tiering"
    file="syn_ftw"
    LAST_SYN=True
    if LAST_SYN:
        file="syn_ftw_f_2_please_back"


    bench = "cg.D"
    other_benchmode = False
    other_benchmode = True
    other_benchmode = False
    if other_benchmode:
        file="TIREDbig_final_results"
        file="promising_results"
        nr_args = 6

    


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
            for line in lines:
                v = line.split(" ")
                if False and other_benchmode:
                    if bench not in v:
                        continue
                    if len(v) < nr_args:
                        continue
                else:
                    if "ALL" in v[-1] and len(v) == 5:
                        pass
                    else:
                        if len(v) < 6:
                            continue
                TIME = 0
                t = float(v[TIME])
                if t < 1: # less than one
                    continue
                print(v)
                if "all_results" in bench_file:
                    DRAM=2
                    SYSTEM=3
                    BENCHED=5
                    if "|" in v:
                        BENCHED=6
                    try:
                        metric = int(v[2]) # this is the system name instead of a FOM
                    except:
                        continue
                    try:
                        if "TPP-ALTO" in v[3]:
                            SYSTEM = 3
                            DRAM = 2
                            BENCHED = 6
                            #dram.append(v[2])
                            #benched.append(v[5])
                            #continue
                            print("innn")
                        SYSTEM = 3
                        def is_system_right():
                            return "ASMEM" not in  v[SYSTEM] and "TPP" not in v[SYSTEM] and "MEMTIS" not in v[SYSTEM] and "SOAR" not in v[SYSTEM] and "ALL_FAST" not in v[SYSTEM] and "ALL_SLOW" not in v[SYSTEM]
                        if is_system_right():
                            SYSTEM=5
                            DRAM=3
                            if v[3] == "0":
                                DRAM = 2
                                
                            BENCHED=-1
                            #exit(0)

                        if is_system_right():
                            SYSTEM = 4
                            DRAM=2
                            BENCHED=6
                            
                        if is_system_right():
                            print(v[SYSTEM], "im leaving..")
                            print(v)
                            exit(0)
                        s = v[SYSTEM].strip()
                        d = v[DRAM].strip()
                        b = v[BENCHED].strip()
                        b = b.split("/")[-1].split("_")[0]
                        print("OUT_LINE", s,int(d),b,t)
                        dram.append(d)
                        system.append(s)
                        benched.append(b)

                    except Exception as e:
                        print(v)
                        print("ERROR")
                        print(e)
                        exit(0)
                    time.append(float(t))
                    continue
                else:
                    DRAM=3
                    SYSTEM=5
                #print(v)

                    if bench_name == "JOINED":
                        if "TPP" in v[3]:
                            system.append(v[3])
                            dram.append(int(v[2]))
                            benched.append(v[6].split("/")[-1])
                            continue
                        else:
                            benched.append(v[3])
                            dram.append(int(v[2]))
                            system.append(v[6])
                            continue

                    if LAST_SYN:
                        if "ALL" in v[-1]: 
                            system.append(v[-1])
                            dram.append(0)
                        else:
                            system.append(v[5])
                            dram.append(int(v[3]))
                    else:
                        system.append(v[4])


                    if other_benchmode:
                        #bench in v and not 
                        dram.append(int(v[2]))
                    else:
                        arand.append(int(v[2]))
                        aptr.append(int(v[1]))
                        ratio.append(v[-2])
                time.append(float(t))
        ratio = np.array(ratio)
        arand = np.array(arand)
        aptr = np.array(aptr)
        time = np.array(time)
        system = np.array(system)
        dram = np.array(dram)
        print("dram", dram, "lo")
        benched = np.array(benched)
        bench = "bc"
        bench = 'mg.C'
        def agnost_plot(bench):
                plt.figure()
                plt.title(bench +  " performance by DRAM")
                plt.xlabel("DRAM")
                plt.ylabel("Execution time")
                bench_idxs = benched == bench
                DRAMS = np.unique(dram[bench_idxs])
                xticks = []
                xticks_labels = []
                #for i in range(len(DRAMS)):

        other_benchmode = True
        if other_benchmode or bench_name == "JOINED":
            dram = np.array(dram)
            def other_plot(bench):
                plt.figure()
                plt.xlabel("DRAM")
                plt.ylabel("Execution time")
                DRAMS = np.unique(dram)

                xticks = []
                xticks_labels = []
                print("DRAMOS ", DRAMS)
                print(benched)
                #exit(0)
                SCATTER = True
                    
                for i in range(len(DRAMS)):
                    o = i*2
                    idx = dram == DRAMS[i]
                    #print(system)
                    #print(np.unique(benched))
                    print(DRAMS[i], "THIS")

                    if bench_name == "JOINED" or True:
                        bench_sel = 'kron.sg__-i4_-n5' == benched[idx] 
                        bench_sel = 'mg.C' == benched[idx] 
                        bench_sel = bench == benched[idx] 
                        bench_sel = 'kron.sg__-i4_-n5' in benched[idx] 
                        print(benched[idx], "---- for fram", DRAMS[i])

                        bench = "mg.C"

                        bench_sel = ("bck" == benched[idx]) # # # # # # # # # or ('-i4_-n5' in benched[idx] )
                        bench = "mg.C"
                        bench = "bck"
                        bench_sel = bench == benched[idx] 
                        bench_sel = ("bck" == benched[idx]  ) | ("kron.sg" == benched[idx] ) # # # # # # # # # or ('-i4_-n5' in benched[idx] )

                        print("we are not eve here..")
                        print(benched, benched[idx][bench_sel], 'lol')
                        #continue
                    


                        #bench_sel = benched[idx] != "o"
                        print("iiiiiiiiiiiiiii")
                        #print(benched[idx])
                        #print(system[idx])
                        idx_mem_norm = ((( "MEMTIS" == system[idx] ) ) & bench_sel)
                        idx_mem = ((( "MEMTIS-1" == system[idx] ) ) & bench_sel)
                        idx_asm = ((( "ASMEM" == system[idx] ) ) & bench_sel )#plt.bar("MEMTIS", np.mean(time[])) #plt.bar("AsMem", np.mean(time[]))
                        idx_tpp = ((( "TPP" == system[idx] ) ) & bench_sel )#plt.bar("MEMTIS", np.mean(time[])) #plt.bar("AsMem", np.mean(time[]))
                        idx_tpp_alto = ((( "TPP-ALTO" == system[idx] ) ) & bench_sel )#plt.bar("MEMTIS", np.mean(time[])) #plt.bar("AsMem", np.mean(time[]))
                        #idx_mem = ((("MEMTIS" in system[idx] ) | (system[idx] == "MEMTIS")) & bench_sel)
                        #idx_asm = ((("ASMEM" in system[idx] ) | (system[idx] == "AsMem")) & bench_sel )#plt.bar("MEMTIS", np.mean(time[])) #plt.bar("AsMem", np.mean(time[]))
                        print("-------------")
                        print("mem", system[idx][idx_mem])
                        print("asm", system[idx][idx_asm])
                        print("tpp", system[idx][idx_tpp])

                    else:
                        bench_sel = system[idx] != 'LKASDJALISKDJ'
                        if LAST_SYN:
                            idx_mem = (((system[idx] == "MEMTIS\n") | (system[idx] == "MEMTIS")) & bench_sel)
                            idx_asm = (((system[idx] == "AsMem\n") | (system[idx] == "AsMem") | (system[idx] == "ASMEM")) & bench_sel )#plt.bar("MEMTIS", np.mean(time[])) #plt.bar("AsMem", np.mean(time[]))
                        else:
                            idx_mem = (((system[idx] == "0\n") | (system[idx] == "0")) & bench_sel) 
                            idx_asm = (((system[idx] == "4\n") | (system[idx] == "4")) & bench_sel) #plt.bar("MEMTIS", np.mean(time[])) #plt.bar("AsMem", np.mean(time[]))
                    bench = "bck"
                    bench = "mg.C"
                    bench = "bck"
                    bench_sel = bench == benched[idx] 
                    PERCENT_DRAM = True
                    benchmarkss = {
                        'mg.C' : [4000+2000]
                    }
                    #RSS = 7000 + 4000
                    RSS = benchmarkss[bench][0]
                    idx_all_fast_ = (((system == "ALL_FAST\n") | (system == "ALL_FAST")) & (bench == benched))
                    idx_all_slow_ = (((system == "ALL_SLOW\n") | (system == "ALL_SLOW")) & (bench == benched))
                    slow_time = np.mean(time[idx_all_slow_])
                    fast_time = np.mean(time[idx_all_fast_])
                    print(slow_time, fast_time, "BLA")
                    #slow_time = 80
                    fast_time = 80/100
                    norm = fast_time
                    if SCATTER:
                        idx_all_fast = (((system[idx] == "ALL_FAST\n") | (system[idx] == "ALL_FAST")) & bench_sel)
                        idx_all_slow = (((system[idx] == "ALL_SLOW\n") | (system[idx] == "ALL_SLOW")) & bench_sel)
                        idx_soar = (((system[idx] == "SOAR")) & bench_sel)
                        percentage = int(DRAMS[i]) 
                        if  len(time[idx][idx_mem] ) < 3 or len(time[idx][idx_asm]) < 3:
                            print("WARNING too few points!", len(time[idx][idx_mem]), len(time[idx][idx_asm]), "for DRAM", percentage, "and bench", bench)
                            #continue
                        if PERCENT_DRAM:
                            percentage *=100/RSS
                        alfa=0.7
                        systems = [idx_mem, idx_asm, idx_tpp, idx_tpp_alto, idx_all_fast, idx_all_slow]
                        for s in systems:
                            if np.sum(time[idx][s] == 0) >= 1:
                                print("BAD")
                                exit(0)
                            else: 
                                print("Not bad!")
                                if len(time[idx][idx_tpp]) > 0:
                                    print("TPPIIII",DRAMS[i],  (time[idx][idx_tpp]))
                        plt.scatter(percentage, np.mean(time[idx][idx_mem]/norm), color="blue", alpha=alfa)
                        plt.scatter(percentage, np.mean(time[idx][idx_asm]/norm), color="orange", alpha=alfa)
                        if len(time[idx][idx_tpp]) != 0:
                            plt.scatter(percentage,  np.mean(time[idx][idx_tpp]/norm), color="red", alpha=alfa)
                        if len(time[idx][idx_tpp_alto]) != 0:
                            plt.scatter(percentage, np.mean(time[idx][idx_tpp_alto]/norm), color="green", alpha=alfa)
                        #plt.scatter(percentage, np.mean(time[idx][idx_all_fast]), color="purple", alpha=alfa)
                        #plt.scatter(percentage, np.mean(time[idx][idx_all_slow]), color="grey", alpha=alfa)
                        #plt.scatter(percentage, np.mean(time[idx][idx_mem_norm]), color="black", alpha=alfa)

                        plt.scatter(0, np.mean(time[idx][idx_all_slow]), color="grey", alpha=alfa)
                        #plt.scatter(, np.mean(time[idx][idx_soar]), color="black")
                    if not SCATTER:
                        plt.bar(i+o, np.mean(time[idx][idx_mem]), width=0.5, color="blue")
                        plt.bar(i+o+0.5, np.mean(time[idx][idx_asm]), width=0.5, color="orange")
                        print("time")
                        print(time[idx][idx_tpp])
                        print(time[idx][idx_tpp_alto])
                        
                        plt.bar(i+o+1, np.minimum(500,  np.mean(time[idx][idx_tpp])), width=0.5, color="red")
                        plt.bar(i+o+1.5, np.minimum(500, np.mean(time[idx][idx_tpp_alto])), width=0.5, color="green")

                        idx_all_fast = (((system[idx] == "ALL_FAST\n") | (system[idx] == "ALL_FAST")) & bench_sel)
                        idx_all_slow = (((system[idx] == "ALL_SLOW\n") | (system[idx] == "ALL_SLOW")) & bench_sel)
                        plt.bar(i+o+2, np.minimum(500, np.mean(time[idx][idx_all_fast])), width=0.5, color="purple")
                        plt.bar(i+o+2.5, np.minimum(500, np.mean(time[idx][idx_all_slow])), width=0.5, color="grey")
                        xticks.append(i+o+0.5)
                        xticks_labels.append(str(DRAMS[i]))

                from matplotlib.lines import Line2D
                color_handles = [
                    Line2D([0], [0],  color='blue', label='MEMTIS'),
                    Line2D([0], [0],  color='orange', label='AsMem'),
                    Line2D([0], [0],  color='grey', label='Slow tier only'),
                    Line2D([0], [0],  color='purple', label='Fast tier only'),

                    Line2D([0], [0],  color='red', label='TPP'),
                    Line2D([0], [0],  color='green', label='TPP-ALTO'),
                ]
                all_handles = color_handles
                plt.legend(handles=all_handles, loc='best') #, bbox_to_anchor=(1, 1))
                if not SCATTER:
                    plt.xticks(xticks, xticks_labels)
                plt.xlabel("Percentage of fast tier")
                plt.ylabel("Execution time")
                if PERCENT_DRAM:
                    plt.xlim(0, 100)
                else:
                    plt.xlim(0, RSS)    
                plt.ylim(0, 200)
                plt.title(bench +  " performance by DRAM")
                extra = ""
                if LAST_SYN:
                    extra = "last_sy_"
                if bench_name == "JOINED":
                    extra = "joined_"
                plt.savefig(f"{FIGS_FOLDER}/../report/_{extra}{bench}_drams_{bench_file.split('/')[-1]}{extra}.png")
                print("saving to", f"{FIGS_FOLDER}/../report/{extra}{bench.split('/')[-1]}_drams_{bench_file.split('/')[-1]}{extra}.png")
                plt.close()
                exit(0)
            print("bouto..")
            other_plot(bench)
            return

    #do_plot("__", 5, "JOINED", False)
    
    LAST_SYN=False
    file = "/mnt/nas/inesc/ist196723/all_results"
    nr_args = 5
    do_plot(file, nr_args, bench, True)
    print(system, dram)
    return

    LAST_SYN=True
    if LAST_SYN:
        file="syn_ftw_f_2_please_back_NOW_RIGHT"
    nr_args = 4
    bench = "SYNTHETHIC"
    file = "syn_ftw_f_2_please_back_NOW_RIGHT_QQ"
    do_plot(file, nr_args, bench, False)
    """
    return
    bench = "cg.D"
    nr_args = 6
    #do_plot("TIREDbig_final_results", 4, bench, True)
    do_plot("promising_results", nr_args, bench, True) 
    #do_plot("promising_results", nr_args, bench, True) 
    other_benchmode = False
    other_benchmode = True
    if other_benchmode:
        file="TIREDbig_final_results"
        file="promising_results"
        nr_args = 6

    do_plot("resos", 5, bench, True)
    file="final_synthethic_tiering" 
    file="syn_ftw"
    # LOAD THE DATA FOR THE NEXT CODE

    do_plot(file, nr_args, bench, False)
    """
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
            
            DRAM_USED=190
            #print(dram, idx)
            idx_mem = (arand[idx] == current_arand) & (system[idx] == "MEMTIS-1-1\n") & (dram[idx] == DRAM_USED) #(dram[idx] == 320)
            idx_asm = (arand[idx] == current_arand) & (system[idx] == "ASMEM\n") & (dram[idx] == DRAM_USED) #(dram[idx] == 320)

            idx_all_fast = ( arand[idx] == current_arand) & ((system[idx] == "ALL_FAST\n") | (system[idx] == "ALL_FAST"))
            idx_all_slow = ( arand[idx] == current_arand) & (((system[idx] == "ALL_SLOW\n") | (system[idx] == "ALL_SLOW"))) 

            baseline_fast = np.mean(time[idx][idx_all_fast])
            baseline_fast = np.mean(time[idx][idx_all_slow])
            o = i*1.1

            print("----------")
            print(len(time[idx][idx_mem]))
            print(len(time[idx][idx_asm]))
            print("----------")
            plt.bar(i+o, np.mean(time[idx][idx_mem])/baseline_fast, width=0.5, color="blue")
            plt.bar(i+o+0.5, np.mean(time[idx][idx_asm])/baseline_fast, width=0.5, color="orange")
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
        ]

        # Combine marker and color handles
        all_handles =  color_handles

        # Show legend with all handles
        plt.legend(handles=all_handles, loc='best')
        plt.title(f"Performance with {r} pointer chasings")
        plt.savefig(f"{FIGS_FOLDER}/../report/aptr_{r}.png")
    
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
        exit(0)
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
        plt.savefig(f"{FIGS_FOLDER}/../report/ratio_{r}.png")
    


def plot_sy():
    categories = ["All CXL", "Pessimal Alloc", "Optimal Alloc", "All DRAM"]
    values = [1.842, 1.719, 1.006, 1.000 ] # "CXL DS"  1.700,
    plt.figure()
    plt.title("Performance by static allocation")
    plt.xlabel("Static allocation mode")
    plt.ylabel("Norm Perf")
    plt.bar(categories, values, color='grey')
    #plt.xticks(categories,roddtation=45)
    plt.ylim(0.5,2)


    plt.savefig(f"{FIGS_FOLDER}/../report/static_alloc_synth.png")

    
    fname="weights_over_time"
    folder="/mnt/nas/inesc/ist196723/latency_benchmark/tests_syn/plot_time_math"
    files={
        "inst_weights": "inst_weights",
        "acc_time_weights": "acc_time_weights",
        #"mlp_weight_weights": "mlp_weight_weights",
        "stall_cycles_weights": "stall_weights",
        "by_mlp_avg_weights": "by_mlp_avg_weights",
        "arand" : "arand_",
        "aptr" : "aptr_",
    }


    values = {}
    values80 = {}
    for k,v in files.items():
        values[k] = np.loadtxt(f"{folder}/{v}")
        if k not in ['arand', 'aptr']:
            values80[k] = np.loadtxt(f"{folder}/{v}80")
            
            print(len(values[k]), len(values80[k]))
            print(k, np.mean(values80[k]), np.mean(values[k]))

    SELECTED_INPUTS_FEW=True
    if SELECTED_INPUTS_FEW:
        for k in values:
            values[k] = values[k][:10]
        for k in values80:
            values80[k] = values80[k][:10]


    plt.figure()
    plt.title("Instruction weights in function of inputs")
    plt.xlabel("Number of sequential reads")
    plt.ylabel("Weight")
    insts_unique = np.unique(values['inst_weights'])

    streams =  np.unique(values['arand'])
    DO_DIFF=False
    for o in [1]:
        if SELECTED_INPUTS_FEW:
            continue
        idx = values['arand'] >= 0 #  LOOOOOOOOOOOOOOOST HOURS had > instead of >= . which took out an element. then, later, another array that should have the same size did not ! because it did not go through this index!


        mask_X = [inst == insts_unique[0] for inst in values['inst_weights'][idx]]
        mask_O = [inst == insts_unique[1] for inst in values['inst_weights'][idx]]
        #mask_O = [not cond for cond in mask_X]
        if not DO_DIFF:
            diff = np.zeros(len(values['arand'][idx][mask_X]))

        diff = diff if not DO_DIFF else np.array(values80['acc_time_weights'])[idx][mask_X]
        plt.scatter(np.array(values['arand'])[idx][mask_X],  np.abs(diff - np.array(values['acc_time_weights'] )[idx][mask_X]), 
                    label='Access time Stream', marker='X', color="blue")
        diff = diff if not DO_DIFF else np.array(values80['acc_time_weights'])[idx][mask_O]
        plt.scatter(np.array(values['arand'])[idx][mask_O], np.abs(diff - np.array(values['acc_time_weights'])[idx][mask_O]), 
                    label='Access time Pointer Chase', marker='o', color="blue")
        
        diff = diff if not DO_DIFF else np.array(values80['stall_cycles_weights'])[idx][mask_X]
        plt.scatter(np.array(values['arand'])[idx][mask_X], np.abs(diff - np.array(values['stall_cycles_weights'])[idx][mask_X]), 
                    label='Stall cycles Stream', marker='X', color="orange")
        diff = diff if not DO_DIFF else np.array(values80['stall_cycles_weights'])[idx][mask_O]
        plt.scatter(np.array(values['arand'])[idx][mask_O], np.abs(diff - np.array(values['stall_cycles_weights'])[idx][mask_O]), 
                    label='Stall cycles Pointer Chase', marker='o', color="orange")
        diff = diff if not DO_DIFF else np.array(values80['by_mlp_avg_weights'])[idx][mask_X]
        plt.scatter(np.array(values['arand'])[idx][mask_X], np.abs(diff - np.array(values['by_mlp_avg_weights'])[idx][mask_X]), 
                    label='Stall cycles/MLP Stream', marker='X', color="green")
        diff = diff if not DO_DIFF else np.array(values80['by_mlp_avg_weights'])[idx][mask_O]
        plt.scatter(np.array(values['arand'])[idx][mask_O], np.abs(diff - np.array(values['by_mlp_avg_weights'])[idx][mask_O]), 
                    label='Stall cycles/MLP Pointer Chase', marker='o', color="green")
        # marker legent
        #plt.legend(handles=[Line2D([0], [0], marker='x', color='w', label='MU'), Line2D([0], [0], marker='o', color='w', label='inst')])

        # make legend where color is associated with  the  Y value (the metric )and the marker  is associated with the instruction 
        from matplotlib.lines import Line2D

        marker_handles = [
            Line2D([0], [0], marker='o', color='black', label='Pointer Chasing',
                markerfacecolor='black', markersize=6, linestyle='None'),
            Line2D([0], [0], marker='X', color='black', label='Streaming Read',
                markerfacecolor='black', markersize=6, linestyle='None')
        ]

        # Color legend handles
        color_handles = [
            Line2D([0], [0], marker='o', color='blue', label='Access time',
                markerfacecolor='blue', markersize=4, linestyle='None'),
            Line2D([0], [0], marker='o', color='orange', label='Stall cycles',
                markerfacecolor='orange', markersize=4, linestyle='None'),
            Line2D([0], [0], marker='o', color='green', label='Stall cycles/MLP',
                markerfacecolor='green', markersize=4, linestyle='None'),
        ]

        # Combine marker and color handles
        all_handles = marker_handles + color_handles

        # Show legend with all handles
        plt.legend(handles=all_handles, loc='best')
        # tight layout
        #plt.tight_layout()

        # plt.legend()
        s="1"
        plt.savefig(f"{FIGS_FOLDER}/../report/{fname}___{s}.png")

        
        #values80['inst_weights']  == 
        plt.figure()
        plt.title("Weight proportion between Pointer Chase and Streaming Reads")
        plt.bar("Access time", np.mean(values['acc_time_weights'][mask_O])/np.mean(values['acc_time_weights'][mask_X]), color="grey")
        plt.bar("Stall cycles/MLP", np.mean(values['by_mlp_avg_weights'][mask_O])/np.mean(values['by_mlp_avg_weights'][mask_X]), color="grey")
        plt.bar("Stall cycles", np.mean(values['stall_cycles_weights'][mask_O])/np.mean(values['stall_cycles_weights'][mask_X]), color="grey")
        plt.bar("Iteration time", 13, color="grey")
        plt.savefig(f"{FIGS_FOLDER}/../report/{fname}_proportion.png")

        plt.figure()
        plt.title("Slow tier metrics")
        """
        print(values80['acc_time_weights'][idx]) print(len(values80['acc_time_weights']), len(values['acc_time_weights'])) print(values80['acc_time_weights'][-10:]) print(values['acc_time_weights'][-10:]) print(values80['acc_time_weights'][:10]) print(values['acc_time_weights'][:10]) print(len(idx), sum(idx),"boool dude") 
        """ 
        mask_X80 = [inst == insts_unique[0] for inst in values80['inst_weights']]
        mask_O80 = [inst == insts_unique[1] for inst in values80['inst_weights']]
        #mask_O80 = [not cond for cond in mask_X80]

        plt.bar("Access time", (np.mean(values80['acc_time_weights'][mask_O80]) - np.mean(values['acc_time_weights'][mask_O]))/(np.mean(values80['acc_time_weights'][mask_X80]) - np.mean(values['acc_time_weights'][mask_X])), color="grey")
        print("Access time", (np.mean(values80['acc_time_weights'][mask_O80]) - np.mean(values['acc_time_weights'][mask_O]))/(np.mean(values80['acc_time_weights'][mask_X80]) - np.mean(values['acc_time_weights'][mask_X])))
        #print("Access time", np.mean(values80['acc_time_weights'][mask_O80]) - np.mean(values['acc_time_weights'][mask_O]), np.mean(values80['acc_time_weights'][mask_X80]) - np.mean(values['acc_time_weights'][mask_X]))
        plt.bar("Stall cycles/MLP", (np.mean(values80['by_mlp_avg_weights'][mask_O80]) - np.mean(values['by_mlp_avg_weights'][mask_O]))/(np.mean(values80['by_mlp_avg_weights'][mask_X80]) - np.mean(values['by_mlp_avg_weights'][mask_X])), color="grey")
        print("Stall cycles/MLP", (np.mean(values80['by_mlp_avg_weights'][mask_O80]) - np.mean(values['by_mlp_avg_weights'][mask_O]))/(np.mean(values80['by_mlp_avg_weights'][mask_X80]) - np.mean(values['by_mlp_avg_weights'][mask_X])))
        #print("Stall cycles/MLP", (np.mean(values80['by_mlp_avg_weights'][mask_O80]) - np.mean(values['by_mlp_avg_weights'][mask_O])) (np.mean(values80['by_mlp_avg_weights'][mask_X80]) - np.mean(values['by_mlp_avg_weights'][mask_X])))
        plt.bar("Stall cycles", (np.mean(values80['stall_cycles_weights'][mask_O80]) - np.mean(values['stall_cycles_weights'][mask_O]))/(np.mean(values80['stall_cycles_weights'][mask_X80]) - np.mean(values['stall_cycles_weights'][mask_X])), color="grey")
        print("Stall cycles", (np.mean(values80['stall_cycles_weights'][mask_O80]) - np.mean(values['stall_cycles_weights'][mask_O]))/(np.mean(values80['stall_cycles_weights'][mask_X80]) - np.mean(values['stall_cycles_weights'][mask_X])))
        #print("Stall cycles", np.mean(values80['stall_cycles_weights'][mask_O80]) - np.mean(values['stall_cycles_weights'][mask_O]), np.mean(values80['stall_cycles_weights'][mask_X80]) - np.mean(values['stall_cycles_weights'][mask_X]))
        ##plt.bar("Slow down", 13, color="grey")
        plt.xlabel("Metric")
        plt.ylabel("Increase")
        plt.savefig(f"{FIGS_FOLDER}/../report/{fname}_diff_proportion.png")
        
        plt.figure()
        plt.title("Metric increase in slow tier")
        """
        print(values80['acc_time_weights'][idx]) print(len(values80['acc_time_weights']), len(values['acc_time_weights'])) print(values80['acc_time_weights'][-10:]) print(values['acc_time_weights'][-10:]) print(values80['acc_time_weights'][:10]) print(values['acc_time_weights'][:10]) print(len(idx), sum(idx),"boool dude") 
        """ 
        mask_X80 = [inst == insts_unique[0] for inst in values80['inst_weights']]
        mask_O80 = [inst == insts_unique[1] for inst in values80['inst_weights']]
        #mask_O80 = [not cond for cond in mask_X80]

        i=0
        ticks = []
        labels = []
        spacing=0.12
        ptr_color = "blue"
        seq_color = "orange"
        i+=spacing
        w=0.5
        plt.bar(i, (np.mean(values80['acc_time_weights'][mask_O80]) - np.mean(values['acc_time_weights'][mask_O])), width=w, color=ptr_color)
        i+=0.5
        ticks.append(i-w/2)
        labels.append("Access time")
        plt.bar(i, (np.mean(values80['acc_time_weights'][mask_X80]) - np.mean(values['acc_time_weights'][mask_X])), width=w, color=seq_color)
        #tick
        """

        "Access time Ptr"
        "Access Time Seq"
        """
        print("Access time", (np.mean(values80['acc_time_weights'][mask_O80]) - np.mean(values['acc_time_weights'][mask_O]))/(np.mean(values80['acc_time_weights'][mask_X80]) - np.mean(values['acc_time_weights'][mask_X])))
        #print("Access time", np.mean(values80['acc_time_weights'][mask_O80]) - np.mean(values['acc_time_weights'][mask_O]), np.mean(values80['acc_time_weights'][mask_X80]) - np.mean(values['acc_time_weights'][mask_X]))

        

        i+=w+spacing
        plt.bar(i, (np.mean(values80['stall_cycles_weights'][mask_O80]) - np.mean(values['stall_cycles_weights'][mask_O])), width=w, color=ptr_color)
        i+=0.5
        ticks.append(i-w/2)
        labels.append("Stall cycles")
        plt.bar(i, (np.mean(values80['stall_cycles_weights'][mask_X80]) - np.mean(values['stall_cycles_weights'][mask_X])), width=w, color=seq_color)

        

        print("Stall cycles/MLP", (np.mean(values80['by_mlp_avg_weights'][mask_O80]) - np.mean(values['by_mlp_avg_weights'][mask_O]))/(np.mean(values80['by_mlp_avg_weights'][mask_X80]) - np.mean(values['by_mlp_avg_weights'][mask_X])))
        #print("Stall cycles/MLP", (np.mean(values80['by_mlp_avg_weights'][mask_O80]) - np.mean(values['by_mlp_avg_weights'][mask_O])) (np.mean(values80['by_mlp_avg_weights'][mask_X80]) - np.mean(values['by_mlp_avg_weights'][mask_X])))
        i+=w+spacing

        plt.bar(i, (np.mean(values80['by_mlp_avg_weights'][mask_O80]) - np.mean(values['by_mlp_avg_weights'][mask_O])), width=w, color=ptr_color)
        #"Stall cycles/MLP Seq"
        i+=0.5
        ticks.append(i-w/2)
        labels.append("Stall cycles/MLP")
        plt.bar(i, (np.mean(values80['by_mlp_avg_weights'][mask_X80]) - np.mean(values['by_mlp_avg_weights'][mask_X])), width=w, color=seq_color)

        
        

        print("Stall cycles", (np.mean(values80['stall_cycles_weights'][mask_O80]) - np.mean(values['stall_cycles_weights'][mask_O]))/(np.mean(values80['stall_cycles_weights'][mask_X80]) - np.mean(values['stall_cycles_weights'][mask_X])))
        #print("Stall cycles", np.mean(values80['stall_cycles_weights'][mask_O80]) - np.mean(values['stall_cycles_weights'][mask_O]), np.mean(values80['stall_cycles_weights'][mask_X80]) - np.mean(values['stall_cycles_weights'][mask_X]))
        ##plt.bar("Slow down", 13, color="grey")
        plt.xticks(ticks, labels)
        plt.legend(["Pointer Chase", "Stream read"])
        plt.xlabel("Metric")
        plt.savefig(f"{FIGS_FOLDER}/../report/{fname}_diff_ptr_seq_proportion.png")
        
        


    

OLD_V4=False

    

# 
# 
"""
python3 bin/python_parser.py "plot_synthethic()"
./controller.sh do_over_math $1

"""
def plot_synthethic():
    math_lvl = np.array([])
    inst = []
    keys = ['totalTime', 'stallTime', 'stallCyclesMLPLoad', 'average_mlp', 'average_l3mlp']
    d = {'lat': np.array([]), 'address': np.array([])}
    EIGHT_MODE=False
    for k in keys:
        d[k] = np.array([])

    for r in data:
        if '0' not in data[r]:
            print("NOT 0", data[r])
            continue
        exe = data[r]['0']['bench'].split("/")[-1]
        if "outa" not in exe:
            continue
        parts = exe.split("-")
        if len(parts) == 2:
            math = int(parts[1])
            print(exe, math)
            try:
                i = load_inst_fields(data, r)
                i80 = load_inst_fields(data, r,'80')
            except:
                print("error loading", exe)
                continue

            
            try:
                math_lvl = np.concat((math_lvl, np.ones(len(i['totalTime']))*math)) #np.ones(len(i80['totalTime']))*math))
                #continue
            except:
                print("error loading (not found totalTime)", exe)
                continue
            d['address'] = np.concat((d['address'], i['address']))
            d['lat'] = np.concat((d['lat'], np.zeros(len(i['totalTime'])))) 
            print("C",len(i['totalTime']), len(i['address']))
            if EIGHT_MODE:
                math_lvl = np.concat((math_lvl, np.ones(len(i80['totalTime']))*math)) #np.ones(len(i80['totalTime']))*math))
                d['lat'] = np.concat((d['lat'], np.ones(len(i80['totalTime']))*80))
            
            for k in keys:
                d[k] = np.concat((d[k], i[k]))
                if EIGHT_MODE:
                    d[k] = np.concat((d[k], i80[k]))
            
    inst = np.unique(d['address'])
    inst_sorted = np.sort(inst)

    for j,inst in enumerate(inst_sorted):
        print("LENS", len(inst_sorted), len(d['totalTime']),  len(math_lvl))
        idx = (d['address'] == inst) & (d['lat'] == 0)
        if j > 4:
            continue

    
        plt.figure()
        if j == 1:
            plt.title("Stall time over latency")
        #plt.scatter(math_lvl[idx], d['lat'][idx], color='blue', label='Latency')
        plt.scatter(math_lvl[idx], d['totalTime'][idx],  label='Access time')
        plt.scatter(math_lvl[idx], d['stallTime'][idx], label='Stall cycles')
        #plt.scatter(math_lvl[idx], d['stallCyclesMLPLoad'][idx],  label='Stall cycles/MLP')
        plt.ylabel("Metric")
        plt.legend()

        ax2 = plt.twinx()
        #ax2.scatter(math_lvl[idx], d['average_l3mlp'][idx], label='Average L3 MLP')
        ax2.scatter(math_lvl[idx], d['average_l3mlp'][idx],color='grey', label='Average MLP')
        ax2.set_ylabel('Average MLP')

        plt.xlabel("Math level")
        #plt.legend()
        plt.savefig(f"{FIGS_FOLDER}/../report/synthethic_over_mat_{j}.png")
        plt.close()

            #inst.append(i)
    
        


"""
python3 bin/python_parser.py "simple_weight()"
"""
writes=0
def simple_weight():
    global run_meta
    global DATA_FOLDER
    global RUN_DATA_FOLDER
    global OLD_V4
    RESULT_FOLDER="maps"
    OLD_V4=True
    OLD_V4=False
    if OLD_V4:
        RUN_DATA_FOLDER="/mnt/nas/inesc/ist196723/osdi26/v4/results_gem5"
        #RUN_DATA_FOLDER="/mnt/nas/inesc/ist196723/osdi26/results_gem5"
        run_meta=f"{RUN_DATA_FOLDER}/gem5_pids.txt"
        RESULT_FOLDER="mapsv4"
        #data = load_bench_data()
    
    ONLY_SYN=False

    MULTI=True
    TARGET_BIN = None
    TARGET_BIN = "cg.D"
    #MULTI=False
    if MULTI:
        RESULT_FOLDER="multi"
    def simp(data,r):
        global writes
        EIGHT_MODE=False
        this_binary = data[r]['0']['bench'].split("/")[-1]
        if TARGET_BIN and TARGET_BIN not in this_binary:
            return
        benchset = data[r]['0']['benchset']
        if benchset != "npb_result-iter":
            print("skip")
        else:
            print("Found", TARGET_BIN)
            

        i = load_inst_fields(data, r)
        if EIGHT_MODE:
            i = load_inst_fields(data, r, '80')   # i80 = ... instead of i = ... <--------- HOURS LOST !
        benchset = data[r]['0']['benchset']
        print(benchset)
        print('benchname', data[r]['0']['bench'].split("/")[-1], data[r]['0']['benchnr'])
        #if "bc" not in data[r]['0']['bench'].split("/")[-1]:
        #return
        print(benchset)
        if "synth" not in benchset and ONLY_SYN:
            return
        print("------------------")
        # def load_multiple(data, r_list)
        keys_used = ['address', 'stallCyclesMLPLoad', 'totalTime', 'stallTime', 'average_mlp']
        SKIP_START=000 # time to let the cache load     16Kb/8bytes = 2000 
        for k in keys_used:
            print(len(i[k][SKIP_START:]),k, "lol")
            i[k] = i[k][SKIP_START:]

        if(len(load_inst_fields(data, r )['totalTime']) != len(load_inst_fields(data, r )['address']) ):
                        print("big mistake!!")
                        exit(0)
            
        print(data[r])
        rs = []
        """

        if(len(load_inst_fields(data, ru )['totalTime']) != len(load_inst_fields(data, ru )['address']) ):
            continue
        """

        if MULTI :
            if '0' not in data[r]:
                return
            #if data[r]['0']['benchset'] == 'npb_result':
            for ru in data:
                if '0' not in data[ru]:
                    continue
                binary = data[ru]['0']['bench'].split("/")[-1]

                if binary == this_binary and data[ru]['0']['benchset'] == data[r]['0']['benchset']:

                    try:
                        for k in keys_used: 
                            load_inst_fields(data, ru )[k][SKIP_START:] # test that it works
                        
                    except:
                        continue


                    rs.append(ru)
                    for k in keys_used:
                        try:

                            v =  np.concatenate((i[k], load_inst_fields(data, ru )[k][SKIP_START:]))
                            i[k] = v
                        except :
                            print("FAILED??")
                            exit(0)
                            break
                
            print("Used", len(rs), "for ", data[r]['0']['bench'].split("/")[-1])
            if len(rs) == 1:
                return
        else:
            return
            pass
            #return
        for k in keys_used:
            print(len(i[k][SKIP_START:]),k)


        print('benchname is ', data[r]['0']['bench'])
        sel = i['totalTime'] != 0
        add = i['address'][sel]
        print("Unique addresses:", np.unique(i['address']))
        uniq_add = np.sort(np.unique(add[add < 140000000000335 ]))

        # <------------------------------------------- WAS SKIPPING BECAUSE OF PARTIAL ( the original constrains were alliviated for higher iteration time!)
        j=0
        #print("uniq insts", len(uniq_add))
        #if len(uniq_add) > 50:
        #return
        header = (str(len(uniq_add+1)) + " ") * 10 + "\n"
        out = header
        ints_1 = []
        ints_2 = []
        inst_priority = []
        import math 
        for addr in uniq_add:
            sel = i['address'] == addr # & i['totalTime']  != 0
            j+=1
            mlpWeighted = int(np.mean(i['stallCyclesMLPLoad'][sel]))
            freq = sel.sum()
            if not OLD_V4:
                mlpWeighted /= 1024
                mlp_by_mean = int(np.mean(i['stallTime'][sel]/(i['average_mlp'][sel]+1)))
                hyper = i['stallTime'][sel] - (i['totalTime'][sel] - i['stallTime'][sel])
                hyper = np.mean( np.where(hyper > 0, hyper, 0) ) 
                #max(0, hyper)
                hyper_thread_weight = int(np.mean((hyper) /(i['average_mlp'][sel]+1))) # aka 2x stall time - total time
                hyper_thread_no_mlp = int(np.mean((hyper))) # aka 2x stall time - total time
            else:
                mlp_by_mean = mlpWeighted
                hyper_thread_weight = mlpWeighted
                hyper_thread_no_mlp = mlpWeighted
            # int(np.mean(i['average_mlp'][sel])), "--->", 

            out += str(addr) + " " + str(int(np.mean(i['totalTime'][sel]))) + " " + str(int(np.mean(i['stallTime'][sel]))) + " " + str(int(mlpWeighted))  + " " + str(mlp_by_mean) + " " + str(hyper_thread_weight) + " " + str(hyper_thread_no_mlp) + " " + str(int(len(i['stallTime'][sel]))) +  " " + str(freq) + " " + str(1) + "\n"
            ints_1.append(mlp_by_mean)
            ints_2.append(int(mlp_by_mean/2))
            if mlpWeighted >= 1: 
                inst_priority.append(2**(int((mlp_by_mean)/(2))))

            else:
                inst_priority.append(mlpWeighted)

        
        bench = data[r]['0']['bench'].split("/")[-1]
        extra = ""
        extra += "_80" if EIGHT_MODE else ""
        if OLD_V4:
            extra += "_v4"
        extra += str(writes) + "-" + str(len(rs))
        writes+=1
        fname=f"{FIGS_FOLDER}/{RESULT_FOLDER}/{benchset}-{bench}{extra}"
        print("WRITE TO", fname)
        with open(fname, "w") as f:
                print(fname)
                f.write(out)
        if "syn" in benchset:
            header = (str(3) + " ") * 10 
            a = out.split("\n")
            a.insert(1, "0 0 0 0 0 0 0")
            a[0] = header
            out = "\n".join(a)
            with open(f"{FIGS_FOLDER}/{RESULT_FOLDER}/igstart{('80' if EIGHT_MODE else '')}-{benchset}-{bench}" , "w") as f:
                f.write(out)
        
        def do_compressed(values, uniq_insts):
            diff = np.diff(np.array(values))
            j = 0
            out = header
            prev_diff = 1
            for addr in uniq_insts:
                sel = i['address'] == addr 
                if prev_diff == 0:
                    continue
                prev_diff = diff[j]
                out += str(addr) + " " + str(values[j]) + "\n"
                j+=1
            return out

        with open(f"{FIGS_FOLDER}/maps_compressed_1/{bench}", "w") as f:
            f.write(do_compressed(ints_1, uniq_add))
        with open(f"{FIGS_FOLDER}/maps_compressed_2/{bench}", "w") as f:
            f.write(do_compressed(ints_2, uniq_add))
        with open(f"{FIGS_FOLDER}/compressed_3/{bench}", "w") as f:
            f.write(do_compressed(inst_priority, uniq_add)) # keep same priority

    data = load_bench_data()

    iterate_over_benches(data, simp)

text = ""
def WARMUP_TIME():
    benchset = []
    benchname = []
    time = []
    def warm(data, r):
        global text
        SKIP_START = 2000
        sel = load_inst_fields(data, r )['totalTime'] > 70
        data[r]['0']['time_to_warm'] = load_inst_fields(data, r )['start_cycle'][sel][SKIP_START] - load_inst_fields(data, r )['start_cycle'][sel][0]
        bname = data[r]['0']['bench'].split("/")[-1]
        benchset_ = data[r]['0']['benchset']
        text += benchset_ + " " + bname + " " + str(data[r]['0']['time_to_warm'] * (1/3e9)) + "\n"  # at 3GHz this is the time it took to warm
        benchset.append(benchset_)
        benchname.append(bname)
        time.append(data[r]['0']['time_to_warm'] * (1/3e9))
    iterate_over_benches(data, warm)
    print(text, benchset, benchname, time)
    benchset = np.array(benchset)
    benchname = np.array(benchname)
    time = np.array(time)

    with open("warmup.txt", "w") as f:
        f.write(text)
    # select npb_result and 1GB_GRAPH benchsets
    npb = benchset == "npb_result"
    graph = benchset == "1GB_GRAPH"
    # select bc bench, cg.D and mg.C
    bc = benchname == "bc"
    cg = benchname == "cg.D"
    mg = benchname == "mg.C"
    print(benchname, benchset, time)
    # do a bar plot, for each of the benches, where x is the name of the bennch, and Y is the workload simulated time 
    # print the lenght of each selecxtion
    print("npb e cg", len(benchname[npb & cg]))
    print("npb e mg", len(benchname[npb & mg]))
    print("graph e bc", len(benchname[graph & bc]))
    print("npb e cg", len(benchname[npb & cg]))

    print(benchname[npb & cg][0])
    print(benchname[npb & mg][0])
    print(benchname[graph & bc][0])
    plt.bar(benchname[npb & cg][0], np.mean(time[npb & cg])*1000)
    plt.bar(benchname[npb & mg][0], np.mean(time[npb & mg])*1000)
    plt.bar(benchname[graph & bc][0], np.mean(time[graph & bc])*1000)
    plt.xlabel("Benchmarks")
    plt.ylabel("Time to warmup (ms)")
    plt.title("Average simulation time consumed to warm the caches")
    plt.savefig(f"./final_data/new_gen/_warmup.png")



    


def iterate_over_benches(data, function):
    global bench_nr
    global bench_name
    
    ok_runs = 0 
    okay_names = []
    bad_runs = 0
    total_runs = len(data)
    last_error = None
    for r in data:
        if '0' not in data[r].keys() or '80' not in data[r].keys(): # <---------
            pass
            #print("Skipped run", list(data[r].values())[0]['benchnr'])
            #pass
            #continue

        try:
            bench_nr = data[r]['0']['benchnr']
            bench_name = data[r]['0']['bench'].split("/")[-1]
        except:
            print("Skipped run", list(data[r].values())[0]['benchnr'])
            continue
        try:
            function(data, r)
            ok_runs += 1
            okay_names.append(bench_name)

        except Exception as e:
            bad_runs += 1
            
            if last_error and isinstance(e, type(last_error)):
                print(f"ITERATE FAILED {str(e)} x {bad_runs}", end='\r')
            else:
                last_error = e
                # print stack trace if its not FileNotFoundError
                print(f"ITERATE FAILED {str(e)}", end='\r')
                if not isinstance(e, FileNotFoundError):
                    import traceback
                    import sys
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                    print(f'ITERATE_FAILED {"".join(lines)}')
                else:
                    print("ITERATE_FAILED Error", e)
                print(f"---  {str(last_error)} x {bad_runs} ({ok_runs+bad_runs}/{total_runs})", end='\r')
                last_error = e
            continue
    print(f"ITERATE ENDED, ok runs: {ok_runs}, bad runs: {bad_runs}, total: {ok_runs+bad_runs}")
    print('OKAY_NAMES', okay_names)

def varity(data,r):
    i = load_inst_fields(data, r)
    ii = load_inst_fields(data, r, '80')


    if(not np.all(i['stallTime'] < 1000 )):
     failed_values = np.where(i['stallTime'] >= 1000)
     print('ded', 'stallTime',data[r]['0']['bench'].split("/")[-1], data[r]['0']['benchnr'], len(i['stallTime'][failed_values]))


    sel = i['L3MLP_load_at_middle'] != 0
    if( not np.all(i['L3stallTime'][sel] < 1000)):
     failed_values = np.where(i['L3stallTime'][sel] >= 1000)
     print('ded', "stallTime",data[r]['0']['bench'].split("/")[-1], data[r]['0']['benchnr'], len(i['L3stallTime'][failed_values]))

    if( not np.all(i['stallCyclesMLPLoad'] < 1000*64)):
     failed_values = np.where(i['stallCyclesMLPLoad'] >= 1000*64)
     print('ded', "stallCyclesMLPLoad",data[r]['0']['bench'].split("/")[-1], data[r]['0']['benchnr'], len(i['stallCyclesMLPLoad'][failed_values]))

    if( not np.all(i['L3stallCyclesMLPLoad'][sel] < 1000*64)):
     failed_values = np.where(i['L3stallCyclesMLPLoad'][sel] >= 1000*64)
     print('ded',  "L3stallMLP", data[r]['0']['bench'].split("/")[-1], data[r]['0']['benchnr'], len(i['L3stallCyclesMLPLoad'][failed_values]))
        



runs_with_weird_stuff = 0
import os 
AGGREGATE = "aggregate_data"
GLOBAL = "global_stat"
INST = "instruction_data"

average_window_size = 1
cached_fields = {}
RUN_DATA_FOLDER="/mnt/nas/inesc/ist196723/osdi26/v3/results_gem5"

FIGS_FOLDER="/mnt/nas/inesc/ist196723/osdi26/v3/final_data"

FIGS_FOLDER="/mnt/nas/inesc/ist196723/osdi26/final_data"
RUN_DATA_FOLDER="/mnt/nas/inesc/ist196723/osdi26/sad_gem5/results_gem5"
RUN_DATA_FOLDER="/mnt/nas/inesc/ist196723/osdi26/results_gem5"


# for obtaining a and b in soar
RUN_DATA_FOLDER="/mnt/nas/inesc/ist196723/osdi26/v4/results_gem5"
#RUN_DATA_FOLDER="/mnt/nas/inesc/ist196723/osdi26/v5MIRAGE/results_gem5"

RUN_DATA_FOLDER="/mnt/nas/inesc/ist196723/osdi26/results_gem5"


import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler
from scipy.optimize import differential_evolution, minimize


import numpy as np
import os
import glob

all_slowdowns = np.zeros(10000)
#all_costs = 

#def get_all(data,r):


vectors = {}
def plot_my_soar():
    global RUN_DATA_FOLDER
    global run_meta
    #RUN_DATA_FOLDER="/mnt/nas/inesc/ist196723/osdi26/v5MIRAGE/results_gem5"
    #run_meta=f"{RUN_DATA_FOLDER}/gem5_pids.txt"
    print("plotting my soar")
    data = load_bench_data()
    
    iterate_over_benches(data, my_soar)
    print('Fitting...')
    for key, lst in vectors.items():
        if key == 'selections':
            continue
        try:
            if key == 'actual_slowdown': 
                continue
            for i in range(len(lst)):
                lst[i] =  np.array(lst[i])
            #vectors[key] = np.array(vectors[key])
        except Exception as e:
            print(f"Failed to convert {key} to numpy array: {e}", vectors[key])
            continue
    for k in vectors:
        plt.figure()
        plt.title("Accumulated instruction costs by " + k)
        plt.xlabel("Actual slowdown")
        plt.ylabel("Accumulated instruction costs " + k)
        #print(len(vectors['soar_slowdown']), len(vectors['soarMetric']), len(vectors['soarMetric5050']), len(vectors['soarMetric8020']), len(vectors['soarMetric2080']))
        from scipy.stats.mstats import winsorize
        #vectors['actual_slowdown'] = winsorize(vectors['actual_slowdown'], limits=[0.01, 0.01])
        

        vu = vectors[k]
        vu = winsorize(np.array(vectors[k]), limits=[0.01, 0.01])
        plt.scatter(vectors['soar_slowdown'], vu, s=2, alpha=0.3, color='blue')
        #plt.scatter(vectors['soar_slowdown'], vectors['soarMetric5050'], s=2, alpha=0.3, color='green')
        #plt.scatter(vectors['soar_slowdown'], vectors['soarMetric8020'], s=2, alpha=0.3, color='red')
        #plt.scatter(vectors['soar_slowdown'], vectors['soarMetric2080'], s=2, alpha=0.3, color='yellow')
        plt.savefig(f"{FIGS_FOLDER}/new_gen/soar_inst_vs_soar_all_{k}.png")
        plt.close()


    exit(0)
    
    plot_soar_results('all')
    
def plot_soar_results(bench):
    #0.148, 0.146 
    # 38% error..
    vectors['actual_slowdown'] = np.array(vectors['actual_slowdown'])
    for mlp in ['L3MLP_load_at_middle', 'L3MLP_load_at_start', 'L3MLP_load_at_end']:
        fitted, a, b, rmse = obtain_soar_inst(vectors['selections'], vectors[mlp], vectors['L3stallTime'],vectors['totalTime'], vectors['actual_slowdown'])
        print("A,B",a,b)
        from scipy.stats.mstats import winsorize
        #vectors['actual_slowdown'] = winsorize(vectors['actual_slowdown'], limits=[0.01, 0.01])
        #vectors['L3stallTime'] = winsorize([ np.array(n) for n in vectors['L3stallTime']], limits=[0.01, 0.01])
        plt.figure()
        plt.title(f"Accumulated instruction costs by w/Soar ({mlp})")
        plt.xlabel("Actual slowdown")
        plt.ylabel("Accumulated instruction costs")
        # (fitted*np.array([ np.sum(n) for n in vectors['L3stallTime']]))/vectors['fast_cycles'],
        plt.scatter(vectors['actual_slowdown'], fitted, s=2, alpha=0.3)
        ax2 = plt.twinx()
        ax2.scatter(vectors['actual_slowdown'], vectors['diff_stalls'], s=2, alpha=0.3, color='red')
        plt.savefig(f"{FIGS_FOLDER}/new_gen/v5NICE_{rmse}_{bench}_{mlp}.png")
        plt.close()
    #soar_metric = i['stallTime'][sel] /  ( i['L3MLP_load_at_middle'][sel] * b  + a * i['totalTime'][sel] ) 
    #total_cost = np.sum(soar_metric)

def my_soar(data,r):   # CHANGE TO NP MEAN
    i = load_inst_fields(data, r)
    g0 = load_global_fields(data, r)
    using_real_slow = False
    try:
        print(g0['currentCycle'])
    except:
        bench = data[r]['0']['bench'].split("/")[-1]
        print(bench, "has no cycle'?")
        raise Exception("has no cycle!")
    
    if using_real_slow:
        last_idx = get_last_idx_of_smallest_vector(g80['currentCycle'],g0['currentCycle'])
        i80 = load_inst_fields(data, r, '80')
        g80 = load_global_fields(data, r, '80')
        i80 = load_inst_fields(data,r, "80")
    else:
        last_idx = len( g0['currentCycle'])-1
    print("LLLLLLLLLLLLLLAST", last_idx)
    #if len(g80['currentCycle']) < 500  or len(g0['currentCycle']) <500 :
    i = load_inst_fields(data, r)
    SKIP_START = 1000
    MAX_ITER=10000
    if last_idx < SKIP_START:
        return
    if last_idx > MAX_ITER:
        step = int(last_idx/MAX_ITER)
    else:
        step = 1
    print(step)
    if(last_idx == 0):
        return
    
    print("RUN", last_idx, step)
    for cycle_nr in range(SKIP_START,last_idx,step): # ignore the first
        #print("cycooooo")
        #print(cycle_nr, step, last_idx, "OOOO")
        current_cycle = g0['currentCycle'][cycle_nr] 
        previous_cycle = g0['currentCycle'][cycle_nr-1]
        #print("triiiilii")
        WINDOW = 0
        next_cycle = g0['currentCycle'][cycle_nr+WINDOW]
        mlp = 'average_mlp' # 'L3MLP_load_at_middle'
        sel = (i[mlp] > 0) & (i['start_cycle'] < current_cycle) & (previous_cycle < i['start_cycle']) & (i['totalTime'] > 60)
        #for k in [ 'totalMLPStalledCyclesSummed', 'totalMLPStalledCycles_D_TimeSummed']: #,'totalMLPStalledCycles_D_TimeSummed', 'totalMLPStalledCyclesSummed', 'totalMLPStalledCyclesSummed']:
        if np.sum(sel)  < 5:
            #print(np.sum(sel), "SUMMM")
            continue
            pass
            #continue
        #print("triiiilii")
        vectors.setdefault('MLPstallTime', []).append(np.sum(i['stallCyclesMLPLoad'][sel]))               # CHANGE TO NP MEAN
        if using_real_slow:
            sel80 = (i80[mlp] > 0) & (i80['start_cycle'] < current_cycle) & (previous_cycle < i80['start_cycle']) & (i80['totalTime'] > 60)
            diff = np.sum(np.subtract(np.sum(i80['L3stallTime'][sel80]) , np.sum(i['L3stallTime'][sel]) ,dtype=np.int64 ))
        #diff = np.sum((i['L3stallTime'][sel]))
        #diff = np.sum(sel)
        #print("LEN OF SEL", np.sum(sel), data[r]['0']['bench'].split("/")[-1])
            actual_slowdown = (np.subtract(g80['currentCycle'][cycle_nr+WINDOW] , g0['currentCycle'][cycle_nr+WINDOW], dtype=np.int64)) # /g0['currentCycle'][cycle_nr]
        #print("triiiilii")
        fast_cycles = g0['currentCycle'][cycle_nr]
        #print("trololo")

        aol = g0['cyclesWithMemrequests'][cycle_nr]/g0['commitedLoads'][cycle_nr] 
        aol = np.where(g0['commitedLoads'][cycle_nr] == 0, 0, aol) 
        #aol = g0['stalledCycles'][cycle_nr]/g0['currentCycle'][cycle_nr]
        a = 1.0155768028621026
        b = -0.2562029379967975
        soar_slowdown =  (g0['stalledCycles'][cycle_nr]/g0['currentCycle'][cycle_nr]) * 1/(a + b/aol)
        vectors.setdefault('soar_slowdown', []).append(soar_slowdown)
        vectors.setdefault('llc_count', []).append(len(i['totalTime'][sel]))
        #return
        t = i['totalTime'][sel]
        vectors.setdefault('totalTime', []).append(np.sum(t))               # CHANGE TO NP MEAN
        s = i['stallTime'][sel]
        vectors.setdefault('stallTime', []).append(np.sum(s))
        m =  s/( i['average_mlp'][sel] * b  + a * t ) 
        vectors.setdefault('soarMetric', []).append((np.sum(m)))
        m = s/( i['average_mlp'][sel] * 0.5  + 0.5 * t ) 
        vectors.setdefault('soarMetric5050', []).append((np.sum(m)))
        m = s/( i['average_mlp'][sel] * 0.8  + 0.2 * t ) 
        vectors.setdefault('soarMetric8020', []).append((np.sum(m)))
        m = s/( i['average_mlp'][sel] * 0.2  + 0.8 * t ) 
        vectors.setdefault('soarMetric2080', []).append((np.sum(m)))
        m = s/( i['average_mlp'][sel] * 0  + 1 * t ) 

        vectors.setdefault('soarMetric01', []).append((np.sum(m)))
        m = s/( i['average_mlp'][sel] * 1  + 0 * t ) 
        vectors.setdefault('soarMetric10', []).append((np.sum(m)))

        vectors.setdefault('percentage total time', []).append((np.sum(i['stallTime'][sel]/i['totalTime'][sel])))
        #vectors.setdefault('totalMLPStalledCyclesSummed', []).append((g0['totalStalledCyclesSummed']))
        #vectors.setdefault('totalMLPStalledCycles_D_TimeSummed', []).append((g0['totalMLPStalledCycles_D_TimeSummed']))
        #vectors.setdefault('totalMLPStalledCyclesSummed', []).append((g0['totalMLPStalledCyclesSummed']))
        

        
        #vectors.setdefault('stalledCycles', []).append(np.mean(i['stalledCycles'][sel]))


        ##vectors.setdefault('actual_slowdown', []).append(actual_slowdown)
        #for mlp in ['L3MLP_load_at_middle', 'L3MLP_load_at_start', 'L3MLP_load_at_end']:
        #vectors.setdefault(mlp, []).append(i[mlp][sel])
				
        #vectors.setdefault('diff_stalls', []).append(diff)
        #vectors.setdefault('L3stallTime', []).append(np.sum(i['L3stallTime'][sel]))
        #vectors.setdefault('selections', []).append(sel)
        #vectors.setdefault('soarMetric2080', []).append((np.sum(m)))
        #vectors.setdefault('totalMLPStalledCyclesSummed', []).append((g0['totalStalledCyclesSummed'][cycle_nr]))
        #vectors.setdefault('totalMLPStalledCycles_D_TimeSummed', []).append((g0['totalMLPStalledCycles_D_TimeSummed'][cycle_nr]))
        #vectors.setdefault('totalMLPStalledCyclesSummed', []).append((g0['totalMLPStalledCyclesSummed'][cycle_nr]))
    		

def my_soar_aggregate(data, r):
    """
    Similar to my_soar but uses aggregate metrics instead of per-instruction data.
    
    Key differences from my_soar:
    - Uses load_aggregate_fields() instead of load_inst_fields()
    - Works with aggregated instruction statistics (count-weighted metrics)
    - Computes weighted averages for MLP metrics instead of per-instruction values
    - Stores results with 'agg_' prefix to distinguish from instruction-level data
    - More memory efficient for large datasets with many instructions
    
    Analyzes performance using aggregated statistics over time windows to correlate
    slowdown with aggregate stall times and MLP characteristics.
    """
    # Load aggregate data for both tiers
    ag0 = load_aggregate_fields(data, r, '0')
    ag80 = load_aggregate_fields(data, r, '80')
    
    # Load global fields for cycle information
    g0 = load_global_fields(data, r)
    g80 = load_global_fields(data, r, '80')
    
    last_idx = get_last_idx_of_smallest_vector(g80['currentCycle'], g0['currentCycle'])
    
    for cycle_nr in range(1, last_idx):  # ignore the first
        current_cycle = g0['currentCycle'][cycle_nr]
        previous_cycle = g0['currentCycle'][cycle_nr-1]
        WINDOW = 0
        
        # Filter aggregate data for instructions with L3 MLP and sufficient execution time
        # Using aggregate fields: count, L3MLP_load_at_middle, totalTime, etc.
        sel = (ag0['L3MLP_load_at_middle'] > 0) & (ag0['count'] > 0) & (ag0['totalTime'] > 60)
        
        # Calculate aggregate metrics
        selected_count = np.sum(ag0['count'][sel])
        
        if selected_count < 20:
            continue
            
        print("AGGREGATE COUNT", selected_count, data[r]['0']['bench'].split("/")[-1])
        
        # Calculate actual slowdown between tiers
        actual_slowdown = np.subtract(g80['currentCycle'][cycle_nr+WINDOW], 
                                     g0['currentCycle'][cycle_nr+WINDOW], 
                                     dtype=np.int64)
        
        # Aggregate stall time difference
        agg_stall_diff = np.sum(ag80['L3stallTime'][sel] * ag80['count'][sel]) - \
                         np.sum(ag0['L3stallTime'][sel] * ag0['count'][sel])
        
        fast_cycles = g0['currentCycle'][cycle_nr]
        
        # Store aggregate metrics
        vectors.setdefault('fast_cycles', []).append(fast_cycles)
        vectors.setdefault('actual_slowdown', []).append(actual_slowdown)
        
        # Store aggregate MLP metrics (weighted by count)
        for mlp in ['L3MLP_load_at_middle', 'L3MLP_load_at_end', 'MLP_load_at_end']:
            if mlp in aggregate_types:
                weighted_mlp = np.sum(ag0[mlp][sel] * ag0['count'][sel]) / selected_count if selected_count > 0 else 0
                vectors.setdefault(f'agg_{mlp}', []).append(weighted_mlp)
        
        # Store aggregate stall and time metrics
        vectors.setdefault('agg_diff_stalls', []).append(agg_stall_diff)
        vectors.setdefault('agg_totalTime', []).append(np.sum(ag0['totalTime'][sel] * ag0['count'][sel]))
        vectors.setdefault('agg_L3stallTime', []).append(np.sum(ag0['L3stallTime'][sel] * ag0['count'][sel]))
        vectors.setdefault('agg_stallTime', []).append(np.sum(ag0['stallTime'][sel] * ag0['count'][sel]))
        vectors.setdefault('agg_count', []).append(selected_count)

def plot_my_soar_aggregate():
    """
    Plot aggregate SOAR results using aggregate metrics.
    """
    print("plotting my soar aggregate")
    iterate_over_benches(data, my_soar_aggregate)
    print('Converting aggregate data...')
    
    # Convert aggregate vectors to numpy arrays
    vectors['actual_slowdown'] = np.array(vectors['actual_slowdown'])
    for key in ['agg_diff_stalls', 'agg_totalTime', 'agg_L3stallTime', 'agg_stallTime', 'agg_count', 'fast_cycles']:
        if key in vectors:
            vectors[key] = np.array(vectors[key])
    
    # Convert MLP aggregate vectors
    for mlp in ['L3MLP_load_at_middle', 'L3MLP_load_at_end', 'MLP_load_at_end']:
        agg_key = f'agg_{mlp}'
        if agg_key in vectors:
            vectors[agg_key] = np.array(vectors[agg_key])
    
    # Plot aggregate results
    plt.figure(figsize=(10, 6))
    plt.title("Aggregate Slowdown vs Stall Time")
    plt.xlabel("Actual slowdown (cycles)")
    plt.ylabel("Aggregate L3 Stall Time")
    plt.scatter(vectors['actual_slowdown'], vectors['agg_L3stallTime'], s=2, alpha=0.3)
    plt.savefig(f"{FIGS_FOLDER}/new_gen/AGGREGATE_slowdown_vs_stalls.png")
    plt.close()
    
    # Plot aggregate MLP metrics
    for mlp in ['L3MLP_load_at_middle', 'L3MLP_load_at_end', 'MLP_load_at_end']:
        agg_key = f'agg_{mlp}'
        if agg_key not in vectors:
            continue
            
        plt.figure(figsize=(10, 6))
        plt.title(f"Aggregate {mlp} vs Slowdown")
        plt.xlabel("Actual slowdown (cycles)")
        plt.ylabel(f"Weighted Average {mlp}")
        plt.scatter(vectors['actual_slowdown'], vectors[agg_key], s=2, alpha=0.3, label=mlp)
        
        # Add secondary axis for stall difference
        ax2 = plt.twinx()
        ax2.scatter(vectors['actual_slowdown'], vectors['agg_diff_stalls'], s=2, alpha=0.3, color='red', label='Stall Diff')
        ax2.set_ylabel("Aggregate Stall Difference", color='red')
        
        plt.legend(loc='upper left')
        ax2.legend(loc='upper right')
        plt.savefig(f"{FIGS_FOLDER}/new_gen/AGGREGATE_{mlp}.png")
        plt.close()
    
    print(f"Aggregate analysis complete. Processed {len(vectors['actual_slowdown'])} data points.")

def conv():
            for key, lst in vectors.items():
                if key == 'selections':
                    continue
                try:
                    if key == 'actual_slowdown': 
                        continue
                    for i in range(len(lst)):
                        lst[i] =  np.array(lst[i])
                    #vectors[key] = np.array(vectors[key])
                except Exception as e:
                    print(f"Failed to convert {key} to numpy array: {e}", vectors[key])
                    continue


def single_my_soar(data,r):
    global vectors
    vectors = {}
    bench_name = data[r]['0']['bench'].split("/")[-1]
    bench_nr = data[r]['0']['benchnr']
    my_soar(data,r)
    conv()
    plot_soar_results(f'FINAL_{bench_name}_{bench_nr}')
    
    
def iter_single_my_soar():
    global RUN_DATA_FOLDER
    global run_meta
    RUN_DATA_FOLDER="/mnt/nas/inesc/ist196723/osdi26/results_gem5"
    run_meta=f"{RUN_DATA_FOLDER}/gem5_pids.txt"
    data = load_bench_data()
    iterate_over_benches(data, single_my_soar)


def plot_sampling_cost():
    d = {
        # 839234342140 <------------ tsc
        # total SAMns 839234342140 10282 <- why total time so small???

        # 1490523994 totalSAMns 839234342140   
        'MEMTIS (no CPU cap)' :            [      1291106, ],# 363012000               2509685216000
        # 825483551488 total CPUns

        
        #   1030150904 
        # 837137431530

        # 1030150904 totalSAMns 837137431530      <-- 
        # 837137431530 894033138
        'MEMTIS (default CPU cap)' :            [ 1287857], #  366640000    cpu usage  4160968320000
        # 1428674964 total CPUns

        

        # 2167801116 837793533518   <-- time processing vs time exec

        # totalSAMns 837793533518 21667
        'AsMem - Compressed Array (no CPU cap)': [1324427] ,  #                         158017923200                      #  833010627020
        # 833010627020 total CPUns
        'AsMem - Hashtable (no CPU cap)': 1
    }

    samples_per_cycle = {
           'MEMTIS (no CPU cap)' :            [   1030150904/1232484    ],# 363012000               2509685216000
        'MEMTIS (default CPU cap)' :            [ 1490523994/1014182 ], #  366640000    cpu usage  4160968320000
        'AsMem - Compressed Array (no CPU cap)': [2167801116/875723 ] ,  #                         158017923200                      #  833010627020
        'AsMem - Hashtable (no CPU cap)': [       2028373070/862294]
        
        
        
    }
    sample_ratio = {

        # 902172825 total runtime  of others
                                                  
        'MEMTIS (no CPU cap)' :            [       1014182, ],# 363012000               2509685216000
        'MEMTIS (default CPU cap)' :            [  1232484], #  366640000    cpu usage  4160968320000
        'AsMem - Compressed Array (no CPU cap)': [          875723] ,  #                         158017923200                      #  833010627020
        'AsMem - Hashtable (no CPU cap)': [         37829,  862294] #  total spend computing  2028373070

        # u64                                               922793 1318656
        #total all 839938150430
        # 1000000000000 # execution time  of hashtable
        #   sample        total 
        #  3432718152 843376061096
        
    }
    

    normalized = {}
    for k in d:
        normalized[k]   = d[k]/d['MEMTIS (no CPU cap)']
    
    plt.figure()
    plt.title("Number of Samples Processed")
    plt.xlabel("Tiering System")
    plt.ylabel("Number of Samples Processed")
    d = sample_ratio
    plt.bar(range(len(d)), list(d.values()))
    plt.xticks(range(len(d)), list(d.keys()))
    plt.savefig(f"{FIGS_FOLDER}/real_data/systems/sampling_cost.png")
    plt.close()

    plt.figure()
    plt.title("Number of Samples Processed")
    plt.xlabel("Tiering System")
    plt.ylabel("Number of Samples Processed")
    d = sample_ratio
    plt.bar(range(len(d)), list(d.values()))
    plt.xticks(range(len(d)), list(d.keys()))
    plt.savefig(f"{FIGS_FOLDER}/real_data/systems/sampling_cost.png")
    plt.close()
    


def plot_hit_ratio():
    folder=f"{NAS}/osdi26/real_data/clean_try/real_data/batch"
    runs = glob.glob(f"{folder}/mcf_s_*2000-*")


    for run in sorted(runs):
        stats=folder +"/"+"STATS-" + os.path.basename(run)
        log_file = stats 
        cmd = f"awk '/dram_hits/ {{print $7}}' {log_file}"
        print(cmd)
        with os.popen(cmd) as pipe:
            raw_text = pipe.read()
            #print(raw_text)
            #continue
            dram_text = raw_text

            try:
                pass
               # dram_hits = int(raw_text.split("\n")[0]) #np.loadtxt(pipe, dtype=int)
            except:
                print('error', raw_text)
                continue
            #print(dram_hits)
        cmd = f"awk '/dram_hits/ {{print $12}}' {log_file}"
        with os.popen(cmd) as pipe:
            raw_text = pipe.read()
            slow_text = raw_text
            try:
                #slow_hits = int(raw_text.split("\n")[0]) #np.loadtxt(pipe, dtype=int)
                pass
            except:
                print('error', raw_text)
                continue
            #print(slow_hits)
        print("-->",dram_text, slow_text, "<---")
        continue
        if slow_hits == 0:
            continue
        nat_run[run] = dram_hits/slow_hits # hit ratio

        print(f"HIT RATIO {run}: {dram_hits/slow_hits}")

    plt.figure(figsize=(50,10))
    plt.title("Hit Ratio")
    plt.xlabel("Run")
    plt.ylabel("Hit Ratio")
    plt.bar(range(len(nat_run)), list(nat_run.values()))
    plt.xticks(range(len(nat_run)), list(nat_run.keys()))
    plt.savefig(f"{FIGS_FOLDER}/real_data/systems/hit_ratio.png")
    plt.close()
    exit(0)

#plot_hit_ratio()
#exit(0)
    
def get_cdf_array(data, normalizeByTotal=False):
                sorted_data = np.sort(data)
                n = len(sorted_data)
                if normalizeByTotal:
                    cdf = np.cumsum(sorted_data)
                    cdf = cdf/ np.sum(sorted_data)
                    # replace NaNs with 0
                    cdf = np.nan_to_num(cdf)
                else:
                    cdf = np.arange(1, n+1) / n
                return sorted_data, cdf #migrations_cdf
human = collections.defaultdict(lambda: lambda x: x, {
    'stallTime': 'Stall cycles',
    'mcf' : 'Speccpu\'s  605.mcf_s',
})
def get_bname(data,r):
    return data[r]['0']['bench'].split('/')[-1]
def get_bnr(data,r):
    return data[r]['0']['benchnr']
def do_cdf_of_instructions(data,r):
    ag = load_aggregate_fields(data,r)
    inst_values = [] # total
    inst_avg_metric = [] # avg
    metric = 'stallTime'
    total_samples = ag['count'].sum()
    total_stall_time = np.sum(ag[metric]*ag['count'])
    uniq_insts = np.unique(ag['address'])
    inst_both = []
    for n in uniq_insts:
        mask = (ag['address'] == n) & (ag['count'] > 0) ###################### REMOVE STORES! 
        inst_value = np.sum(ag[metric][mask] * ag['count'][mask]) 
        avg = np.sum(ag[metric][mask]) /np.sum( ag['count'][mask]) 
        inst_avg_metric.append(avg)
        inst_values.append(inst_value)
        inst_both.append((inst_value, avg))

    mask = (ag['address'] > 0) & (ag['count'] > 0) ###################### REMOVE STORES! 
    mask_greater_than_2000 = (ag[metric][mask]/ag['count'][mask]) > 2000
    stall_time_greater_than_2000 = np.sum(mask_greater_than_2000)
    #print(f"Number of times stall time is greater than 2000 in {get_bname(data,r)}_{get_bnr(data,r)}: {stall_time_greater_than_2000}")
    if stall_time_greater_than_2000:
        print(f"WARNING: {get_bname(data,r)}_{get_bnr(data,r)} has stall times greater than 2000 ({stall_time_greater_than_2000} times). Its average of ", np.mean(ag[metric][mask]/ag['count'][mask]))

    #print(inst_values)
    #bandwidth_sorted = np.sort(inst_values)
    #n = len(bandwidth_sorted)
    #migrations_cdf = np.cumsum(bandwidth_sorted) / total_stall_time

    x, contrib_total_lat = get_cdf_array(inst_values, normalizeByTotal=True)

    sorted_data = sorted(inst_both, key=lambda x: x[1])
    n = len(sorted_data)
    #if normalizeByTotal:
    cdf = np.cumsum([ x[0] for x in sorted_data])
    cdf = cdf/ np.sum([ x[0] for x in sorted_data])
    # replace NaNs with 0
    #cdf = np.nan_to_num(cdf)
    #cdf = np.arange(1, n+1) / n
    #x, contrib_total_lat = get_cdf_array(ag[metric], normalizeByTotal=True)
    # most of the latency comes from what nr of stall cycles??
    plt.figure()
    plt.title("CDF of Instructions")
    plt.xlabel(human[metric])
    plt.ylabel("CDF")
    plt.plot([ x[1] for x in sorted_data], cdf ) # x[0] for x in sorted_data])
    #plt.plot(inst_avg_metric,contrib_total_lat)
    plt.savefig(f"{FIGS_FOLDER}/gen/insts/cdf/{get_bname(data,r)}_{get_bnr(data,r)}.png")
    plt.close()


def non_l3_inst(i, inverse=False):
    if inverse: 
        return (i['L3MLP_load_at_middle'] != 0)  | (i['L3MLP_load_at_middle'] != 0)
    return (i['L3MLP_load_at_middle'] == 0)  & (i['L3MLP_load_at_middle'] == 0)
    
found_synthetics = 1000
def do_cdf_mlp(data, r):
    # plot
    i = load_inst_fields(data, r)
    i80 = load_inst_fields(data, r, '80')
    # Is there a difference between the MLP found in higher latency memory devices? (likely to increase!)
    # Is there a stop/start behaviour? 
    #       single access pattern i.e. a low MLP request, then MLP keeps increasing and stabilizes
    #       combined patterns i.e. ?

    # color under the line is the 
    all_mlp_fields = ['MLP_store_at_start', 
                     'MLP_store_at_start', 
                     'MLP_load_at_start',
                     'MLP_load_at_end',

    ]
    hit_selector = non_l3_inst(i) 
    l3_selector = non_l3_inst(i, inverse=True)  
    l3_mlp_fields = [
                     'L3MLP_load_at_middle',
                     'L3MLP_store_at_start',
                     'L3MLP_load_at_start',
                     'L3MLP_store_at_middle',
                     ]
    
    #fig, axs = plt.subplots(6, 6, figsize=(15, 15))
    iii=0
    fig, axs = plt.subplots(3, 3, figsize=(15, 15))
    axes = axs.flat
    for fields, tier_sel,tier_name in ((all_mlp_fields,hit_selector, 'Hits'), (l3_mlp_fields, l3_selector ,'LLC misses'), 
                                         (l3_mlp_fields+ all_mlp_fields, l3_selector | hit_selector, "All" ) 
                                       ):
                                    
        for atype_sel, access_type  in ((i['isLoad'] == 0, 'Store'), (i['isLoad'] == 1, 'Load'), (( ( i['isLoad'] == 0) | (i['isLoad'] ==1))  , 'ALL ALL')):
            # pass 
            sel = np.intersect1d(np.where(tier_sel),np.where(atype_sel))
            #plt.figure()
            for f in fields:
                d = i[f][sel]
                # normalize by the total MLP or the nr of data points (total MLP does not make sense. aggregate only for stall cycles for instance)
                x,y = get_cdf_array(d, normalizeByTotal=False)
                
                field_type = " ".join(f.split("_")[1:])
                line_style  = "--" if "L3" in f else "-"
                #do a different line type according to weather the field has L3 on its name or not, have the same color for each field that has the sample 
                axes[iii].plot(x,y, label=field_type, linestyle=line_style)
                ##jjif any(fld in field.split("_") if fld == "L3"):
                #el#jse:
                #    plt.plot(x,y, label=f, linestyle='-')
            #plt.xlim(0, 4.0)
            #plt.ylim(0, 1.0)
            #plt.plot(migrations_cdf,bandwidth_sorted, label="CDF")
            #bench = data[r]['0']['bench'].split("/")[-1]
            #print(data[r])
            bench = data[r]['0']['bench'].split("/")[-1]
            benchnr = data[r]['0']['benchnr']
            axes[iii].set_title("CDF of MLP for " + bench )
            axes[iii].legend()
            if "synth" in bench:
                found_synthetics += 1

            axes[iii].set_ylabel("CDF")
            axes[iii].set_xlabel("MLP")
            iii+=1
    os.makedirs(f"{FIGS_FOLDER}/gen/benchmarks/_MLP_CDFS/{bench}", exist_ok=True)
    pid = data[r]['0']['pid']
    plt.savefig(f"{FIGS_FOLDER}/gen/benchmarks/_MLP_CDFS/{bench}/_mlp_cdf_{benchnr}.png")
    plt.close()
            



    
def plot_migrations_overtime():

    folder=f"{NAS}/osdi26/real_data/clean_try/real_data/batch"

    runs = glob.glob(f"{folder}/mcf**MEMTIS*")
    bench = "mcf"
    normal= folder+"/mcf_s_base.NOavxprota-m64-MEMTIS-NORMAL-2000-1759761341"
    mais_mais = folder+"/mcf_s_base.NOavxprota-m64-MEMTIS-MAIS_MAIS-3--2000-1759778315"

    print(len(runs), "dead runs")
    def get_mig_data(run):
        stats=folder +"/"+"STATS-" + os.path.basename(run)
        #stats=folder+"/"+"STATS-" + run
        log_file = stats 
        cmd = f"awk '/pgmigrate_success/ {{print $NF}}' {log_file}"
        with os.popen(cmd) as pipe:
            migrations = np.loadtxt(pipe, dtype=int)
        migrations -= migrations[0]
        t = np.arange(0, len(migrations) * 250, 250)
        return t, migrations

    t_normal, migrations_normal = get_mig_data(normal)
    t_mais_mais, migrations_mais_mais = get_mig_data(mais_mais)
    print(migrations_normal[-1],"n")
    print(migrations_mais_mais[-1],"n")

    #migrations_cdf_extended = np.append(migrations_cdf, 1.0)  # 100% of data below 4 GB/s
    page_size = 4096
    plt.figure(figsize=(10,10))

    for (migrations,name) in [(migrations_normal,"Memtis"), (migrations_mais_mais,"AsMem")]:
        bandwidth = np.diff(migrations)*page_size/250/(1024*1024)
        bandwidth_sorted = np.sort(bandwidth)
        n = len(bandwidth_sorted)
        cdf = np.arange(1, n+1) / n
        migrations_cdf = np.cumsum(bandwidth_sorted)/cdf
        plt.plot(bandwidth_sorted,migrations_cdf, label=name)
        break
    plt.xlim(0, 4.0)
    plt.ylim(0, 1.0)
    #plt.plot(migrations_cdf,bandwidth_sorted, label="CDF")
    plt.title("CDF of migrations bandwidth for " + bench )
    plt.ylabel("CDF")
    plt.xlabel("Bandwidth (GB/s)")
    plt.savefig(f"{FIGS_FOLDER}/real_data/" + "combined_bw_cdf.png")
    plt.close()
    #exit(0)
    #return

    def plot_migrations_over_timeeee(t, migrations, title, name):
        color = "blue" if "NORMAL" in run else "orange"
        plt.plot(t, migrations, label="Migrations per 250ms", c=color)
        plt.xlabel("Time (ms)")
        plt.ylabel("Total pages migrated")
        plt.title(title)
        #plt.ylim(0, 5e7)

    plt.figure(figsize=(10,10))
    for run in sorted(runs):
        try:
            t, migrations = get_mig_data(run)
            name = os.path.basename(run)
            if name == normal:
                name = "Memtis"
                print("found memtis")
            elif name == mais_mais:
                name = "AsMem"
                print("found asmem")
            else:
                pass
                #continue
            if migrations[-1] < 100:
                continue
            plot_migrations_over_timeeee(t, migrations, "Migrations over time for 605.mcf_s", "l")
            continue
            
            page_size = 4096
            bandwidth = np.diff(migrations)*page_size/250/(1024*1024)
            bandwidth_sorted = np.sort(bandwidth)
            n = len(bandwidth_sorted)
            cdf = np.arange(1, n+1) / n
            migrations_cdf = np.cumsum(bandwidth_sorted)/cdf
            #migrations_cdf_extended = np.append(migrations_cdf, 1.0)  # 100% of data below 4 GB/s
            plt.plot(bandwidth_sorted,migrations_cdf, label=name)
            #plt.figure(figsize=(10,10))
            #plot_migrations_over_time(t, migrations, "Total pages migrated over time for " + bench, run)
            #continue




            plt.figure(figsize=(10,10))
            page_size = 4096
            bandwidth = np.diff(migrations)*page_size/250/(1024*1024)
            plt.plot(t[:-1], bandwidth, label="Bandwidth")
            plt.title("Bandwidth tiering overhead over time for " + bench )
            plt.xlabel("Time (ms)")
            plt.ylabel("Bandwidth (GB/s)")
            plt.ylim(0, 3)
            plt.savefig(f"{FIGS_FOLDER}/real_data/" + os.path.basename(run) + "_bandwidth.png")
            plt.close()

            
            from scipy import stats
            bandwidth_sorted = np.sort(bandwidth)
            #migrations_cdf = stats.rankdata(bandwidth_sorted, method='max') / len(bandwidth)

            #bandwidth_extended = np.append(bandwidth_sorted, 4.0)
            n = len(bandwidth_sorted)
            cdf = np.arange(1, n+1) / n
            migrations_cdf = np.cumsum(bandwidth_sorted)/cdf
            #migrations_cdf_extended = np.append(migrations_cdf, 1.0)  # 100% of data below 4 GB/s

            plt.plot(bandwidth_sorted,migrations_cdf, label="CDF")
            plt.xlim(0, 4.0)
            plt.ylim(0, 1.0)
            #plt.plot(migrations_cdf,bandwidth_sorted, label="CDF")
            plt.title("CDF of migrations bandwidth for " + bench )
            plt.ylabel("CDF")
            plt.xlabel("Bandwidth (GB/s)")
            plt.savefig(f"{FIGS_FOLDER}/real_data/" + os.path.basename(run) + "_migrations_cdf.png")
            plt.close()
        except Exception as e:
            print(e)
            pass
        
    plt.savefig(f"{FIGS_FOLDER}/real_data/" + os.path.basename(run) + "_combined_OT_migrations.png")
    plt.close()
    plt.xlim(0, 4.0)
    plt.ylim(0, 1.0)
    #plt.plot(migrations_cdf,bandwidth_sorted, label="CDF")
    plt.title("CDF of migrations bandwidth for " + bench )
    plt.ylabel("CDF")
    plt.xlabel("Bandwidth (GB/s)")
    plt.savefig(f"{FIGS_FOLDER}/real_data/COMBINED_migrations_cdf.png")
    plt.close()
        #plt.savefig(f"{FIGS_FOLDER}/../real_data/plots/{b}_speedup.png")
    exit(0)
    
    

#plot_migrations_overtime()
#exit(0)


def real_parser():
    path ="/home/ist196723/nas/osdi26/real_data/numpy/"
    files = os.listdir(path)
    data = {}
    for file in files:
        bfile = os.path.basename(file) 
        if bfile == "mode" or bfile == "bin":
            # import as a numpy with strings
            data[bfile] = np.genfromtxt(path + file, dtype=str, filling_values=np.nan)
        else:
            data[bfile] =  np.genfromtxt(path + file, dtype=float, filling_values=np.nan)
    # visualize all the collected data
    for k in data.keys():
        print(k)
        print(data[k])

    systems = {
        "all_cxl": data['mode'] == "MEMTIS-numactl-0",
        "fast_baseline": data['mode'] == "MEMTIS-numactl-90000",
        "asmem": np.char.startswith(data['mode'], "MEMTIS-MAIS_MAIS"), 
        "memtis_no_mig_slow": data['mode']== "MEMTIS-NORMAL-0",
        "memtis_no_mig_fast": data['mode'] == "MEMTIS-NORMAL-90000",
        "memtis": data['mode'] == "MEMTIS-NORMAL-(?!90000|0)[0-9]+"
    }
    baseline_system = "fast_baseline"
    baseline_mig = "memtis"
    ## check where are nans

    systems_avg_time = {
    }
    systems_avg_mig = {
    }

    benches = np.unique(data['bin'])
    print("Doing averages")
    for b in benches:
        #idx = np.where(data['bin'] == b)
        
        print(b)
        systems_avg_time[b] = {}
        systems_avg_mig[b] = {}
        for name,sel  in systems.items():
            try:
                intersect = np.where((data['bin'] == b) & sel)[0]
                if len(intersect) == 0:
                    print(name, " slice is empty")
                    continue
                # remove outliers by percentile
                outliers_percentile = 10
                outliers_idx = np.where(data['time'][intersect] > np.percentile(data['time'][intersect], outliers_percentile))[0]
                intersect = np.delete(intersect, outliers_idx)
                print(name, "{:.2f}".format(np.average(data['time'][intersect])), "{:.2f}".format(np.average(data['migs'][intersect])))
                print(name, data['time'][intersect])
                systems_avg_time[b][name] = np.average(data['time'][intersect])
                if "all_cxl" in name or "fast_baseline" in name: 
                    continue
                systems_avg_mig[b][name] = np.average(data['migs'][intersect])
            except Exception as e:
                print(e)
                pass

    print("Normalizing")
    """
    for b in benches:
        for name,sel in systems.items():
            try:
                if np.isnan(systems_avg_time[b][baseline_system]) or np.isnan(systems_avg_mig[b][baseline_system]):
                    print("Skipping", b, name, "because it has nan values")
                    continue
                systems_avg_time[b][name] = systems_avg_time[b][name]/systems_avg_time[b][baseline_system]
                systems_avg_mig[b][name] = systems_avg_mig[b][name]/systems_avg_mig[b][baseline_system]
            except KeyError:
                print("Skipping", b, name, "because it is not in the dictionary")
                continue
    """
    # plot the data
    for b in benches:
        bi= b
        #for i in range(0,len(benches),10):
            ##plt.subplot(len(benches)//10,1,i//10+1)
        col_values = [
            systems_avg_time[bi][mode]
            for mode in systems_avg_time[bi].keys()
        ]
        col_values_mig = [
            systems_avg_time[bi][mode]
            for mode in systems_avg_time[bi].keys()
        ]
        col_names = [
            bi + "_" + mode
            for mode in systems_avg_time[bi].keys()
        ]
        print(len(col_names), col_names)
        print(len(col_values), col_values)
        print(len(col_values),"mig", col_values_mig)


        plt.figure(figsize=(10,10))
        plt.bar(col_names, col_values)
        # xticks 5
        plt.xticks(rotation=45)
        plt.title("Execution time for " + b)
        plt.ylabel("Time")
        plt.xlabel("Systems")
        plt.savefig(f"{FIGS_FOLDER}/../real_data/plots/{b}_speedup.png")
        plt.close()
        plt.figure(figsize=(10,10))

        col_names = [
                bi + "_" + mode 
            
            for mode in systems_avg_mig[bi].keys() if mode != "all_cxl" and mode != "fast_baseline"
        ]
        col_values_mig = [
            systems_avg_mig[bi][mode]
            for mode in systems_avg_mig[bi].keys() if mode != "all_cxl" and mode != "fast_baseline"
        ]
        plt.bar(col_names, col_values_mig)
        # xticks 5
        plt.xticks(rotation=0)
        plt.title("Migrations for " + bi)
        plt.ylabel("Migrations")
        plt.xlabel("Systems")
        plt.savefig(f"{FIGS_FOLDER}/../real_data/plots/{b}_migrations.png")
        plt.close()
    exit(0)
        
    plt.figure(figsize=(20,6))
    #for i in range(0,len(benches),10):
        ##plt.subplot(len(benches)//10,1,i//10+1)
    col_names = [
        bi + "_" + mode
        for bi in benches
        for mode in systems_avg_time[bi].keys()
    ]
    col_values = [
        systems_avg_time[bi][mode]
        for bi in benches
        for mode in systems_avg_time[bi].keys()
    ]
    print(len(col_names), col_names)
    print(len(col_values))


    plt.bar(col_names, col_values)
    # xticks 5
    plt.xticks(rotation=45)
    plt.title("Speedup")
    plt.ylabel("Speedup")
    plt.xlabel("Systems")
    plt.savefig(f"{FIGS_FOLDER}/../real_data/plots/speedup.png")
    plt.close()
    exit(0)

    plt.figure(figsize=(10,10))
    for i in range(0,len(benches),10):
        plt.subplot(len(benches)//10,1,i//10+1)
        plt.bar(list(systems_avg_mig.keys()), [systems_avg_mig[k][i] for k in systems_avg_mig.keys()])
        plt.title(benches[i])
        plt.ylabel("Migration Rate")
        plt.xlabel("Systems")
    plt.savefig(f"{FIGS_FOLDER}/../real_data/plots/migs.png")
    plt.close()
    
    
            

#real_parser()



# list all the files in RUN_DATA_FOLDER
"""
check_correctness = {}
for f in  os.listdir(RUN_DATA_FOLDER):
    if not "global_stat" in f:
        continue
    if f.split("_")[1] in check_correctness:
        print("Duplicate run!!!!!!!!!!!")
    check_correctness[f.split("_")[1]] = f
print("no duplicates found")
"""

global_learn = {
    'inputs' : [],
    'results' : [],
    
    'inputs_direct' : []

    
}
def append_dict(k,d):
    if k not in global_learn:
        global_learn[k] = []
    global_learn[k].append(d)

import numpy as np
def do_important_plots(data):
    calculate_derivates(data)
    # plot correlation of each one of the metrics inside by_instruction_all

    
    # PLOT by_interval
    for m in by_interval['metrics'].keys():
        plt.figure()
        print(by_interval['metrics'][m])

        from scipy.stats.mstats import winsorize
        try:
            by_interval['metrics'][m] = winsorize(by_interval['metrics'][m], limits=[0, 0.1])
        except:
            print("Failed to winsorize", m)
            continue
        plt.plot(by_interval['real_slowdown'], by_interval['metrics'][m])
        plt.title(m)
        plt.savefig(f'{FIGS_FOLDER}/gen/insts/AGGREGATE_{w.replace("/", "D").replace("%", "P")}_{mode}.png')
        plt.xlabel('Slow down')
        plt.ylabel('Comulated ' + m)
        plt.legend()
        plt.show()
    
    
    
    
    
    
    
    
    
    
    
    
    

    weights = ("cost_inst_MLP",
               #"cost_inst_MLP/stall", "cost_inst_LLCmiss",
    #"cost_buffer_pressure",
    #"cost_delta_time",
    #"cost_delta_l3stall",

    "cost_inst_L3MLP",
    #"cost_inst_diff_%L3MLP",
            "cost_inst_total_time",
   # 'cost_aggregate_l3mlp'   ,
   # 'cost_aggregate_mlp'     ,
   # 'cost_aggregate_time'    ,
   # 'cost_aggregate_l3stalls'           ,
   # 'cost_aggregate_stalls'            ,

"cost_inst_stalls", 
"cost_inst_L3stalls",
"cost_inst_LLCmiss",
#    'cost_inst_LLCmiss_abs',
#    'cost_inst_stall_time_abs',
#    'cost_inst_L3stall_time_abs',
#    'cost_inst_L3MLP_abs',
#    'cost_inst_MLP_abs'
                        "cost_inst_diff_stall",
                        "cost_inst_diff_total",

    )
    print(len(by_instruction_all), "length of by_instruction_all")
    """
    indexes_that_fit_l3 = []
    w = "const_inst_L3MLP"
    all_data_real = []
    all_data_weight = []
    for i in range(0, len(by_instruction_all)):
        all_data_real.append(by_instruction_all[i]['real_slowdown'])
        all_data_weight.append(by_instruction_all[i][w])
    all_data_real = np.array(all_data_real)
    all_data_weight = np.array(all_data_weight)
    """
    #indexes = np.where(all_data_real < np.percentile(all_data_real, 90))
    #all_data_real = all_data_real[indexes]
    #all_data_weight = all_data_weight[indexes]
    #indexes_that_fit_l3.append(indexes)


    for w in weights:
        try:
            print("WEIGHT ", w , "being done!!!!")
            plt.figure()

            if 'abs' in w:
                plt.title("Real slowdown vs aggregate costs type " + w)
            else:
                if w == "cost_inst_LLCmiss_abs":
                    plt.title("Correlation between LLC miss counting and increase in runtime")
                elif w == "cost_inst_stall_time_abs":
                    plt.title("Correlation between stall time counting and increase in runtime")
                elif w == "cost_inst_L3stall_time_abs":
                    plt.title("Correlation between LLC miss stall time counting and increase in runtime")
                elif w == "cost_inst_L3MLP_abs":
                    plt.title("Correlation between L3 MLP weighted stall cycles counting and increase in runtime")
                elif w == "cost_inst_MLP_abs":
                    plt.title("Correlation between MLP weighted stall cycles counting and increase in runtime")
                else:
                    plt.title("Correlation between WHAT and increase in runtime" + w)
            # or absolute number of stall cycles and increase in run time
            #plt.title("Correlation between slow down and cumulative  ")

            #indexes = np.where(by_instruction_all[i]['real_slowdown'] < np.percentile(by_instruction_all[i]['real_slowdown'], 90))
            #by_instruction_all[i]['real_slowdown'] = by_instruction_all[i]['real_slowdown'][indexes]
            #by_instruction_all[i][w] = by_instruction_all[i][w][indexes]
            all_data_real = []
            all_data_weight = []
            all_avg_mlp = []


            for i in range(0, len(by_instruction_all)):
                print(i)
                try: 
                    #/proc/[pid]/numa_maps real_slowdown
                    #v = by_instruction_all[i]['stall_cycles'] #  if "abs" not in w else "absolute_increase" ]
                    v = by_instruction_all[i]['real_slowdown'] #  if "abs" not in w else "absolute_increase" ]
                    v1 = by_instruction_all[i][w]
                    v2 = by_instruction_all[i]['average_mlp_end']

                    all_data_real.append(v)
                    all_data_weight.append(v1)
                    all_avg_mlp.append(v2)    
                except Exception as e:
                    print(e)
                    continue
            all_data_real = np.array(all_data_real)
            
            print(len(all_data_weight), "length of all_data_weight", all_data_weight)
            all_data_weight = np.array(all_data_weight)
            no_nans_index = np.where(all_data_weight != np.nan)
            all_data_weight = all_data_weight[no_nans_index]
            all_data_real = all_data_real[no_nans_index]
            # remove all_data weight poitns greater than 1e10
            new_data_weight = all_data_weight[all_data_weight < 1e10]
            all_data_real = all_data_real[all_data_weight < 1e10]
            all_data_weight = new_data_weight

            #indexes_real = np.where(all_data_real < np.percentile(all_data_real, 90))
            #indexes = np.where(all_data_weight < np.percentile(all_data_weight, 95))
            #indexes_weight = np.where(all_data_weight < np.percentile(all_data_weight, 10))
            #indexes = np.intersect1d(indexes_real, indexes_weight)
            # wisconsin filter

            from scipy.stats.mstats import winsorize
            #all_data_real = winsorize(all_data_real, limits=[0, 0.9])
            #all_data_weight = winsorize(all_data_weight, limits=[0, 0.9])
            #if 'abs' not in w:
            #else:
            #    all_data_real = winsorize(all_data_real, limits=[0, 0.9])
            # clor based on average_mlp_middle key value
            all_data_color = np.array(all_avg_mlp)
            all_data_weight = winsorize(all_data_weight, limits=[0, 0.1])
            # convert all_data_to a color map between 0 and 255

            # use greys color map
            
            all_data_color = plt.cm.Reds(all_data_color / np.max(all_data_color))
            
            
            #all_data_real = all_data_real[indexes]
            #all_data_weight = all_data_weight[indexes]
            #all_data_color = all_data_color[indexes]
            plt.scatter(all_data_real, all_data_weight, alpha=0.3)# c=all_data_color)
            #if "abs" not in w:
            #    plt.xlim(0, 2)
            for mode in ['log', 'linear']:
                plt.yscale(mode)
                plt.xscale(mode)
                plt.savefig(f'{FIGS_FOLDER}/gen/insts/IN_THE_END{w.replace("/", "D").replace("%", "P")}_{mode}.png')
                plt.xlabel('Slow down')
                plt.ylabel('Total number of LLC misses normalized')
                plt.legend()
            plt.close()
        except Exception as e:
            print("sadly it did not work out..")
            import traceback
            traceback.print_exc()
            print(e)


def pot_errors(data,loader, r=None, name="errors_msr", transorm=lambda x : x):

    def plot_pred(data, loader, r=None, name="", transorm=lambda x : x):
            global bench_name
            global bench_nr
            if r is not None:
                bench_name = data[r]['0']['bench'].split("/")[-1]
                bench_nr = data[r]['0']['benchnr']
            res = obtain_derivate_metrics(data,r, loader)
            # plot real slow down vs predicted slow down for each metric
            # number of keys that do not start with pred_
            key_to_plot = lambda k :  k.startswith('pred_')  #and knk.startswith('pred_
            keys = len([k for k in res.keys() if key_to_plot(k)]) # c reate figure with num_keys subplots #fi
            g, axs = plt.subplots(num_keys, 1, figsize=(20, 20))
            plt.figure(figsize=(20, 20))
            i = 0
            def r_squared(y_true, y_pred):
                return np.square(np.subtract(y_true, y_pred)).mean()
            for k in res.keys():
                if key_to_plot(k): 
                    plt.bar(k.split('pred_')[1],r_squared(res['real_slow_down'], res[k]), label=k.split('pred_')[1])
                    i += 1
            f = f'{FIGS_FOLDER}/gen/pmu_pred/TRY_MSRE{name}.png'
            print('Saving', f)
            plt.savefig(f)
            plt.close()
            print("Done with", bench_name, bench_nr)
    try:
        plot_pred(data, loader, r, name)
    except:
        return
        #print("Failed to plot", bench_name, bench_nr)

results_by_run = {}
real_by_run = []
def plot_sum_errors(data,loader, r=None, name="errors_msr", transorm=lambda x : x):
    global results_by_run
    try:
        run0 = load_global_fields_final_pmu(data,r)
        run80 = load_global_fields_final_pmu(data,r,'80')
        l = load_aggregate_fields_frequency_normalized(data,r)

        d = {}

        d['cost_inst_stall_time'] = np.sum(l['stallTime'], dtype=np.float64) 
        d['cost_inst_L3stall_time'] = np.sum(l['L3stallTime'], dtype=np.float64) 

        d['cost_inst_L3MLP'] = np.sum(l['L3stallCyclesMLPLoad'], dtype=np.float64) 
        d['cost_inst_MLP'] = np.sum(l['stallCyclesMLPLoad'], dtype=np.float64) 

        d['cost_inst_L3stall/total'] = np.sum(l['L3stallTime']/l['totalTime'], dtype=np.float64) 
        d['cost_inst_L3stall'] = np.sum(l['L3stallTime'], dtype=np.float64) 

        l3_stall_is_0 = np.where(l['L3stallTime'] == 0)
        d['cost_inst_3MLP/3stall'] =  np.sum(l['L3stallCyclesMLPLoad'][l3_stall_is_0]/l['L3stallTime'][l3_stall_is_0], dtype=np.float64) 
        d['cost_inst_MLP*total/stall'] = np.sum(l['stallCyclesMLPLoad']*l['totalTime']/(l['stallTime']), dtype=np.float64)

        d['cost_inst_MLP/stall'] = np.sum(l['stallCyclesMLPLoad']/l['totalTime'], dtype=np.float64)
        d['cost_inst_MLP/total'] = np.sum(l['stallCyclesMLPLoad']/l['totalTime'], dtype=np.float64) 
        real_by_run.append(run80['currentCycle']-run0['currentCycle'])
        for k in d.keys():
            #d[k] = regress(d[k], run80['currentCycle']-run0['currentCycle'])
            if k not in results_by_run:
                results_by_run[k] = []
            print(k, d[k])
            results_by_run[k].append(d[k])
        print("SUCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC")
        
    except FileNotFoundError:
        import traceback
        traceback.print_exc()
        pass
    except:
        import traceback
        traceback.print_exc()
        pass
    
def actually_plot_sum_errors():
            name='some'
            def r_squared(y_true, y_pred):
                return np.square(np.subtract(y_true, y_pred)).mean()
            # grab the soar counter at that moment and use that as weight
            plt.figure(figsize=(10, 12))
            i = 0

            for k in results_by_run.keys():
                    not_nans = np.where(np.logical_not(np.isnan(results_by_run[k])))
                    results_by_run_pred = regress(np.array(results_by_run[k])[not_nans], np.array(real_by_run)[not_nans])
                    plt.bar(k,r_squared(np.array(real_by_run)[not_nans], np.array(results_by_run_pred)))
                    i += 1
            f = f'{FIGS_FOLDER}/gen/aggregate/aggregate_errors{name}.png'
            # 45 degree tick
            plt.xticks(rotation=45)
            print('Saving', f)
            plt.savefig(f)
            plt.close()
            print("Done with", bench_name, bench_nr)
            for k in results_by_run.keys():
                    plt.figure()
                    not_nans = np.where(np.logical_not(np.isnan(results_by_run[k])))
                    results_by_run_pred = regress(np.array(results_by_run[k])[not_nans], np.array(real_by_run)[not_nans])
                    plt.scatter(np.array(real_by_run)[not_nans], np.array(results_by_run_pred))
                    plt.title(k)
                    plt.xlabel('Real Slowdown')
                    plt.ylabel('Predicted Slowdown')
                    plt.savefig(f'{FIGS_FOLDER}/gen/aggregate/aggregate_errors{name}_{k}.png')
                    plt.close()

    
    


def plot_pred(data, loader, r=None, name="", transorm=lambda x : x):
    res = obtain_derivate_metrics(data,r, loader)
    # plot real slow down vs predicted slow down for each metric
    # number of keys that do not start with pred_
    key_to_plot = lambda k :  k.startswith('pred_') and k != 'real_slow_down'
    num_keys = len([k for k in res.keys() if key_to_plot(k)])
    # create figure with num_keys subplots
    fig, axs = plt.subplots(num_keys, 1, figsize=(20, 20))
    i = 0
    for k in res.keys():
        if key_to_plot(k): 
            axs[i].scatter(res['real_slow_down'], res[k], label=k.split('pred_')[1])
            axs[i].set_xlabel('Real Slowdown')
            axs[i].set_ylabel('Predicted ' + k.split('pred_')[1])
            axs[i].set_title("Real vs Predicted Slowdown for " + bench_name + " " + bench_nr)
            i += 1
    f = f'{FIGS_FOLDER}/gen/pmu_pred/{name}.png'
    print('Saving', f)
    plt.savefig(f)
    plt.close()
    print("Done with", bench_name, bench_nr)

ll= 0
def F():
    #obtain_derivate_metrics(data, load_global_fields)
    def _(data,r):
        global ll
        ll += 1
        return plot_no_pred(data,load_global_fields,r,"UPPER"+str(ll))
    iterate_over_benches(data, _)

def plot_no_pred(data,loader,r=None, name=""):
    res = obtain_derivate_metrics(data,r, loader)
    key_to_plot = lambda k :  not k.startswith('pred_') and k != 'real_slow_down'
    num_keys = len([k for k in res.keys() if key_to_plot(k)])
    fig, axs = plt.subplots(num_keys, 1, figsize=(20, 40))
    #  current error index 0 is out of bounds for axis 0 with size 0

    bench_name = data[r]['0']['bench'].split("/")[-1]
    #bname = data[r]['0']['bench']
    if num_keys == 0:
        print("No keys to plot!!"*10)
        return
    i = 0
    from scipy.stats.mstats import winsorize
    # 22 very good
         
    for k in res.keys():
        if key_to_plot(k): 
            axs[i].scatter(res['real_slow_down'], winsorize(res[k], limits=[0.01, 0.01]), label=k, s=1, alpha=0.2)
            axs[i].set_xlabel('Real Slowdown')
            axs[i].set_ylabel('Predicted ' + k)
            axs[i].set_title("Global real vs predicted Slowdown w/" + k)
            i += 1
    f = f'{FIGS_FOLDER}/gen/pmu_pred/_UP_scatter_{name}{bench_name}.png'
    print('Saving', f)
    plt.savefig(f)
    plt.close()
    print("Done with", bench_name, bench_nr)

################################################################################## MEMTIS ++ INFRA

WEIGHT_MODES={                      #s e  v                  s = start of the percentile, e = end of the percentile, v = value to set
    "ONLY_TOP_SENSITIVE": { 'values' : [(0,75,0), (75,100,1)]},
    "INSTA_PROMOTE-WEIGHT_REST": { 'values' : [(0,75,1), (75,100,100)]},
    "ONLY_MID_SENSITIVE": { 'values' : [(0,50,0), (50,100,1)]},
    "3_LEVEL_WEIGHTS-ignore_lowest": { 'values' : [(0,25,0), (25,75,2), (75,100,4)]}, # 
    "3_LEVEL_WEIGHTS": { 'values' : [(0,25,1), (25,50,2), (50,100,4)]}
}
import numpy as np
def statistical_weight(weight_map, mode):
    """ weight_map is a numpy array. 
    returns a new numpy array with the values set according to the mode"""
    if mode not in WEIGHT_MODES:
        raise ValueError(f"Mode '{mode}' not found in WEIGHT_MODES. Available modes: {list(WEIGHT_MODES.keys())}")
    
    if len(weight_map) == 0:
        return np.array([])
    
    result = np.zeros_like(weight_map, dtype=float)
    percentile_rules = WEIGHT_MODES[mode]['values']
    percentile_rules = sorted(percentile_rules, key=lambda x: x[0])
    for i, (start_percentile, end_percentile, weight_value) in enumerate(percentile_rules):
        start_threshold = np.percentile(weight_map, start_percentile)
        end_threshold = np.percentile(weight_map, end_percentile)
        
        if start_threshold == end_threshold:
            if end_percentile == 100 or i == len(percentile_rules) - 1:
                mask = weight_map == start_threshold
            else:
                continue
        else:
            if i == len(percentile_rules) - 1:  # Last rule - include end boundary
                mask = (weight_map >= start_threshold) & (weight_map <= end_threshold)
            else:
                mask = (weight_map >= start_threshold) & (weight_map < end_threshold)
        result[mask] = weight_value
    
    return result

def test_statistical_weight(): 
    # Test with sample data
    test_data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20])
    print("Original data:", test_data)
    print()
    
    # Test each weighting mode
    for mode_name in WEIGHT_MODES.keys():
        weighted_result = statistical_weight(test_data, mode_name)
        print(f"Mode: {mode_name}")
        print(f"Rules: {WEIGHT_MODES[mode_name]['values']}")
        print(f"Result: {weighted_result}")
        print(f"Unique weights: {np.unique(weighted_result)}")
        print("-" * 50)
def lossless_normalize_weight(weight_set):
    return weight_set -np.min(weight_set)+1 
def lossy_normalize_weight(weight_set):
    return weight_set / np.min(weight_set)
    

by_binary_weights = {}

def serialize_weights(metricas_finais, instructions, data,r):
            global success_run
            # each entry of metricas_finais is a column and each instruction is a line/row
            out= ""
            #mmm = sorted(metrics_names.keys())
            # approved metrics
            """
            mmm = [ "cost_inst_L3stall_time", "cost_inst_L3MLP", "cost_inst_MLP", "cost_inst_L3stall/total", "cost_inst_3MLP/3stall", "cost_inst_MLP/stall", "cost_inst_MLP/total"]
            mmm = list(metricas_finais.keys())
            mmm = [m for m in metricas_finais.keys() if any(m in mu for mu in mmm) ]
            """
            def print_numerated_column(lst):
                i=1
                info = ""
                for m in lst:
                    info += str(i) + "-" + m + " "
                    i+=1
                print(info)
            """
            for m in metricas_finais:
                smallest = np.min(metricas_finais[m])
                metricas_finais[m] = metricas_finais[m] - smallest + 1
            """
            
            if len(instructions) <= 2:
                print('Less than 2 instructions... aborting')
                return

            #print_numerated_column(mmm)
            
            print("There are ", len(instructions), "instructions!!!!")
            for i in range(len(instructions)):
                out += str(int(instructions[i])) + " "
                for m in sorted(metricas_finais.keys()):
                        try:
                            print(str([ int(metricas_finais[m][i]) for i  in range(len(instructions))]), " metric", m, "inst", instructions[i])
                            value = str(int(metricas_finais[m][i]))
                        except Exception as e:
                            value = "1234"
                            raise e
                        out += value + " "
                out += "\n"
            out = (str(len(instructions)+1) + " ") * 10 + "\n" +  out
            print("FINAL",out)
            # basename of data[r]['0']['bench']
            binary =  os.path.basename(data[r]['0']['bench']) 
            print("Saving", f'{FIGS_FOLDER}/maps/{binary} {r}.txt')
            print("#"*20)
            # print only first 10 and last 10 lines
            print('\n'.join(out.split('\n')[:10])  + "\n...\n" + '\n'.join(out.split('\n')[-10:]))
            print("#"*20)

            #os.makedirs(f"{FIGS_FOLDER}/maps/{binary}{r]/vars/{var}", exist_ok=True)
            #plt.savefig(f"{FIGS_FOLDER}/gen/vars/{var}/_0_{bench_name}_{bench_nr}_0.png")
            with open(f'{FIGS_FOLDER}/maps/{binary} {r}.txtWOW', 'w') as f:
                f.write(out)
            success_run += 1
            return out 

corrupted_vars = {}
def ow():
    global RUN_DATA_FOLDER
    global inst_types
    global OLD_V4
    #RUN_DATA_FOLDER="/mnt/nas/inesc/ist196723/osdi26/v4/results_gem5"
    data = load_bench_data()
    #iterate_over_benches(data, obtain_weights) 
    iterate_over_benches(data, ooo) 

def to_numpy(dict_of_insts, instructions):
    d = dict_of_insts
    metrics_names = (list(d[instructions[0]].keys()))
    metricas_numpiadas = {}
    for m in metrics_names:
        metricas_numpiadas[m] = np.zeros(len(instructions))
        for i, inst in enumerate(instructions):
            metricas_numpiadas[m][i] = d[inst][m]
    return metricas_numpiadas
        

def ooo(data,r):
    global aggregate_fields
    global RUN_DATA_FOLDER
    RUN_DATA_FOLDER="/mnt/nas/inesc/ist196723/osdi26/results_gem5"
    

    l = load_aggregate_fields(data, r)
    l80 = load_aggregate_fields(data, r, 80)
    unique_instructions = np.unique(l['address'])
    valid_entries = (l['accessBracket'] > 1) & (l['count'] >= 1)  # & (l['address'] != 0)
    # access bracket must be > 2 , acces Count >= 1
    MLP_PRECISION_FACTOR=1024
    d = {}
    for i in unique_instructions:
        d[i] = {}
    for n in unique_instructions:
        sel = np.where(l['address'] == n)
        sel = np.intersect1d(sel, valid_entries)
        print(l['stallTime'][sel].sum(), l['count'][sel].sum())
        print('average',  l['L3stallTime'][sel].sum() / l['count'][sel].sum())
        if l['totalTime'][sel].sum() < l['count'][sel].sum():
            raise Exception("Stall time is less than count")
            #print(l['stallTime'][sel].sum(), l['count'][sel].sum())

        return
        
        d[n]['Acost_inst_stall_time'] = np.sum(l['stallTime'][sel], dtype=np.float64) / l['count'][sel].sum()
        d[n]['Bcost_inst_L3stall_time'] = np.sum(l['L3stallTime'][sel], dtype=np.float64) / l['count'][sel].sum()
        d[n]['Ccost_inst_L3MLP'] = np.sum(l['L3stallCyclesMLPLoad'][sel]/MLP_PRECISION_FACTOR, dtype=np.float64) / l['count'][sel].sum()
        d[n]['Dcost_inst_MLP'] = np.sum(l['stallCyclesMLPLoad'][sel]/MLP_PRECISION_FACTOR, dtype=np.float64) / l['count'][sel].sum()
        d[n]['Fcost_inst_totalTime'] = np.sum(l['totalTime'][sel]/MLP_PRECISION_FACTOR, dtype=np.float64) / l['count'][sel].sum()
        
        for m in d[n].keys():
            d[n][m] = np.where(np.isnan(d[n][m]), 0, d[n][m])
    serialize_weights(to_numpy(d, unique_instructions), unique_instructions, data,r)
    
        
def obtain_weights(data,r):
    global corrupted_vars
    global inst_types

    inst_types['address'] = np.uint32 
    inst_types['L3stallCyclesMLPLoad'] = np.uint64
    inst_types['stallCyclesMLPLoad'] = np.uint32
    inst_types['stallTime'] = np.uint16
    #inst_types['L3stallTime'] = np.uint16
    inst_types['totalTime'] = np.uint16
    #{'average_l3mlp': np.uint8,'tlb_miss': np.uint8,'isLoad': np.uint8,'isStore': np.uint8,'isMicroop': np.uint8,'address': np.uint64,'lastStallTime': np.uint16,'totalTime': np.uint16, 'stallTime': np.uint16, 'L3stallTime': np.uint16, 
    #        'L3stallCyclesMLPLoad': np.uint64, 'stallCyclesMLPBoth': np.uint64, 'MLP_store_at_start': np.uint8, 'MLP_store_at_end': np.uint8, 'MLP_load_at_start': np.uint8, 'MLP_load_at_end': np.uint8, 'L3MLP_store_at_start': np.uint8, 'L3MLP_store_at_end': np.uint8, 'L3MLP_load_at_start': np.uint8, 'L3MLP_load_at_end': np.uint8, 'L3MLP_store_at_middle': np.uint8, 'L3MLP_load_at_middle': np.uint8,
    print("Obtaining weights for", r)
    
    #l = load_aggregate_fields(data, r)
    #l80 = load_aggregate_fields(data, r, 80)
    #l = l80

    i = load_inst_fields(data, r)
    i80 = load_inst_fields(data, r, '80')

    by_instruction_sampling = True # '/mnt/nas/inesc/ist196723/osdi26/results_gem5/100227/
    if by_instruction_sampling:
        l = i
        l80 = i80
        #l = l80

    def split_data_by_instruction(nparray, instructions,l3_idx):
        new_arrays = []
        for i in instructions:
            idx = np.where((nparray !=  i))
            # zero out the array where idx is false
            new_arrays.append(np.intersect1d(l3_idx, idx))
            #new_arrays.append(nparray[idx])
        return new_arrays
    
    try:

        print(len(l['totalTime']), len(l['address']), "GIVE UP")
        if by_instruction_sampling:
            l3_idx = (np.where(l['totalTime']  > 30  )) # & (l['tlb_miss'] == 0) )) # ignore TLB misses. we cannot optimize them 
            # np array of the same size as l['totalTime']
            l['count'] = np.ones_like(l['totalTime'])
        else: #:(l['isStore'] == 0)
            #accessBracket
            l['accessBracket'] = l['accessBracket'] * 16
            l3_idx = (np.where(l['accessBracket']  > 0)) #&     (l['tlb_miss'] == 0) ) # ignore TLB misses. we cannot optimize them 
            #l3_idx =np.intersect1d(np.where(l['count'] > 0),   np.where(l['accessBracket'] > 32) )# , np.where(l['tlbMiss'] == 0))
        #l3_idx = np.where(l['count'] > 0)
        #idxs = split_data_by_instruction(l['address'], unique_instructions, l3_idx)
        #print(len(l['totalTime']), len(l['address']), "GIVE UP")
        #return
        print('wow', len(l['address'][l3_idx]), len(l['L3stallCyclesMLPLoad']))
        unique_instructions = np.unique(l['address'][l3_idx])

        print(np.histogram(l['L3stallCyclesMLPLoad'][l3_idx]), 'jooo')
        print("There ARE!!", len(unique_instructions), "for", data[r]['0']['bench'],data[r]['0']['benchnr'] )
        print("There ARE!", len(unique_instructions), "instructions and ", len(l['address']), "totall", "Number of lost instructions due to the narrow criteria:", len(np.unique(l['address'])) - len(unique_instructions))
        print(((l['L3stallCyclesMLPLoad'][l3_idx] > 1024*200).sum() / len(l['L3stallCyclesMLPLoad'][l3_idx])) * 100 , "% of L3stallCyclesMLPLoad that are above 1024*200")
        #l3_to_ignore = (l['L3stallCyclesMLPLoad'] <  1)#(l['L3stallCyclesMLPLoad'] <  1024*200)
        #print("unique_instructions", unique_instructions)
        d = {}
        for i in unique_instructions:
            d[i] = {}

        if len(l['totalTime'] > 600) > 0:
            corrupted_vars['totalTime'] = True
        if len(l['stallTime'] > 600) > 0:
            corrupted_vars['stallTime'] = True
        #if len(l['L3stallTime'] > 600) > 0:
        #    corrupted_vars['L3stallTime'] = True
        if len(l['L3stallCyclesMLPLoad'] > 600*MLP_PRECISION_FACTOR) > 0:
            corrupted_vars['L3stallCyclesMLPLoad'] = True
        if len(l['stallCyclesMLPLoad'] > 600*MLP_PRECISION_FACTOR) > 0:
            corrupted_vars['stallCyclesMLPLoad'] = True
        i = 0
        metrics = []
        MLP_PRECISION_FACTOR = 1024
        for inst in unique_instructions:
            sel = np.where(l['address'] == inst)
            sel = np.intersect1d(sel, l3_idx)
            #length_sel = len(sel)
            #length_sel = 1
            if inst == 0:
                continue
            
            l3_stall_is_nan = np.isnan(l['L3stallTime'][sel])
            print("L3 STALL IS NAN", len(l3_stall_is_nan))
            d[inst]['Acost_inst_stall_time'] = np.sum(l['stallTime'][sel], dtype=np.float64) / l['count'][sel].sum()
            d[inst]['Bcost_inst_L3stall_time'] = np.sum(l['L3stallTime'][sel][~l3_stall_is_nan], dtype=np.float64) / l['count'][sel][~l3_stall_is_nan].sum()
            d[inst]['Ccost_inst_L3MLP'] = np.sum(l['L3stallCyclesMLPLoad'][sel]/MLP_PRECISION_FACTOR, dtype=np.float64) / l['count'][sel].sum()
            d[inst]['Dcost_inst_MLP'] = np.sum(l['stallCyclesMLPLoad'][sel]/MLP_PRECISION_FACTOR, dtype=np.float64) / l['count'][sel].sum()
            d[inst]['Fcost_inst_totalTime'] = np.sum(l['totalTime'][sel]/MLP_PRECISION_FACTOR, dtype=np.float64) / l['count'][sel].sum()
            continue

            #print("length_sel", length_sel)
            #print(np.sum(l['stallTime'][sel] / l['count'][sel]) / length_sel)
            #print(np.sum(l['stallTime'][sel]/l['count'][sel], dtype=np.float64) / length_sel)
            d[inst]['Acost_inst_stall_time'] = np.sum(l['stallTime'][sel], dtype=np.float64) / l['count'][sel].sum()
            #print(int(d[inst]['cost_inst_stall_time']))
            l3_sel = np.intersect1d(sel, l3_to_ignore)
            l3_sel_length = len(l3_sel)
            l3_sel_length = 1
            l3_stall_is_nan = np.isnan(l['L3stallTime'][l3_sel])
            if np.any(l3_stall_is_nan):
                print("There are NaNs in L3stallTime for", inst)
                print("Count of NaNs:", np.count_nonzero(l3_stall_is_nan))
                print("Count of non NaNs:", np.count_nonzero(~l3_stall_is_nan))
                print("Fraction of NaNs:", np.count_nonzero(l3_stall_is_nan)/len(l3_sel))
            count_non_zero = np.count_nonzero(l['count'][sel] != 0)
            print("Fraction of non zero counts:", count_non_zero/len(sel), "sum of counts",  l['count'][l3_sel][~l3_stall_is_nan].sum(),  l['count'][l3_sel].sum())

            d[inst]['Bcost_inst_L3stall_time'] = np.sum(l['L3stallTime'][l3_sel][~l3_stall_is_nan], dtype=np.float64) / l['count'][l3_sel][~l3_stall_is_nan].sum()
            if np.isnan(d[inst]['Bcost_inst_L3stall_time']):
                print("There are NaNs in Bcost_inst_L3stall_time for", inst)
                if 'bfs' in data[r]['0']['bench'] or 'bc' in data[r]['0']['bench']:
                    print('SAD ENDING')
                    exit()


            d[inst]['Ccost_inst_L3MLP'] = np.sum(l['L3stallCyclesMLPLoad'][l3_sel]/MLP_PRECISION_FACTOR, dtype=np.float64) / l['count'][l3_sel].sum()
            d[inst]['Dcost_inst_MLP'] = np.sum(l['stallCyclesMLPLoad'][sel]/MLP_PRECISION_FACTOR, dtype=np.float64) / l['count'][sel].sum()

            #d[inst]['cost_inst_L3stall/stall'] = np.sum(l['L3stallTime'][sel]/l['count'][sel]/l['stallTime'][sel], dtype=np.float64) / length_sel
            #d[inst]['cost_inst_L3stall'] = np.sum(l['L3stallTime'][sel]/l['count'][sel], dtype=np.float64) / length_sel

            # TODO WHY??
            #d[inst]['cost_inst_3MLP/3stall'] = 10 #  np.sum(l['L3stallCyclesMLPLoad'][sel]/l['count'][sel]/l['L3stallTime'][sel], dtype=np.float64) / length_sel
            #d[inst]['cost_inst_MLP*total/stall'] = np.sum(l['stallCyclesMLPLoad'][sel]*l['totalTime'][sel]/(l['stallTime'][sel]*l['count'][sel]), dtype=np.float64) / length_sel

            #d[inst]['Ecost_inst_MLP/stall'] = np.sum((l['stallCyclesMLPLoad'][sel]/MLP_PRECISION_FACTOR)/l['stallTime'][sel]/l['count'][sel], dtype=np.float64) / length_sel
            d[inst]['Ecost_inst_MLP/stall'] = np.sum((l['stallCyclesMLPLoad'][sel]/MLP_PRECISION_FACTOR)) / l['count'][sel].sum()
            # if d[inst]['Ecost_inst_MLP/stall'] < 0:
            #    d[inst]['Ecost_inst_MLP/stall'] = 0

            d[inst]['Fcost_inst_MLP/total'] = np.sum((l['stallCyclesMLPLoad'][sel]/MLP_PRECISION_FACTOR)/l['totalTime'][sel], dtype=np.float64) / l['count'][sel].sum()

            d[inst]['Gcost_inst_stall*cost_inst_MLP'] = np.sum(l['stallCyclesMLPLoad'][sel]/MLP_PRECISION_FACTOR*l['stallTime'][sel], dtype=np.float64) / l['count'][sel].sum()
            d[inst]['Hcost_inst_stall*cost_inst_MLP'] = np.sum(l['stallCyclesMLPLoad'][sel]/MLP_PRECISION_FACTOR*l['stallTime'][sel], dtype=np.float64) / l['count'][sel].sum()
            metrics = d[inst].keys()
            """
            """
            #d[i]['cost_inst_delta'] = np.sum(
            #    (l80['stallTime'][idxs80[a]]/l80['count'][idxs80[a]]) - (l['L3stallTime'][sel]/l['count'][sel]))
            i+=1
        # convert from dictionary INST METRIC to dicitonary METRIC numpy array  
        metricas_numpy = {}
        instructions = np.array(sorted(list(d.keys())))
        for m in metrics:
            print("metricccccccccccc", m)
            metricas_numpy[m] = np.zeros(len(instructions))
            for i, inst in enumerate(instructions):
                metricas_numpy[m][i] = d[inst][m]
        #for inst, inst_addr in enumerate(instructions):
        #    #m#etricas_numpy['Gcost_inst_stall*cost_inst_MLP'] =
        print(metricas_numpy.keys())
        metricas_numpy['Gcost_inst_stall*cost_inst_MLP'][:][ (metricas_numpy['Ccost_inst_L3MLP'][:] <= np.percentile(metricas_numpy['Ccost_inst_L3MLP'][:], 25))] = 1
        metricas_numpy['Gcost_inst_stall*cost_inst_MLP'][:][ (metricas_numpy['Ccost_inst_L3MLP'][:] > np.percentile(metricas_numpy['Ccost_inst_L3MLP'][:], 25)) & (metricas_numpy['Ccost_inst_L3MLP'][:] <= np.percentile(metricas_numpy['Ccost_inst_L3MLP'][:], 75)) ] = 2
        metricas_numpy['Gcost_inst_stall*cost_inst_MLP'][:][metricas_numpy['Ccost_inst_L3MLP'][:] < np.percentile(metricas_numpy['Ccost_inst_L3MLP'][:], 75)] = 4
        #Hcost_inst_stall*cost_inst_MLP
        #metricas_numpy['Ftop_10'] = np.copy(metricas_numpy['Ccost_inst_L3MLP']) 
        #metricas_numpy['Ftop_10'][metricas metricas_numpy['Ccost_inst_L3MLP'] > np.percent(metricas_numpy['Ccost_inst_L3MLP'],90)] = 10
        #metricas_numpy['Ftop_10'][ metricas metricas_numpy['Ccost_inst_L3MLP'] < np.percent(metricas_numpy['Ccost_inst_L3MLP'],90) ] = 1

        if data[r]['0']['benchnr'] == '75':
            exit(0)
        
        #d[inst]['Hcost_inst_stall*cost_inst_MLP'] 
        #d[inst]['Hcost_inst_stall*cost_inst_MLP']  = 
        #np.percentile(d[inst]['Ccost_inst_l3_mlp'], 75)
        #np.percentile(d[inst]['Ccost_inst_l3_mlp'], 75)
        
        """
        for m in sorted(list(metricas_numpy.keys()))[0:1]:
            #for i in range(len(metricas_numpy[m])):
            min = np.min(metricas_numpy[m][inst])
            max = np.max(metricas_numpu[m])    
            low_1_percent = np.percentile(metricas_numpy[m], 1)
            if low_1_percent*0.5 > 1:
                low_1_percent = low_1_percent*0.5
            

            bins = np.array([ v for v in range(min, max,  low_1_percent)]) #np.linspace(0, 500, quantization_level)
            digitized = np.digitize(metricas_numpy[m], bins)
            for m in sorted(list(metricas_numpy.keys()))[0:1]:
            print("max", np.max(metricas_numpy[m]))
        """
        """
        for quantization_level in range(10, 500, 10): # only cap the top at the last
            bins = np.array([ v for v in range(0, 500, quantization_level)]) #np.linspace(0, 500, quantization_level)
            for m in sorted(list(metricas_numpy.keys()))[0:1]:
                digitized = np.digitize(metricas_numpy[m], bins)
                diff =  np.insert(np.diff(digitized), 0, 1)
                compressed_map = digitized[diff != 0]
                #print("Compressed ",  len(compressed_map) / len(digitized), " times!")
        """

        """

        
        print("There ARE!!", len(unique_instructions), "for", data[r]['0']['bench'],data[r]['0']['benchnr'] )

        """
        # add columns to this numpy array for each metric
        metrics_names = (list(d[instructions[0]].keys()))
        metricas_numpiadas = {}
        for m in metrics_names:
            metricas_numpiadas[m] = np.zeros(len(instructions))
            for i, inst in enumerate(instructions):
                metricas_numpiadas[m][i] = d[inst][m]
        
        #
        metricas_finais = {}

        # BUGGGGGGGGGGGGGG HERE BUG
        """
        for m in ["const_inst_L3MLP"]:#metrics_names:
            metricas_finais[m] = np.copy(metricas_numpiadas[m])
            for mode in WEIGHT_MODES:
                metricas_finais["{}-{}".format(m, mode)] = statistical_weight(metricas_numpiadas[m], mode)
            metricas_finais["{}-{}".format(m, "lossless") ] = lossless_normalize_weight(metricas_numpiadas[m])
            metricas_finais["{}-{}".format(m, "lossy") ] = lossy_normalize_weight(metricas_numpiadas[m])
        """

            
        """
        binary = data[r]['0']['bench'].split("/")[-1]
        if binary not in by_binary_weights:
            by_binary_weights[binary] = []
        by_binary_weights[binary].append(d)
        """
        serialize_weights(metricas_numpy, instructions, data, r)
        print('obtained weight nicely')


        
        """

        
        # do the mean across each metric
        total = {} # iterate through insts
        count = {} # iterate through insts
        smallest = {}
        # 
        for k in d: # iterate through insts
            for k2 in d[k]: # iterate through keys
                if k2 not in total:
                    total[k2] = 0
                    count[k2] = 0
                    smallest[k2] = float('inf')
                total[k2] += d[k][k2]
                count[k2] += 1
                if d[k][k2] < smallest[k2]:
                    smallest[k2] = d[k][k2]
        # obtain average
        for k in total:
            total[k] = total[k] / count[k]
        # remove the average or the minimum value  (increase the gap between the values)
        #minimo = 0
        for k in d:
            for k2 in d[k]:
                change = total[k2]
                if smallest[k2]-1 < total[k2]:
                    change = smallest[k2]-1
                d[k][k2] -= change
        # this reducion is essential, so ensure 1) priorities are strong this 1)discourages new migrations 2) ensures noise in sampling does not affect outcomes  2) ensures there are no overflows in the htmm code
            
        sorted_insts = sorted(unique_instructions)
        #print("INSTO", sorted_insts )
        """
        """
        line = ""
        a = -1
        for sel in idxs:
            a += 1
            length_sel = len(sel)
            if(length_sel == 0):
                continue
            instruction  = sorted_insts[a]
            #print("INSTA", instruction)
            i = d[instruction]
            if i == 0:
                continue
            line += str(instruction) + " "
            line += str(int(i['cost_inst_stall_time'])) + " "
            line += str(int(i['cost_inst_L3stall_time'])) + " "
            line += str(int(i['cost_inst_L3MLP'])) + " "
            line += str(int(i['cost_inst_MLP'])) + " "
            line += str(int(i['cost_inst_L3stall/total'])) + " "
            line += str(int(i['cost_inst_3MLP/3stall'])) + " "
            line += str(0) +" "# int(i['cost_inst_MLP*total/stall'])) + " "
            line += str(int(i['cost_inst_MLP/stall'])) + " "
            line += str(int(i['cost_inst_MLP/total'])) + " "
            #line += str(i['cost_inst_delta']) + "\n"
            line += "\n"
    
        """

        

    except FileNotFoundError as e:
        raise e
        print("... f not found..")
        import traceback
        traceback.print_exc()
        return
    except Exception as e:
        raise e
        print("Failed to obtain weights for", r)
        print(e)
        print("MUAH")
        import traceback
        traceback.print_exc()
        return

def learn_improved(inputs_matrix, real_costs, objective_function, initial_weights):
    """
    Improved learning with feature scaling and better optimization
    """
    # Convert data to matrix format
    
    # Feature scaling to normalize inputs
    scaler = StandardScaler()
    inputs_scaled = scaler.fit_transform(inputs_matrix)
    #kinputs_scaled = inputs_matrix #scaler.fit_transform(inputs_matrix)
    #scaler = None
    
    
    print("=== IMPROVED OPTIMIZATION WITH FEATURE SCALING ===")
    #print(f"Original input range examples:")
    #print(f"  L3stallTime: [{inputs_matrix[:, 0].min():.2f}, {inputs_matrix.max():.2f}]")
    #print(f"  TotalTime: [{inputs_matrix[:, 4].min():.2f}, {inputs_matrix[:, 4].max():.2f}]")
    
    print(f"Scaled input range (should be ~[-3, 3]):")
    #print(f"  L3stallTime: [{inputs_scaled[:, 0].min():.2f}, {inputs_scaled[:, 0].max():.2f}]")
    #print(f"  TotalTime: [{inputs_scaled[:, 4].min():.2f}, {inputs_scaled[:, 4].max():.2f}]")
    
    # Try multiple optimization methods
    methods = ['BFGS', 'L-BFGS-B', 'Powell']
    results = {}
    
    for method in methods:
        print(f"\n--- Method: {method} ---")
        
        try:
            result = minimize(
                fun=objective_function,
                x0=initial_weights, 
                args=(inputs_scaled, real_costs), # args to the function!!
                method=method,
                options={'disp': False, 'maxiter': 1000000}
            )
            
            print(f"Success: {result.success}")
            print(f"Final MSE: {result.fun:.2f}")
            print(f"Iterations: {result.nit if hasattr(result, 'nit') else 'N/A'}")
            print(f"Optimal weights: {result.x}")
            
            results[method] = result
            
        except Exception as e:
            print(f"Failed: {e}")
            results[method] = None
    
    # Try Differential Evolution (global optimization)
    print(f"\n--- Method: Differential Evolution (Global) ---")
    """
    bounds = [(-10, 10) for _ in range(7)]  # Bounds for each weight
    
    
    de_result = differential_evolution(
        objective_function,              # FIXED: use 'fun=' explicitly
        initial_weights,  
        bounds=bounds,
        args=(inputs_scaled, real_costs),
        seed=42,
        maxiter=100
    )
    
    print(f"Success: {de_result.success}")
    print(f"Final MSE: {de_result.fun:.2f}")
    print(f"Iterations: {de_result.nit}")
    print(f"Optimal weights: {de_result.x}")
    
    results['differential_evolution'] = de_result
    
    """
    # Find best result
    best_method = None
    best_cost = float('inf')
    
    for method, result in results.items():
        if result is not None and result.success and result.fun < best_cost:
            best_cost = result.fun
            best_method = method
    
    print(f"\n=== BEST RESULT ===")
    print(f"Best method: {best_method}")
    if best_method:
        best_result = results[best_method]
        print(f"Best MSE: {best_result.fun:.2f}")
        print(f"Best weights: {best_result.x}")
        
        return best_result.x, best_result, scaler
    else:
        print("No successful optimization found")
        return None, None, scaler

# Run improved learning
#best_weights, best_result, feature_scaler = learn_improved(dataset)


"""
struct FinalMetrics{
    uint32_t address;
    uint16_t totalTime ;
    uint16_t stallTime ;
    uint16_t lastStallTime ; // First these store the cycles at start, then, we grab the end on the cpu and these store the difference
    uint16_t stallCyclesMLPLoad ; // First these store the cycles at start, then, we grab the end on the cpu and these store the difference
    uint64_t start_cycle ; // at EA
    uint16_t stallCyclesMLPStore ;
    uint16_t stallCyclesMLPBoth ;

    uint8_t MLP_store_at_start   ;
    uint8_t MLP_store_at_end  ;
    uint8_t MLP_load_at_start  ;
    uint8_t MLP_load_at_end ;
    bool isMicroop : 1;
    bool tlb_miss : 1;
    bool isLoad : 1;
    bool isStore : 1;
};

struct GlobalStatsss{
    float stallCyclesMLPLoad;
    float stallCyclesMLPStore;
    float stallCyclesMLPBoth;
    uint64_t stalledCycles;
    uint64_t stalledCyclesDuringStore;
    uint64_t stalledCyclesWithMemRequests;
    uint64_t stalledCyclesWithStores;
    uint64_t cyclesWithMemrequests; // the diff between 2 = A1 of SOAR
    uint64_t commitedStores ;
    uint64_t commitedLoads ;  // The dif betweeen 2 = A2
    uint64_t commitedAtomic ;
    uint64_t commitedInstructions ;
    uint64_t totalSquashed ;
    uint64_t lastStallTime ;
    uint64_t currentCycle ;
    uint64_t loadCountByLatency[16];
    uint64_t tlbMisses;
};

struct InstructionData {
    uint32_t count ;
    uint64_t stallTime ;
    uint64_t totalTime ;
    uint64_t lastStallTime ;
    uint64_t stallCyclesMLPLoad ;
    uint64_t stallCyclesMLPStore ;
    uint64_t stallCyclesMLPBoth ;
    uint8_t accessBracket ;
    bool tlbMiss ;
};

"""

class InstructionData(Structure):
    _fields_ = [
        ("count", c_uint32),
        ("stallTime", c_uint64),
        ("totalTime", c_uint64),
        ("lastStallTime", c_uint64),
        ("stallCyclesMLPLoad", c_uint64),
        ("stallCyclesMLPStore", c_uint64),
        ("stallCyclesMLPBoth", c_uint64),
        ("accessBracket", c_uint8),
        ("tlbMiss", c_bool),
    ]
class FinalMetrics(Structure):
    _fields_ = [
        ("address", c_uint32),
        ("totalTime", c_uint16),
        ("stallTime", c_uint16),
        ("lastStallTime", c_uint16),
        ("stallCyclesMLPLoad", c_uint16),
        ("stallCyclesMLPStore", c_uint16),
        ("stallCyclesMLPBoth", c_uint16),
        ("MLP_store_at_start", c_uint8),
        ("MLP_store_at_end", c_uint8),
        ("MLP_load_at_start", c_uint8),
        ("MLP_load_at_end", c_uint8),
        ("isMicroop", c_bool),
        ("tlb_miss", c_bool),
        ("isLoad", c_bool),
        ("isStore", c_bool),
    ]
class GlobalStatsss(Structure):
    _fields_ = [
        ("stallCyclesMLPLoad", c_float),
        ("stallCyclesMLPStore", c_float),
        ("stallCyclesMLPBoth", c_float),
        ("stalledCycles", c_uint64),
        ("stalledCyclesDuringStore", c_uint64),
        ("stalledCyclesWithMemRequests", c_uint64),
        ("stalledCyclesWithStores", c_uint64),
        ("cyclesWithMemrequests", c_uint64),
        ("commitedStores", c_uint64),
        ("commitedLoads", c_uint64),
        ("commitedAtomic", c_uint64),
        ("commitedInstructions", c_uint64),
        ("totalSquashed", c_uint64),
        ("lastStallTime", c_uint64),
        ("currentCycle", c_uint64),
        ("loadCountByLatency", c_uint64 * 16),
        ("tlbMisses", c_uint64),
    ]
    

def load_struct(constructor, file):
    with open(file, 'rb') as file:
        result = []
        x = constructor()
        while file.readinto(x) == sizeof(x):
            result.append(x)
    return result


run_meta=f"{RUN_DATA_FOLDER}/gem5_pids.txt"
def build_run_data(line):
    """
    pid: 85060 benchset: benches_final benchnr: 37 bench: /mnt/nas/inesc/ist196723/benchmarks/cpu2017/benchspec/CPU/644.nab_s/exe/nab_s_base.NOavxprota-m64 increase: 0 host: cc8ece5416c5 TERMINATED
    pid: 85062 benchset: benches_final benchnr: 37 bench: /mnt/nas/inesc/ist196723/benchmarks/cpu2017/benchspec/CPU/644.nab_s/exe/nab_s_base.NOavxprota-m64 increase: 80 host: cc8ece5416c5 TERMINATED
    pid: 84762 benchset: benches_final benchnr: 28 bench: /mnt/nas/inesc/ist196723/benchmarks/cpu2017/benchspec/CPU/605.mcf_s/exe/mcf_s_base.NOavxprota-m64 increase: 0 host: cc8ece5416c5 TERMINATED
    """
    return {
        "pid": line.split("pid: ")[1].split(" ")[0].strip(),
        "benchset": line.split("benchset: ")[1].split(" ")[0].strip(),
        "benchnr": line.split("benchnr: ")[1].split(" ")[0].strip(),
        "bench": line.split("bench: ")[1].split(" ")[0].strip(),
        "increase": line.split("increase: ")[1].split(" ")[0].strip(),
        "host": line.split("host: ")[1].split(" ")[0].strip(),
        "terminated": line.split("host:")[1].split(" ")[0].strip(),
        "line" : line
        #"terminated-status": line.split("host:")[-1].split(" ")[-1].strip()
        }

        

import glob

def NOOOOOload_from_splitted():
    all_data = {}
    all_lines = []
    with open(run_meta, 'r') as file:
        for line in file:
            all_lines.append(line)


        for line in all_lines[-10:]:
            print(line)
            try:
                _  = build_run_data(line)
            except Exception as e:
                print(e)
                print(line)
                continue
            r_number = _['benchnr']
            if not r_number in all_data:
                all_data[r_number] = {}
            if _['increase'] in all_data[r_number]: 
                print("WARNING: Duplicate increase")
                i = load_inst_fields(all_data, _)
                #all_data[r_number][_['increase']] = _  ####### CHANGE
            else:
                pass
                #all_data[r_number][_['increase']] = _ 
            try:
                print(i['average_l3mlp'])
            except Exception as e:
                print(e)
                continue
            #_['global'] = load_struct(GlobalStatsss,glob.glob(f"/mnt/nas/inesc/ist196723/osdi26/results_gem5/global_{_['pid']}_{_['host']}*.bin")[0])
            #_['inst'] = load_struct(InstructionData,glob.glob(f"/mnt/nas/inesc/ist196723/osdi26/results_gem5/aggregate_{_['pid']}_{_['host']}*.bin")[0])
            #_['final'] = load_struct(FinalMetrics,glob.glob(f"/mnt/nas/inesc/ist196723/osdi26/results_gem5/inst_{_['pid']}_{_['host']}*.bin")[0])
                #f"/mnt/nas/inesc/ist196723/osdi26/results_gem5/output_{rdata["host"]}.bin")

import re
def get_print_timestamps(run):
    # obtain output file
    output_file = glob.glob(f"/mnt/nas/inesc/ist196723/osdi26/results_gem5/output_*_{run['benchnr']}_0_")[0]
    print("For benchnr", run['benchnr'], "output file is", output_file)
    timestamp = 0

    timestamps = []
    lines = []
    started = False
    with open(output_file, 'r') as file:
        for line in file:
            # ignore first 50 lines
            if not started:
                if 'Running O3' in line:
                    started = True
                continue
            if 'ELAPSED' in line:
                continue
            if "Instruction count:" in line:
                try:
                    timestamp = int(line.split(" ")[2])
                    continue
                except Exception as e:
                    # a program line was mixed with this output...
                    # extract the timestamp from the line (there is no seperator, just a unknown letter or number, use regex)
                    timestamp = int(re.search(r'\d+', line).group())
                    line = line.split(str(timestamp))[1]


            timestamps.append(timestamp)
            lines.append(line)
                
    return [timestamps, lines]

    

#class RunData:
#def __init__(self, run):
        
def load_bench_data_pids():
    f="/mnt/nas/inesc/ist196723/osdi26/l3mlp_dudes" 
    all_data = {}
    with open(f, 'r') as file:
        for line in file:
            pid = int(line.strip())
            run = {
                'benchid' :pid,
                'benchnr' :pid,
                'increase' : 0,
                'host' : 'cc8ece5416c5',
                'terminated' : 'TERMINATED',
                'line' : line,
                'bench': "unknown",
                'pid': pid
            }
            all_data[pid] = {}
            all_data[pid]['0'] = run
            all_data[pid]['80'] = run
    return all_data



def load_bench_data():
    global inst_types
    all_data = {}
    all_lines = []
    if OLD_V4:
        #inst_types={'average_l3mlp': np.uint8, 'average_mlp' :np.uint8, 'tlb_miss': np.uint8,'isLoad': np.uint8,'isStore': np.uint8,'isMicroop': np.uint8,'address': np.uint64,'lastStallTime': np.uint16,'totalTime': np.uint16, 'stallTime': np.uint16, 'L3stallTime': np.uint16, 
        #    'L3stallCyclesMLPLoad': np.uint64, 'stallCyclesMLPBoth': np.uint64, 'MLP_store_at_start': np.uint8, 'MLP_store_at_end': np.uint8, 'MLP_load_at_start': np.uint8, 'MLP_load_at_end': np.uint8, 'L3MLP_store_at_start': np.uint8, 'L3MLP_store_at_end': np.uint8, 'L3MLP_load_at_start': np.uint8, 'L3MLP_load_at_end': np.uint8, 'L3MLP_store_at_middle': np.uint8, 'L3MLP_load_at_middle': np.uint8}

        inst_types={'tlb_miss': np.uint8,'isLoad': np.uint8,'isStore': np.uint8,'isMicroop': np.uint8,'address': np.uint32,'lastStallTime': np.uint16,'totalTime': np.uint16, 'stallTime': np.uint16, 'L3stallTime': np.uint16, 
            'L3stallCyclesMLPLoad': np.uint16,
            'stallCyclesMLPBoth': np.uint64, 'MLP_store_at_start': np.uint8, 'MLP_store_at_end': np.uint8, 'MLP_load_at_start': np.uint8, 'MLP_load_at_end': np.uint8, 'L3MLP_store_at_start': np.uint8, 'L3MLP_store_at_end': np.uint8, 'L3MLP_load_at_start': np.uint8, 'L3MLP_load_at_end': np.uint8, 'L3MLP_store_at_middle': np.uint8, 'L3MLP_load_at_middle': np.uint8,

'stallCyclesMLPLoad': np.uint16,
'stallCyclesMLPStore': np.uint16,
'stallCyclesMLPBoth': np.uint16,
            
            }

    with open(run_meta, 'r') as file:
        for line in file:
            all_lines.append(line)


        for line in all_lines:
            try:
                _  = build_run_data(line)
                _['line'] = line
            except Exception as e:
                print(e)
                print(line)
                continue

            r_number = _['benchnr']
            if not r_number in all_data:
                all_data[r_number] = {}
            if _['increase'] in all_data[r_number]: 
                print("WARNING: Duplicate increase", line)
            

            all_data[r_number][_['increase']] = _ 
            #def get_run_name(run):
            #    return os.path.basename(run['0']['bench']).split('.')[0]

            #_['global'] = load_struct(GlobalStatsss,glob.glob(f"/mnt/nas/inesc/ist196723/osdi26/results_gem5/global_{_['pid']}_{_['host']}*.bin")[0])
            #_['inst'] = load_struct(InstructionData,glob.glob(f"/mnt/nas/inesc/ist196723/osdi26/results_gem5/aggregate_{_['pid']}_{_['host']}*.bin")[0])
            #_['final'] = load_struct(FinalMetrics,glob.glob(f"/mnt/nas/inesc/ist196723/osdi26/results_gem5/inst_{_['pid']}_{_['host']}*.bin")[0])
                #f"/mnt/nas/inesc/ist196723/osdi26/results_gem5/output_{rdata["host"]}.bin")


    return all_data

import numpy as np
import matplotlib.pyplot as plt





def get_field(run, struct,field_name, type_, convolve_skip=False, PID_ONLY=False, run_folder=None):
    if run_folder is None:
        run_folder = RUN_DATA_FOLDER
    if (run['pid'], struct, field_name) in cached_fields:
        return cached_fields[(run['pid'], struct, field_name)]
    if PID_ONLY:
        folder_chosen = f"{run_folder}/{run['pid']}" 
    else: 
        folder_chosen = f"{run_folder}/{run['pid']}-{run['host']}" 
    """
    candidates_expr = f"{RUN_DATA_FOLDER}/{run['pid']}-*/"
    candidates = glob.glob(candidates_expr)
    if len(candidates) == 0:
        raise Exception(f"No candidates found for {candidates_expr}")
    timestamp = run['STARTED']
    folder_chosen = ''
    if len(candidates) > 1:
        time = 999999
        for c in candidates:
            c_timestamp = c.split("-")[1]
            if timestamp > c_timestamp and time > c_timestamp:
                folder_chosen = c
    if folder_chosen == '':
        print(candidates, 'candidates')
        raise Exception("No candidate found for timestamp", timestamp)
    """
    arr =  np.fromfile(f"{folder_chosen}/_{struct}_{field_name}_{run['pid']}.txt", dtype=type_)
    #arr =  np.fromfile(f"{RUN_DATA_FOLDER}/{run['pid']}-{run['host']}/_{struct}_{field_name}_{run['pid']}.txt", dtype=type_)
    #print("Average window size", average_window_size)
    #print("convo", convolve_skip)
    if type(convolve_skip) == int and convolve_skip > 0:
        #print("humm")
        average_window_size = convolve_skip
        arr = np.convolve(arr, np.ones(average_window_size)/average_window_size, mode='valid')
        #print("Convolved", arr.shape[0], "to", arr.shape[0])
    cached_fields[(run['pid'], struct, field_name)] = arr
    return arr


#commited_0 = (get_field(data[r]['0'], GLOBAL, 'commitedInstructions', np.uint64))
#commited_0.shape[0]
def fill_if_needed(arr, size=None): 
    arr = np.diff(arr)
    # add 0 at the start
    #arr = np.insert(arr, 0, 0)
    if size is not None and arr.shape[0] < size:
        arr = np.pad(arr, (0, size - arr.shape[0]), 'constant')
    
    return arr

regress_error = []

def regress(arr, target):
    global regress_error
    # if dim does not match target fill to match
    biggest_size = max(arr.shape[0], target.shape[0])
    print(arr.shape[0], target.shape[0], "shappppping")
    if arr.shape[0] != target.shape[0]:
        # cut by the smallest
        if arr.shape[0] < target.shape[0]:
            target = target[:arr.shape[0]]
        else:
            arr = arr[:target.shape[0]]
    try:
        reg_stall =  np.linalg.lstsq(arr.reshape(-1, 1), target, rcond=None)
    except Exception as e:
        # if it fails to converge, return the original array.
        return arr
    # another method is to use curve fit. in that case, we need to define a function
    # and then use curve fit to find the best fit
    #print("Stall regression", reg_stall[0])
    predicted = arr * reg_stall[0]
    # pad to biggest size
    predicted = np.pad(predicted, (0, biggest_size - predicted.shape[0]), 'constant')
    # MSRE for this regression
    rmse = np.sqrt(np.mean((target - predicted) ** 2))
    #msre = np.mean(np.square(target - predicted) / target)
    regress_error.append(rmse)

    residuals = target - predicted
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((target - np.mean(target))**2)
    r_squared = 1 - ss_res / ss_tot
    #print(f"R² = {r_squared:.6f} 1-VAR")
    # 3 decimal float
    print(f'MSRE-N {rmse:.3f}')
    return predicted
    
from scipy.optimize import curve_fit
def obtain_soar_inst(selections, L3_MLP, L3_stall, acess_time, real):
    import numpy as np
    from scipy.optimize import curve_fit

    def fit_func(r, a, b):

    # A,B -0.4477149036453043 0.1349315011644008
        #soar_metric = i['stallTime'][sel] /  ( i['L3MLP_load_at_middle'][sel] * b  + a * i['totalTime'][sel] ) 
        results = np.zeros(len(selection))
        print('ho')
        for i in range(len(selection)):
            results[i] = np.sum( L3_stall[i] / (a*L3_MLP[i] + b * acess_time[i]) )
        print('hi')
        return results

    print('0llll')
    initial_guess = [10, 1]
    popt, pcov = curve_fit(fit_func, np.array(range(len(selections))), real, p0=initial_guess, maxfev=1000)
    a_opt, b_opt = popt
    a_err, b_err = np.sqrt(np.diag(pcov))
    fitted_real = fit_func(L3_stall, a_opt, b_opt)

    residuals = real - fitted_real
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((real - np.mean(real))**2)
    r_squared = 1 - ss_res / ss_tot
    rmse = np.sqrt(np.mean((real - fitted_real) ** 2))
    regress_error.append(rmse)
    print(f'MSRE-S {rmse:.3f}')
    return [fitted_real, a_opt, b_opt, rmse]
OPTIMAL_A = None
OPTIMAL_B = None
def obtain_soar_mlp_aware_slowdown(unadjusted, AOL, out):
    global OPTIMAL_A
    global OPTIMAL_B
    import numpy as np
    from scipy.optimize import curve_fit

    # Example data arrays; replace these with your actual data
    # AOL: array of AOL values
    # unadj: array of unadjusted_slowdown values
    # real: array of real_slow_down values
    real = out

    # Define the fitting function:
    # f(AOL, a, b) = unadjusted_slowdown * 1 / (a + b / AOL)
    def model(AOL, a, b, unadjusted):
        return unadjusted * 1.0 / (a + b / AOL)

    # We need a wrapper that takes AOL and parameters a, b, then uses unadj inside
    def fit_func(AOL, a, b):
        return model(AOL, a, b, unadjusted)

    # Initial guesses for a and b
    initial_guess = [0.78, 0.231]

    # Perform the curve fit
    popt, pcov = curve_fit(fit_func, AOL, real, p0=initial_guess)

    # Extract the optimal parameters
    a_opt, b_opt = popt
    # Compute standard deviations (uncertainties) of the parameters
    a_err, b_err = np.sqrt(np.diag(pcov))

    #print(f"Fitted parameters:")
    #print(f" a = {a_opt:.6f} ± {a_err:.6f}")
    #print(f" b = {b_opt:.6f} ± {b_err:.6f}")

    # Optional: compute the fitted real_slow_down values
    fitted_real = fit_func(AOL, a_opt, b_opt)
    print('OPTIMAL A AND B ', a_opt, b_opt)
    OPTIMAL_A = a_opt
    OPTIMAL_B = b_opt
    # Example: compute and print R-squared
    residuals = real - fitted_real
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((real - np.mean(real))**2)
    r_squared = 1 - ss_res / ss_tot
    #print(f"R² = {r_squared:.6f} SOAR")

    rmse = np.sqrt(np.mean((real - fitted_real) ** 2))
    #msre = np.mean(np.square(target - predicted) / target)
    regress_error.append(rmse)


    print(f'MSRE-S {rmse:.3f}')
    #print('MSRE-S', rmse)
    return fitted_real

# TAG absolute_increase

by_interval = {'real_slowdown': np.array([]), 'run': ([]), 'metrics': 
    {
'llc_count': np.array([]),
'stall_cycles': np.array([]), 
'totalTime': np.array([]),
'L3stalls': np.array([]), 
'stallsMLP': np.array([]),
'L3stallsMLP': np.array([]),
    }
               
               
               }

def get_last_idx_of_smallest_vector(a,b):
                        len_a = len(a)
                        len_b = len(b)
                        smalleset = min(len_a, len_b)
                        return smalleset - 1
def calculate_by_sample_cost(data,r):
                def get_all_instructions():
                    global runs_with_weird_stuff
                    #
                    d = {} # load_aggregate_fields(data,r)
                    gcres = load_global_fields_crescendo(data,r)
                    gcres80 = load_global_fields_crescendo(data,r,'80')
                    g0 = load_global_fields(data,r)
                    g80 = load_global_fields(data,r,'80')
                    last_idx = get_last_idx_of_smallest_vector(gcres80['currentCycle'],gcres['currentCycle'])
                    print("LASST_IDX", last_idx)


                    ######################## NOW - optimizing L3MLP 
                    # indexes changed
                    #

                    stop_getting_samples = gcres['currentCycle'][last_idx]
                    i = load_inst_fields(data,r, stop=stop_getting_samples)
                    inst = i
                    i80 = load_inst_fields(data,r,'80', stop=stop_getting_samples)
                    # check that len(i['address'] is the same as  i['L3MLP_load_at_middle']
                    #if len(i['address']) != len(i['L3MLP_load_at_middle']):
                    #    raise Exception("Length of address and L3MLP_load_at_middle is not the same")
                    ignore_no_stalls_in_l3 = True
                    instruction_metrics = True
                    if not instruction_metrics: 
                        i = load_aggregate_fields(data,r)
                        i80 = load_aggregate_fields(data,r,'80')
                    else:
                        #'totalTime', 'L3stallTime',
                        err=0
                        for v in [
                            'MLP_store_at_start', 'MLP_store_at_end', 'MLP_load_at_start', 'MLP_load_at_end',
                            'L3MLP_load_at_middle', 'L3MLP_load_at_end',
                             'L3MLP_store_at_start', 'L3MLP_store_at_middle', 'L3MLP_store_at_end', 'L3MLP_load_at_start']:
                            # verify that no value is less than 0 or greater than 50
                            print(v, np.histogram(i[v], bins=5))
                            if np.min(i[v]) < 0 or np.max(i[v]) > 50:
                                print("ERROR VALUES IN"*100, v)
                                print(np.unique(i[v]))
                                err=1
                                # print unique values 
                                runs_with_weird_stuff += 1
                                print(runs_with_weird_stuff)
                        if err:
                            raise Exception(f"Values in {v} are out of bounds")
                    
                    # TLB MISS IS BROKEN ...................................................
                    if ignore_no_stalls_in_l3:
                        print(np.unique(i['isLoad']))
                        #(i['L3stallTime'] > 0)
                        indexes =  ( (i['totalTime'] > 100)  & (i['isStore'] == 0) & (i['isLoad'] == 1)  & (i['tlb_miss'] == 0) )
                    else:
                        indexes =  (i['totalTime'] > 100)
                    
                    
                    indexes = np.where(indexes)
                    #indexes = all
                    indexes = np.where(i['totalTime'] > 0)


                    #np.where((i['totalTime'] > 30) & (i['tlbMiss'] == 0))
                    # print the distribution of totalTime

                    #return d
                    
                    #d['absolute_increase'] =  (gcres80['currentCycle'][last_idx] - gcres['currentCycle'][last_idx]) 
                    # obtain nr of entries
                    nr_of_insts = len(inst['stallTime'][indexes])
                    print("Nr of insts", nr_of_insts)
                    if nr_of_insts == 0:
                        raise Exception("No instructions found")

                    #if last_idx < 1000:
                    #    raise Exception("Not enough cycles found")

                                            
                    cycles_elapsed = gcres['currentCycle'][last_idx]  / 1000 
                    #commitedInstructions']
                    
                    print("CYCLES ELAPSED", cycles_elapsed)
                    #for normalizing_factor in ( (cycles_elapsed, "_cycles"), (1, "_abs")):

                    def by_interval_calc():
                        by_interval['run'].append(r)
                        #slow_downs = g80['currentCycle']-g0['currentCycle']
                        ag80 =  load_aggregate_fields(data,r,'80')
                        ag0 =  load_aggregate_fields(data,r)
                        indexes = np.where((ag0['totalTime'] > 30) & (ag0['address'] != 0))
                        # flat append
                        #ag0['count']
                        try:
                            import warnings
                            with warnings.catch_warnings():
                                warnings.filterwarnings('error', category=RuntimeWarning)  # Convert warning into error
                                try:
                                    ########################################## :last_idx
                                    slow = gcres80['currentCycle'][:last_idx]/gcres['currentCycle'][:last_idx]
                                    #(gcres80['currentCycle'][last_idx]-gcres80['currentCycle'][5]) - (gcres['currentCycle'][last_idx]-gcres['currentCycle'][5])  #slow g80['currentCycle'][last_idx] / g0['currentCycle'][last_idx] #g0 (gcres80['currentCycle'][last_idx] ) / gcres['currentCycle'][last_idx]
                                    #by_interval['real_slowdown'] = slow 
                                    by_interval['real_slowdown'] = np.append(by_interval['real_slowdown'], slow)
                                except RuntimeWarning as e:
                                    # print stack trace
                                    import traceback
                                    traceback.print_exc()
                                    return
                                # sum in invervals where count == 0 and address = 0 in ag0
                                indexes = np.where((ag0['count'] == 0) & (ag0['address'] == 0))
                                # for each index, get the list of indexes until the next index
                                for i in range(len(indexes)-1):
                                    # get the list of indexes until the next index
                                    len_interval = indexes[i+1] - indexes[i]
                                    indexes_in_interval = [n for n in range(indexes[i], indexes[i+1])]
                                    indexes = np.intersect1d(indexes_in_interval, np.where(ag0['totalTime'] > 30)[0])
                                    # sum the values in the list

                                    by_interval['metrics']['llc_count'] = np.append(by_interval['metrics']['llc_count'], ag0['count'][indexes].sum())
                                    by_interval['metrics']['stall_cycles'] = np.append(by_interval['metrics']['stall_cycles'], (ag0['stallCyclesMLPLoad'][indexes]*ag0['count'][indexes]).sum())
                                    by_interval['metrics']['totalTime'] = np.append(by_interval['metrics']['totalTime'], (ag0['totalTime'][indexes]*ag0['count'][indexes]).sum())
                                    by_interval['metrics']['L3stalls'] = np.append(by_interval['metrics']['L3stalls'], (ag0['L3stallTime'][indexes]*ag0['count'][indexes]).sum())
                                    by_interval['metrics']['stallsMLP'] = np.append(by_interval['metrics']['stallsMLP'], (ag0['stallCyclesMLPLoad'][indexes]*ag0['count'][indexes]).sum())
                                    by_interval['metrics']['L3stallsMLP'] = np.append(by_interval['metrics']['L3stallsMLP'], (ag0['L3stallCyclesMLPLoad'][indexes]*ag0['count'][indexes]).sum())

                        except Exception as e:
                            print("saddddlly")
                            raise e
                            exit(0)
                            pass
                    by_interval_calc()
                    try:
                        import warnings
                        with warnings.catch_warnings():
                            warnings.filterwarnings('error', category=RuntimeWarning)  # Convert warning into error
                            try:
                                #   - gcres['currentCycle'][last_idx]
                                slow = gcres80['currentCycle'][last_idx]/gcres['currentCycle'][last_idx]
                                #(gcres80['currentCycle'][last_idx]-gcres80['currentCycle'][5]) - (gcres['currentCycle'][last_idx]-gcres['currentCycle'][5])  #slow g80['currentCycle'][last_idx] / g0['currentCycle'][last_idx] #g0 (gcres80['currentCycle'][last_idx] ) / gcres['currentCycle'][last_idx]
                                d['real_slowdown'] = slow 
                            except RuntimeWarning as e:
                                # print stack trace
                                import traceback
                                traceback.print_exc()
                                raise e
                        d['stall_cycles'] =  gcres['stalledCycles'][last_idx] 


                        d['RUN_DATA'] = data[r]
                        # cost * rate of accesses
                        cycles_elapsed = cycles_elapsed 
                        inside_factor = i['L3stallTime'][indexes]/100 # multiply by rate of sampling  #/nr_of_insts
                        inside_factor = 1
                        d['cost_inst_LLCmiss_abs'] = nr_of_insts 
                        d['cost_inst_stall_time_abs'] = np.sum(i['stallTime'][indexes]/inside_factor) 
                        d['cost_inst_L3stall_time_abs'] = np.sum(i['L3stallTime'][indexes]/inside_factor) 
                        d['cost_inst_L3MLP_abs'] = np.sum(i['L3stallCyclesMLPLoad'][indexes]/inside_factor) 
                        d['cost_inst_stalls'] = np.sum(i['stallTime'][indexes]/inside_factor) /cycles_elapsed
                        d['cost_inst_MLP_abs'] = np.sum(i['stallCyclesMLPLoad'][indexes]/inside_factor) 
                        d['cost_inst_stall_time'] = np.sum(i['stallTime'][indexes]/inside_factor) / cycles_elapsed
                        d['cost_inst_L3stall_time'] = np.sum(i['L3stallTime'][indexes]/inside_factor) / cycles_elapsed
                        d['cost_inst_L3MLP'] = np.sum(i['L3stallCyclesMLPLoad'][indexes]/inside_factor) / (cycles_elapsed*MLP_PRECISION_FACTOR)
                        d['cost_inst_MLP'] = np.sum(i['stallCyclesMLPLoad'][indexes]/inside_factor) / (cycles_elapsed*MLP_PRECISION_FACTOR)


                        d['average_mlp_middle'] = np.sum(inst['L3MLP_load_at_middle'][indexes]) / cycles_elapsed
                        d['average_mlp_end'] = np.sum(inst['L3MLP_load_at_end'][indexes]) / cycles_elapsed
                        d['average_mlp_start'] = np.sum(inst['L3MLP_load_at_start'][indexes]) / cycles_elapsed
                        d['cost_inst_LLCmiss'] = nr_of_insts / cycles_elapsed
                        d['cost_inst_total_time'] = np.sum(i['totalTime'][indexes]) / cycles_elapsed

                        d['cost_inst_diff_stall'] = np.sum(i80['stallTime']-i['stallTime']) / gcres['currentCycle'][-1]
                        d['cost_inst_diff_total'] = np.sum(i80['totalTime']-i['totalTime']) / gcres['currentCycle'][-1]
                    except:
                        import traceback
                        traceback.print_exc()
                        print("NOT OKAY")


                    return d
                    d['cost_inst_L3stall/total'] = np.sum(i['L3stallTime']/i['totalTime']) / gcres['currentCycle'][last_idx]

                    d['cost_inst_3MLP/3stall'] = np.sum(i['L3stallCyclesMLPLoad']/i['L3stallTime']) / gcres['currentCycle'][last_idx]
                    d['cost_inst_MLP/stall'] = np.sum(i['stallCyclesMLPLoad']/i['stallTime']) / gcres['currentCycle'][last_idx]
                    d['cost_inst_MLP*total/stall'] = np.sum(i['stallCyclesMLPLoad']*i['totalTime']/i['stallTime']) / gcres['currentCycle'][last_idx]
                    d['cost_inst_MLP/total'] = np.sum(i['stallCyclesMLPLoad']/i['totalTime']) / gcres['currentCycle'][last_idx]

                    gcres = load_global_fields_crescendo(data,r)
                    d['cost_aggregate_l3mlp'   ] = np.sum(d['L3stallCyclesMLPLoad']*d['count']) / gcres['currentCycle'][last_idx]
                    d['cost_aggregate_mlp'     ] = np.sum(d['stallCyclesMLPLoad']*d['count']) / gcres['currentCycle'][last_idx]
                    d['cost_aggregate_time'    ] = np.sum(d['totalTime']*d['count']) / gcres['currentCycle'][last_idx]
                    d['cost_aggregate_l3stalls'] = np.sum(d['L3stallTime']*d['count']) / gcres['currentCycle'][last_idx]
                    d['cost_aggregate_stalls'  ] = np.sum(d['stallTime']*d['count']) / gcres['currentCycle'][last_idx]


                    #d['cost_inst_diff_l3stall'] = np.sum(i80['L3stallTime']-i['L3stallTime'])
                    # limit arrays to be of the smallest size of the two
                    def limit_array(arr1, arr2):
                        return arr1[:min(len(arr1), len(arr2))], arr2[:min(len(arr1), len(arr2))]
                    i80['stallTime'], i['stallTime'] = limit_array(i80['stallTime'], i['stallTime'])
                    i80['L3stallCyclesMLPLoad'], i['L3stallCyclesMLPLoad'] = limit_array(i80['L3stallCyclesMLPLoad'], i['L3stallCyclesMLPLoad'])
                    i80['totalTime'], i['totalTime'] = limit_array(i80['totalTime'], i['totalTime'])
                    try:
                        d['cost_inst_diff_stall'] = np.sum(i80['stallTime']-i['stallTime']) / gcres['currentCycle'][-1]
                        d['cost_inst_diff_%L3MLP'] = np.sum(((i80['L3stallCyclesMLPLoad']/i80['totalTime'])-(i['L3stallCyclesMLPLoad']/i['totalTime'])))/ gcres['currentCycle'][-1]
                    except:
                        pass



                    d['L3stallTime80'] = get_field(data[r]['80'], AGGREGATE, 'L3stallTime', np.uint64)
                    d['stallTime80'] = get_field(data[r]['80'], AGGREGATE, 'stallTime', np.uint64)
                    d['totalTime80'] = get_field(data[r]['80'], AGGREGATE, 'totalTime', np.uint64)




                    # filter all indexes where accessBracket * 16 > 30
                    #print(d['accessBracket'])

                    time_step_changes = np.where(d['count'] == 0)
                    unique_instructions = np.unique(d['address'])
                    unique_accessBrackets = np.unique(d['accessBracket'])
                    print("Run name", data[r]['0']['bench'])
                    print("Unique instructions", unique_instructions.shape)
                    print("Unique access brackets", unique_accessBrackets.shape)
                    print("Number of samples", np.sum(d['count']))
                    # do np.diff between indexes that have the same instruction, accessBracket on the variable given
                    def diff_by_instruction_and_accessBracket(fields):
                        for i in unique_instructions:
                            idx = np.where(d['address'] == i)
                            for ab in unique_accessBrackets:
                                idx2 = np.where(d['accessBracket'] == ab)
                                idx = np.intersect1d(idx, idx2)
                                for v in fields:
                                    d[v][idx] = np.diff(d[v][idx])
                    #diff_by_instruction_and_accessBracket(['L3MLP_store_at_middle', 'L3MLP_load_at_middle', 'L3stallTime', 'L3stallCyclesMLPLoad']) 

                    


                    

                    

                    valid_reports = np.where(d['count'] != 0)

                    d['accessBracket'] = d['accessBracket'] * 16
                    # print the type of accessBracket
                    #print(d['accessBracket'].dtype, d['accessBracket'].shape)
                    l3_idx = np.where(d['accessBracket'] > 0) # TRY ALL

                    l3_idx = np.intersect1d(l3_idx, valid_reports)
                    
                    

                    # distribution of accessBracket
                    def plot_histogram(data, bins=20):
                        for v in data:
                            plt.figure()
                            print("Doing v", v)
                            plt.hist(data[v][l3_idx]/data['count'][l3_idx], bins=bins)
                            plt.xlabel(v)
                            plt.ylabel('Frequency (normalized)')
                            plt.title(f'Histogram of {v}')
                            plt.savefig(f"{FIGS_FOLDER}/gen/vars/histogram_{v}_{bench_name}_{bench_nr}.png", dpi=300)
                            plt.close()
                            

                    #plot_histogram(d)
                    

                    def calc_cost_simple(dp):
                        return np.sum((d[dp][l3_idx]*d['count'][l3_idx])) #/np.sum(d['count'])

                    def calc_cost_buffer_pressure(dp):
                        idx = np.where(d['L3MLP_store_at_middle'][l3_idx]/d['count'][l3_idx] > 5)                       
                        print('L3MLP_store_at_middle',  d['L3MLP_store_at_middle'][l3_idx])
                        # duplicate the weight where idx is true
                        #copy the array

                        d['count-'] = np.copy(d['count'][l3_idx])
                        d['count-'][idx] = d['count'][l3_idx][idx]*100
                        return np.sum((d[dp][l3_idx]*d['count-'])) #/np.sum(d['count'])
                    
                    aggregate_cost =  ((d['L3stallTime'][l3_idx]*d['count'][l3_idx]) /d['totalTime'][l3_idx])
                    d['cost_avg_percentage_l3stall'] = np.sum(aggregate_cost) #/ np.sum(d['count'][l3_idx])

                    #idx = np.where(d['L3MLP_store_at_middle'][l3_idx]/d['count'][l3_idx] > 5)                       
                    high_mlp = d['L3MLP_load_at_middle'][l3_idx]/d['count'][l3_idx] > 5
                    # print range of values (smallest and greatest) of L3MLP_load_at_middle
                    print('L3MLP_load_at_middle', np.min(d['L3MLP_load_at_middle'][l3_idx]/d['count'][l3_idx]), np.max(d['L3MLP_load_at_middle'][l3_idx]/d['count'][l3_idx]), 
                    # print median
                    np.median(d['L3MLP_load_at_middle'][l3_idx]/d['count'][l3_idx])
                          
                          
                          )
                    print('L3MLP_store_at_middle', np.min(d['L3MLP_store_at_middle'][l3_idx]/d['count'][l3_idx]), np.max(d['L3MLP_store_at_middle'][l3_idx]/d['count'][l3_idx]), 
                    # print median
                    np.median(d['L3MLP_store_at_middle'][l3_idx]/d['count'][l3_idx]))

                    #d['count-'] = np.copy(d['count'][l3_idx])
                    # make array of 0.5  where is true and of 1 where its not
                    d['weights'] = np.where(high_mlp, 0.5, 1)
                    #d['count-'][idx] = d['count'][l3_idx][idx]/2
                    aggregate_cost =  ((d['L3stallTime'][l3_idx]*d['count'][l3_idx]*d['weights']))
                    d['cost_avg_%_l3stall_buffpre'] = np.sum(aggregate_cost) #/ np.sum(d['count'][l3_idx])



                    
                    #d['cost_aggregate_stalls'] = np.sum(d['stalledCycles'][l3_idx]*d['count'][l3_idx]) / gcres['currentCycle'][-1]
                    
                    d['cost_inst_l3_mlp'] = np.sum(np.sqrt(inst['L3stallCyclesMLPLoad']*inst['L3stallTime']))
                    d['cost_inst_l3stall'] = np.sum(inst['L3stallTime'])
                    d['cost_inst_stall'] = np.sum(inst['stallTime'])
                    print("NUMBER OF SAMPLES", inst['L3stallTime'].shape)
                        


                    d['cost_avg_l3_stalls'] = calc_cost_simple('L3stallTime')
                    d['cost_avg_l3_mlp'] = calc_cost_simple('L3stallCyclesMLPLoad')
                    d['cost_l3_mlp'] = np.sum(d['L3stallCyclesMLPLoad'][l3_idx]*d['count'][l3_idx])


                    gcres = load_global_fields_crescendo(data,r,'0')
                    #d['cost_delta_l3stall'] =  np.sum((d['L3stallTime80'][l3_idx]-d['L3stallTime'][l3_idx])*d['count'][l3_idx]) / gcres['currentCycle'][-1]
                    #d['cost_delta_stall'] =  np.sum((d['stallTime80'][l3_idx]-d['stallTime'][l3_idx])*d['count'][l3_idx]) / gcres['currentCycle'][-1]
                    #d['cost_delta_time'] =  np.sum((d['totalTime80'][l3_idx]-d['totalTime'][l3_idx])*d['count'][l3_idx]) /  gcres['currentCycle'][-1]

                    d['cost_buffer_pressure'] = calc_cost_buffer_pressure('L3stallCyclesMLPLoad')  
                    
                    # COMPARE COST WITH --> GET THE SOAR WEIGHT FOR THIS INSTANT AND MULTIPLY BY THE SAMPLE
                    # sum(PER timestep nr _of samples *mem_stalls_0/cycles_0)
                    # sum(PER timestep adjusted soar * nr of samples  ) 

                    return d

                print('Cost....')
                d = get_all_instructions()
                return d
                #cost_keys = ['stallCyclesMLPLoad', 'stallCyclesMLPStore', 'stallCyclesMLPBoth', 'stalledCycles', 'L3stalledCycles' , 'L3stallCyclesMLPLoad'] # delta
                fast_execution_time = get_field(data[r]['0'], GLOBAL, 'currentCycle', np.uint64)[-1] 
                slow_execution_time = get_field(data[r]['80'], GLOBAL, 'currentCycle', np.uint64)[-1] 

                #total_l3_cost = get_field(data[r]['0'], GLOBAL, 'L3stalledCycles', np.uint64)[-1] 

                #############  learn_weights(data,r)
             

                all_memory_stalls_0 = get_field(data[r]['0'], GLOBAL, 'stalledCycles', np.uint64)[-1]
                memory_stalls_0 = get_field(data[r]['0'], GLOBAL, 'L3stalledCycles', np.uint64)[-1]
                memory_stalls_80 =get_field(data[r]['80'], GLOBAL, 'L3stalledCycles', np.uint64)[-1]
                # print how close a variable is to uint64 max in percentage
                print('HEALTH: memory_stalls', memory_stalls_0 / np.iinfo(np.uint64).max)
                def v_health(d, v):
                    # if is not a a scaler
                    value = d[v]
                    if not np.isscalar(d[v]):
                        value = d[v][-1]
                    way =  value / np.iinfo(np.uint64).max
                    if way > 0.5:
                        print("HEALTH", v, way)
                for k in list(d.keys()):
                    v_health(d, k)

                d['cost_soar_simple'] = memory_stalls_0 / fast_execution_time
                d['cost_l3_stalls'] = memory_stalls_0
                d['cost_all_stalls'] = all_memory_stalls_0
                d['cost_demand_pressure'] =  np.sum(d['L3MLP_load_at_middle'])/ fast_execution_time
                d['cost_store_pressure'] =  np.sum(d['L3MLP_store_at_middle'])/ fast_execution_time

                d['cost_real'] =  slow_execution_time / fast_execution_time 
                for k in list(d.keys()):
                    if 'cost' not in k:
                        continue
                    """
                    d['cost_' + k + "_normalized"] = d[k]/ fast_execution_time
                    d['cost_' + k + "_normalized_m0"] = d[k]/ memory_stalls_0
                    d['cost_' + k + "_normalized_m80"] = d[k]/ memory_stalls_80
                    if 'cost_' + k + "_normalized" not in cost_workloads:
                        cost_workloads['cost_' + k + "_normalized"] = []
                        cost_workloads['cost_' + k + "_normalized_m0"] = []
                        cost_workloads['cost_' + k + "_normalized_m80"] = []
                    cost_workloads['cost_' + k + "_normalized"].append(d['cost_' + k + "_normalized"])
                    cost_workloads['cost_' + k + "_normalized_m0"].append(d['cost_' + k + "_normalized_m0"])
                    cost_workloads['cost_' + k + "_normalized_m80"].append(d['cost_' + k + "_normalized_m80"])
                    """

                    if k not in cost_workloads:
                        cost_workloads[k] = []
                    
                    cost_workloads[k].append(d[k])
                
                naming_cost_workloads.append(f"{bench_name}_{bench_nr}")
                print(cost_workloads['cost_real'])
                
                print("Cost real", d['cost_real'])
                print("Cost avg percentage l3 stall", d['cost_avg_percentage_l3stall'])
                print("Cost avg l3 stalls", d['cost_avg_l3_stalls'])
                print("Cost avg l3 mlp", d['cost_avg_l3_mlp'])
                return d

def giant_pair_plot(data):
    import pandas as pd
    import seaborn as sns
    import matplotlib.pyplot as plt
    return 

    # Suppose `df` is your DataFrame with 100 columns named X1…X100
    # df = pd.read_csv("your_data.csv")

    # 1. Option A: Seaborn pairplot (includes histograms on the diagonal)
    sns.set(style="ticks")
    plt.figure(figsize=(20,20))

    # By default, pairplot samples 250 rows; you can override with `subset`
    # or pass your full DataFrame at your own risk of slowness:
    # to reduce memory usage we can
    # only plot the first 250 rows
    # show the shapes of all dataframes
        
    # sample 250 rows from each dataframe

    # do N pair plots instead of a gigantic one

    
    # reduce all numbers to uint64
    print("---")
    print(data.shape)
    print(len(data))
    #data=data.copy()
    print(data.shape)
    print(len(data))

    print("---")

    print("---")
    for k in data:
        print(k)
        data.loc[:, k] = data.loc[:, k].astype(np.uint64)
        print(len(data.loc[:, k]))

    # AOL correlation with slow down
    # AOL * unadjusted_slowdown correlation

    # remove commitedInstructions column
    data = data.drop(columns=['commitedInstructions'])
    # rem commitedAtomic_delta
    data = data.drop(columns=['commitedAtomic_delta'])
    # drop 
    data = data.drop(columns=['stalledCyclesWithMemRequests_delta'])

    
    #df_sample = data.sample(n=3000, random_state=42, replace=True)
    pair_grid = sns.pairplot(data,
                            corner=True,        # if True, only lower triangle
                            diag_kind="hist",    # or "kde"

                            plot_kws={'s':5, 'alpha':0.5}) # this variable controls the size of the points


    # Tighten layout and show
    plt.tight_layout()
    # save  with ultra high resolution 
    plt.savefig(f"{FIGS_FOLDER}/gen/correlation/pairplot_{bench_name}_{bench_nr}.png", dpi=300)
    plt.show()



global_results = {'real_slowdown': [], 'stall_cycles': [], 'mlp_stall': [], 'load+commit': [], 'cycles': [],
'mem_stalls': [],
'store_stalls': [],
'mem_stalls_weighted': [],
'aol': [],
'commitedLoads': [], 'currentCycle' : [], 'percentStallCycles': [], 'percentmem_stalls_weighted': []
                  
                  }
    
# each should be numpy arrays, that will be concated together
global_all_dps_results = {'real_slowdown': np.array([]), 'stall_cycles': np.array([]), 'mlp_stall': np.array([]), 'load+commit': np.array([]), 'cycles': np.array([]),
'mem_stalls': np.array([]),
'store_stalls': np.array([]),
'mem_stalls_weighted': np.array([]),
'aol': np.array([]),
'commitedLoads': np.array([]), 
'percentStallCycles': np.array([]),
'percentmem_stalls_weighted': np.array([])
                  }
            

default_set = global_results.copy()
global_results_per_bench = []
global_results_per_bench_id = []

cost_workloads = {'cost_avg_percentage_l3stall': [], 'cost_avg_l3_stalls': [], 'cost_avg_l3_mlp': [], 'cost_real': []}
naming_cost_workloads = []
BEST_MODELED_WORKLOADS = []

class DictWithGet(dict):
    def set_getter(self, getter):
        self.getter = getter
        
    def __getitem__(self, key):
        if key in self:
            return super().__getitem__(key)
        else:
            v =  self.getter(key)
            self[key] = v
            return v

fields = ['address' ,'totalTime', 'accessBracket','L3MLP_store_at_middle', 'L3MLP_load_at_middle', 'stallTime', 'L3stallTime', 'count' , 'stallCyclesMLPLoad', 'stallCyclesMLPStore', 'stallCyclesMLPBoth', 'L3stallCyclesMLPLoad'] # delta
inst_types={'average_l3mlp': np.uint8, 'average_mlp' :np.uint8, 'tlb_miss': np.uint8,'isLoad': np.uint8,'isStore': np.uint8,'isMicroop': np.uint8,'address': np.uint64,'lastStallTime': np.uint16,'totalTime': np.uint16, 'stallTime': np.uint16, 'L3stallTime': np.uint16, 
            'L3stallCyclesMLPLoad': np.uint32, # CHANGE
            'stallCyclesMLPBoth': np.uint64, 'MLP_store_at_start': np.uint8, 'MLP_store_at_end': np.uint8, 'MLP_load_at_start': np.uint8, 'MLP_load_at_end': np.uint8, 'L3MLP_store_at_start': np.uint8, 'L3MLP_store_at_end': np.uint8, 'L3MLP_load_at_start': np.uint8, 'L3MLP_load_at_end': np.uint8, 'L3MLP_store_at_middle': np.uint8, 'L3MLP_load_at_middle': np.uint8,



'start_cycle': np.uint64,
'L3stallTime': np.uint16,
'stallCyclesMLPLoad': np.uint64,
'stallCyclesMLPStore': np.uint64,
'stallCyclesMLPBoth': np.uint64,
            
            }

inst_types={'average_l3mlp': np.uint8, 'average_mlp' :np.uint8, 'tlb_miss': np.uint8,'isLoad': np.uint8,'isStore': np.uint8,'isMicroop': np.uint8,'address': np.uint64,'lastStallTime': np.uint16,
            'totalTime': np.uint16, 'stallTime': np.uint16, 'L3stallTime': np.uint16, 
            'L3stallCyclesMLPLoad': np.uint32, 'stallCyclesMLPBoth': np.uint32, 'MLP_store_at_start': np.uint8, 'MLP_store_at_end': np.uint8, 'MLP_load_at_start': np.uint8, 'MLP_load_at_end': np.uint8, 'L3MLP_store_at_start': np.uint8, 'L3MLP_store_at_end': np.uint8, 'L3MLP_load_at_start': np.uint8, 'L3MLP_load_at_end': np.uint8, 'L3MLP_store_at_middle': np.uint8, 'L3MLP_load_at_middle': np.uint8,



'start_cycle': np.uint64,
'L3stallTime': np.uint16,
'stallCyclesMLPLoad': np.uint32,
'stallCyclesMLPStore': np.uint32,
'stallCyclesMLPBoth': np.uint32,
            
            }

#inst_types={'accessedMemory': np.uint64,'address': np.uint64,'totalTime': np.int16, 'stallTime': np.int16, 'L3stallTime': np.int16, 'lastStallTime': np.int16, 'stallCyclesMLPLoad': np.int64, 'stallCyclesMLPStore': np.int64, 'stallCyclesMLPBoth': np.int64, 'L3stallCyclesMLPLoad': np.int64, 'MLP_store_at_start': np.uint8, 'MLP_store_at_end': np.uint8, 'MLP_load_at_start': np.uint8, 'MLP_load_at_end': np.uint8, 'L3MLP_store_at_start': np.uint8, 'L3MLP_store_at_middle': np.uint8, 'L3MLP_store_at_end': np.uint8, 'L3MLP_load_at_start': np.uint8, 'L3MLP_load_at_middle': np.uint8, 'L3MLP_load_at_end': np.uint8, 'isMicroop': np.uint8, 'tlb_miss': np.uint8,'isLoad': np.uint8,'isStore': np.uint8,'start_cycle': np.uint64,}
inst_fields = fields + ['lastStallTime']
def load_inst_fields(data, r, tier='0', stop=np.inf):
    inst = DictWithGet()
    def gettter(f, stop):
        field =  get_field(data[r][tier], INST, f, inst_types[f], convolve_skip=False)
        if f == 'start_cycle':
            return field
        if stop == np.inf:
            return field
        idxs = np.where(inst['start_cycle'] < stop)
        return field[idxs]
    inst.set_getter(lambda f: gettter(f,stop))
    return inst
aggregate_types = {'totalTime': np.uint64, 
                   'count': np.uint64, 
                   'accessBracket': np.uint8, 'address': np.uint64,
                   'isLoad' : np.uint8,
                   'isStore' : np.uint8,
                   'isMicroop' : np.uint8,
                   'tlbMiss' : np.uint8,
                   'stallTime' : np.uint64,
                   'L3stallTime': np.uint64,
                   'totalTime': np.uint64,
                   'lastStallTime': np.uint64,
                   'L3MLP_load_at_end': np.uint64,
                   'MLP_load_at_end': np.uint64,
                   'MLP_store_at_end': np.uint64,
                   'L3MLP_store_at_end': np.uint64,
                   'L3MLP_store_at_middle': np.uint64,
                   'L3MLP_load_at_middle': np.uint64,
                   'stallCyclesMLPLoad': np.uint64,
                   'L3stallCyclesMLPLoad': np.uint64,
                   'stallCyclesMLPStore': np.uint64,
                   'stallCyclesMLPBoth': np.uint64,
                   }

"""
aggregate_types = {'totalTime': np.uint64, 
                   'count': np.uint64, 
                   'accessBracket': np.uint8, 'address': np.uint64,
                   'isLoad' : np.uint8,
                   'isStore' : np.uint8,
                   'isMicroop' : np.uint8,
                   'tlbMiss' : np.uint8,
                   'stallTime' : np.uint64,
                   'L3stallTime': np.uint64,
                   'totalTime': np.uint64,
                   'lastStallTime': np.uint64,
                   'L3MLP_load_at_end': np.uint64,
                   'MLP_load_at_end': np.uint64,
                   'MLP_store_at_end': np.uint64,
                   'L3MLP_store_at_end': np.uint64,
                   'L3MLP_store_at_middle': np.uint64,
                   'L3MLP_load_at_middle': np.uint64,
                   'stallCyclesMLPLoad': np.uint64,
                   'L3stallCyclesMLPLoad': np.uint64,
                   'stallCyclesMLPStore': np.uint64,
                   'stallCyclesMLPBoth': np.uint64,
                   }
"""

global_types = {'totalSquashed': np.uint64,
'totalStalledCyclesSummed': np.uint64,
'totalL3StalledCyclesSummed': np.uint64,
'totalL3MLPStalledCyclesSummed': np.uint64,
'totalMLPStalledCyclesSummed': np.uint64,
    'L3stallCyclesMLPLoad': np.uint64,
    'stallCyclesMLPStore': np.uint64,
    'stallCyclesMLPBoth': np.uint64,
    'currentCycle': np.uint64, 'L3stalledCycles': np.uint64, 'stalledCycles': np.uint64, 'stalledCyclesDuringStore': np.uint64, 'stalledCyclesWithMemRequests': np.uint64, 'stalledCyclesWithStores': np.uint64, 'cyclesWithMemrequests': np.uint64, 'commitedStores': np.uint64, 'commitedLoads': np.uint64, 'commitedAtomic': np.uint64, 'commitedInstructions': np.uint64, 'totalSquashed': np.uint64, 'lastStallTime': np.uint64, 'currentCycle': np.uint64,  'tlbMisses': np.uint64}

global_types = {
    'totalMLPsummed' : np.uint64,
    'totalL3MLPsummed' : np.uint64,
    'totalStalledCyclesSummed': np.uint64,
    'totalL3StalledCyclesSummed': np.uint64,
    'totalL3MLPStalledCyclesSummed': np.uint64,
    'totalMLPStalledCyclesSummed': np.uint64,


    'totalAccessTimeSummed': np.uint64,
    'totalL3AccessTimeSummed': np.uint64,
    'commitedL3Misses': np.uint64,
    'totalL3MLP_D_TotalAccessTimeSummed': np.uint64,
    'totalL3_D_TotalAccessTimeSummed': np.uint64,  # L333 stalls
    'totalMLPStalledCycles_D_TimeSummed': np.uint64,

    'totalL3StallSummed': np.uint64,

    'stallCyclesMLPLoad': np.uint64,
    'stallCyclesMLPStore': np.uint64,
    'stallCyclesMLPBoth': np.uint64,
    'stalledCycles': np.uint64,
    'stalledCyclesDuringStore': np.uint64,
    'stalledCyclesWithMemRequests': np.uint64,
    'stalledCyclesWithStores': np.uint64,
    'cyclesWithMemrequests': np.uint64,  # the diff between 2 = A1 of SOAR
    'commitedStores': np.uint64,
    'commitedL3Loads': np.uint64,  # The dif betweeen 2 = A2
    'commitedLoads': np.uint64,  # The dif betweeen 2 = A2
    'commitedAtomic': np.uint64,
    'commitedInstructions': np.uint64,
    'totalSquashed': np.uint64,
    'lastStallTime': np.uint64,
    'currentCycle': np.uint64,
    'loadCountByLatency': np.uint64,
    'tlbMisses': np.uint64,

    'onlyLoadsStalled': np.uint64,
    'onlyStoresStalled': np.uint64,
    'L3onlyLoadsStalled': np.uint64,
    'L3onlyStoresStalled': np.uint64,

    'L3stallCyclesMLPLoad': np.uint64,
    'L3stallCyclesMLPStore': np.uint64,
    'L3stallCyclesMLPBoth': np.uint64,
    'L3stalledCycles': np.uint64,
    'L3stalledCyclesDuringStore': np.uint64,
    'L3cyclesWithMemrequests': np.uint64,  # the diff between 2 = A1 of SOAR
}

def load_aggregate_fields_frequency_normalized(data, r, tier='0'):
    # TODO
    d = DictWithGet()
    def get_it(f):
        global_to_inst_keys = {'cycles': 'totalTime'}
        if f in global_to_inst_keys:
            f = global_to_inst_keys[f]
        
        v = get_field(data[r][tier], AGGREGATE, f, np.uint64 if f not in aggregate_types else aggregate_types[f], convolve_skip=True)
        if f != 'count':
            return v/np.sum(d['count'])
        return v
    d.set_getter(get_it)
    return d 
def load_aggregate_fields_inst_normalized(data, r, tier='0'):
    # TODO
    d = DictWithGet()
    d.set_getter(lambda f : get_field(data[r][tier], AGGREGATE, f, aggregate_types[f], convolve_skip=True))
    return d 

def load_aggregate_fields(data, r, tier='0'):
    d = DictWithGet()
    d.set_getter(lambda f : get_field(data[r][tier], AGGREGATE, f, aggregate_types[f], convolve_skip=True))
    return d 

def load_global_fields_final_pmu(data, r, tier='0'):
    d = DictWithGet()
    d.set_getter(lambda f : get_field(data[r][tier], GLOBAL, f, global_types[f], convolve_skip=True)[-1])
    return d 

def load_global_fields_crescendo(data, r, tier='0'):
    d = DictWithGet()
    d.set_getter(lambda f : get_field(data[r][tier], GLOBAL, f, global_types[f], convolve_skip=True))
    return d 
def load_global_fields(data, r, tier='0', convolve=True, PID_ONLY=False, run_folder=None):
    d = DictWithGet()
    d.set_getter(lambda f : fill_if_needed(get_field(data[r][tier], GLOBAL, f, global_types[f], convolve_skip=convolve, PID_ONLY=PID_ONLY, run_folder=run_folder)))
    return d 

FAILURES_LINES = []
def all_bench_loader_inst(data,r, filter=lambda data,r: data[r]['0']['benchset'] == 'benches_final'):
    all_bench = DictWithGet()
    def get_all(f):
        """
        def obtain_aggregate_metrics(data, r):
            d = obtain_derivate_metrics(data,r, load_global_fields)
            for f in d:
                append_dict(f,d)
        """
        joined_arrays = []
        def get_f(data,r):
            if not filter(data,r):
                return
            try:
                joined_arrays.append(load_inst_fields(data,r)[f])
            except:
                FAILURES_LINES.append(data[r]['line'])
                pass
        iterate_over_benches(data, get_f) 
        return np.concatenate(joined_arrays)
    all_bench.set_getter(get_all)
    return all_bench
def all_bench_loader(data,r, filter=lambda data,r: data[r]['0']['benchset'] == 'benches_final'):
    all_bench = DictWithGet()
    def get_all(f):
        """
        def obtain_aggregate_metrics(data, r):
            d = obtain_derivate_metrics(data,r, load_global_fields)
            for f in d:
                append_dict(f,d)
        """
        joined_arrays = []
        def get_f(data,r):
            if not filter(data,r):
                return
            try:
                _ = load_global_fields(data,r)
                for r in fields:
                    n = _[r]
            except:
                FAILURES_LINES.append(data[r]['0']['line'])
            try:
                _80 = load_global_fields(data,r, '80')
                for r in fields: 
                    n80 = _80[r]
            except:
                FAILURES_LINES.append(data[r]['80']['line'])
            try:
                joined_arrays.append(_[f])
            except:
                #FAILURES_LINES.append(data[r]['line'])
                pass
        iterate_over_benches(data, get_f) 
        return np.concatenate(joined_arrays)
    all_bench.set_getter(get_all)
    return all_bench

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

def viz_accesses_over_time():
    file = "perf.txt"
    
    # Parse perf script output
    data = pd.read_csv(file, sep=r'\s+', header=None, dtype=str)
    
    timestamps = pd.to_numeric(data[3], errors='coerce')
    addresses = data[6].apply(lambda x: int(x, 16) if x.startswith('0x') else 0)
    
    # Remove invalid entries
    valid = (~np.isnan(timestamps)) & (addresses > 0)
    timestamps = timestamps[valid].values
    addresses = addresses[valid].values
    
    # Pages
    page_numbers = addresses // 4096
    page_indices = page_numbers - page_numbers.min()
    
    # Heatmap
    heatmap, _, _ = np.histogram2d(
        timestamps, page_indices,
        bins=[np.linspace(timestamps.min(), timestamps.max(), 100),
              np.arange(page_indices.max() + 2)]
    )
    
    # Plot
    plt.figure(figsize=(14, 8))
    plt.imshow(heatmap.T, aspect='auto', origin='lower', 
               norm=LogNorm(vmin=heatmap[heatmap>0].min(), vmax=heatmap.max()),
               cmap='YlOrRd')
    plt.xlabel('Time (μs)')
    plt.ylabel('Page Number')
    plt.title('L3 Cache Miss Heatmap Over Time')
    plt.colorbar(label='Miss Count')
    plt.tight_layout()
    plt.savefig('access_heatmap.png', dpi=150)
    plt.show()


def viz_accesses_over_time():
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    from matplotlib.colors import LogNorm
    
    file = "perf.txt"
    
    timestamps = []
    addresses = []
    
    with open(file, 'r') as f:
        for line in f:
            parts = line.split()
            if len(parts) < 7:
                continue
            
            try:
                # perf format: command pid cpu timestamp: count event: address ...
                # Your format: outa 2053578 5180451.545242: 2500 mem_load_retired.l3_miss:uppp: 7fdc2bda92e8 ...
                
                # Find timestamp (contains ':' at end)
                timestamp_idx = None
                for i, part in enumerate(parts):
                    if part.endswith(':') and i > 1:
                        try:
                            ts = float(part.rstrip(':'))
                            timestamp_idx = i
                            break
                        except ValueError:
                            continue
                
                if timestamp_idx is None:
                    continue
                
                # Address is typically 2-3 columns after the event name
                # Look for hex address (starts with 7f or other memory range)
                address_idx = None
                for i in range(timestamp_idx + 3, min(timestamp_idx + 6, len(parts))):
                    if parts[i].startswith(('7f', '55', '40', '3f')):  # Common address ranges
                        try:
                            addr = int(parts[i], 16)
                            if addr > 0:
                                address_idx = i
                                break
                        except ValueError:
                            continue
                
                if address_idx is None:
                    print(f"DEBUG: Could not find address in: {' '.join(parts[:10])}")
                    continue
                
                timestamp = float(parts[timestamp_idx].rstrip(':'))
                address = int(parts[address_idx], 16)
                
                timestamps.append(timestamp)
                addresses.append(address)
                
            except (ValueError, IndexError) as e:
                print(f"DEBUG: Parse error: {e} in line: {' '.join(parts[:10])}")
                continue
    
    print(f"Parsed {len(addresses)} entries")
    
    if not timestamps or len(addresses) == 0:
        print("ERROR: No valid entries parsed!")
        print("Sample line structure:")
        with open(file, 'r') as f:
            for i, line in enumerate(f):
                if i < 3:
                    print(f"  {line.strip()}")
                    print(f"  Parts: {line.split()[:15]}")
        return
    
    timestamps = np.array(timestamps)
    addresses = np.array(addresses)
    
    print(f"Addresses range: {addresses.min():#x} - {addresses.max():#x}")
    print(f"Timestamps range: {timestamps.min():.6f} - {timestamps.max():.6f}")
    
    # Convert to pages
    PAGE_SIZE = 4096
    page_numbers = addresses // PAGE_SIZE
    
    # Check if we have valid pages
    if len(page_numbers) == 0 or page_numbers.max() == page_numbers.min():
        print("ERROR: All addresses map to same page or no pages!")
        return
    
    page_indices = page_numbers - page_numbers.min()
    
    print(f"Pages range: {page_indices.min()} - {page_indices.max()}")
    
    # Create
    # Create 2D histogram
    n_time_bins = min(100, len(np.unique(timestamps)))
    n_page_bins = min(200, int(page_indices.max()) + 2)
    
    print(f"Creating heatmap: {n_time_bins} time bins x {n_page_bins} page bins")
    
    heatmap, time_edges, page_edges = np.histogram2d(
        timestamps, 
        page_indices,
        bins=[n_time_bins, n_page_bins]
    )
    ## iterate overheat map, every 2 million entries 
    # make the upper 50% of pages be worth 107 more
    # and the bottom 50% worth 5x more
    head = int(n_page_bins * 0.5)
    tail = int(n_page_bins * 0.5)
    #heatmap[head:, :] *= 5
    #heatmap[:tail, :] *= 107
    
    
    
    # Plot
    plt.figure(figsize=(14, 8))
    plt.imshow(
        heatmap.T,
        aspect='auto',
        origin='lower',
        norm=LogNorm(vmin=heatmap[heatmap > 0].min(), vmax=heatmap.max()),
        cmap='YlOrRd'
    )
    plt.xlabel('Time (seconds)')
    plt.ylabel('Page Number')
    plt.title('L3 Cache Miss Heatmap Over Time')
    plt.colorbar(label='Miss Count')
    plt.tight_layout()
    plt.savefig('access_heatmap.png', dpi=150)
    plt.show()
    
    print(f"\nSummary:")
    print(f"  Total L3 misses: {len(addresses)}")
    print(f"  Unique pages: {len(np.unique(page_indices))}")
    print(f"  Heatmap saved to: access_heatmap.png")
    


def learn_weights(data,r):
                fast_execution_time = get_field(data[r]['0'], GLOBAL, 'currentCycle', np.uint64)[-1] 
                slow_execution_time = get_field(data[r]['80'], GLOBAL, 'currentCycle', np.uint64)[-1] 
                inst = load_inst_fields(data,r)

                #total_l3_cost = get_field(data[r]['0'], GLOBAL, 'L3stalledCycles', np.uint64)[-1] 

                inputs = [np.sum(inst['lastStallTime']), np.sum(inst['L3stallTime']), np.sum(inst['L3stallCyclesMLPLoad']), np.sum(inst['stallCyclesMLPBoth']), np.sum(inst['totalTime']), np.sum(inst['L3MLP_load_at_middle']), np.sum(inst['L3MLP_store_at_middle'])]
                inputs_for_expanded = [inst['lastStallTime'], inst['L3stallCyclesMLPLoad'], inst['stallCyclesMLPBoth'], inst['totalTime']]
                global_learn['inputs_direct'].append(inputs)

                def split_data_by_mlp(nparray, MLP_arrays):
                    new_arrays = []

                    for mlp in MLP_arrays:
                        for n in range(0,25):
                            idx = np.where((mlp > n) & (mlp < n+1))
                            # zero out the array where idx is false
                            nparray[idx] = 0
                            new_arrays.append(nparray[idx])
                    return new_arrays
                
                for main_cost_driver in ['L3stallTime', 'L3stallCyclesMLPLoad']:
                    expanded_inputs = split_data_by_mlp(inst[main_cost_driver], [ # TODO remove this feature from initial inputs
                        inst['MLP_load_at_start'],
                        inst['MLP_store_at_start'],
                        inst['MLP_load_at_end'], 
                        inst['MLP_store_at_end'], inst['L3MLP_load_at_middle'], inst['L3MLP_store_at_middle']])
                    key = 'inputs_MLPexpanded-'+main_cost_driver
                    append_dict(key, expanded_inputs)

                global_learn['results'].append(slow_execution_time - fast_execution_time) # predict increase in cycles
                for (k, v) in [
                    ('cycle_increase', slow_execution_time - fast_execution_time),  
                    ('slowdown', slow_execution_time/fast_execution_time), 
                    ('l3stalls_increase', get_field(data[r]['80'], GLOBAL, 'L3stalledCycles', np.uint64)[-1] - get_field(data[r]['0'], GLOBAL, 'L3stalledCycles', np.uint64)[-1]),
                     # we are not yet modeling the stores,.. the increase in squashed instructions, ...
                    ]:
                    append_dict('results-'+k,v)
                    
def is_miss_aligned(data,r):
    # if benchset is 1GB or npb_result
    if "1GB" in data[r]['0']['benchset'] or "npb_result" in data[r]['0']['benchset']:
        return True
    return False


BY_MOMENT=False
NORM = "user"
INTENSITY_metric = None

def should_skip_key(k):
    return False
    if "Soar" not in k:
        return True
    return False
def should_scatter(k):
    return False


def metric_evalit():
    global NORM
    global BY_MOMENT
    global INTENSITY_metric
    for b in [True, False]:
        BY_MOMENT = b
        for i in [None]: #   'average_l3mlp', None, 'average_mlp']: # None,, 'average_mlp']: # None,
            INTENSITY_metric = i
            print("intensity is", i, INTENSITY_metric)
            for n in ["user" ] : #  , "TPP" ]: #, "TPP", "PEBS"]:
                NORM = n
                metric_eval()
                print("intensity is", i, INTENSITY_metric)

def metric_eval():
    global NORM
    global BY_MOMENT
    per_bench = []
    benchset  = []
    benchname = []
    def valo(data, r):
        if is_miss_aligned(data,r):

            raise Exception("Unaligned execution detected!!")
            return
    

        glob_0 = load_global_fields(data,r) #convolve=500)
        if "80" not in data[r]:
            print("No 80 run", data[r]['0']['benchset'], data[r]['0']['bench'])
            if r in data_v4 and "80" in data_v4[r]:
                print("BUT V4 COULD SAVE!")
                glob_80 = load_global_fields(data_v4, r, "80", PID_ONLY=True, run_folder=RUN_DATA_FOLDER_V4)
            else:
                raise Exception("Unaligned execution detected!!")
                return
        else:
            glob_80 = load_global_fields(data,r,"80") # convolve=500)
        #data_v4

        if len(glob_0['currentCycle']) < 50:
            print("Not enough execution time..." , len(glob_0['currentCycle']),   data[r]['0']['benchset'], data[r]['0']['bench'])
            raise Exception("Not enough execution time...")
            return


        last_idx = get_last_idx_of_smallest_vector(glob_80['currentCycle'],glob_0['currentCycle']) 
        globy = {}
        def aggregate_op(array, positive=True):
            if BY_MOMENT:
                array = array.astype(np.int64)
                return np.where(array == 0, 1 if positive else 0, array)
            r = np.sum( array.astype(np.int64), dtype=np.int64)
            return r if not positive or (positive and r != 0) else 1
        def norm_function():
            if NORM == "TPP":
                return  aggregate_op(glob_0['commitedLoads'][:last_idx]) # user
            if NORM == "PEBS":
                return  aggregate_op(glob_0['commitedL3Misses'][:last_idx]) # user
            if NORM  == "user":
                return  aggregate_op(glob_0['currentCycle'][:last_idx]) # user
            else:
                exit("Unknown norm: " + NORM)
            #return norm = np.sum(glob_0['currentCycle'][:last_idx]) # user
        def get(key, positive=True):
            # TODO if 0 = 1
            return aggregate_op(glob_0[key][:last_idx], positive)
        def getSLOW(key, positive=True):
            return aggregate_op(glob_80[key][:last_idx], positive)

        norm = norm_function()
        global_slowdown = getSLOW('currentCycle')/get('currentCycle')
        globy = {
            'global_slowdown': global_slowdown,
        }
        benchsett = data[r]['0']['benchset'] 
        benchnamee = data[r]['0']['bench']
        if benchsett != "benches_final":
            print(benchsett)
            print("Not an instruction aligned execution ")
            raise Exception("Unaligned execution detected!!")
            return
        if ( np.sum(np.abs( getSLOW('commitedLoads') - get('commitedLoads')) > 50) > 2):
            print("Unaligned execution detected!!", benchsett, benchnamee)

            raise Exception("Unaligned execution detected!!")
            return

        """
        print(data[r]['0']['line'])
        print(get('currentCycle'))
        print(get('commitedLoads'))
        print(getSLOW('commitedLoads'))
        print(getSLOW('currentCycle'))
        print(np.histogram(getSLOW('currentCycle')/ get('currentCycle'), bins=[0,0.2,0.4,0.6,1,2] ))
        print(np.sum(global_slowdown < 0.8),data[r]['0']['bench'], len(global_slowdown) )
        return
        """
        globy['Core Stall Cycles'] = aggregate_op(glob_0['stalledCycles'][:last_idx]) /norm
        globy['Core MLP Stall Cycles'] = aggregate_op(glob_0['stallCyclesMLPLoad'][:last_idx]) /norm
        globy['Core MLP Stall Cycles (during LLC misses)'] = aggregate_op(glob_0['L3stallCyclesMLPLoad'][:last_idx]) /norm
        globy['Core Stall Cycles (during LLC misses)'] = aggregate_op(glob_0['L3stalledCycles'][:last_idx]) /norm


        norm_diff =  aggregate_op(glob_0['stalledCycles'][:last_idx])
        norm_diff = norm 
        globy['∆ Core Stalls Cycles'] = (getSLOW('stalledCycles') - get('stalledCycles')) /norm_diff
        norm_diff = get('stallCyclesMLPLoad') 
        norm_diff = norm 
        globy['∆ Core MLP Stalls Cycles'] = (getSLOW('stallCyclesMLPLoad') - get('stallCyclesMLPLoad')) /norm_diff
        norm_diff = get('L3stallCyclesMLPLoad') 
        norm_diff = norm 
        globy['∆ Core MLP Stalls Cycles (during LLC misses)'] = (getSLOW('L3stallCyclesMLPLoad') - get('L3stallCyclesMLPLoad')) /norm_diff
        norm_diff = get('L3stalledCycles') 
        norm_diff = norm 
        globy['∆ Core Stalls Cycles (during LLC misses)'] = (getSLOW('L3stalledCycles') - get('L3stalledCycles')) /norm_diff
        summedKeys = ['totalAccessTimeSummed' ] #, 'average_mlp', 'average_l3mlp']
        diffKeys = ['totalAccessTimeSummed']
        for k in summedKeys:
            globy[k] = get(k)/norm
        for k in diffKeys:
            norm_diff = get(k)
            globy['diff_'+k] = (getSLOW(k) - get(k)) /norm_diff






        tot_keys = ['totalL3MLPStalledCyclesSummed', 'totalL3StalledCyclesSummed', 'totalStalledCyclesSummed', 'totalMLPStalledCyclesSummed']
        for k in tot_keys:
            globy['k'] = get(k)/norm

        globy['Instruction Stall cycles/MLP (LLC misses)'] = (aggregate_op(glob_0['totalL3MLPStalledCyclesSummed'][:last_idx]))/norm 
        globy['Instruction Stall cycles (LLC misses)'] = (aggregate_op(glob_0['totalL3StalledCyclesSummed'][:last_idx]))/norm 
        globy['Instruction Stall cycles'] = (aggregate_op(glob_0['totalStalledCyclesSummed'][:last_idx]))/norm 
        globy['Instruction Stall cycles/MLP'] = (aggregate_op(glob_0['totalMLPStalledCyclesSummed'][:last_idx]))/norm 

        globy['Slow Instruction Stall cycles/MLP (LLC misses)'] = (aggregate_op(glob_80['totalL3MLPStalledCyclesSummed'][:last_idx]))/norm 
        globy['Slow Instruction Stall cycles (LLC misses)'] = (aggregate_op(glob_80['totalL3StalledCyclesSummed'][:last_idx]))/norm 
        globy['Slow Instruction Stall cycles'] = (aggregate_op(glob_80['totalStalledCyclesSummed'][:last_idx]))/norm 
        globy['Slow Instruction Stall cycles/MLP'] = (aggregate_op(glob_80['totalMLPStalledCyclesSummed'][:last_idx]))/norm 

        globy['∆ Instruction Stall cycles/MLP (LLC misses)'] = (aggregate_op(glob_80['totalL3MLPStalledCyclesSummed'][:last_idx]) - aggregate_op(glob_0['totalL3MLPStalledCyclesSummed'][:last_idx]))/norm 
        globy['∆ Instruction Stall cycles (LLC misses)'] = (aggregate_op(glob_80['totalL3StalledCyclesSummed'][:last_idx]) - aggregate_op(glob_0['totalL3StalledCyclesSummed'][:last_idx]))/norm 
        globy['∆ Instruction Stall cycles '] = (aggregate_op(glob_80['totalStalledCyclesSummed'][:last_idx]) - aggregate_op(glob_0['totalStalledCyclesSummed'][:last_idx]))/norm 
        globy['∆ Instruction Stall cycles/MLP '] = (aggregate_op(glob_80['totalMLPStalledCyclesSummed'][:last_idx]) - aggregate_op(glob_0['totalMLPStalledCyclesSummed'][:last_idx]))/norm 

        WIDE_80_USE = False
        if WIDE_80_USE:
            i80 = load_inst_fields(data,r,"80")
            globy['DIFFtotalStalledCyclesSummed'] = (aggregate_op(glob_80['totalStalledCyclesSummed'][:last_idx])-aggregate_op(glob_0['totalStalledCyclesSummed'][:last_idx]))/norm 
            globy['DIFFtotalL3MLPStalledCyclesSummed'] = (aggregate_op(glob_80['totalL3MLPStalledCyclesSummed'][:last_idx])-aggregate_op(glob_0['totalL3MLPStalledCyclesSummed'][:last_idx]))/norm 

        globy['Commited loads'] = aggregate_op(glob_0['commitedLoads'][:last_idx])/norm # should be the same for each of them..
        globy['Commited loads (LLC misses)'] = aggregate_op(glob_0['commitedL3Misses'][:last_idx])/norm
        #globy['norma'] = 1 # norm

        b = 24.67
        a = 0.87 
        a = 1.0155768028621026
        b = -0.2562029379967975
        cycles_with_demand_read_0 = get('cyclesWithMemrequests') #aggregate_op(glob_0['cyclesWithMemrequests'][:last_idx])
        number_of_demand_reads_0 = get('commitedLoads') #aggregate_op(glob_0['commitedLoads'][:last_idx])

        globy['average_mlp'] =  get('totalMLPsummed', False)/cycles_with_demand_read_0
        #print(np.histogram(globy['average_mlp']))
        globy['average_l3mlp'] = get('totalL3MLPsummed', False)/get('L3cyclesWithMemrequests')
        #print("l3", np.histogram(globy['average_l3mlp']))

        AOL = cycles_with_demand_read_0/number_of_demand_reads_0 
        #AOL = np.where(number_of_demand_reads_0 == 0 | np.isnan(AOL)|  cycles_with_demand_read_0 == 0, 1, AOL)# 
        AOL = np.where((number_of_demand_reads_0 == 0) | (np.isnan(AOL)) | (cycles_with_demand_read_0 == 0), 1, AOL) 
        unadjusted_slowdown = aggregate_op(glob_0['stalledCycles'][:last_idx])/aggregate_op(glob_0['currentCycle'][:last_idx])
        globy['Soar slowdown'] = unadjusted_slowdown * (1/(a + b/AOL))

        AOL_agg = cycles_with_demand_read_0/number_of_demand_reads_0 
        # convolve points for mean 
        """
        cycles_with_demand_read_0_agg =  np.convolve(cycles_with_demand_read_0, np.ones(10)/10, mode='valid')
        number_of_demand_reads_0_agg = np.convolve(number_of_demand_reads_0, np.ones(10)/10, mode='valid')
        AOL_agg = cycles_with_demand_read_0_agg/number_of_demand_reads_0_agg
        #AOL = np.where(number_of_demand_reads_0 == 0 | np.isnan(AOL)|  cycles_with_demand_read_0 == 0, 1, AOL)# 
        AOL_agg = np.where((number_of_demand_reads_0_agg == 0) | (np.isnan(AOL_agg)) | (cycles_with_demand_read_0_agg == 0), 1, AOL_agg) 
        unadjusted_slowdown = np.convolve(glob_0['stalledCycles'][:last_idx], np.ones(10)/10, mode='valid') /np.convolve(glob_0['currentCycle'][:last_idx], np.ones(10)/10, mode='valid')
        globy['Soar slowdown agg'] = unadjusted_slowdown * (1/(a + b/AOL_agg))
        """

        i = load_inst_fields(data, r)
        llc_misses = i['totalTime'] >= 70
        after_last0 = last_idx+1 if last_idx+1 < len(glob_0['currentCycle']) else last_idx
        sel0 = llc_misses & (i['start_cycle'] < glob_0['currentCycle'][after_last0])
        globy['inst_l3mlp'] = (np.sum(i['L3stallCyclesMLPLoad'][sel0])) / norm
        globy['inst_mlp'] = (np.sum(i['stallCyclesMLPLoad'][sel0])) / norm
        globy['inst_llc_misses'] = np.sum(i['totalTime'][sel0] >= 70) / norm 

        #globy['Coarse inst SOAR'] =  get('stalledCycles')/( get('currentCycle') * a + get('average_mlp') * b)
        globy['inst_soar'] = np.sum( i['stallTime'][sel0] / ( i['totalTime'][sel0] * a + i['average_mlp'][sel0] * b))/norm
        if BY_MOMENT:
            per_bench.append(globy)
            benchset.append(benchsett)
            benchname.append(benchnamee)
            return 
        i0 = load_inst_fields(data,r)
        # version using instructions 
        i80 = load_inst_fields(data, r, '80')
        if np.sum(sel0) < 3000:
            print("Not enough samples... for bench", np.sum(sel0),  data[r]['0']['benchset'], data[r]['0']['bench'])
            

        samp =   np.sum(glob_0['commitedL3Misses'][:last_idx])  / np.sum(sel0)  
        print(samp, np.sum(sel0), last_idx - len(glob_0['commitedL3Misses']) , np.sum(glob_0['commitedLoads'][:last_idx]), np.sum(glob_0['commitedL3Misses'][:last_idx]))
        norm = norm  #/ samp

        #soar_mlp_aware_slowdown = obtain_soar_mlp_aware_slowdown(unadjusted_slowdown, AOL, real_slow_down)
        

        globy['inst_stalls'] = aggregate_op(i['stallTime'][sel0]) / norm
        globy['inst_l3_stalls'] =  aggregate_op(i['L3stallTime'][sel0]) / norm


        if WIDE_80_USE:
            after_last80 = last_idx+1 if last_idx+1 < len(glob_80['currentCycle']) else last_idx
            sel80 = (i80['totalTime'] >= 70) & (i80['start_cycle'] < glob_80['currentCycle'][after_last80])
            globy['inst_l3_stalls_diffDfastCycles'] = (np.sum(i80['L3stallTime'][sel80]) - np.sum(i['L3stallTime'][sel0])) / norm
            globy['inst_stalls_diffDfastCycles'] = (np.sum(i80['stallTime'][sel80]) - np.sum(i['stallTime'][sel0])) / norm
            globy['inst_l3_stalls_MEANdiffDfastCycles'] = (np.mean(i80['L3stallTime'][sel80]) - np.mean(i['L3stallTime'][sel0])) / norm
            globy['inst_stalls_MEANdiffDfastCycles'] = (np.mean(i80['stallTime'][sel80]) - np.mean(i['stallTime'][sel0])) / norm
            globy['inst_llc_missesSLOW'] = np.sum(i80['totalTime'][sel80] >= 70) / norm 


        # % of stall time
        # % of stall time by Soars metrics 
        per_bench.append(globy)
        benchset.append(data[r]['0']['benchset'])
        benchname.append(data[r]['0']['bench'])
        return
        #globy['iTotalL3StalledCyclesSummed'] = np.sum(glob_0['totalL3StalledCyclesSummed'][:last_idx])/norm
    # plot x = global_slowdown
    # y = each of the keys
    iterate_over_benches(data, valo)
    all_together = {}
    print("about do do globaos de outrs" )

    for b in per_bench:
        for k in b:
            if k not in all_together:
                all_together[k] = []
            all_together[k].append(b[k])
    benchsets =  [ "cpu2017", "gapbs",   "NPB-CPP",            "pkgs/apps",   "pkgs/kernels" ,"XSBench", "liblinear", "pkgs/splash"]
    benchsetsHUMAN =  [ "CPU2017", "GAPBS",   "NPB",            "PARSEC-apps",   "PARSEC-kernels" ,"XSBench", "liblinear", "PARSEC-splash"]
    colors = ['blue', 'orange', 'purple', 'green', 'red', 'black', 'pink', 'brown', 'gray']
    def calculate_point_colors(metric=None):
        benchset_colors = []
        #col_idxes = []

        
        for b in benchname:
            found = False
            for name in benchsets:
                print(name in b , name, b)
                if name in b:
                    benchset_colors.append(benchsets.index(name))
                    found = True
                    break
            if found:
                continue
            benchset_colors.append(-1) # other
            print("other is ", b)
        final_colors = []
        for c in benchset_colors:
            final_colors.append(colors[c])
        return final_colors
    final_colors = calculate_point_colors()


    if BY_MOMENT:
        colors_of_each = []
        if INTENSITY_metric is not None:
            for k in all_together:
                for i in range(len(all_together[k])):
                    all_together[INTENSITY_metric][i] = np.nan_to_num(all_together[INTENSITY_metric][i])
                    #print(np.histogram(all_together[INTENSITY_metric][i]))
                    #print(np.max(all_together[INTENSITY_metric][i])) 
                    mlp_intensity = (all_together[INTENSITY_metric][i]) # np.max(all_together[INTENSITY_metric][i])
                    # capt the MLP to 32
                    mlp_intensity = np.clip(mlp_intensity, 0, 16)/16

                    mlp_intensity = np.column_stack((mlp_intensity, np.zeros_like(mlp_intensity), np.zeros_like(mlp_intensity)))
                    colors_of_each.append(mlp_intensity)
                break        
            # using one array, create one array of tuples: [(mlp_intensity[0], 0, 0), (mlp_intensity[1],0,0) (0,...) ] such that It can be used to color in matplotlib 
            #exit()
        else:

            for k in all_together:
                for i in range(len(all_together[k])):
                    colors_of_each.append(np.full(len(all_together[k][i]), final_colors[i]))
                break
        colors_of_each = np.concatenate(colors_of_each)
        final_colors = colors_of_each
        for k in all_together: ### THIS IS SHARED ACROSS BOTH OF THE ABOVE PATHS <-- 
            #print(k)
            all_together[k] = np.concatenate(all_together[k])
                

    
    print(benchsets, all_together.keys())


    def plot_keypair(key, altogether, BY_MOMENT):
        pass

    for k in all_together:
        if should_skip_key(k):
            continue
        if not BY_MOMENT:
            plt.figure()
        else:
            plt.figure(figsize=(20,20))
        from scipy.stats.mstats import winsorize
        #print(final_colors)
        all_together[k] = winsorize(np.array(all_together[k]), limits=[0, 0.01])
        

        #print(all_together[k])
        if BY_MOMENT:
            alfa = 0.1
            size=0.1
        else:
            size=1
            alfa = 0.7
        if INTENSITY_metric is not None:
            alfa = 1
            size=0.005
        size=0.01
        alfa=1

        #print(k)
        print(final_colors)
        plt.scatter(all_together['global_slowdown'], all_together[k], s=size, alpha=alfa , c=final_colors) 
        def do_legend():
            import matplotlib.patches as mpatches
            if INTENSITY_metric is not None:
                m = all_together[INTENSITY_metric]
                legend_patches = [
        mpatches.Patch(color=plt.cm.hot(intensity), label=f'{benchset} (intensity: {intensity:.2f})')
                for benchset, intensity in zip(benchsetsHUMAN, m/np.max(m))
                ]
            else:
                legend_patches = [mpatches.Patch(color=color, label=benchset) 
                                for benchset, color in zip(benchsetsHUMAN, colors)]
            plt.legend(handles=legend_patches, loc='upper left', fontsize=10)
        do_legend()

        plt.xlabel('Slowdown')
        kind = ""
        if k.startswith("∆ Core "):
            plt.title("Slowdown relationship between the difference of fast and slow tier only metrics")
        elif k.startswith("Core "):
            plt.title("Relationship between fast tier CPU core metrics and slowdown")
        else:
            plt.title("Relationship between fast tier instruction level metrics and slowdown")
        plt.ylabel(k)


        plt.title(f"Relationship between CPU Core metrics and {'workload' if BY_MOMENT else 'global'} slow down ")
        plt.savefig(f'./_finos/A---{"BY_MOMENT" if BY_MOMENT else ""} {INTENSITY_metric if INTENSITY_metric else  ""} - {NORM} globos de ouro' + k.replace("/", "D") + '.png' )

        plt.close()
        if BY_MOMENT:
            plt.figure(figsize=(20,20))
            plt.hexbin(all_together['global_slowdown'], all_together[k], gridsize=50, cmap="hot") 
            plt.savefig(f'./_finos/AHEXA---{"BY_MOMENT" if BY_MOMENT else ""} {INTENSITY_metric if INTENSITY_metric else  ""} - {NORM} globos de ouro' + k.replace("/", "D") + '.png' )

            
            plt.close()
            """
            plt.figure(figsize=(20,20))
            plt.hexbin(all_together['global_slowdown'], all_together[k], gridsize=50, cmap='hot') 
            plt.savefig(f'./_finos/AHEXA---{"BY_MOMENT" if BY_MOMENT else ""} {INTENSITY_metric if INTENSITY_metric else  ""} - {NORM} globos de ouro' + k.replace("/", "D") + '.png' )
            plt.close()
            """

        

        plt.figure(figsize=(20,20))
        plt.xlabel('MLP')
        plt.ylabel(k)
        col =  2-np.clip(all_together['global_slowdown'],1,2) 
        coli = np.column_stack((col, np.zeros_like(col), np.zeros_like(col)))
        coli = np.concatenate([coli])
        plt.scatter(all_together[k], all_together['average_mlp'], s=size, alpha=alfa , c=list(coli)) 
        plt.savefig(f'./_finos/BMLP---{"BY_MOMENT" if BY_MOMENT else ""} {INTENSITY_metric if INTENSITY_metric else  ""} - {NORM} globos de ouro' + k.replace("/", "D") + '.png' )
        plt.close()

        for k in [ 'Slow Instruction Stall cycles (LLC misses)',
        'Slow Instruction Stall cycles',
        'Slow Instruction Stall cycles/MLP',
            'Slow Instruction Stall cycles (LLC misses)']:
            plt.figure(figsize=(20,20))
            plt.scatter(all_together[k], all_together[k.split("Slow ")[-1]], s=size, alpha=alfa , c=col) 
            plt.xlabel(k)
            plt.ylabel(k.split("Slow ")[-1])
            plt.savefig(f"./_finos/C--diff metrics -{'BY_MOMENT' if BY_MOMENT else ''} - {NORM} globos de ouro" + k.replace("/", "D") + '.png' )

        print('savefig')
        # ledged with benchstsHUMAN

        plt.close()
    print(len(all_together['global_slowdown']))

    

    
    

FIELDS_OF_INTEREST = ['currentCycle', 'stalledCycles', 'cyclesWithMemrequests', 'commitedLoads', 'commitedL3Misses', 'commitedLoads',  'L3stalledCycles', 'L3stallCyclesMLPLoad']
def obtain_derivate_metrics(data,r, loader):
    print("About to start!")
    glob_0 = loader(data,r, convolve=500)
    glob_80 = loader(data,r,"80", convolve=500)
    # depending on the load functions, we may be operating with integers or arrays!


    #glob_0['commitedLoads'][0] = 1
    #glob_0['currentCycle'][0] = 1
    #gob_80['currentCycle'][0] = 1
    #kint(glob_0['commitedLoads'])
    #real_slow_down = glob_0['stalledCycles']/glob_0['currentCycle']
    #_ = glob_0['L3stallCyclesMLPLoad'] 
    #glob_0['L3stallCyclesMLPLoad']  = _/1024
    ONE_POINT = True     
    if ONE_POINT:
        pass
        #last_idx = get_last_idx_of_smallest_vector(g80['currentCycle'],g0['currentCycle'])

    print("Mido")
    glob_0['currentCycle'][0] = 1
    glob_80['currentCycle'][0] = 1
    last_idx = get_last_idx_of_smallest_vector(glob_80['currentCycle'],glob_0['currentCycle']) 

    glob_0['currentCycle'] = glob_0['currentCycle'][:last_idx]
    glob_80['currentCycle'] = glob_80['currentCycle'][:last_idx]
    glob_0['stalledCycles'] = glob_0['stalledCycles'][:last_idx]
    glob_0['L3stalledCycles'] = glob_0['L3stalledCycles'][:last_idx]
    glob_80['stalledCycles'] = glob_80['stalledCycles'][:last_idx]
    glob_80['L3stalledCycles'] = glob_80['L3stalledCycles'][:last_idx]
    glob_0['totalStalledCyclesSummed'] = glob_0['totalStalledCyclesSummed'][:last_idx]
    glob_80['totalStalledCyclesSummed'] = glob_80['totalStalledCyclesSummed'][:last_idx]
    glob_0['totalL3StalledCyclesSummed'] = glob_0['totalL3StalledCyclesSummed'][:last_idx]
    glob_80['totalL3StalledCyclesSummed'] = glob_80['totalL3StalledCyclesSummed'][:last_idx]
    glob_0['totalMLPStalledCyclesSummed'] = glob_0['totalMLPStalledCyclesSummed'][:last_idx]
    glob_80['totalMLPStalledCyclesSummed'] = glob_80['totalMLPStalledCyclesSummed'][:last_idx]
    glob_0['totalL3MLPStalledCyclesSummed'] = glob_0['totalL3MLPStalledCyclesSummed'][:last_idx]
    glob_80['totalL3MLPStalledCyclesSummed'] = glob_80['totalL3MLPStalledCyclesSummed'][:last_idx]
    glob_0['L3stallCyclesMLPLoad'] = glob_0['L3stallCyclesMLPLoad'][:last_idx]
    glob_80['L3stallCyclesMLPLoad'] = glob_80['L3stallCyclesMLPLoad'][:last_idx]
    
    glob_0['cyclesWithMemrequests'] = glob_0['cyclesWithMemrequests'][:last_idx]
    glob_80['cyclesWithMemrequests'] = glob_80['cyclesWithMemrequests'][:last_idx]
    glob_0['commitedLoads'] = glob_0['commitedLoads'][:last_idx]
    glob_80['commitedLoads'] = glob_80['commitedLoads'][:last_idx]
    glob_0['commitedL3Misses'] = glob_0['commitedL3Misses'][:last_idx]
    glob_80['commitedL3Misses'] = glob_80['commitedL3Misses'][:last_idx]

    cycles_with_demand_read = glob_0['cyclesWithMemrequests'] 
    cycles_with_demand_read_80 = glob_80['cyclesWithMemrequests'] 
    number_of_demand_reads = glob_0['commitedLoads'] 
    real_slow_down = (glob_80['stalledCycles'][:last_idx]-glob_0['stalledCycles'][:last_idx])


    #delta_store_stalls = (glob_80['stalledCyclesDuringStore'] - glob_0['stalledCyclesDuringStore'])/glob_0['currentCycle']
    #res['delta_store_stalls'] = delta_store_stalls
    #predicted_store_stalls = regress(glob_0['stalledCyclesDuringStore'], real_slow_down)
    #predicted_load_n_store_weighted = regress(glob_0['stallCyclesMLPBoth'] , real_slow_down)
    l3_misses = glob_0['commitedL3Misses'] 
    norm =  1 #  glob_0['currentCycle']
    res = {'real_slow_down': real_slow_down, 
           
           'l3_misses' : l3_misses, #/glob_0['currentCycle'],
           'number_of_demand_reads' : number_of_demand_reads / norm
           }


    if False:
        i = load_inst_fields(data, r)
        i80 = load_inst_fields(data, r, '80')
        res['inst_stalls'] = np.sum(i['stallTime'])
        res['inst_l3_stalls'] =  np.sum(i['L3stallTime']) / norm
        res['inst_l3_stalls_diff/fastCycles'] = (np.mean(i80['L3stallTime']) - np.mean(i['L3stallTime'])) / norm
        res['inst_stalls_diff/fastCycles'] = (np.mean(i80['stallTime']) - np.mean(i['stallTime'])) / norm
        res['inst_l3mlp'] = (np.sum(i['L3stallCyclesMLPLoad'])) 
        res['inst_mlp'] = (np.sum(i['stallCyclesMLPLoad']))

    res['totalL3MLPStalledCyclesSummed'] = (glob_0['totalL3MLPStalledCyclesSummed'][:last_idx]) # ['L3stallCyclesMLPLoad'])) 
    res['totalL3StalledCyclesSummed'] = (glob_0['totalL3StalledCyclesSummed'][:last_idx]) # ['L3stallCyclesMLPLoad'])) 
    res['totalStalledCyclesSummed'] = (glob_0['totalStalledCyclesSummed'][:last_idx]) # ['L3stallCyclesMLPLoad'])) 
    res['DIFFtotalStalledCyclesSummed'] = (glob_80['totalStalledCyclesSummed'][:last_idx]-glob_0['totalStalledCyclesSummed'][:last_idx]) # ['L3stallCyclesMLPLoad'])) 
    res['DIFFtotalL3MLPStalledCyclesSummed'] = (glob_80['totalL3MLPStalledCyclesSummed'][:last_idx]-glob_0['totalL3MLPStalledCyclesSummed'][:last_idx]) # ['L3stallCyclesMLPLoad'])) 

    res['totalMLPStalledCyclesSummed'] = (glob_0['totalMLPStalledCyclesSummed'][:last_idx]) # ['L3stallCyclesMLPLoad'])) 
    print("-----")
    print(np.histogram(glob_0['stalledCycles']))
    print(np.histogram(glob_80['stalledCycles']))
    print("-----")


    res['stalls'] = (glob_80['stalledCycles'][:last_idx])
    res['stalls_diff/fastCycles'] = (glob_80['stalledCycles'][:last_idx] - glob_0['stalledCycles'][:last_idx]) / norm
    res['l3stalls_diff/fastCycles'] = (glob_80['L3stalledCycles'][:last_idx] - glob_0['L3stalledCycles'][:last_idx]) / norm
    ####### CHANGE res['l3stalls(SoarSimple)'] = (glob_80['L3stalledCycles'] - glob_0['L3stalledCycles']) 
    #res['l3stalls(SoarSimple)'] = (glob_80['L3stalledCycles'] - glob_0['L3stalledCycles']) 

    res['l3mlp_stalls_diff/fastCycles'] = (glob_80['L3stallCyclesMLPLoad'][:last_idx] - glob_0['L3stallCyclesMLPLoad'][:last_idx]) / norm
    #res['l3mlp_stalls_diff'] = (glob_80['L3stallCyclesMLPLoad'] - glob_0['L3stallCyclesMLPLoad']) 
    res['mlp_stalls_diff/fastCycles'] = (glob_80['stallCyclesMLPLoad'][:last_idx] - glob_0['stallCyclesMLPLoad'][:last_idx]) / norm
    #res['mlp_stalls_diff'] = (glob_80['stallCyclesMLPLoad'] - glob_0['stallCyclesMLPLoad']) 

    res['l3mlp/fastCycles'] = (glob_0['L3stallCyclesMLPLoad'][:last_idx]/norm)

    #res['l3mlp/fastCycles'] = regress(res['l3mlp/fastCycles'], real_slow_down) # SOAR LIKE

    #res['weight_stalls_with_mlp'] = ( glob_0['L3stalledCycles'] / (glob_80['L3stallCyclesMLPLoad'] / glob_80['currentCycle']) ) 
    res['weight_stalls_with_mlp'] = ( glob_0['L3stalledCycles'][:last_idx] / (glob_80['L3stallCyclesMLPLoad'][:last_idx] / glob_80['currentCycle'][:last_idx]) ) 
    res['weight_stalls_with_mlp'] = np.where(glob_80['L3stallCyclesMLPLoad'][:last_idx] == 0, 0, res['weight_stalls_with_mlp'][:last_idx])
    
    #res['pred_weight_stalls_with_mlp'] = regress(weight_stalls_with_mlp, real_slow_down)
    # all indexes
    """
    for k in list(res.keys()):
        if k == 'real_slow_down':
            continue
        res['pred_'+k] = regress(res[k], real_slow_down)
    """


    AOL = glob_0['cyclesWithMemrequests'][:last_idx]/glob_0['commitedLoads'][:last_idx] 
    AOL = np.where(glob_0['commitedLoads'][:last_idx] == 0, 1, AOL) 
    #AOL_80 = cycles_with_demand_read_80/number_of_demand_reads
    # TODO does AOL change in the slow tier? yes -> MLP changes wiht device latency
    unadjusted_slowdown = glob_0['stalledCycles'][:last_idx]/glob_0['currentCycle'][:last_idx]
    # fit unadjusted_slowdown * 1 / (a + b/AOL) =  real_slow_down to find a and b
    print(AOL)
    # print the range of each vector
    print("Range of AOL: ", np.min(AOL), np.max(AOL))
    print("Range of unadjusted_slowdown: ", np.min(unadjusted_slowdown), np.max(unadjusted_slowdown), glob_0['stalledCycles'], glob_80['currentCycle'])
    print("Range of real_slow_down: ", np.min(real_slow_down), np.max(real_slow_down))
    res['pred_soar_mlp'] = obtain_soar_mlp_aware_slowdown(unadjusted_slowdown, AOL, real_slow_down)
    print("AOL in the end")

    #predicted_soar_simple_clean = regress(glob_0['stalledCycles'], real_slowdown_clean)
    #predicted_mlp_simple_clean = regress(glob_0['L3stallCyclesMLPLoad'], real_slowdown_clean)
    #predicted_soar_simple_clean = regress(glob_0['stalledCycles'], real_slowdown_clean)
    #soar_mlp_aware_slowdown_clean = obtain_soar_mlp_aware_slowdown(unadjusted_slowdown, AOL, real_slow_down)
    return res


by_instruction_all = []
def calculate_derivates(data):
    global bench_nr
    global bench_name
    
    doing_runs = []
    for r in data:
        bench_nr = data[r]['0']['benchnr']
        bench_name = data[r]['0']['bench'].split("/")[-1]
        to_plot = {'Slow down': [],
                   'Stall cycles': [],
                   'MLP stall': [],
                   'Commited Instructions': []

                   
                   }
        i = 0
        doing_runs.append(r)
        if '0' not in data[r].keys() or '80' not in data[r].keys():
            print("Skipped run", list(data[r].values())[0]['benchnr'])
            continue
            
            
        if not (int(data[r]['0']['benchnr']) > 60 and int(data[r]['80']['benchnr']) < 70):
            #continue
            pass
            

        try:
            g = load_global_fields_crescendo(data,r)
            cycles_0 = g['currentCycle']
            if(len(cycles_0) < 50): # gapbs screw results??
                continue
            # iterate over all fields of global insts
            def check_health():
                g = load_global_fields_crescendo(data,r)
                gg = load_global_fields_crescendo(data,r,'80')
                for f in global_types.keys():
                    # check if is there ever a number that is smaller than the previous one
                    if( np.any(np.diff(g[f]) < 0) or np.any(np.diff(gg[f]) < 0)):
                        print("Failed", f)
                print('OK!')
            try:

                d = calculate_by_sample_cost(data,r)
                by_instruction_all.append(d)
                continue
            except Exception as e:
                print(e)
                import traceback
                print(traceback.print_exc())
                continue
            #plot_pred(data,load_global_fields, r, bench_name + "_" + bench_nr)
            continue
                
            continue

            commited_0 = (get_field(data[r]['0'], GLOBAL, 'commitedInstructions', np.uint64))
            #commited_0.shape[0]
            commited_80 = (get_field(data[r]['80'], GLOBAL, 'commitedInstructions', np.uint64))

            
            instructions = get_field(data[r]['0'], INST, 'address', np.uint64)
            print("Instructions shape", instructions.shape)
            # do histogram of instructions 
            #hist = np.histogram(instructions, bins=1)
            # print number of insts
            #print("Number of instructions", hist[0].shape[0])
            

            

            stalled_0 = fill_if_needed(get_field(data[r]['0'], GLOBAL, 'stalledCycles', np.uint64), commited_0.shape[0])
            stalled_80 = fill_if_needed(get_field(data[r]['80'], GLOBAL, 'stalledCycles', np.uint64), commited_0.shape[0])

            memory_stalls_0 = fill_if_needed(get_field(data[r]['0'], GLOBAL, 'stalledCyclesWithMemRequests', np.uint64), commited_0.shape[0])
            memory_stalls_80 = fill_if_needed(get_field(data[r]['80'], GLOBAL, 'stalledCyclesWithMemRequests', np.uint64), commited_0.shape[0]) 
            stalled_0 = memory_stalls_0
            stalled_80 = memory_stalls_80

            # 16:04
            # normalize the sum of all slow downs to be 1
            # increase_in_stalls_instant * (1/total_stall_increase)
            # 
            

            cycles_0 = fill_if_needed(get_field(data[r]['0'], GLOBAL, 'currentCycle', np.uint64), commited_0.shape[0])
            #  find which items are 0 in cycles_0
            print("0000000000000", len(cycles_0[cycles_0 == 0]))
            cycles_0[cycles_0 == 0] = int(np.iinfo(np.uint64).max)
            

            cycles_80 = fill_if_needed(get_field(data[r]['80'], GLOBAL, 'currentCycle', np.uint64), commited_0.shape[0])


            

            

            #AOL_80 = cycles_with_demand_read_80/number_of_demand_reads
            # TODO does AOL change in the slow tier? yes -> MLP changes wiht device latency
            unadjusted_slowdown = stalled_0/cycles_0




            import pandas as pd


            print("Real slowdown") 
            real_slow_down = (cycles_80 - cycles_0) / cycles_0
            clean_idxs =  real_slow_down < 1000 #np.abs(real_slow_down - np.median(real_slow_down)) < np.percentile(np.abs(real_slow_down - np.median(real_slow_down)), 90) # @ 95 we get big outliers
            clean_idxs = np.argsort(real_slow_down)[:int(len(real_slow_down)/4)]
            print(len(real_slow_down[clean_idxs]))
            stall_difference = (stalled_80 - stalled_0) / cycles_0

            all_data = {}
            def import_var(name, struct):
                field = name
                all_data[name + "_0"] = fill_if_needed(get_field(data[r]['0'], struct,field, np.uint64), commited_0.shape[0]) 
                all_data[name + "_80"] = fill_if_needed(get_field(data[r]['80'], struct,field, np.uint64), commited_0.shape[0]) 
                all_data[name + "_delta"] = (all_data[name + "_80"] - all_data[name + "_0"])/cycles_0
                all_data[name + "_predicted"] = regress(all_data[name + "_0"], real_slow_down)
            import_var("stalledCyclesDuringStore", GLOBAL)
            import_var("stallCyclesMLPLoad", GLOBAL)
            import_var("stallCyclesMLPStore", GLOBAL)
            import_var("stallCyclesMLPBoth", GLOBAL)
            import_var("stalledCyclesWithMemRequests", GLOBAL)
            import_var("stalledCyclesWithStores", GLOBAL)
            import_var("stalledCycles", GLOBAL)
            import_var("commitedStores", GLOBAL)
            import_var("commitedLoads", GLOBAL)
            import_var("commitedInstructions", GLOBAL)
            import_var("totalSquashed", GLOBAL)
            import_var("lastStallTime", GLOBAL)
            import_var("currentCycle", GLOBAL)
            #import_var("loadCountByLatency", GLOBAL)
            import_var("tlbMisses", GLOBAL)
            import_var("commitedAtomic", GLOBAL)
            #import_var("address", INST)


            df = pd.DataFrame(all_data)
            # have only the _delta columns
            giant_pair_plot(df[[col for col in df.columns if "_delta" in col]])

                



                



            mlp_stalls_0 = fill_if_needed(get_field(data[r]['0'], GLOBAL, 'L3stallCyclesMLPLoad', np.uint64), commited_0.shape[0])
            mlp_stalls_80 = fill_if_needed(get_field(data[r]['80'], GLOBAL, 'L3stallCyclesMLPLoad', np.uint64), commited_0.shape[0])
            #print("MLP stall increase", mlp_stalls_0)
            # fill the vectors if needed such that it has the same size as the others
            #(mlp_stalls_80 -
            mlp_stall_increase =   glob_0['L3stallCyclesMLPLoad'] / glob_0['currentCycle']

            # plot mlp_stalls_0 for each index 
            v = {}
            v['mlp_stalls_0'] = mlp_stalls_0
            def plot_var(var, di):
                plt.figure()
                plt.plot(di[var])
                plt.xlabel("Index")
                plt.ylabel("MLP stalls 0")
                plt.title("MLP stalls 0")
                # os make dir gen/mlp_stalls
                os.makedirs(f"{FIGS_FOLDER}/gen/vars/{var}", exist_ok=True)
                plt.savefig(f"{FIGS_FOLDER}/gen/vars/{var}/_0_{bench_name}_{bench_nr}_0.png")
                plt.close()
                
            plot_var("mlp_stalls_0", v)



            mlp_stalls_difference = (glob_80['L3stallCyclesMLPLoad'] - glob_0['L3stallCyclesMLPLoad']) / glob_0['currentCycle']
            reg_mlp = np.linalg.lstsq((mlp_stalls_0/cycles_0).reshape(-1, 1), real_slow_down, rcond=None)
            predicted_mlp_simple = mlp_stalls_0 * reg_mlp[0] #/memory_stalls_0
            if global_only:
                continue

            # scatter plot mlp_stalls_0 vs mlp_stalls_80
            def scatters():
                plt.figure()
                plt.scatter(real_slow_down,predicted_mlp_simple) #memory_stalls_0
                plt.xlabel("Real slowdown")
                plt.ylabel("MLP stalls STL increase")
                plt.legend()
                plt.title("MLP stalls STL increase vs Real slowdown")
                #print('DOOOOO')
                plt.savefig(f"{FIGS_FOLDER}/gen/mlp_best_{bench_name}_{bench_nr}.png")

                plt.figure()
                plt.scatter(mlp_stalls_0[clean_idxs], mlp_stalls_80[clean_idxs])
                plt.legend()
                plt.xlabel("MLP stalls 0")
                plt.ylabel("MLP stalls 80")
                plt.title("MLP stalls 0 vs MLP stalls 80")
                plt.savefig(f"{FIGS_FOLDER}/gen/mlp_stalls_{bench_name}_{bench_nr}.png")
                # scatter the difference vs real slowdown
                plt.figure()
                plt.scatter(real_slow_down[clean_idxs], mlp_stalls_difference[clean_idxs]*number_of_demand_reads[clean_idxs])
                plt.xlabel("Real slowdown")
                plt.ylabel("MLP stalls difference")
                plt.legend()
                plt.title("MLP stalls difference vs Real slowdown")
                plt.savefig(f"{FIGS_FOLDER}/gen/mlp_stalls_difference_{bench_name}_{bench_nr}.png")
                plt.figure()
                # scatter _0 vs real slowdown
                colors = ((delta_store_stalls[clean_idxs] / np.mean(delta_store_stalls[clean_idxs])))
                colors = (colors - np.min(colors)) / (np.max(colors) - np.min(colors))
                colors = colors * 255
                colors = colors.astype(np.uint8)

                plt.scatter(real_slow_down[clean_idxs], mlp_stall_increase[clean_idxs]*number_of_demand_reads[clean_idxs], c=colors)
                # color based on the store stall cycles 
                            
                plt.xlabel("Real slowdown")
                plt.ylabel("MLP stalls increase")
                plt.legend()
                plt.title("MLP stalls increase vs Real slowdown")
                plt.savefig(f"{FIGS_FOLDER}/gen/mlp_stall_increase_{bench_name}_{bench_nr}.png")
                # build correlation plot of all of these variables against each other
                plt.figure()
                plt.scatter(real_slow_down, mlp_stall_increase)
                # color based on the store stall cycles 
                            
                plt.xlabel("Real slowdown")
                plt.ylabel("MLP stalls STL increase")
                plt.legend()
                plt.title("MLP stalls STL increase vs Real slowdown")
                plt.savefig(f"{FIGS_FOLDER}/gen/mlp_no_adjust_{bench_name}_{bench_nr}.png")




            try:
                scatters()
            except Exception as e:
                print(e, "CONTII")
                #raise e
                
                pass
            

            # check if there are infinit numbers in stalled_0 or mlp_stalls_0
            if np.isinf(stalled_0).any() or np.isinf(mlp_stalls_0).any():
                print("Infinit numbers in stalled_0 or mlp_stalls_0")
                #continue


            # fit to find an x, such that stalled_0 * x = real_slow_down and the error is minimized
            # linear regression
            reg_stall =  np.linalg.lstsq((stalled_0/cycles_0).reshape(-1, 1), real_slow_down, rcond=None)
            #print("Stall regression", reg_stall[0])
            predicted_soar_simple = stalled_0 * reg_stall[0]


            """
            _ = mlp_stalls_0/memory_stalls_0
            plt.figure()
            plt.scatter(_, real_slow_down)
            plt.xlabel("MLP stalls increase")
            plt.ylabel("Real slowdown")
            plt.title("MLP stalls increase vs Real slowdown")
            plt.savefig(f"{FIGS_FOLDER}/gen/TRY_{bench_name}_{bench_nr}.png")
            continue
            # reg_mlp = np.linalg.lstsq((_).reshape(-1, 1), real_slow_down, rcond=None)
            predicted_mlp_prefit_memstalls = _ * reg_mlp[0]
            there is ABSOLUTELY no correlation between mlp_stalls_0/memory_stalls_0
            """

            #print("MLP regression", reg_mlp[0])
            # instead of trying to minimize the error in ALL points, try to minimize the error in 90% points closest to the median
            median = np.median(mlp_stalls_0)
            # find the 90% points closest to the median
            mlp_stalls_0_wout = mlp_stalls_0[np.abs(mlp_stalls_0 - median) < np.percentile(np.abs(mlp_stalls_0 - median), 90)]
            real_slow_down_wout = real_slow_down[np.abs(mlp_stalls_0 - median) < np.percentile(np.abs(mlp_stalls_0 - median), 90)]
            reg_mlp_wout = np.linalg.lstsq(mlp_stalls_0_wout.reshape(-1, 1), real_slow_down_wout, rcond=None)


            #reg_mlp_wout = np.linalg.lstsq(mlp_stalls_0_wout[200:].reshape(-1, 1), real_slow_down[200:], rcond=None)
            predicted_mlp_simple_wout = mlp_stalls_0 * reg_mlp_wout[0]
            #print("MLP regression wout", reg_mlp_wout[0])

            

            

            



            ############### TO DELETE
            AOL = cycles_with_demand_read/number_of_demand_reads 
            AOL = np.where(number_of_demand_reads == 0, 0, AOL) 
            #AOL_80 = cycles_with_demand_read_80/number_of_demand_reads
            # TODO does AOL change in the slow tier? yes -> MLP changes wiht device latency
            unadjusted_slowdown = stalled_0/cycles_0
            # fit unadjusted_slowdown * 1 / (a + b/AOL) =  real_slow_down to find a and b
            soar_mlp_aware_slowdown = obtain_soar_mlp_aware_slowdown(unadjusted_slowdown, AOL, real_slow_down)
            #soar_mlp_aware_slowdown_err = 



            



            
            #aol = commited_0.shape[0] - stall_difference.shape[0]


            # identify which points in real_slow_down are outliers
            #print("Max real slowdown now ", np.max(real_slow_down[clean_idxs]), "before was ", np.max(real_slow_down))
            real_slowdown_clean = real_slow_down[clean_idxs]

            AOL = cycles_with_demand_read/number_of_demand_reads 
            AOL = np.where(number_of_demand_reads == 0, 0, AOL) 
            #AOL_80 = cycles_with_demand_read_80/number_of_demand_reads
            # TODO does AOL change in the slow tier? yes -> MLP changes wiht device latency
            unadjusted_slowdown = stalled_0/cycles_0
            # fit unadjusted_slowdown * 1 / (a + b/AOL) =  real_slow_down to find a and b
            soar_mlp_aware_slowdown = obtain_soar_mlp_aware_slowdown(unadjusted_slowdown, AOL, real_slow_down)
            #soar_mlp_aware_slowdown_err = 
            predicted_soar_simple_clean = regress(stalled_0[clean_idxs], real_slowdown_clean)
            predicted_mlp_simple_clean = regress(mlp_stalls_0[clean_idxs], real_slowdown_clean)
            predicted_soar_simple_clean = regress(stalled_0[clean_idxs], real_slowdown_clean)
            soar_mlp_aware_slowdown_clean = obtain_soar_mlp_aware_slowdown(unadjusted_slowdown[clean_idxs], AOL[clean_idxs], real_slow_down[clean_idxs])

            
            global_increase = stalled_80.sum()-stalled_0.sum()
            def delta_contribution_to_slowdown(name):
                predicted = regress(all_data[name + "_0"], real_slow_down) * cycles_0
                all_data[name + "_contribution"] = (predicted)/global_increase #all_data[name + "_80"]-all_data[name + "_0"]

            print("CONTRIBUTE")
            def contribution_to_slowdown(name):
                all_data[name + "_contribution"] = (predicted*cycles_0)/global_increase #all_data[name + "_80"]-all_data[name + "_0"]
            def d(name):
                all_data[name + "_contribution"] = (((all_data[name + "_80"]-all_data[name + "_0"])))/global_increase #all_data[name + "_80"]-all_data[name + "_0"]
            d("currentCycle")
            d("stalledCycles")

            all_data['soar_simple_contribution'] = predicted_soar_simple*cycles_0/global_increase
            all_data['mlp_simple_contribution'] = predicted_mlp_simple*cycles_0/global_increase
            all_data['soar_mlp_aware_contribution'] = soar_mlp_aware_slowdown*cycles_0/global_increase
            all_data['store_stall_contribution'] = predicted_store_stalls*cycles_0/global_increase

            print("CONTRIBUTE")

            for k in all_data:
                if "contribution" in k:
                    all_data[k] *= 10000
                    # real contribution to slow down 
                    rc = all_data['currentCycle_contribution']
                    # small dot size with decreasing overall quality
                    plt.scatter(all_data[k], rc, label=k.split("_contribution")[0], s=1) 
                    plt.ylabel("Contribution to total slowdown")
                    plt.xlabel("Predicted contribution")
                    # x is log scale
                    plt.xscale("log")
                    plt.yscale("log")
                    plt.title(f"{bench_name} {bench_nr}")
                    plt.legend()
            
            plt.xlabel("Contribution to total slowdown")
            plt.savefig(f"{FIGS_FOLDER}/gen/contributions/GLOBAL_CONTRIB{bench_name}_{bench_nr}.png")
            plt.close()
            # plot PCA of all global metrics
            # import PCA
            from sklearn.decomposition import PCA
            try:
                pca = PCA(n_components=2)
                d = np.array([all_data[k] for k in all_data if "contribution" in k])
                # check that all in d have the same size
                pca.fit(d)
                x = pca.transform(d)
                plt.scatter(x[:,0], x[:,1])
                plt.xlabel("PC1")
                plt.ylabel("PC2")
                plt.title(f"{bench_name} {bench_nr}")
            except Exception as e:
                if not all([len(d[i]) == len(d[0]) for i in range(len(d))]):
                    print("Size is not the same for all metrics")
                print("Error in PCA",e)
                #raise e
            # print the most important metrics
            print(pca.components_)
            plt.savefig(f"{FIGS_FOLDER}/gen/contributions/GLOBAL_PCA{bench_name}_{bench_nr}.png")
            plt.close()



            # quando há duvidas, há falta de conhecimento

            # wishkers plot of real_slow and all metrics obtained 
            plt.figure(figsize=(10,15))
            plt.xticks(rotation=45)
            plt.boxplot([real_slow_down, predicted_soar_simple, predicted_mlp_simple, predicted_soar_simple_clean, predicted_mlp_simple_clean], tick_labels=["Real Slowdown", "Soar Simple", "MLP Simple", "Soar Simple Clean", "MLP Simple Clean"])
            plt.ylim(0, 10)
            plt.savefig(f"{FIGS_FOLDER}/gen/box/slowdowns_{bench_name}_{bench_nr}.png")
            plt.close()
            plt.figure(figsize=(10,15))
            plt.xticks(rotation=45)
            plt.boxplot([stalled_0, mlp_stalls_0, number_of_demand_reads], tick_labels=["Stalled Cycles", "MLP Stalled Cycles", "Number of Demand Reads"])
            plt.ylim(0, 500)
            plt.savefig(f"{FIGS_FOLDER}/gen/box/pmu_counters_{bench_name}_{bench_nr}.png")
            plt.close()
            

            
            print("Error for run", r)
            # use R^2 instead of mean squared error
            def r_squared(y_true, y_pred):
                # return not r^2 but correlation
                return np.corrcoef(y_true, y_pred)[0][1]
            def r_squared(y_true, y_pred):
                r = 1 - np.sum((y_true - y_pred) ** 2) / np.sum((y_true - np.mean(y_true)) ** 2)
                r = np.abs(r)
                return r
            def r_squared(y_true, y_pred):
                return np.square(np.subtract(y_true, y_pred)).mean()

            print("Error predict stall cycles", r_squared(real_slow_down, predicted_soar_simple))

            print("Error predict weighed stall cycles", r_squared(real_slow_down, predicted_mlp_simple))
            print("Error predict weighed stall cycles", r_squared(real_slow_down, soar_mlp_aware_slowdown))
            print("Error predict weighed stall cycles", r_squared(real_slow_down, predicted_store_stalls))
            print("Error for CLEAN")
            print("Error Soar Simple", r_squared(real_slow_down[clean_idxs], predicted_soar_simple_clean))
            print("Error MLP Weighed Simple", r_squared(real_slow_down[clean_idxs], predicted_mlp_simple_clean))
            print("Error Soar MLP aware", r_squared(real_slow_down[clean_idxs], soar_mlp_aware_slowdown_clean))
            #print("Error predict weighed stall cycles", np.mean((real_slow_down[clean_idxs] - predicted_store_stalls_clean) ** 2))

            last_stall_time = fill_if_needed(get_field(data[r]['0'], GLOBAL, 'lastStallTime', np.uint64), commited_0.shape[0]) 
                
            # bar plot these errors
            plt.figure(figsize=(15,15))
            # labels at 45 
            plt.xticks(rotation=45)
            # y lim is 100
            #plt.ylim(0, 10)


            plt.bar("Stalled Cycles", r_squared(real_slow_down, stalled_0/cycles_0))
            plt.bar("Mem Stalled Cycles", r_squared(real_slow_down, memory_stalls_0/cycles_0))
            plt.bar("Soar Simple", r_squared(real_slow_down, predicted_soar_simple))
            plt.bar("MLP Simple", r_squared(real_slow_down, predicted_mlp_simple))
            plt.bar("MLP Simple(N CYCLES)", r_squared(real_slow_down, predicted_mlp_simple/cycles_0))
            plt.bar("MLP Simple(N READS)", r_squared(real_slow_down, predicted_mlp_simple/number_of_demand_reads))
            plt.bar("MLP Simple(N M_STL)", r_squared(real_slow_down, predicted_mlp_simple/memory_stalls_0))

            plt.bar("Soar MLP aware", r_squared(real_slow_down, soar_mlp_aware_slowdown))
            plt.bar("Soar MLP aware*L", r_squared(real_slow_down, soar_mlp_aware_slowdown * number_of_demand_reads))
            plt.bar("MLP*N_L ", r_squared(real_slow_down, mlp_stall_increase * number_of_demand_reads))
            plt.bar("MLP*N_L NOR", r_squared(real_slow_down, mlp_stall_increase * number_of_demand_reads/ cycles_0))
            high_precision_stalls = mlp_stall_increase * number_of_demand_reads/ cycles_0
            # fit 
            plt.bar("MLP*N_L FIT", r_squared(regress(high_precision_stalls, real_slow_down), real_slow_down))
            plt.bar("MLP*N_L FIT CLEAN", r_squared(regress(high_precision_stalls[clean_idxs], real_slow_down[clean_idxs]), real_slow_down[clean_idxs]))
            # fit for these 3 variables
            inp = np.column_stack([
                mlp_stall_increase,
                number_of_demand_reads,
                cycles_0
            ])



            # solve the least-squares problem
            coefs, residuals, rank, s = np.linalg.lstsq(inp, real_slow_down, rcond=None)



            # predicted = inp @ coefs
            predicted = inp.dot(coefs)

            complete = np.column_stack([
                store_stalls_0,
                memory_stalls_0,
            ])
            coefs, residuals, rank, s = np.linalg.lstsq(complete, real_slow_down, rcond=None)
            combined_predicted = complete.dot(coefs)
            plt.bar("Combined", r_squared(combined_predicted, real_slow_down))
            #from ltsfit import LtsFit
            # calculate the predicted values
            plt.bar("MLP*N_L 3333", r_squared(predicted, real_slow_down))
            plt.bar("Last Stall Time", r_squared(real_slow_down, last_stall_time))
            #plt.bar("Predicted Store Stalls", r_squared(real_slow_down, predicted_store_stalls))
            plt.bar("Soar Simple CLEAN", r_squared(real_slow_down[clean_idxs], predicted_soar_simple_clean))
            plt.bar("Soar Simple*L CLEAN", r_squared(real_slow_down[clean_idxs], predicted_soar_simple_clean * number_of_demand_reads[clean_idxs]))
            plt.bar("Soar Simple/L CLEAN", r_squared(real_slow_down[clean_idxs], predicted_soar_simple_clean / number_of_demand_reads[clean_idxs]))
            plt.bar("MLP Simple CLEAN", r_squared(real_slow_down[clean_idxs], predicted_mlp_simple_clean))
            plt.bar("MLP*Nr Loads (normalized) CLEAN", r_squared(real_slow_down[clean_idxs], (mlp_stall_increase * number_of_demand_reads/ cycles_0)[clean_idxs]))
            plt.bar("MLP (normalized)", r_squared(real_slow_down[clean_idxs], (mlp_stall_increase / cycles_0)[clean_idxs]))
            plt.bar("Soar MLP aware CLEAN", r_squared(real_slow_down[clean_idxs], soar_mlp_aware_slowdown_clean))
            plt.bar("Soar MLP*L CLEAN", r_squared(real_slow_down[clean_idxs], soar_mlp_aware_slowdown_clean * number_of_demand_reads[clean_idxs]))
            #plt.bar("Predicted Store Stalls CLEAN", r_squared(real_slow_down[clean_idxs], predicted_store_stalls_clean))
            bench_name = data[r]['0']['bench'].split("/")[-1]
            plt.title(f"{bench_name} {bench_nr}")
            plt.savefig(f"{FIGS_FOLDER}/gen/MSREerrors_{bench_name}_{bench_nr}.png")

            def accuracy_cdf(n1, n2):
                plt.figure(figsize=(8, 6))
                actual_slowdown = v[n1]
                predicted_slowdown = v[n2]

                # Plot CDFs using matplotlib's built-in ecdf function
                plt.ecdf(actual_slowdown, label='Actual', color='black', linewidth=2)
                plt.ecdf(predicted_slowdown, label='Predicted', color='#CD5C5C', linewidth=2)

                # Customize the plot
                plt.xlabel('Slowdown (%)', fontsize=12)
                plt.ylabel('Accuracy CDF', fontsize=12)
                plt.title('[a] ΔLLC-Stall\nAccuracy CDF', fontsize=14, pad=20)

                # Set axis limits and formatting
                plt.xlim(0, 100)
                plt.ylim(0, 1)

                # Add legend and grid
                plt.legend(fontsize=12, loc='lower right')
                plt.grid(True, alpha=0.3)

                plt.tight_layout()
                plt.show()

                plt.savefig(f"{FIGS_FOLDER}/gen/correlation/cdf_{bench_name}_{bench_nr}_{n1}_{n2}.png")
                plt.close()
            
            v = {'real': real_slow_down, 'soar_simple': predicted_soar_simple, 'mlp_simple': predicted_mlp_simple, 'soar_mlp_aware': soar_mlp_aware_slowdown}
            for k in v:
                accuracy_cdf('real', k)

            def plot_correlation():
                        # plot the correlation between real slow down and the variables used for prediction
                        plt.figure(figsize=(10,15))
                        plt.scatter(real_slow_down, predicted_soar_simple)
                        plt.scatter(real_slow_down, predicted_mlp_simple)
                        plt.scatter(real_slow_down, soar_mlp_aware_slowdown)
                        plt.legend()
                        # scale log
                        plt.xscale('log')
                        plt.yscale('log')
                        #plt.scatter(real_slow_down, predicted_store_stalls)
                        #plt.scatter(real_slow_down, predicted_load_n_store_weighted)
                        plt.legend(["Soar Simple", "MLP Simple", "Soar MLP aware"])
                        plt.xlabel("Real Slow Down (%)")
                        plt.ylabel("Predicted Slow Down (%)")
                        plt.title(f"{bench_name} {bench_nr}")
                        plt.savefig(f"{FIGS_FOLDER}/gen/correlation/realslow_{bench_name}_{bench_nr}.png")
            plt.close()
            plot_correlation()
                        
            
            # THE MLP weighted does not account for the nr of requests! 

            # if MLP stalls increases a lot = there is a lower level of paralellism when memory is slower!

            LIMIT=commited_0.shape[0]-1
            LIMIT_NR = commited_0[LIMIT]
        except FileNotFoundError as e:
            print(e)
            continue
        except Exception as e:
            print(e)
            print("BIG MISTAKE", e)
            print('RUN', doing_runs[-1], len(doing_runs))
            #raise e
            continue

        # plot x = commited instructions, y = real slow down, soar stall increase, mlp stall increase
        # add jitter and transparency to each 
        #soar_stall_increase = np.random.normal(soar_stall_increase, 0.1, soar_stall_increase.shape[0])
        #mlp_stall_increase = np.random.normal(mlp_stall_increase, 0.1, mlp_stall_increase.shape[0])
        #  real_slow_down = np.random.normal(real_slow_down, 0.1, real_slow_down.shape[0])
        # select only the first 100 points
        # extremely wide figure

        # instead of normal plot function, the plot makes the average of the last n points
def _iterate_time_series(data,r):
    commited_0 = (get_field(data[r]['0'], GLOBAL, 'commitedInstructions', np.uint64))
    #commited_0.shape[0]
    commited_80 = (get_field(data[r]['80'], GLOBAL, 'commitedInstructions', np.uint64))

    
    instructions = get_field(data[r]['0'], INST, 'address', np.uint64)
    print("Instructions shape", instructions.shape)
    # do histogram of instructions 
    #hist = np.histogram(instructions, bins=1)
    # print number of insts
    #print("Number of instructions", hist[0].shape[0])
    

    

    stalled_0 = fill_if_needed(get_field(data[r]['0'], GLOBAL, 'stalledCycles', np.uint64), commited_0.shape[0])
    stalled_80 = fill_if_needed(get_field(data[r]['80'], GLOBAL, 'stalledCycles', np.uint64), commited_0.shape[0])

    memory_stalls_0 = fill_if_needed(get_field(data[r]['0'], GLOBAL, 'stalledCyclesWithMemRequests', np.uint64), commited_0.shape[0])
    memory_stalls_80 = fill_if_needed(get_field(data[r]['80'], GLOBAL, 'stalledCyclesWithMemRequests', np.uint64), commited_0.shape[0]) 
    stalled_0 = memory_stalls_0
    stalled_80 = memory_stalls_80

    # 16:04
    # normalize the sum of all slow downs to be 1
    # increase_in_stalls_instant * (1/total_stall_increase)
    # 
    

    cycles_0 = fill_if_needed(get_field(data[r]['0'], GLOBAL, 'currentCycle', np.uint64), commited_0.shape[0])
    #  find which items are 0 in cycles_0
    print("0000000000000", len(cycles_0[cycles_0 == 0]))
    cycles_0[cycles_0 == 0] = int(np.iinfo(np.uint64).max)
    

    cycles_80 = fill_if_needed(get_field(data[r]['80'], GLOBAL, 'currentCycle', np.uint64), commited_0.shape[0])


    LIMIT=commited_0.shape[0]-1
    LIMIT_NR = commited_0[LIMIT]
    if(commited_0.shape[0] <  50):
        print("BAD FILE")
        return # bad file
    average_window=1 # normal case
    #commited_0 = np.convolve(commited_0, np.ones(average_window)/average_window, mode='valid')
    real_slow_down = np.convolve(real_slow_down, np.ones(average_window)/average_window, mode='valid')
    predicted_soar_simple = np.convolve(predicted_soar_simple, np.ones(average_window)/average_window, mode='valid')
    predicted_mlp_simple = np.convolve(predicted_mlp_simple, np.ones(average_window)/average_window, mode='valid')
    predicted_load_n_store_weighted = np.convolve(predicted_load_n_store_weighted, np.ones(average_window)/average_window, mode='valid')
    predicted_store_stalls = np.convolve(predicted_store_stalls, np.ones(average_window)/average_window, mode='valid')
    stall_difference = np.convolve(stall_difference, np.ones(average_window)/average_window, mode='valid')
    delta_store_stalls = np.convolve(delta_store_stalls, np.ones(average_window)/average_window, mode='valid')
    soar_mlp_aware_slowdown = np.convolve(soar_mlp_aware_slowdown, np.ones(average_window)/average_window, mode='valid')


    def time_series(error=True, gold_metrics=None):
        def plot_aol():
            plt.figure(figsize=(50,10))
            plt.title(f"{bench_name} {bench_nr} AOL")
            plt.xlabel("Commited Instructions")
            plt.ylabel("AOL")
            plt.plot(commited_0[:LIMIT], AOL[:LIMIT+diff], alpha=0.5, label="AOL")
            plt.legend()
            plt.savefig(f"{FIGS_FOLDER}/gen/timeseries/single/aol_{bench_name}_{bench_nr}.png")
            plt.close()

        print("DOING TIME SERIES ", bench_name, bench_nr)
        LIMIT = commited_0.shape[0]-average_window
        diff = 0

        plot_aol()

        plt.figure(figsize=(50,10))
        print(commited_0.shape, soar_mlp_aware_slowdown.shape)
        def adjust_for_error(x):
            # how to subtract uint64 from uint64? and ensure the result is valid?
            # convert to int64
            x = x.astype(np.int64)
            ru = real_slow_down.astype(np.int64)
            error = x - ru[:LIMIT+diff]
            cap = error > 2 
            error[cap] = 2
            cap = error < -2 
            error[cap] = -2
            plt.ylim(-2.1, 2.1)
            return error
        if error:
            adj = adjust_for_error
        else:
            adj = lambda x: x
            
        if gold_metrics is not None:
            plt.plot(commited_0[:LIMIT], adj(soar_mlp_aware_slowdown[:LIMIT+diff]), alpha=0.5, label="Soar MLP Aware Slowdown", linewidth=2)
            #plt.plot(commited_0[:LIMIT], error(predicted_mlp_simple[:LIMIT+diff]/cycles_0[:LIMIT+diff]), alpha=0.5, label="MLP")
            plt.plot(commited_0[:LIMIT], adj(predicted_mlp_simple[:LIMIT+diff]/memory_stalls_0[:LIMIT+diff]), alpha=0.5, label="MLP", linewidth=5)
            plt.plot(commited_0[:LIMIT], adj(predicted_soar_simple[:LIMIT+diff]), alpha=0.5, label="Soar Simple", linewidth=4)
            plt.plot(commited_0[:LIMIT], adj(real_slow_down[:LIMIT+diff]), alpha=0.5, label="Real Slowdown", linewidth=3) # make thick
            # plot over the  number of requests per cycle (this variable is on another scale, thus we need to use a different axis)
            plt.legend()
            plt.twinx()
            plt.plot(commited_0[:LIMIT], AOL[:LIMIT+diff], alpha=0.5, label="AOL", color="red")
        else:
            plt.plot(commited_0[:LIMIT], adj(soar_mlp_aware_slowdown[:LIMIT+diff]), alpha=0.5, label="Soar MLP Aware Slowdown")
            plt.plot(commited_0[:LIMIT], adj(stall_difference[:LIMIT+diff]), alpha=0.5, label="∆Load Stalls/c")
            plt.plot(commited_0[:LIMIT], adj(delta_store_stalls[:LIMIT+diff]), alpha=0.5, label="∆Store Stalls/c")
            plt.plot(commited_0[:LIMIT], adj(predicted_load_n_store_weighted[:LIMIT+diff]), alpha=0.5, label="Predicted Weighed Store+Load Slowdown")
            plt.plot(commited_0[:LIMIT], adj(predicted_soar_simple[:LIMIT+diff]), alpha=0.5, label="Predicted Slowdown with Memory Stalls")
            plt.plot(commited_0[:LIMIT], adj(predicted_mlp_simple[:LIMIT+diff]), alpha=0.5, label="Predicted Weighed Slowdown with weighted Memory Stalls")
            plt.plot(commited_0[:LIMIT], adj(predicted_mlp_simple_wout[:LIMIT+diff]), alpha=0.5, label="Predicted MLP Slowdown (W/o Outliers)")
            #plt.plot(commited_0[:LIMIT], mlp_stall_increase[:LIMIT], alpha=0.5, label="MLP Stall Increase")
            plt.plot(commited_0[:LIMIT], adj(real_slow_down[:LIMIT+diff]), alpha=0.5, label="Real Slowdown", linewidth=3) # make thick
            # at commited_0 = 1000 , place a vertical line
            plt.plot(commited_0[:LIMIT], adj(predicted_store_stalls[:LIMIT+diff]), alpha=0.5, label="Predicted Store Stalls")

    # PLOT average MLP
    # PLOT overfitted SOAR's method -> its overfitted, with more parameters, and its still worst ( damos o benefitio e perdem na mesma)
    # Há uns dias a trás, quando estava a fazer o debug do gem5, acabei por implementar também o tracking de stores. 
    # conclusion: the weighted stall cycles truly represent the extent of the performance degradation
    
    # it becomes above 1 if its estimated to be a slow down greater than 1!

        max_slow_down = np.max(real_slow_down)
        #plt.ylim(0, 2)
        
        def add_timestamps():
            timestamps, lines = get_print_timestamps(data[r]['0'])
            xmax = np.max(commited_0)
            
            last_timestamp = 0
            last_line = ''
            
            ax = plt.gcf().gca()
            tick = ax.get_xticklabels()[0]
            fontsize_pt = tick.get_fontsize()
            dpi = plt.gcf().dpi
            fontsize_px = fontsize_pt * dpi 
            pixels_per_tick = ax.get_xbound()[1] / xmax
            text_height_px = fontsize_px + 1
            space_between_timestamps = pixels_per_tick * text_height_px
            # same thing but for y
            tick = ax.get_yticklabels()[0]
            fontsize_pt = tick.get_fontsize()
            dpi = plt.gcf().dpi
            fontsize_px = fontsize_pt * dpi  / 72.0
            pixels_per_tick = ax.get_ybound()[1] / max_slow_down
            text_height_px = fontsize_px + 1
            space_between_timestamps = pixels_per_tick * text_height_px


            for timestamp, line in zip(timestamps[5:], lines[5:]):
                if timestamp > LIMIT_NR:
                    break
                    
                plt.axvline(x=timestamp, color='g', linestyle='--')
                # ensure the text is spaced enough from the others
                actual_space =  timestamp - last_timestamp 
                # convert to signed int 
                missing_properspace = int(actual_space) - int(space_between_timestamps )
                if  missing_properspace < 0:
                    if "memstate" in last_line and "memstate" in line:
                        continue
                    timestamp = last_timestamp - missing_properspace 
                plt.text(timestamp, 0,  "Created VMAs" if "creating vma" in line else line, rotation=90, verticalalignment='bottom', horizontalalignment='center')

                last_timestamp = timestamp
                last_line = line
        
        plt.legend()
        # get the bench name from the run
        plt.title(f"{bench_name} {bench_nr}")
        plt.savefig(f"{FIGS_FOLDER}/gen/timeseries/{bench_name}_{bench_nr}_{'gold' if gold_metrics else 'all'}_{'error' if error else 'absolute'}.png")
        print("PLOTED")
        plt.close()
    time_series(gold_metrics=1)
    time_series(gold_metrics=1, error=False)
    time_series(gold_metrics=1, error=False)
    time_series(gold_metrics=None)
    return


    

    while len(data[r]['0']['global']) > i+1:
        data[r]['0']['pid']

        cycles = data[r]['0']['global'][i+1].currentCycle - data[r]['0']['global'][i].currentCycle
        if cycles == 0:
            cycles = 1
        commitedInstructions = data[r]['0']['global'][i+1].commitedInstructions - data[r]['0']['global'][i].commitedInstructions


        cycles_on_slow = data[r]['80']['global'][i+1].currentCycle - data[r]['80']['global'][i].currentCycle
        slow_down = ((cycles- cycles_on_slow) / cycles)

        stall_cycles = data[r]['0']['global'][i+1].stalledCycles - data[r]['0']['global'][i].stalledCycles
        stall_cycles_on_slow = data[r]['80']['global'][i+1].stalledCycles - data[r]['80']['global'][i].stalledCycles
        soar_simple_stall_slowdown = (stall_cycles - stall_cycles_on_slow) / cycles

        mlp_stall_fast = (data[r]['0']['global'][i+1].stallCyclesMLPLoad - data[r]['0']['global'][i].stallCyclesMLPLoad)/cycles
        mlp_stall_slow = (data[r]['80']['global'][i+1].stallCyclesMLPLoad - data[r]['80']['global'][i].stallCyclesMLPLoad)/cycles
        mlp_stall_diff = (mlp_stall_fast*cycles - mlp_stall_slow*cycles) / cycles

        to_plot['Slow down'].append(slow_down)
        to_plot['Stall cycles'].append(stall_cycles)
        to_plot['MLP stall'].append(mlp_stall_diff)
        to_plot['Commited Instructions'].append(commitedInstructions)
    # plot over time (x axis is the commited instructions) 
    print(to_plot['Commited Instructions'])
    plt.plot(to_plot['Commited Instructions'], to_plot['Slow down'])
    plt.xlabel('Commited Instructions')
    for k in to_plot:
        if k == 'Commited Instructions':
            continue
        plt.plot(to_plot['Commited Instructions'], to_plot[k])

    # save to file
    plt.savefig(f"{FIGS_FOLDER}/plots/{r}.png")
    plt.close()


def iterate_time_series(data,r):
    try: 
        _iterate_time_series(data,r)
    except Exception as e:
        print(e)
        print(data[r]['0']['bench'])
        #print('RUN', doing_runs[-1], len(doing_runs))
    

def plot_global_results():
    # real slow down vs the fitted metrics
    for k in global_results:
        print(k, len(global_results[k]))
        print(global_results[k])
        global_results[k] = np.array(global_results[k])
    #global_results['predicted_stall_cycles'] = regress( np.array(global_results['stall_cycles']),np.array(    global_results['mem_stalls']))
    #var = np.array(global_results['mem_stalls_weighted'])/np.array(global_results['cycles']) #/ np.array(global_results['commitedLoads'] )
    #global_results['predicted_mlp_simple'] = regress(var,np.array(global_results['real_slowdown']) ) / np.array(global_results['mem_stalls'])

    # iterate over all to convert to np array
    for k in global_results:
        global_results[k] = np.array(global_results[k])

    def multi_regress(vars):
            inp = np.column_stack(vars)
            # solve the least-squares problem
            coefs, residuals, rank, s = np.linalg.lstsq(inp, global_results['real_slowdown'], rcond=None)
            # predicted = inp @ coefs
            predicted = inp.dot(coefs)
            return predicted



    #global_results['predicte d_load_n_store_weighted'] = multi_regress([  global_results['mem_stalls_weighted']/global_results['cycles'], global_results['store_stalls']/global_results['cycles'], ])
    #global_results['predicte d_store_stalls'] = multi_regress([ global_results['store_stalls']/global_results['cycles'], ])

    #print(len(glo))
    print(len(global_results['stall_cycles']), len(global_results['aol']), len(global_results['real_slowdown']), len(global_results['cycles']))
    global_results['predicted_soar_mlp_aware_slowdown'] = obtain_soar_mlp_aware_slowdown(global_results['stall_cycles']/global_results['cycles'], global_results['aol'], global_results['real_slowdown'])
        
    plt.figure()
    # for each key that starts with "predicted" plot against real_slowdown
    plt.plot([0,1], [0,1], label='y = x')
    for k in global_results:
        if k.startswith('predicted'):
            plt.scatter(global_results['real_slowdown'], global_results[k], label=k)
            plt.xlabel('Real Slowdown')
            # draw line y = k * x that better fits the data
            #reg = np.polyfit(global_results['real_slowdown'], global_results[k], 1)
            # draw line from 0 to 1
            #plt.plot([0,1], [0,reg[0]], label=k)
            
    plt.scatter(global_results['real_slowdown'], global_results['predicted_mlp_simple'], label='mlp_simple')
    # draw a line of best fit for each predicted metric
    """
    for k in global_results:
        if k.startswith('predicted'):
            # y = x*k
            coef = np.corrcoef(global_results['real_slowdown'], global_results[k])[0][1]
            # draw line from 0 to 1 
            plt.plot([0,1], [0,coef], label=k)
    """
    plt.legend()
    plt.savefig(f'{FIGS_FOLDER}/gen/global/real_slowdown_vs_predicted_soar_simple.png')
    plt.close()
    # plot the error for each
    def error(y_true, y_pred):
        # MSRE  error
        msre = np.square(np.subtract(y_true, y_pred)).mean()
        #msre = np.mean(np.abs(y_true - y_pred) / y_true)
        
        return msre #np.abs(y_true - y_pred)
    plt.figure()
    for k in global_results:
        if k.startswith('predicted'):
            print('plotting ' + k)
            #plt.boxplot(error(global_results['real_slowdown'], global_results[k]))
            plt.bar(k,error(global_results['real_slowdown'], global_results[k]).mean())
    plt.savefig(f'{FIGS_FOLDER}/gen/global/err_all_msr.png')
    plt.close()

    
# 
data = load_bench_data()

old_RUN_DATA_FOLDER= RUN_DATA_FOLDER
old_run_meta = run_meta

RUN_DATA_FOLDER="/mnt/nas/inesc/ist196723/osdi26/v4/results_gem5"
RUN_DATA_FOLDER_V4="/mnt/nas/inesc/ist196723/osdi26/v4/results_gem5"
#RUN_DATA_FOLDER="/mnt/nas/inesc/ist196723/osdi26/results_gem5"
run_meta=f"{RUN_DATA_FOLDER}/gem5_pids.txt"
data_v4 = load_bench_data()

RUN_DATA_FOLDER=old_RUN_DATA_FOLDER
run_meta=old_run_meta
#print(data)

def plot_global_sample_cost():
    
    print("GLOBAL SAMP COST")
    print(cost_workloads)
    number_of_plots = len(cost_workloads)
    # sub plot all in the same image
    fig, axs = plt.subplots(number_of_plots, 1, figsize=(20, 150))
    for i, f in enumerate(cost_workloads):
        # plot cost_real vs cost_inst_%L3MLPstall
        axs[i].scatter(cost_workloads['cost_real'] , cost_workloads[f])
        axs[i].set_xlabel('Cost Real')
        axs[i].set_ylabel(f)
        axs[i].set_title(f'Cost Real vs Cost Inst {f}')
        axs[i].grid(alpha=0.3)
    name =f'{FIGS_FOLDER}/gen/global/cost_real_vs_cost_inst_all.png' 
    print(name)
    plt.savefig(name)
    plt.close()

    for f in cost_workloads:
        # print the size of each key
        print(f, len(cost_workloads[f]), "REAL", len(cost_workloads['cost_real'])) #, cost_workloads[f].shape, cost_workloads['cost_real'].shape)
        plt.figure(figsize=(8, 8))

        plt.scatter(cost_workloads[f] , cost_workloads['cost_real']) #label=naming_cost_workloads)
        #plt.legend()




        for i in range(len(cost_workloads[f])):
            # get x and y
            continue
            xpos = cost_workloads['cost_real'][i]
            ypos = cost_workloads[f][i]

            # replace nan/inf
            if not np.isfinite(xpos): xpos = 1.5
            if not np.isfinite(ypos): ypos = 1.5e22
            xpos = np.ulong(xpos)
            ypos = np.ulong(ypos)

            # annotate with a small offset
            plt.annotate(
                "pt{}".format(i),
                xy=(xpos, ypos),
                xytext=(5, 5),               # 5 points right, 5 points up
                textcoords='offset points',
                ha='left',
                va='bottom',
                arrowprops=dict(arrowstyle='->', color='gray', lw=0.5),
                fontsize=8
            )

        plt.xlabel('Cost')
        plt.ylabel('Real Slowdown')
        plt.title(f)
        plt.grid(alpha=0.3)
        plt.tight_layout()

        f = f.replace('%', 'P').replace('/', 'D')
        plt.savefig(f'{FIGS_FOLDER}/gen/global/cost_{f}.png')
        plt.close()



    plt.figure(figsize=(30, 30))
    for f in cost_workloads:
        plt.bar(f, np.corrcoef(cost_workloads[f], cost_workloads['cost_real'])[0][1], label=f)
    plt.xlabel('Cost Name')
    plt.ylabel('Correlation')
    plt.xticks(rotation=45)
    plt.title('Correlation of cost with real slowdown')
    plt.legend()
    plt.savefig(f'{FIGS_FOLDER}/gen/global/corr.png')
    plt.close()

merged_slowdown = np.array([])
merged_together = {
    "commitedLoads" : np.array([]),
    "totalStalledCyclesSummed": np.array([]),
    "totalL3StalledCyclesSummed": np.array([]),
    "totalL3MLPStalledCyclesSummed": np.array([]),
    "totalMLPStalledCyclesSummed": np.array([]),
                       }
others_merged = {
    "MLPL3 D stallCycles": np.array([]),
    
}
weird_runs = []
def simple_instruction_slowdown(data,r):
    global runs_with_weird_stuff

    i = load_inst_fields(data, r)
    i80 = load_inst_fields(data, r, '80')
    g0 = load_global_fields(data, r)
    g80 = load_global_fields(data, r, '80')
    try:
        last_idx = get_last_idx_of_smallest_vector(g80['currentCycle'],g0['currentCycle'])
        if len(g80['currentCycle']) < 500  or len(g0['currentCycle']) <500 :
            runs_with_weird_stuff += 1
            return
    except Exception as e :
        runs_with_weird_stuff += 1
        weird_runs.append(data[r])
        return
    slowdown = g80['currentCycle'][last_idx]/g0['currentCycle'][last_idx]

    d = {'cost_inst_LLCmiss_abs': np.array([]),
    'cost_inst_stall_time_abs': np.array([]),
    'cost_inst_L3stall_time_abs': np.array([]),
    'cost_inst_L3MLP_abs': np.array([]),
    'cost_inst_stalls': np.array([]),
    'cost_inst_MLP_abs': np.array([]),
    'cost_inst_stall_time': np.array([]),
    'cost_inst_L3stall_time': np.array([]),
    'cost_inst_L3MLP': np.array([]),
    'cost_inst_MLP': np.array([]),
    'average_mlp_middle': np.array([]),
    'average_mlp_end': np.array([]),
    'average_mlp_start': np.array([]),
    'cost_inst_LLCmiss': np.array([]),
    'cost_inst_total_time': np.array([]),
    'cost_inst_diff_stall': np.array([]),
    'cost_inst_diff_total': np.array([]),
         }
    slowdownsss = np.array([])


    for ii in range(last_idx-1):
        limit_now = g0['currentCycle'][ii] 
        limit_after = g0['currentCycle'][ii+1] ########### boundary condition
        cycles_elapsed = (g80['currentCycle'][ii] -limit_now  ) +1
        indexes = np.where((limit_now < i['start_cycle']) & (i['start_cycle'] < limit_after))
        #indexes = np.where( limit_now < i['start_cycle'] and i['start_cycle'] < limit_after)
        nr_of_insts = len(i['start_cycle'][indexes])

        slow_down = g80['currentCycle'][ii]/g0['currentCycle'][ii]
        slowdownsss = np.append(slowdownsss, slow_down)
        inside_factor = 1
        d['cost_inst_LLCmiss_abs'] = np.append(d['cost_inst_LLCmiss_abs'], nr_of_insts )
        d['cost_inst_stall_time_abs'] = np.append(d['cost_inst_stall_time_abs'], np.sum(i['stallTime'][indexes]/inside_factor) )
        d['cost_inst_L3stall_time_abs'] = np.append(d['cost_inst_L3stall_time_abs'], np.sum(i['L3stallTime'][indexes]/inside_factor) )
        d['cost_inst_L3MLP_abs'] = np.append(d['cost_inst_L3MLP_abs'], np.sum(i['L3stallCyclesMLPLoad'][indexes]/inside_factor) )
        d['cost_inst_stalls'] = np.append(d['cost_inst_stalls'], np.sum(i['stallTime'][indexes]/inside_factor) /cycles_elapsed)
        d['cost_inst_MLP_abs'] = np.append(d['cost_inst_MLP_abs'], np.sum(i['stallCyclesMLPLoad'][indexes]/inside_factor) )
        d['cost_inst_stall_time'] = np.append(d['cost_inst_stall_time'], np.sum(i['stallTime'][indexes]/inside_factor) / cycles_elapsed)
        d['cost_inst_L3stall_time'] = np.append(d['cost_inst_L3stall_time'], np.sum(i['L3stallTime'][indexes]/inside_factor) / cycles_elapsed)
        d['cost_inst_L3MLP'] = np.append(d['cost_inst_L3MLP'], np.sum(i['L3stallCyclesMLPLoad'][indexes]/inside_factor) / (cycles_elapsed*MLP_PRECISION_FACTOR))
        d['cost_inst_MLP'] = np.append(d['cost_inst_MLP'], np.sum(i['stallCyclesMLPLoad'][indexes]/inside_factor) / (cycles_elapsed*MLP_PRECISION_FACTOR))


        d['average_mlp_middle'] = np.append(d['average_mlp_middle'], np.sum(i['L3MLP_load_at_middle'][indexes]) / cycles_elapsed)
        d['average_mlp_end'] = np.append(d['average_mlp_end'], np.sum(i['L3MLP_load_at_end'][indexes]) / cycles_elapsed)
        d['average_mlp_start'] = np.append(d['average_mlp_start'], np.sum(i['L3MLP_load_at_start'][indexes]) / cycles_elapsed)
        d['cost_inst_LLCmiss'] = np.append(d['cost_inst_LLCmiss'], nr_of_insts / cycles_elapsed)
        d['cost_inst_total_time'] = np.append(d['cost_inst_total_time'], np.sum(i['totalTime'][indexes]) / cycles_elapsed)

        #d['cost_inst_diff_stall'] = np.append(d['cost_inst_diff_stall'], np.sum(i80['stallTime']-i['stallTime']) / cycles_elapsed)
        #d['cost_inst_diff_total'] = np.append(d['cost_inst_diff_total'], np.sum(i80['totalTime']-i['totalTime']) / cycles_elapsed)
    for m in d.keys():
        plt.figure(figsize=(30, 30))
        plt.scatter(slowdownsss, d[m])
        plt.xlabel('Real Slowdown')
        plt.ylabel(m)
        plt.title(f'Real Slowdown vs {m}')
        plt.grid(alpha=0.2)
        plt.tight_layout()
        benchname = data[r]['0']['bench'].split("/")[-1]
        benchnr = data[r]['0']['benchnr']
        folder = f'{FIGS_FOLDER}/gen/bench/{benchname}/{benchnr}/inst'
        if not os.path.exists(folder):
            os.makedirs(folder)
        plt.savefig(f'{folder}/interval_slow_{m}.png')
        plt.close()
        
def simple_slow_sown(data,r):
    global runs_with_weird_stuff
    global merged_slowdown
    global merged_together
    gc0 = load_global_fields_crescendo(data, r)
    gc80 = load_global_fields_crescendo(data, r,'80')
    g0 = load_global_fields(data, r)
    g80 = load_global_fields(data, r,'80')
    #g0 = gc0
    #g80 = gc80
    try:
        last_idx = get_last_idx_of_smallest_vector(gc80['currentCycle'],gc0['currentCycle'])
    except:
        runs_with_weird_stuff += 1
        return
    ##############################################
    import math
    # up until last idx

    key = 'commitedInstructions'

    print("bench name", data[r]['0']['bench'])
    correct = np.unique(  np.subtract(g80[key][:last_idx] , g0[key][:last_idx], dtype=np.int64) )
    print("should have the same instructions  = 0", correct)
    key = 'commitedStores'
    correct = np.unique(np.subtract(g80[key][:last_idx] , g0[key][:last_idx], dtype=np.int64))
    #print("stores prop", g80[key][:last_idx]*100/g0[key][:last_idx])
    #print("should have the same stores  = 0", correct)
    key = 'commitedLoads'
    print("loads prop", g80[key][:last_idx]*100/g0[key][:last_idx])
    correct = np.unique(np.subtract(g80[key][:last_idx] , g0[key][:last_idx], dtype=np.int64))
    print("should have the same loads  = 0", correct)
    # print if any of the committedLoads reaches more than 80% of uint64 max 
    print("The first index where this happens is:", np.any(g80[key][:last_idx] > np.uint64(0.8 * 2**64)))
    

    slowlyyy = np.subtract(g80['currentCycle'][:last_idx],g0['currentCycle'][:last_idx],dtype=np.int64) /g80['currentCycle'][:last_idx] 
    merged_slowdown = np.append(merged_slowdown, slowlyyy)
    for m in merged_together:
        # winsorize 1% of the data
        #import scipy.stats as stats
        #slowlyyy = stats.mstats.winsorize(slowlyyy, limits=[0.01, 0.01])
        metricc = g0[m][:last_idx]
        if (slowlyyy.shape[0] == 0 or metricc.shape[0] == 0):
            continue
        plt.figure(figsize=(30, 30))
        plt.scatter(slowlyyy, metricc)
        plt.xlabel('Real Slowdown')
        plt.ylabel(m)
        plt.title(f'Real Slowdown vs {m}')
        plt.grid(alpha=0.2)
        plt.tight_layout()
        benchname = data[r]['0']['bench'].split("/")[-1]
        benchnr = data[r]['0']['benchnr']
        folder = f'{FIGS_FOLDER}/gen/bench/{benchname}/{benchnr}'
        if not os.path.exists(folder):
            os.makedirs(folder)
        plt.savefig(f'{folder}/interval_slow_{m}.png')
        plt.close()
    
    for m in merged_together:
        merged_together[m] = np.append(merged_together[m], g0[m][:last_idx])

    others_merged['MLPL3 D stallCycles'] = np.append(others_merged['MLPL3 D stallCycles'], g0['totalL3MLPStalledCyclesSummed'][:last_idx]/(g0['totalL3StalledCyclesSummed'][:last_idx]+1))

    # each point is 2 million insts.. thus, no need to normalize, the number of requests/etc is capped
    print("Entries lost:", int(abs(len(g0['currentCycle']) - len(g80['currentCycle']))/(1+last_idx)), last_idx)
def plot_merged():
    #put merged together and others merged in the same dict
    m = merged_together.copy()
    m.update(others_merged)
    for k in m:
        plt.figure(figsize=(30, 30))
        # remove all idxs where merged slowdown = 0
        idx = np.where(merged_slowdown != 0)
        plt.scatter(merged_slowdown[idx], m[k][idx])
        plt.xlabel('Real Slowdown')
        plt.ylabel('Metric')
        plt.title('Real Slowdown vs Metric')
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'{FIGS_FOLDER}/gen/global/acc_pmu_{k}.png')
        plt.close()


"""
iterate_over_benches(data, obtain_weights)
exit(0)
print("obtained")
iterate_over_benches(data, do_cdf_of_instructions)
exit(0)
for b in by_binary_weights:
    # merge the metrics obtained
    metricas_numpy = {}
    all_instructions = ((i for i in by_binary_weights[b][a] for a in range(len(by_binary_weights[b]))))
    all_instructions = np.unique(all_instructions)
    for m in list(by_binary_weights[b][0].items())[0].keys():
        metricas_numpy[m] = np.zeros(len(all_instructions))
        for i in range(len(all_instructions)):
            metricas_numpy[m][i] = by_binary_weights[b][m][i]
    for m in by_binary_weights[b]:

        if m in metricas_numpy:
            metricas_numpy[m] = np.append(metricas_numpy[m], by_binary_weights[b][m])
        else:
            metricas_numpy[m] = by_binary_weights[b][m]

    by_binary_weights[b].append(metricas_numpy)

    serialize_weights(by_binary_weights[b])
"""

#print("success_run", success_run)
#exit(0)
#iterate_over_benches(data, simple_slow_sown)
##iterate_over_benches(data, simple_instruction_slowdown)
#print("runs_with_weird_stuff", runs_with_weird_stuff)
#for weird_run in weird_runs:
    #print(weird_run['0']['line'], end="")
#exit(0)
#print("runs_with_weird_stuff", runs_with_weird_stuff)
"""
plot_merged()
exit(0)
do_important_plots(data)
exit(0)
print("obtaining weights...")
iterate_over_benches(data, obtain_weights)
    
iterate_over_benches(data, iterate_time_series)

print("runs_with_weird_stuff", runs_with_weird_stuff)
exit(0)
"""
#exit(0)

def learn(inputs,results):
                    # one matrix has  L3stallTime, L3stallCyclesMLPLoad, L3stallCyclesMLPBoth, totalTime,  L3MLP_load_at_middle, L3MLP_store_at_middle
                    # print the shapes of each
                    #print("SHAPE", inst['L3stallTime'].shape)
                    #print("SHAPE", inst['L3stallCyclesMLPLoad'].shape)
                    #print("SHAPE", inst['stallCyclesMLPBoth'].shape)
                    #print("SHAPE", inst['totalTime'].shape)
                    #print("SHAPE", inst['L3MLP_load_at_middle'].shape)
                    #print("SHAPE", inst['L3MLP_store_at_middle'].shape)
                    # then do feat a * feat b 

                    # another array has the weights for each of the columns
                    # this is the initial guess
                    
                    # save to file inputs and results

                    weights = np.array([0.1, 0.1, 0.1, 0.1, 0.1, 0.1,0.1])
                    # using our cost function, compute the optimal weights

                    
                    #TODO   lastStallTime
                    def objective_function(weights, *args, **kwargs):
                        # calculate the cost for each row
                        # print args and kwargs
                        #print(args)
                        #print(kwargs)
                        #print(weights)
                        global_cost = np.dot(inputs, weights)
                        err = global_cost - global_learn['results']
                        return np.mean(np.abs(err))
                    best_weights, best_result, feature_scaler = learn_improved(inputs, global_learn['results'], objective_function, weights )
                    # print the best weights
                    print("              ", 'L3stallTime', 'L3stallCyclesMLPLoad',   'totalTime', 'L3MLP_load_at_middle', 'L3MLP_store_at_middle')
                    print("Best weights:", best_weights )
                    # plot the results
                    plt.figure()
                    #results = feature_scaler.inverse_transform(best_result)
                    #without scaler
                    #best result is OptimizeResult object
                    #results_to_plot = feature_scaler.inverse_transform(best_result.x)
                    # compute the predicted values
                    predicted = np.dot(inputs, best_weights)
                    plt.scatter(global_learn['results'], predicted)
                    plt.xlabel('Real')
                    plt.ylabel('Predicted')
                    plt.title('Learned Weights')
                    plt.savefig(f'{FIGS_FOLDER}/gen/global/learned_weights.png')
                    plt.close()
                    # print correlation between learned and real
                    print("Correlation between learned and real:", np.corrcoef(global_learn['results'], predicted)[0][1])
                    exit(0)

                    #inputs = 
                    results = np.array(global_learn['results'])

def load_cached_results():
    if global_learn['inputs'] and global_learn['results']:
        np.save(f'{FIGS_FOLDER}/gen/global/inputs.npy', global_learn['inputs'])
        np.save(f'{FIGS_FOLDER}/gen/global/results.npy', global_learn['results'])
    else:
        global_learn['inputs'] = np.load(f'{FIGS_FOLDER}/gen/global/inputs.npy')
        global_learn['results'] = np.load(f'{FIGS_FOLDER}/gen/global/results.npy')

#exit(0)
#print("did derivates")

#print("did global")

failed_to_correlate_idxs = []
i = 0
errors = {'stallCycles' : [], 'soar_aol':[], 'mem_stalls_weighted': []}
def correlate_all():
    global i
    global errors
    # global predict (each benchmark is 1 data point) 
    one_dp_regressions = {'stallCycles' : [], 'soar_aol':[], 'mem_stalls_weighted': []}  # 1 dp to regress per benchmark
    # each entry of the array is a  number, of the aggregate value of the entire array
    all_dp_regressions = {'stallCycles' : [], 'soar_aol':[], 'mem_stalls_weighted': []} # all dp to regress per benchmark
    # each entry of the array is a number, one of the datapoints of a workload (as they were all concatenated)
    clean_all_dp_regressions = {'stallCycles' : [], 'soar_aol':[], 'mem_stalls_weighted': []} # all dp to regress per benchmark
    one_dp_clean_regressions = {'stallCycles' : [], 'soar_aol':[], 'mem_stalls_weighted': []}

    clean_idxs = np.where(global_all_dps_results['real_slowdown'] < 100)
    clean_all_dp_results = {}
    for k in global_all_dps_results.keys():
        #print(k, clean_idxs, global_all_dps_results[k])
        try:
            clean_all_dp_results[k] = global_all_dps_results[k][clean_idxs]
        except:
            continue
    #for k in global_results:
    #    print(k,  global_results[k])
 
    def get_index(idx, d):
        di = {}
        for k in d:
            di[k] = d[k][idx]
        return di
        
        
    def process_it(dest,src):
        global i
        global errors
        # all dp regressions fails to correlate!!
        i+=1

        #print("correlating", i, src)
        #src['stalled_cycles'] = np.array(src['stalled_cycles'])
        src['stall_cycles'] = np.array(src['stall_cycles'])
        src['mem_stalls_weighted'] = np.array(src['mem_stalls_weighted'])
        src['real_slowdown'] = np.array(src['real_slowdown'])
        src['aol'] = np.array(src['aol'])
        src['percentStallCycles'] = np.array(src['percentStallCycles'])
        src['percentmem_stalls_weighted'] = np.array(src['percentmem_stalls_weighted'])
        #print("Type of stallCycles", type(src['stall_cycles']))
        #print("Type of real_slowdown", type(src['real_slowdown']))

        dest['stallCycles'] = regress(src['percentStallCycles'],src['real_slowdown'])
        errors['stallCycles'].append(regress_error[-1])
        dest['mem_stalls_weighted'] = regress(src['percentmem_stalls_weighted'],src['real_slowdown'])
        # convert src['aol'] that is a list of arrays with 1 value to a list of values
        #print(src['real_slowdown'])
        errors['mem_stalls_weighted'].append(regress_error[-1])
        try: 
            #print('aol is', src['aol'])
            #print('stall_cycles is', src['stall_cycles'])
            #print('real_slowdown is', src['real_slowdown'])
            dest['soar_aol'] =  obtain_soar_mlp_aware_slowdown(src['percentStallCycles'], src['aol'], src['real_slowdown'])
            errors['soar_aol'].append(regress_error[-1])
        except Exception as e:
            failed_to_correlate_idxs.append(i)
            print("BIG error in correlating.. sadly..")
        #print('survive', i)
        # average each error 
        #print(errors)
    #for b in bench_runs:
    #    pass

    for  (dest, src) in ((one_dp_regressions, global_results), (all_dp_regressions, global_all_dps_results), (clean_all_dp_regressions, clean_all_dp_results)):
        errors = {'stallCycles' : [], 'soar_aol':[], 'mem_stalls_weighted': []}
        process_it(dest,src)
        print("##################### i",i)
        for r in errors:
            errors[r] = np.mean(np.array(errors[r]))
            print(r, errors[r])
        print("#########################")

    per_bench_stuff = [ ({'stallCycles' : [], 'soar_aol':[], 'mem_stalls_weighted': []},  b) for b in global_results_per_bench
    ]

    # global_results_per_bench_id
    errors = {'stallCycles' : [], 'soar_aol':[], 'mem_stalls_weighted': []}
    k = 0
    for (dest, src) in per_bench_stuff:
        print(global_results_per_bench_id[k]['0']['bench'].split("/")[-1], end=" ")
        process_it(dest,src)
        k+=1
    print("##################### Global final", i)
    for r in errors:
        errors[r] = np.mean(np.array(errors[r]))
        print(r, errors[r])
    print("#########################")
    print(failed_to_correlate_idxs, "FALIED TO CORRELATE")

                
e_count=0
bench_runs =0

#glob_sum = []

def about_to_solve(data):
    def sol(data, r):
        if data[r]['0']['pid'] == 7040:
            print(data[r]['0']['bench'])
            bench = data[r]['0']['bench'].split("/")[-1]

    iterate_over_benches(data, sol)
    
a = 1.0155768028621026
b = -0.2562029379967975
#all_benches_data = np.array()
#l3_dudes = []
#pred_slow = []
def predict_soar_by_inst():
    global RUN_DATA_FOLDER
    global run_meta
    RUN_DATA_FOLDER="/mnt/nas/inesc/ist196723/osdi26/results_gem5"
    run_meta=f"{RUN_DATA_FOLDER}/gem5_pids.txt"
    def bc_bench(data,r):
        a = 1.0155768028621026
        b = -0.2562029379967975

        bench = data[r]['0']['bench'].split("/")[-1]
        if bench != "XSBench":
            return
        runnr = data[r]['0']['benchnr']
            
        print(bench, runnr)
        # pid
        pid = data[r]['0']['pid']
        print(pid)
        g = load_global_fields(data, r)
        i = load_inst_fields(data, r)
        try:
            v = "totalTime"
        except:
            return
        print(v, np.histogram(i[v]))
        print('nicerunnrrunnr')
        for v in ['average_l3mlp', 'average_mlp',  'totalTime','stallTime']:
            print(v, np.histogram(i[v]))
        print('nicerunnrrunnr')
        print('nicerunnrrunnr')
        print('nicerunnrrunnr')
        

        #print(np.unique(i['average_l3mlp']))
        #return
        #print('survie')
        
        #print(np.unique(i['L3MLP_load_at_end']))
        #print(np.histogram(i['L3MLP_load_at_end']))
        #return
        predict = []

        print(len(g['currentCycle']))

        #last_idx = 100000 # int(len(g['currentCycle'])/1000)

        
        #i['stalledCycles'] / (i['totalTime']*a + b* i['L3MLP'])
        variables = {}
        #last_idx = len(g['currentCycle'])
        if len(g['currentCycle']) < 500:
            return
        last_idx = len(g['currentCycle'])-1
        AOL = (g['cyclesWithMemrequests'][1] - g['cyclesWithMemrequests'][last_idx])/( g['commitedLoads'][last_idx] - g['commitedLoads'][1] )
        #AOL = np.where(g['commitedLoads'][1:last_idx] == 0, 1, AOL) 

        #predicted_slow_down = (g['stalledCycles'][1:last_idx]/g['currentCycle'][1:last_idx]) * 1/(a + b/AOL)
        diff_stalls = g['stalledCycles'][last_idx] - g['stalledCycles'][0]
        diff_cycles = g['currentCycle'][last_idx] - g['currentCycle'][0]
        predicted_slow_down = diff_stalls/diff_cycles * 1/(a + b/AOL)
        #print( g['currentCycle'][g['currentCycle'] > 0]  , '11the death of me...')
        #print("stalledCycles", np.histogram(g['stalledCycles'][1:last_idx]))
        #print("currentCycle", np.histogram(g['currentCycle'][1:last_idx]))
        #print("AOL", np.histogram(AOL))

        def obtain_soar_instt(selections, L3_MLP, L3_stall, acess_time, real):
            import numpy as np
            from scipy.optimize import curve_fit

            def fit_func(r, a, b):

                # A,B -0.4477149036453043 0.1349315011644008
                #soar_metric = i['stallTime'][sel] /  ( i['L3MLP_load_at_middle'][sel] * b  + a * i['totalTime'][sel] ) 
                #print('ho')
                return L3_stall /  (a*L3_MLP + b * acess_time)
                #for i in range(len(selection)):
                #    results[i] = np.sum( 
                #print('hi')
                #return results

            print('whhhhhhhh')
            initial_guess = [10, 0.5]
            popt, pcov = curve_fit(fit_func, np.array(range((1))), real, p0=initial_guess, maxfev=1000)
            a_opt, b_opt = popt
            a_err, b_err = np.sqrt(np.diag(pcov))
            fitted_real = fit_func(L3_stall, a_opt, b_opt)
            print('done')

            residuals = real - fitted_real
            ss_res = np.sum(residuals**2)
            ss_tot = np.sum((real - np.mean(real))**2)
            r_squared = 1 - ss_res / ss_tot
            rmse = np.sqrt(np.mean((real - fitted_real) ** 2))
            regress_error.append(rmse)
            print(f'MSRE-S {rmse:.3f}')
            return [fitted_real, a_opt, b_opt, rmse]
        #print("predicted_slow_down", np.histogram(predicted_slow_down))


        #print(np.histogram(l['L3stallCyclesMLPLoad'][l3_idx]), 'jooo')

        bench = pid #r['bench'].split("/")[-1]
        #err = np.sum(abs(predicted_slow_down - g['real_slowdown']))/len(predicted_slow_down)
        #print(bench, err)
            

        print('about to fit')
        predicted_slow_down = np.array(predicted_slow_down) 
        fitted, a, b, rmse = obtain_soar_instt(i['average_l3mlp'] < 255 , i['average_mlp'], i['stallTime'], i['totalTime'], predicted_slow_down)
        print("A,B",a,b,rmse)
        
            
        for j in range(1,last_idx): # https://www.perplexity.ai/search/do-the-average-of-88-470097-15-P6_EPLrkR6iELQv1z4dxZg
            idxs = ( i['start_cycle'] < g['currentCycle'][j] ) & ( i['start_cycle'] < g['currentCycle'][j] )
            _ = (i['totalTime'][idxs]*a + b* i['L3MLP_load_at_end'][idxs])
            #_ = np.where(_ == 0, 1, _)
            predict.append(np.sum(i['stallTime'][idxs] / _))

        plt.figure()
        plt.scatter( predicted_slow_down, predict)
        plt.xlabel('Real Slowdown')
        plt.ylabel('Fitted Real Slowdown')
        plt.title('Real Slowdown vs Fitted Real Slowdown')
        plt.savefig(f'{FIGS_FOLDER}/gen/_inst_to_global/{bench}.png')
        plt.close()
    



    data = load_bench_data()
        
    #data = load_bench_data_pids()
    iterate_over_benches(data, bc_bench)
    exit(0)

all_moment = {}
def collect_one_metric(data,r, convolve=1):
        bad = {}
        g = load_global_fields(data, r, convolve=convolve)
        g80 = load_global_fields(data, r,'80', convolve=convolve)
        variables = {}
        last_idx = get_last_idx_of_smallest_vector(g80['currentCycle'],g['currentCycle'])
        if last_idx < 500:
            return
        AOL = g['cyclesWithMemrequests'][1:last_idx]/g['commitedLoads'][1:last_idx]
        AOL = np.where(g['commitedLoads'][1:last_idx] == 0, 0, AOL) 
        AOL_l3 = g['L3cyclesWithMemrequests'][1:last_idx]/g['commitedLoads'][1:last_idx]
        AOL_l3 = np.where(g['commitedLoads'][1:last_idx] == 0, 0, AOL_l3) 

        slow_down = (g80['currentCycle'][1:last_idx]-g['currentCycle'][1:last_idx]) /g['currentCycle'][1:last_idx]
        #slow_down = g['stalledCycles'][1:last_idx]/g['currentCycle'][1:last_idx]
        #print(slow_down)

        for key in global_types: 
            try:
                variables[key] = g[key][1:last_idx]
            except:
                bad[key] = True
            
        variables['aol'] = AOL
        variables['aol_l3'] = AOL_l3
        variables['real_slowdown'] = slow_down
        return variables

def calc_soar_slowdown(d,idxs):
    a = 1.0155768028621026
    b = -0.2562029379967975
    fitted_real = d['stalledCycles'][idxs]/d['currentCycle'][idxs] * (a + b/d['aol'][idxs])
    return fitted_real

def plot_muetricas(data, r):
    convolve = 1
    all_moment = collect_one_metric(data, r, convolve)
    bench = data[r]['0']['bench'].split("/")[-1]
    os.makedirs(f"{FIGS_FOLDER}/gen/_metricas/{bench}", exist_ok=True)

    idxs = np.where(all_moment['real_slowdown'] > 0.1)
    fitted_real = all_moment['stalledCycles'][idxs]/all_moment['currentCycle'][idxs] * (a + b/all_moment['aol'][idxs])
    #fitted_real = obtain_soar_mlp_aware_slowdown(all_moment['stalledCycles'][idxs]/all_moment['currentCycle'][idxs], all_moment['aol'][idxs], all_moment['real_slowdown'][idxs])
    fitted_real_l3 = all_moment['L3stalledCycles'][idxs]/all_moment['currentCycle'][idxs] * (a + b/all_moment['aol_l3'][idxs])
    # obtain_soar_mlp_aware_slowdown(all_moment['L3stalledCycles'][idxs]/all_moment['currentCycle'][idxs], all_moment['aol_l3'][idxs], all_moment['real_slowdown'][idxs])
    ms = ['L3onlyLoadsStalled', 'L3stallCyclesMLPLoad', 'commitedLoads', 'stallCyclesMLPLoad', 'L3stalledCycles']

    # remove all datapoints where all_moment['real_slowdown'] < 0.01
    for m in ms:
        print(m)
        fitted= regress(all_moment[m][idxs], all_moment['real_slowdown'][idxs])
        plt.figure(figsize=(30, 30))
        plt.scatter(all_moment['real_slowdown'][idxs], fitted)
        plt.xlabel('Real Slowdown')
        plt.ylabel(m)
        plt.title('Real Slowdown vs ' + m)
        plt.savefig(f'{FIGS_FOLDER}/gen/_metricas/{bench}/{m}_{convolve}.png')
        plt.close()


    plt.figure(figsize=(30, 30))
    plt.scatter(all_moment['real_slowdown'][idxs], fitted_real)
    plt.xlabel('Real Slowdown')
    plt.ylabel('Fitted Real Slowdown')
    plt.title('Real Slowdown vs Fitted Real Slowdown')
    plt.savefig(f'{FIGS_FOLDER}/gen/_metricas/{bench}/soar_{convolve}.png')
    plt.close()
def by_bench_muetricas():
    iterate_over_benches(data, plot_muetricas)

def get_metrics_from_all_by_moment():
    global all_moments
    bad = {}
    convolve=1
    def get_all(data,r):
        g = load_global_fields(data, r, convolve=convolve)
        g80 = load_global_fields(data, r,'80', convolve=convolve)
        variables = {}
        last_idx = get_last_idx_of_smallest_vector(g80['currentCycle'],g['currentCycle'])
        if last_idx < 500:
            return
        AOL = g['cyclesWithMemrequests'][1:last_idx]/g['commitedLoads'][1:last_idx]
        AOL = np.where(g['commitedLoads'][1:last_idx] == 0, 0, AOL) 
        AOL_l3 = g['L3cyclesWithMemrequests'][1:last_idx]/g['commitedLoads'][1:last_idx]
        AOL_l3 = np.where(g['commitedLoads'][1:last_idx] == 0, 0, AOL_l3) 

        slow_down = (g80['currentCycle'][1:last_idx]-g['currentCycle'][1:last_idx]) /g['currentCycle'][1:last_idx]
        #slow_down = g['stalledCycles'][1:last_idx]/g['currentCycle'][1:last_idx]
        #print(slow_down)

        for key in global_types: 
            try:
                variables[key] = g[key][1:last_idx]
            except:
                bad[key] = True
            
        variables['aol'] = AOL
        variables['aol_l3'] = AOL_l3


        for k in global_types:
            if k in bad or k not in variables:
                continue
            if k not in all_moment:
                all_moment[k] = []
            all_moment[k].append(variables[k])
        if 'real_slowdown' not in all_moment or 'aol' not in all_moment:
            all_moment['real_slowdown'] = []
            all_moment['aol'] = []
            all_moment['aol_l3'] = []
        all_moment['real_slowdown'].append(slow_down)
        all_moment['aol'].append(AOL)
        all_moment['aol_l3'].append(AOL_l3)
    iterate_over_benches(data, get_all)
    for k in all_moment:
        if k in bad:
            continue
        all_moment[k] = np.concatenate(all_moment[k])
    
    for k in all_moment:
        print(f"{k}: {len(all_moment[k])} entries")
    for k in bad:
        print(f"{k}: {bad[k]} ", end=" ")

    idxs = np.where(all_moment['real_slowdown'] > 0.1)
    fitted_real = obtain_soar_mlp_aware_slowdown(all_moment['stalledCycles'][idxs]/all_moment['currentCycle'][idxs], all_moment['aol'][idxs], all_moment['real_slowdown'][idxs])
    fitted_real_l3 = obtain_soar_mlp_aware_slowdown(all_moment['L3stalledCycles'][idxs]/all_moment['currentCycle'][idxs], all_moment['aol_l3'][idxs], all_moment['real_slowdown'][idxs])
    ms = ['commitedL3Misses', 'L3onlyLoadsStalled', 'L3stallCyclesMLPLoad', 'commitedLoads', 'stallCyclesMLPLoad', 'L3stalledCycles']

    # remove all datapoints where all_moment['real_slowdown'] < 0.01
    for m in ms:
        print(m)
        fitted= regress(all_moment[m][idxs], all_moment['real_slowdown'][idxs])
        plt.figure(figsize=(30, 30))
        plt.scatter(all_moment['real_slowdown'][idxs], fitted)
        plt.xlabel('Real Slowdown')
        plt.ylabel(m)
        plt.title('Real Slowdown vs ' + m)
        plt.savefig(f'{FIGS_FOLDER}/gen/_metrica/{m}_{convolve}.png')
        plt.close()


    plt.figure(figsize=(30, 30))
    plt.scatter(all_moment['real_slowdown'][idxs], fitted_real)
    plt.xlabel('Real Slowdown')
    plt.ylabel('Fitted Real Slowdown')
    plt.title('Real Slowdown vs Fitted Real Slowdown')
    plt.savefig(f'{FIGS_FOLDER}/gen/all_moment_errors_{convolve}.png')
    plt.close()
    exit(0)

    for m in  ['stalledCycles', 'currentCycle', 'stallCyclesMLPLoad', 'totalTime', 'L3stallTime', 'L3stallCyclesMLPLoad']:
        try:
            plt.figure(figsize=(30, 30))
            plt.scatter(all_moment['real_slowdown'], all_moment[m])
            plt.xlabel('Real Slowdown')
            plt.ylabel(  m)
            plt.title('Real Slowdown vs Fitted Real Slowdown')
            plt.savefig(f'{FIGS_FOLDER}/gen/_metrica/{m}.png')
            plt.close()
        except Exception as e:
            print(f"Failed to plot {m}: {e}")
            pass
    #for m in ['mlp']
    #fitted, a, b, rmse = obtain_soar_inst(all_moment['selections'], all_moment[mlp], all_moment['L3stallTime'],all_moment['totalTime'], all_moment['actual_slowdown'])
    #print("A,B",a,b)
    #print('ho')
    
    

def aggregate_all_benchmarks(data,r):
                global e_count
                global bench_runs
                GOT = lambda g: (get_field(data[r]['80'], GLOBAL,g, np.uint64)[-1] - get_field(data[r]['0'], GLOBAL,g, np.uint64)[-1]) / final_cycles
                GOT_o = lambda g: (get_field(data[r]['80'], GLOBAL,g, np.uint64)[-1] - get_field(data[r]['0'], GLOBAL,g, np.uint64)[-1]) / final_cycles
                get_last = lambda g:(get_field(data[r]['0'], GLOBAL,g, np.uint64)[-1])
                
                # GLOBAL_FINAL
                try:
                    final_cycles = get_field(data[r]['0'], GLOBAL, 'currentCycle', np.uint64)[-1]
                    all_real_slowdown = (get_field(data[r]['80'], GLOBAL,'currentCycle', np.uint64) - get_field(data[r]['0'], GLOBAL,'currentCycle', np.uint64)) / get_field(data[r]['0'], GLOBAL,'currentCycle', np.uint64)

                    variables = []
                    variables.append(('currentCycle', GOT('currentCycle')))
                    variables.append(('stall_cycles', GOT_o('stalledCycles')))
                    variables.append(('real_slowdown', all_real_slowdown[-1]))




                    #variables.append(('percentmem_stalls_weighted', (GOT_o('L3stallCyclesMLPLoad')*get_last('L3cyclesWithMemrequests'))/(final_cycles)))
                    AOL = get_last('cyclesWithMemrequests')/get_last('commitedLoads')
                    AOL = np.where(get_last('commitedLoads') == 0, 0, AOL) 
                    # if aol has only 1 value, then return the value not the array
                    variables.append(('percentmem_stalls_weighted', #(GOT_o('stallCyclesMLPLoad')*get_last('cyclesWithMemrequests'))/(final_cycles)))
                    #d['percentmem_stalls_weighted'] = np.append(
                            #d['percentmem_stalls_weighted'],
                            get_last('stallCyclesMLPLoad')*AOL/get_last('currentCycle')
                            #get_field(data[r]['0'], GLOBAL,'stalledCyclesWithMemRequests', np.uint64)/

                            # d['percentmem_stalls_weighted'] = np.append(d['percentmem_stalls_weighted'],get_field(data[r]['0'], GLOBAL,'L3stallCyclesMLPLoad', np.uint64)/get_field(data[r]['0'], GLOBAL,'stalledCyclesWithMemRequests', np.uint64)/get_field(data[r]['0'], GLOBAL,'currentCycle', np.uint64))
                        ))

                    #variables.append(('stalledCyclesWithMemRequests', GOT_o('stalledCycles')))
                    #variables.append(('stalledCyclesWithStores', GOT_o('stalledCyclesWithMemRequests')))
                    variables.append(('mlp_stall', GOT_o('stallCyclesMLPLoad')))
                    #variables.append(('cyclesWithMemrequests', get_last('cyclesWithMemrequests')/get_last('commitedLoads')))
                    #variables.append(('commitedLoads', get_last('commitedLoads')))
                    variables.append(('percentStallCycles', GOT_o('stalledCycles')/final_cycles))
                    variables.append(('aol', AOL))
                    # ADDEDDDDDDDDD
                    variables.append(
                    ('cycles',get_field(data[r]['0'], GLOBAL,'currentCycle', np.uint64))
                    )

                    # deep copy
                    a =  {'real_slowdown': np.array([]), 'stall_cycles': np.array([]), 'mlp_stall': np.array([]), 'load+commit': np.array([]), 'cycles': np.array([]),
    'mem_stalls': np.array([]),
    'store_stalls': np.array([]),
    'mem_stalls_weighted': np.array([]),
    'aol': np.array([]),
    'commitedLoads': np.array([]),
    'percentStallCycles': np.array([]),
    'percentmem_stalls_weighted': np.array([])
                    }
                    for d in (a, global_all_dps_results): ################################
                        
                        d['cycles'] = np.append(d['cycles'],get_field(data[r]['0'], GLOBAL,'currentCycle', np.uint64))
                        d['real_slowdown'] = np.append(d['real_slowdown'],all_real_slowdown)
                    # all stall cycles
                        d['stall_cycles'] =np.append(d['stall_cycles'],get_field(data[r]['0'], GLOBAL,'stalledCycles', np.uint64)) 
                        d['mem_stalls'] = np.append(d['mem_stalls'],get_field(data[r]['0'], GLOBAL,'stalledCyclesWithMemRequests', np.uint64))
                        d['store_stalls'] = np.append(d['store_stalls'],get_field(data[r]['0'], GLOBAL,'stalledCyclesWithStores', np.uint64))
                        d['mem_stalls_weighted'] = np.append(d['mem_stalls_weighted'],get_field(data[r]['0'], GLOBAL,'stallCyclesMLPLoad', np.uint64))

                        d['percentStallCycles'] = np.append(d['percentStallCycles'],get_field(data[r]['0'], GLOBAL,'stalledCycles', np.uint64)/get_field(data[r]['0'], GLOBAL,'currentCycle', np.uint64))
                        AOL = get_field(data[r]['0'], GLOBAL,'cyclesWithMemrequests', np.uint64)/get_field(data[r]['0'], GLOBAL,'commitedLoads', np.uint64)
                        AOL = np.where(get_field(data[r]['0'], GLOBAL,'commitedLoads', np.uint64) == 0, 0, AOL) 
                        d['percentmem_stalls_weighted'] = np.append(
                            d['percentmem_stalls_weighted'],
                            get_field(data[r]['0'], GLOBAL,'stallCyclesMLPLoad', np.uint64)*AOL/get_field(data[r]['0'], GLOBAL,'currentCycle', np.uint64)
                            #get_field(data[r]['0'], GLOBAL,'stalledCyclesWithMemRequests', np.uint64)/

                            # d['percentmem_stalls_weighted'] = np.append(d['percentmem_stalls_weighted'],get_field(data[r]['0'], GLOBAL,'L3stallCyclesMLPLoad', np.uint64)/get_field(data[r]['0'], GLOBAL,'stalledCyclesWithMemRequests', np.uint64)/get_field(data[r]['0'], GLOBAL,'currentCycle', np.uint64))
                        )
                        if len(AOL) == 1:
                            AOL = AOL[0]
                        d['aol'] = np.append(d['aol'],AOL)
                        d['commitedLoads'] = np.append(d['commitedLoads'],get_field(data[r]['0'], GLOBAL,'commitedLoads', np.uint64))

                    global_results_per_bench.append(a) ############################################
                    global_results_per_bench_id.append(data[r])

                    for var_name, var_value in variables:
                        global_results[var_name].append(var_value)        ##################### 
                    bench_runs+=1
                    #print("rrrrrrrrrrrrrrruu")
                    #print(global_results['stall_cycles'])
                except Exception as e:
                    raise e
                    #print("Error", e,e_count, bench_runs)
                    #e_count+=1
                    #pass # do not add this bench to the list



def combine_plots(folder):
    folder = f"{FIGS_FOLDER}/gen/mlp_stalls"
    files = os.listdir(folder)
    files = [f for f in files if f.endswith('.png')]
    files = sorted(files)
    # join all in a single image 
    a = int(np.sqrt(len(files)))+1
    b = int(np.sqrt(len(files)))+1
    fig, ax = plt.subplots(a, b, figsize=(10, 10))
    for i, file in enumerate(files):
        img = plt.imread(os.path.join(folder, file))
        ax[i//b][i%b].imshow(img)
        ax[i//b][i%b].axis('off')
    plt.savefig(os.path.join(folder, 'combined.png'), bbox_inches='tight', pad_inches=0)

def plot_histogram(data, r):
    ag80 =  load_aggregate_fields(data,r,'80')
    ag0 =  load_aggregate_fields(data,r)
    fields = aggregate_types.keys()
    data, bins=20
    #l3_idx = 
    for v in fields:
        plt.figure()
        print("Doing v", v)
        plt.hist(data[v][l3_idx]/data['count'][l3_idx], bins=bins)
        plt.xlabel(v)
        plt.ylabel('Frequency (normalized)')
        plt.title(f'Histogram of {v}')
        plt.savefig(f"{FIGS_FOLDER}/gen/vars/histogram_{v}_{bench_name}_{bench_nr}.png", dpi=300)
        plt.close()
                            
def plot_access_time_is_not_enough(data, r):

    bench_name = get_bname(data,r)
    bench_nr = get_bnr(data, r)
    for (ag0,ag80, name) in ((load_aggregate_fields(data,r) ,load_aggregate_fields(data,r,'80'), 'AGG'),):
        unique_accessBrackets = np.unique(ag0['accessBracket'])
        access_times = {}
        # !!! different selections for 0 and 80
        # - ignore L3 hits
        # - and tlb misses
        # - IGNORE STORES!
        for ab in unique_accessBrackets:
            sel = (ag0['accessBracket'] == ab) & (ag0['count'] > 0) & (ag0['totalTime'] > 0)
            sel80 = (ag80['accessBracket'] == ab) & (ag80['count'] > 0) & (ag80['totalTime'] > 0)
            avg_factor = ag0['count'][sel].sum()
            access_times[ab] = {}
            access_times[ab]['totalTime'] = 0
            access_times[ab]['stallTime'] = 0
            access_times[ab]['activeCycles'] = 0
            access_times[ab]['activeCycles%'] = 0
            access_times[ab]['stallTime%'] = 0
            access_times[ab]['count'] = 0
            access_times[ab]['increaseStall'] = 0
            if avg_factor == 0:
                continue
            access_times[ab]['count'] = ag0['count'][sel].sum()
            access_times[ab]['totalTime'] = (ag0['totalTime'][sel]* ag0['count'][sel]).sum()/avg_factor
            access_times[ab]['stallTime'] = (ag0['stallTime'][sel]* ag0['count'][sel]).sum()/avg_factor

            a = ag0
            f = (a['totalTime'][sel]* a['count'][sel]).sum() #/ avg_factor

            a = ag80
            s = (a['stallTime'][sel80]* a['count'][sel80]).sum() #/ a['count'][sel].sum()
            access_times[ab]['increaseStall'] = np.subtract(s,f, dtype=np.int64)
            # print total time and stall time
            #print("Total time", access_times[ab]['totalTime'])
            ##print("Stall time", access_times[ab]['stallTime'])
            # mode PERCENTAGE OF STALL CYCLES, if not linear increase ....
            # absolute
            access_times[ab]['activeCycles'] = (access_times[ab]['totalTime'] - access_times[ab]['stallTime']) #/access_times[ab]['totalTime']
            access_times[ab]['activeCycles%'] = (access_times[ab]['totalTime'] - access_times[ab]['stallTime'])/access_times[ab]['totalTime']
            access_times[ab]['stallTime%'] = (access_times[ab]['stallTime'])/access_times[ab]['totalTime']

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Subplot 1: Stall cycles increase
        ax1.bar(unique_accessBrackets*16, 
                [access_times[ab]['increaseStall'] for ab in unique_accessBrackets],
                width=15,
                )
        ax1.legend()
        ax1.set_title(f'Slow tier\'s stall cycles increase by latency {r}')
        
        # Subplot 2: Distribution of accesses
        v=  np.array([access_times[ab]['count'] for ab in unique_accessBrackets])
        final =                100*v/v.sum()
        ax2.bar(unique_accessBrackets*16, 
                final,
                width=15,
                label='Number of accesses')
        max_val = np.max(final)
        for i in range(len(unique_accessBrackets)):
            if final[i] > max_val:
                ax2.text(unique_accessBrackets[i]*16+7, final[i], f"{int(final[i])}%", ha='center', va='bottom')
        ax2.set_ylim(0,np.max(final[3:])*1.1)
        print(v)
        ax2.legend()
        ax2.set_title(f'Distribution of accesses by latency {r}')
        
        # Subplot 3: Active and stall time histogram
        ax3.bar(unique_accessBrackets*16, 
                [access_times[ab]['activeCycles'] for ab in unique_accessBrackets],
                width=15,
                label='activeCycles')
        ax3.bar(unique_accessBrackets*16, 
                [access_times[ab]['stallTime'] for ab in unique_accessBrackets], 
                bottom=[access_times[ab]['activeCycles'] for ab in unique_accessBrackets],
                width=15,
                label='stallTime')
        ax3.legend()
        ax3.set_title(f'Histogram of cycles of active and stall time  for {human[r]}')
        
        # Subplot 4: Percentage of active and stall time
        ax4.bar(unique_accessBrackets*16, [access_times[ab]['activeCycles%'] for ab in unique_accessBrackets], 
                width=15,
                label='activeCycles')
        ax4.bar(unique_accessBrackets*16, [access_times[ab]['stallTime%'] for ab in unique_accessBrackets], 
                bottom=[access_times[ab]['activeCycles%'] for ab in unique_accessBrackets], 
                width=15,
                label='stallTime')
        ax4.legend()
        ax4.set_ylabel("Percentage")
        ax4.set_xlabel("Access latency")
        ax4.set_title(f'Histogram of percentage of active and stall time for each instruction for {human[r]}')
        
        plt.tight_layout()
        plt.savefig(f"{FIGS_FOLDER}/gen/aggregate/combined_plots_{bench_name}_{bench_nr}_{r}_{name}.png", dpi=300)
        plt.close()

#iterate_over_benches(data, aggregate_all_benchmarks)
#plot_global_results()

def do_all_now():
    global run_meta
    global DATA_FOLDER
    global RUN_DATA_FOLDER
    global global_types
    global aggregate_types
    OLDV4 = False
    if OLDV4:
        global_types = {'totalSquashed': np.uint64,
            'L3stallCyclesMLPLoad': np.uint64,
            'stallCyclesMLPStore': np.uint64,
            'stallCyclesMLPBoth': np.uint64,
            'currentCycle': np.uint64, 'L3stalledCycles': np.uint64, 'stalledCycles': np.uint64, 'stalledCyclesDuringStore': np.uint64, 'stalledCyclesWithMemRequests': np.uint64, 'stalledCyclesWithStores': np.uint64, 'cyclesWithMemrequests': np.uint64, 'commitedStores': np.uint64, 'commitedLoads': np.uint64, 'commitedAtomic': np.uint64, 'commitedInstructions': np.uint64, 'totalSquashed': np.uint64, 'lastStallTime': np.uint64, 'currentCycle': np.uint64,  'tlbMisses': np.uint64}
        data = load_bench_data()

        RUN_DATA_FOLDER="/mnt/nas/inesc/ist196723/osdi26/v4/results_gem5"
        run_meta=f"{RUN_DATA_FOLDER}/gem5_pids.txt"
        data = load_bench_data()
    plot_no_pred(data,all_bench_loader, name="ROBALO")

import sys

arg0 = sys.argv[1]

if arg0 == "iterate_over_benches":
    function = eval(sys.argv[2])
    iterate_over_benches(data, function)
else:
    print("evaling", " ".join(sys.argv[1:]))
    eval(" ".join(sys.argv[1:]))
#  ./report/images/load_images.sh 'pdo plot_my_soar()'

exit(0)
correlate_all()


bench_name="global"; bench_nr=""
#pot_errors(data,all_bench_loader, name="global")


iterate_over_benches(data, lambda d,r: plot_sum_errors(d,lambda x: x, r) )
actually_plot_sum_errors()
#exit(0)

iterate_over_benches(data, lambda d,r:  pot_errors(data, load_global_fields, r, name="global_glob_point"))




bench_name="global"; bench_nr=""
bench_name="global"; bench_nr=""
plot_pred(data,all_bench_loader, name="global")

print("did global")
#exit(0)

plot_global_sample_cost()
#learn( np.array(global_learn['inputs']), np.array(global_learn['results']) )

print(len(data.keys()))




combine_plots('j')
