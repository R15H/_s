from ctypes  import *
import collections
global_only = False
success_run = 0
MLP_PRECISION_FACTOR = 1024
import matplotlib.pyplot as plt
import sys

from scipy import stats

import matplotlib.lines as mlines
import matplotlib.pyplot as plt

# KNOB
LIMIT_BY_AGG = False
DATASET_S = ""
OVERRIDE_PID_ONLY = False
OVERRIDE_RUN_FOLDER = None
AOL_BIG = False
SHOULD_PLOT_KEY = lambda x: True
GEM5_PIDS_TAIL=0
GEM5_PIDS_TAIL=-100
OVERRIDE_DATASET=None
OVERRIDE_DATASET=1
OVERRIDE_DATASET=4
ERROR_VIEW=False
BY_HOT=False
LLC_ONLY=False
REGRESS_SOAR=True
REGRESS_SOAR=False
NO_WINSOR=True
NO_WINSOR=False
#10 #
TRACE_MODE =   sys.maxsize # 1 # sys.maxsize 
#KEYS_TO_DO = ['Instruction Store Bound + Load Stall Cycles/MLP']
def ALL_DESIRED_KEYS(globy):
    #return  '∆ Load/Store bound cycles' in key.lower()
    return False
    return all([ k in list(globy.keys()) for k in KEYS_TO_DO]) 
def HIGH_PRIORITY_KEYS(key):
    if "fcount" in key.lower() or "scount"  in key.lower():
        return False
    #return  '∆ Load/Store bound cycles' in key.lower()
    return True
    if 'store' in key.lower():
        return True
    return False

#False
def get_color_bin(bin):
    benchsets =  [ "cpu2017", "gapbs",   "NPB-CPP",            ] # ]/apps",   "pkgs/kernels" , "pkgs/splash"]
    benchsetsHUMAN =  [ "CPU2017", "GAPBS",   "NPB", "Others"] # ,   "PARSEC-kernels" , "PARSEC-splash"]
    colors = ['blue', 'orange', 'purple',  'grey']
    for i,b in enumerate(benchsets):
        if b in bin:
            return colors[i]
    return colors[-1]
def dr(d, k, value):
    if k not in d:
        d[k] = [value]
    return d[k]

# python3 bin/python_parserFTW.py "plot_llc_change()" 
array_lengths = 0
def load_count_data(filepath):
    import pandas as pd
    try:
        df = pd.read_csv(filepath, sep=" "*6, header=None)
        df.iloc[:, 0] = df.iloc[:, 0].str.replace(",", "").astype(int)
        print("DATA", np.array(df[0]))
        array_lengths = len(df[0])
        return np.array(df[0])
    except:
        print("FAILED TO LOAD", filepath)
        return np.ones(array_lengths)




def realistic_stalls():
    llc_changes = []
    folder="real_stalls"
    #folder = "real_stalls/before_proper/before_counting_cycles"

    files = glob.glob(f"/mnt/nas/inesc/ist196723/osdi26/bin/{folder}/*")
    r = {}
    nrs = np.loadtxt(f"/mnt/nas/inesc/ist196723/osdi26/bin/{folder}/binary", dtype=str)
    print(nrs)
    mode = np.loadtxt(f"/mnt/nas/inesc/ist196723/osdi26/bin/{folder}/mode", dtype=str)
    print(mode)

    threads = np.loadtxt(f"/mnt/nas/inesc/ist196723/osdi26/bin/{folder}/threads", dtype=int)

    any_stalls = load_count_data(f"/mnt/nas/inesc/ist196723/osdi26/bin/{folder}/countTOTAL")
    store_stalls = load_count_data(f"/mnt/nas/inesc/ist196723/osdi26/bin/{folder}/countANY")
    cycles = load_count_data(f"/mnt/nas/inesc/ist196723/osdi26/bin/{folder}/countCYCLES")
    l3_stalls = load_count_data(f"/mnt/nas/inesc/ist196723/osdi26/bin/{folder}/count")
    time = np.loadtxt(f"/mnt/nas/inesc/ist196723/osdi26/bin/{folder}/countTIME", dtype=float)

    

    print("TIME", time)
    #return
    with open(f"/mnt/nas/inesc/ist196723/osdi26/bin/{folder}/ARGS",'r')  as f:
        args = np.array(f.readlines())

    group_list = ["args", "nrs", "mode", "threads"]
    df = pd.DataFrame([nrs, mode, threads, any_stalls, store_stalls, l3_stalls, time, args, cycles]).T
    df.columns = ["nrs", "mode", "threads", "any_stalls", "store_stalls", "l3_stalls", "time", "args", "cycles"]
    #print((df['nrs']))
    #exit(0)
    #print(df)
    _df = df.groupby(list(set(group_list) - set("mode"))).filter(lambda x: 'SLOW' in x['mode'].values ).reset_index()
    #print(_df)
    _df = df.groupby(list(set(group_list) - set("mode"))).filter(lambda x: 'SLOW' not in x['mode'].values ).reset_index()
    #print(_df)
    #list(set(group_list) - set("mode"))
    #print( list(set(group_list) - set("mode"))  )
    _df = df.groupby(["args", "nrs", "threads"]).filter(lambda x: 'SLOW'  in x['mode'].values and 'FAST' in x['mode'].values and any(i > 1 for i in x['time']) ).reset_index(drop=True)
    #print(_df)
    #exit(0)
    df = df.groupby(["args", "nrs", "threads"]).filter(lambda x: 'SLOW' in x['mode'].values and 'FAST' in x['mode'].values and all(i > 1 for i in x['time'])).reset_index(drop=True)
    #print(x["nrs"].values, x['mode'].values,'SLOW' in x['mode'].values , 'FAST' in x['mode'].values ) and 
    #print(df)
    #exit(0)
    
    
    #filter(lambda x: 
    #print(x["nrs"].values, x['mode'].values,'SLOW' in x['mode'].values , 'FAST' in x['mode'].values )  and 'SLOW' in x['mode'].values and 'FAST' in x['mode'].values )
    ##sum([ 1 for a in x['mode'].values if 'SLOW' == a ])  == sum([ 1 for a in x['mode'].values if 'FAST' == a ])).reset_index(drop=True)
    print("SOO")
    print(df)
    #exit(0)

    ak = 'cycles'
    NORMALIZE = 0
    if NORMALIZE % 2 == 0:
        df['any_stalls'] /= df[ak] #*df['cycles']
        df['store_stalls'] /= df[ak] #*df['cycles']
        df['l3_stalls'] /= df[ak] #*df['cycles']
    #print(df_with_means)
    df = df.groupby(group_list).agg({"any_stalls": "mean", "store_stalls": "mean", "l3_stalls": "mean", 'time': 'mean', 
                                     }).reset_index() # drop index will drop the groups stable keys
                
    print("BEFORE cry", df.columns)
    def trans(x):
        print("---")
        print(x.columns)
        print(x.values)
        for k in x.columns:
            if k == 'time':
                continue
            if k == 'mode':
                continue
            if k == "slowdown":

                continue
            #x[k][x['mode'] == 'SLOW'] = 0 # x[k][x['mode'] == 'FAST']
            #x[k + "_slow"] = x[k][x['mode'] == 'SLOW']

        """
        #x['time'] = x['time']
        print(x)
        print(x['mode'].values)
        print(x['mode'].values)
        print(x['mode'].values)
        print(x['mode'].values)
        time_fast = x['time'][x['mode'] == 'FAST']
        time_slow = x['time'][x['mode'] == 'SLOW']
        print(time_fast, time_slow)
        print(time_fast, time_slow)
        print(time_fast, time_slow)
        print(time_fast, time_slow)
        """
        
        delta = lambda x,k : x[k][x['mode'] == 'SLOW'].mean() - x[k][x['mode'] == 'FAST'].mean()
        x['slowdown'] = 100*x['time'][x['mode'] == 'SLOW'].mean()/x['time'][x['mode'] == 'FAST'].mean()  
        x['delta_any'] = delta(x,'any_stalls')
        #(x['any_stalls'][x['mode'] == 'SLOW'].mean() - x['any_stalls'][x['mode'] == 'FAST'].mean())
        x['delta_l3'] = delta(x, 'l3_stalls')
        x['delta_store'] = delta(x, 'store_stalls')
        return x
        if 'time' not in x:
            print(x," WHAT")
        #return 
        # take the first element
        x = x.iloc[0]
        return x
    print("bifo")
    print(df)
    #df = pd.DataFrame(df)
    print(df)
     
    #df =  df.reset_index(drop=True)
    df = df.groupby(
#["args", "nrs", "threads"]
list(set(group_list) - set(["mode"])) ######### BE CAREFULL DOING A SET OF STRING INSTEAD OF THE LIST W/ 1 STRING
       # (list(["mode"]))
        ).apply(trans) #.agg({ 'mode': trans}) #['time'] #.diff() # .agg(trans).reset_index(drop=True)

    df = df[df['mode'] != 'SLOW']
    print(df)
    #exit(0)

    """
    df =  df.groupby((list(set(group_list) - set("mode")))).pivot_table(
        index = list(set(group_list) - set("mode")),
        columns = "mode",
        values = list(set(group_list) - set("mode") + set(["any_stalls", "store_stalls", "l3_stalls", "time"]))
        #aggfunc = "mean"
    )

    
    """
    #.agg({'time': trans}).reset_index(drop=True)
    plt.figure() #figsize=(50,10)
    plt.title("Stall cycles variation in real machine")
    plt.xlabel("time")
    for threads in df['threads'].unique():
        subset = df[df['threads'] == threads]
        if threads != 1:
            pass
            continue
        l3 = "l3_stalls"
        ss = 'store_stalls'
        aa = 'any_stalls'
        k = 'delta_any'
        k = 'delta_l3'
        k = 'delta_store'
        y = subset['delta_any'] - (subset['delta_l3'] + subset['delta_store'])  

        y = subset['delta_l3'] #+ subset['delta_store']
        y = subset[l3] + subset[ss]
        y = subset[l3]
        y = subset[aa]
        y = subset[aa] - (subset[l3] + subset[ss])  
        y = subset['delta_l3'] #+ subset['delta_store']
        y = subset['delta_any'] - (subset['delta_l3'] + subset['delta_store'])   # the increase in L3 stall cycles and store stall cycles is greater than  the increase in total cycles
        y = subset['any_stalls'] - (subset[l3] + subset[ss])
        y = subset[l3]


        plt.ylabel("Non store/load cycles %")
        plt.ylabel("Store/Load bound cycles %")
        plt.ylabel("∆ All stalls - ∆ Store bound - ∆ LLC bound cycles (%)")
        plt.xlabel("Slowdown (%)")
        WINSORIZE = 0
        y = subset['any_stalls'] - (subset[l3] + subset[ss]), # we have less any_stalls... but this is not absolue 
        x = subset[l3]
        x = subset[aa]
        y = subset['slowdown']

        if WINSORIZE % 2 == 0:
            from scipy.stats.mstats import winsorize
            x = winsorize(np.array(x), limits=[0.05, 0.05])
            y = winsorize(np.array(y), limits=[0.05, 0.05])
            

        plt.scatter(
            x, y,
          
            # the higher the percentage of mem stalls.. the lower the 
            #subset['slowdown'], y*100, 

        #c=subset['slowdown'], 
        c=(subset['any_stalls']-subset[l3]-subset['store_stalls']),
        #cmap="BuGn"
        cmap="RdYlGn"
        #c=[i for i in range(0,len(subset['slowdown']))], cmap="tab10"
                    #label=f'threads={threads}', 
                    #color=f'C{df["threads"].unique().tolist().index(threads)}'
                    , s=50, alpha=0.5)
    plt.legend()
    plt.savefig(f"{FIGS_FOLDER}/gen/any_stalls_time_threads.png")
    plt.close()
    exit(0)
    plt.figure() #figsize=(50,10)
    plt.title("Stall cycles variation in real machine")
    plt.xlabel("time")
    for threads in df['threads'].unique():
        subset = df[df['threads'] == threads]
        if threads != 1:
            pass
            continue
        l3 = "l3_stalls"
        ss = 'store_stalls'
        aa = 'any_stalls'
        k = 'delta_any'
        k = 'delta_l3'
        k = 'delta_store'
        y = subset['delta_any'] - (subset['delta_l3'] + subset['delta_store'])  

        y = subset['delta_l3'] #+ subset['delta_store']
        y = subset[l3] + subset[ss]
        y = subset[l3]
        y = subset[aa]
        y = subset[aa] - (subset[l3] + subset[ss])  
        y = subset['delta_l3'] #+ subset['delta_store']
        y = subset['delta_any'] - (subset['delta_l3'] + subset['delta_store'])   # the increase in L3 stall cycles and store stall cycles is greater than  the increase in total cycles
        y = subset['delta_l3'] #+ subset['delta_store']

        plt.ylabel("Store/Load bound cycles %")
        plt.ylabel("LLC bound cycles (%)")
        plt.ylabel("Stall cycles")
        plt.xlabel("Slowdown (%)")

        y = subset['delta_l3'] #+ subset['delta_store']
        y = subset[l3] #+ subset['delta_store']
        plt.scatter(subset['slowdown'], y*100, 
                    label=f'∆ LLC bound cycles', 
                    color='blue',
                    #color=f'C{df["threads"].unique().tolist().index(threads)}', 
                    s=50, alpha=0.5)
        y = subset[ss] + subset[l3]
        plt.scatter(subset['slowdown'], y*100, 
                    label=f'∆ ( Store + LLC) bound cycles', 

                    color='orange',
                    #color=f'C{df["threads"].unique().tolist().index(threads)}', 
                    s=50, alpha=0.5)


    plt.legend()
    plt.savefig(f"{FIGS_FOLDER}/gen/any_stalls_time_threadsDELTA_BOTH.png")
    plt.figure() #figsize=(50,10)
    plt.title("Stall cycles variation in real machine")
    plt.xlabel("time")
    for threads in df['threads'].unique():
        subset = df[df['threads'] == threads]
        if threads != 1:
            pass
            continue
        l3 = "l3_stalls"
        ss = 'store_stalls'
        aa = 'any_stalls'
        k = 'delta_any'
        k = 'delta_l3'
        k = 'delta_store'
        y = subset['delta_any'] - (subset['delta_l3'] + subset['delta_store'])  

        y = subset['delta_l3'] #+ subset['delta_store']
        y = subset[l3] + subset[ss]
        y = subset[l3]
        y = subset[aa]
        y = subset[aa] - (subset[l3] + subset[ss])  
        y = subset['delta_l3'] #+ subset['delta_store']
        y = subset['delta_any'] - (subset['delta_l3'] + subset['delta_store'])   # the increase in L3 stall cycles and store stall cycles is greater than  the increase in total cycles
        y = subset[l3]
        y = subset['delta_store'] #+ subset['delta_store']

        plt.ylabel("Non store/load cycles %")
        plt.ylabel("Store/Load bound cycles %")
        plt.ylabel("LLC bound cycles (%)")
        plt.xlabel("Slowdown (%)")
        plt.scatter(subset['slowdown'], y*100, 
                    #label=f'threads={threads}', 
                    color=f'C{df["threads"].unique().tolist().index(threads)}', s=50, alpha=0.5)
    plt.legend()
    plt.savefig(f"{FIGS_FOLDER}/gen/any_stalls_time_threadsDELTA_STORE.png")
    plt.close()

    exit(0)

    #print("----uuu")
    #print(df)
    #print(df)
    #print("----uuu")

    #for group in df_with_means:
    #    print(group)
    #    #group['mode']
    #    #if 'SLOW' in group:
    #    #    df_with_means[group] = df_with_means[group] - df_with_means[group.replace('SLOW', 'FAST')]
    #exit(0)
    


    # 
    #group_by_df = df.groupby(["args", "nrs", "mode"])
    #time_by_group = group_by_df["time"].mean()
    #delta_time_by_group = df_with_means[df_with_means['mode'] == 'FAST']['time'] - df_with_means[df_with_means['mode'] == 'SLOW']['time']

    #df['time'] = df.groupby(group_list)['time'].transform(lambda x: x[x['mode'] == 'FAST'] - x[x['mode'] == 'SLOW'])


    """
    _df = df[df['mode'] == 'FAST'].groupby(group_list) #["args", "nrs"]
    any_stalls_by_group = _df["any_stalls"].mean()
    store_stalls_by_group = _df["store_stalls"].mean()
    l3_stalls_by_group = _df["l3_stalls"].mean()
    # get delta between time when mode = SLOW and mode = FAST
    # remove those that do not have both 'SLOW' and 'FAST'
    """
    #delta_time_by_group = df[df['mode'] == 'SLOW'].groupby(group_list).apply(lambda x: x["time"].mean())
    #fast_time_by_group = df[df['mode'] == 'FAST'].groupby(group_list).apply(lambda x: x["time"].mean())




    #print(np.sum(np.array(df['mode'] == 'SLOW')), "SUMATRA")
    print(len(delta_time_by_group.values))
    print(len(fast_time_by_group.values))
    slowdown = delta_time_by_group.values / fast_time_by_group.values
    slowdown *= 100
    print(slowdown)
    # plot slow down in function of stalls
    mark_types = ['o', '^', 's', 'x'] # dots
    plt.figure()
    print(df['threads'], "DEAD")

    agg = df.groupby(group_list).agg({"any_stalls": "mean", "store_stalls": "mean", "l3_stalls": "mean", 'time': 'mean'})
    agg = agg[agg['mode'] != 'SLOW']
    print(agg)
    exit(0)


    for i, (group) in enumerate(np.unique(df['threads'])):
        print(i, group, "BL")
        c = delta_time_by_group['threads'] == group
        slow = delta_time_by_group[c]/fast_time_by_group[fast_time_by_group['threads'] == group]
        #slow = slowdown[slowdown['threads'] == group] 
        plt.scatter(slow, any_stalls_by_group[any_stalls_by_group['threads'] == group].values, color='green', label='Any Stalls', marker=mark_types[i%len(mark_types)])
    #for i, (group, df) in enumerate(store_stalls_by_group.groupby(df['threads'])):
        df = store_stalls_by_group[store_stalls_by_group['threads'] == group]
        plt.scatter(slow, df.values, color='blue', label='Store Stalls', marker=mark_types[i%len(mark_types)])
    #for i, (group, df) in enumerate(l3_stalls_by_group.groupby(df['threads'])):
        df  = l3_stalls_by_group[l3_stalls_by_group['threads'] == group]
        plt.scatter(slow, df.values, color='orange', label='L3 Stalls', marker=mark_types[i%len(mark_types)])
    plt.xlabel('Slowdown')
    plt.ylabel('Stalls')
    plt.legend()
    print("DONE")
    plt.savefig('______store_l3_stalls_slowdown.png')
    plt.close()
    exit(0)



    # plot slow down, color by thread, dot type by type of stall, y axis is each of the stalls
    def t():
        import pandas as pd
        import matplotlib.pyplot as plt
        import numpy as np

        # Your grouping code (simplified and fixed)
        group_by_df = df.groupby(["threads", "args", "nrs", "mode"])
        time_by_group = group_by_df["time"].mean()
        any_stalls_by_group = group_by_df["any_stalls"].mean()
        store_stalls_by_group = group_by_df["store_stalls"].mean()
        l3_stalls_by_group = group_by_df["l3_stalls"].mean()

        # Calculate slowdown (SLOW vs FAST mode)
        # Unstack mode to compare SLOW and FAST directly
        time_unstacked = time_by_group.unstack(level='mode', fill_value=0)
        slowdown = (time_unstacked['SLOW'] - time_unstacked['FAST']) / time_unstacked['FAST']

        # Create a comparison dataframe
        comparison_df = pd.DataFrame({
            'slowdown': slowdown,
            'any_stalls': any_stalls_by_group.unstack(level='mode').apply(lambda x: x['SLOW'] - x['FAST'], axis=1),
            'store_stalls': store_stalls_by_group.unstack(level='mode').apply(lambda x: x['SLOW'] - x['FAST'], axis=1),
            'l3_stalls': l3_stalls_by_group.unstack(level='mode').apply(lambda x: x['SLOW'] - x['FAST'], axis=1),
        }).reset_index()

        # Create visualization
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        stall_types = ['any_stalls', 'store_stalls', 'l3_stalls']
        markers = {stall: marker for stall, marker in zip(stall_types, ['o', 's', '^'])}

        colors = {threads: f'C{i}' for i, threads in enumerate(comparison_df['threads'].unique())}

        for idx, stall_type in enumerate(stall_types):
            ax = axes[idx]
            
            for threads in comparison_df['threads'].unique():
                subset = comparison_df[( comparison_df['threads'] == threads) ] 
                
                ax.scatter(
                    subset[stall_type], 
                    subset['slowdown'],
                    label=f'threads={threads}',
                    color=colors[threads],
                    marker='o',
                    s=100,
                    alpha=0.7
                )
            
            ax.set_xlabel(f'{stall_type} (SLOW - FAST)', fontsize=11)
            ax.set_ylabel('Slowdown ratio', fontsize=11)
            ax.set_title(f'Slowdown vs {stall_type}', fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.legend()

        plt.tight_layout()
        plt.savefig('___slowdown_analysis.png', dpi=300, bbox_inches='tight')
        #plt.show()





    #criteria = (args == n) & (threads == THREAD) s = (i == nrs ) & (mode == "FAST")


    plt.scatter(store_stalls.mean(axis=1), time.mean(axis=1)[1:] - time.mean(axis=1)[:-1], c=threads, cmap='viridis')
    plt.xlabel('Store Stalls')
    plt.ylabel('Time')
    plt.colorbar(label='Threads')
    plt.title(f'{folder}')
    plt.show()






    print(r)
    print(nrs, mode)
    plt.figure(figsize=(14,6),dpi=600)
    idx = 0
    xticks = []
    xlabels = []
    """
    for i,n in enumerate(nrs):
        b = i.split("/")[-1].split("NOavxprota")[0]
        if "bench_btree" in b:
            pass
        else:
            b = b.split("_")[0]
        nrs[b] = i
    """
        
    print(np.unique(nrs))
    idxxx = []
    #exit(0)
    for THREAD in np.unique(threads):
        i = threads == n 
        for i in np.unique(nrs):    ################### WIDTH for loop that catches rejects and continues

            rejects = ['small', 'trainI', 'sssp', "m64I"]
            if any(reject in i for reject in rejects):
                continue
            width = 3 # 1.8 instead of 1.5?
            width_actual = 5.5
            #print(i)
            s = (i == nrs ) & (mode == "FAST")
            f = (i == nrs ) & (mode == "SLOW")
            b = i.split("/")[-1].split("NOavxprota")[0]
            ex = ""
            if "test" in b:
                ex = "(test)"
            if "bwaves" in b:
                b = "bwaves"
            if "bench_btree" in b:
                b = "btree_mt"
            else:
                if "pr_spmv" not in b:
                    b = b.split("_")[0]
            b += ex

            sub_bench = 0
            start_pos = idx +  sub_bench*(width_actual )
            gap = 0.2
            
            criteria = (args == n) & (threads == THREAD)
            for n in np.unique(args[s]):
                fast_llc = np.mean(count[f & criteria])/THREAD
                slow_llc = np.mean(count[s & criteria])/THREAD
                if not (np.sum([s & criteria]) > 2 and  np.sum([f & criteria]) > 2):
                    return
                    exit(0)
                ratio = slow_llc/fast_llc
                print(f"{i}: {ratio} {slow_llc} {fast_llc}")
                FACTOR = 100
                print("LABEL", b, slow_llc, fast_llc)

                idxxx.append(idx)
            
                plt.bar(idx, ratio*FACTOR, width=width_actual,  label=b, color=get_color_bin(i))
                idx += gap
                sub_bench+=1
                idx +=  ((width_actual ))  ### WAS SCALING THE SPACING IN FUNCTION OF NR OF BENCHES! BUT THE ADD ALREADY DOES THAT! 

            idx -= (gap + ((width_actual )))

            if sub_bench > 1:
                sub_bench -= 1
            #idx = idx + (sub_bench)*(width + 4)
            end_pos = idx 
                
            plt.ylim(0.1*100, 175)
            # put xticks according to b
            if end_pos == start_pos:
                pass
                #end_pos += width
            xticks.append((end_pos+start_pos)/2 )
            xlabels.append(b)
            idx += width + width*2
        print(xticks, xlabels)
        print(idxxx, np.diff(np.array(idxxx)))

        #plt.tight_layout()
        plt.subplots_adjust(bottom=0.25)

        plt.title("Memory location impact on number of LLC misses observed in the real machine")
                #Ratio of LLC misses in the real machine observed in the slow tier vs fast tier")
        plt.xlabel("Benchmark")
        plt.ylabel("LLC miss (%)")
            
        plt.xticks(xticks, xlabels, rotation=85, ha='center')
        plt.savefig("./_____STALL_QUALITY.png")

        # Set the legend properties
        #plt.legend(["Blue = speccpu", "Orange = gapbs", "Pink = NPB", "Green = parsec"], facecolor='white', framealpha=1, fontsize='x-small', loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=4, fancybox=True, shadow=True)

        # After all bars are plotted, check the bar container:
        for patch in plt.gca().patches:
            print(f"Bar x={patch.get_x()}, width={patch.get_width()}")


        #; count = []; binary = []; mode = []; benchset_names =[]; 
        return llc_changes

def plot_llc_change():
    llc_changes = []
    files = glob.glob("/mnt/nas/inesc/ist196723/osdi26/bin/real/*")
    r = {}
    nrs = np.loadtxt("/mnt/nas/inesc/ist196723/osdi26/bin/real/binary", dtype=str)
    print(nrs)
    mode = np.loadtxt("/mnt/nas/inesc/ist196723/osdi26/bin/real/mode", dtype=str)
    with open("/mnt/nas/inesc/ist196723/osdi26/bin/real/ARGS",'r')  as f:
        args = np.array(f.readlines())
    #args = np.loadtxt("", dtype=str) #, delimiter="\n", comments="\r")
    #args = np.array([" ".join(entry) for entry in args])

    #print(args)
    #exit(0)
    #mode = np.append(mode, "FAST")

    count = []
    time = []
    for f in files:
        f = "/mnt/nas/inesc/ist196723/osdi26/bin/real/count"
        try: 
            lines = []
            
            with open(f,'r' ) as fu:
                for l in fu:
                #lines = fu.readlines()
                    if "mem_" in l:
                        lines.append(int(l.replace(",","").split("mem_load")[0]))
            r[f] = lines
            count = lines
        except Exception as e:
            print(f"Error loading {f}: {e}")
            pass


    count = np.array(count)
    print(np.array(count))
    print(r)
    print(nrs, mode)
    plt.figure(figsize=(14,6),dpi=600)
    idx = 0
    xticks = []
    xlabels = []
    """
    for i,n in enumerate(nrs):
        b = i.split("/")[-1].split("NOavxprota")[0]
        if "bench_btree" in b:
            pass
        else:
            b = b.split("_")[0]
        nrs[b] = i
    """
        
    print(np.unique(nrs))
    idxxx = []
    #exit(0)
    for i in np.unique(nrs):    ################### WIDTH for loop that catches rejects and continues
        rejects = ['small', 'trainI', 'sssp', "m64I"]
        if any(reject in i for reject in rejects):
            continue
        width = 3 # 1.8 instead of 1.5?
        width_actual = 5.5
        #print(i)
        s = (i == nrs ) & (mode == "FAST")
        f = (i == nrs ) & (mode == "SLOW")
        b = i.split("/")[-1].split("NOavxprota")[0]
        ex = ""
        if "test" in b:
            ex = "(test)"
        if "bwaves" in b:
            b = "bwaves"
        if "bench_btree" in b:
            b = "btree_mt"
        else:
            if "pr_spmv" not in b:
                b = b.split("_")[0]
        b += ex

        sub_bench = 0
        start_pos = idx +  sub_bench*(width_actual )
        gap = 0.2
        
        for n in np.unique(args[s]):
            fast_llc = np.mean(count[f & (args == n)])  
            slow_llc = np.mean(count[s & (args == n)]) 
            if not (np.sum([s & (args == n)]) > 2 and  np.sum([f & (args == n)]) > 2):
                exit(0)
            ratio = slow_llc/fast_llc
            print(f"{i}: {ratio} {slow_llc} {fast_llc}")
            FACTOR = 100
            print("LABEL", b, slow_llc, fast_llc)

            idxxx.append(idx)
        
            plt.bar(idx, ratio*FACTOR, width=width_actual,  label=b, color=get_color_bin(i))
            idx += gap
            sub_bench+=1
            idx +=  ((width_actual ))  ### WAS SCALING THE SPACING IN FUNCTION OF NR OF BENCHES! BUT THE ADD ALREADY DOES THAT! 

        idx -= (gap + ((width_actual )))

        if sub_bench > 1:
            sub_bench -= 1
        #idx = idx + (sub_bench)*(width + 4)
        end_pos = idx 
            
        plt.ylim(0.1*100, 175)
        # put xticks according to b
        if end_pos == start_pos:
            pass
            #end_pos += width
        xticks.append((end_pos+start_pos)/2 )
        xlabels.append(b)
        idx += width + width*2
    print(xticks, xlabels)
    print(idxxx, np.diff(np.array(idxxx)))

    #plt.tight_layout()
    plt.subplots_adjust(bottom=0.25)

    plt.title("Memory location impact on number of LLC misses observed in the real machine")
              #Ratio of LLC misses in the real machine observed in the slow tier vs fast tier")
    plt.xlabel("Benchmark")
    plt.ylabel("LLC miss (%)")
        
    plt.xticks(xticks, xlabels, rotation=85, ha='center')
    plt.savefig("./___________BARO.png")

    # Set the legend properties
    #plt.legend(["Blue = speccpu", "Orange = gapbs", "Pink = NPB", "Green = parsec"], facecolor='white', framealpha=1, fontsize='x-small', loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=4, fancybox=True, shadow=True)

    # After all bars are plotted, check the bar container:
    for patch in plt.gca().patches:
        print(f"Bar x={patch.get_x()}, width={patch.get_width()}")


    #; count = []; binary = []; mode = []; benchset_names =[]; 
    return llc_changes

OLD_V4 = True

def all_over_time_real():
    master_file="over_time_files"
    # check if master exists, if not call 
    if not os.path.exists(master_file):
        os.system("/home/ist196723/nas/osdi26/real_analysis.sh")
    systems = {'MEMTIS': [], 'ASMEM':  [], 'MEMTIS-1':[]}
    with open(master_file) as f:
        lines = f.readlines()
        print("----------------\n", lines, "-------------\n")
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
    def get_partial(partial_key, dictt):
        for key in dictt.keys():
            if partial_key in key:
                return dictt[key]
        print("NO key found for ", partial_key, dictt.keys())
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
                print(system_data[system][file] , "JJJJJJ")
                try:
                    j = len(system_data[system][file] )
                except:
                    continue

                #system_data[system][file + "YURI"] = np.sum(system_data[system][file] )
                #print(, system, file, "IMPO")
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
                    #system_data[system][file] = (8000 - system_data[system][file]) / 8000 # remove_outliers(system_data[system][file])
                    # remove 10 first entries
                    system_data[system][file] = system_data[system][file]
                    #system_data[system][file] = np.concatenate((np.cumsum(system_data[system][file][0:15]), system_data[system][file][15:]))
                    #N = 10
                    #system_data[system][file] = np.array([np.sum(system_data[system][file][i:i+N]) for i in range(0, len(system_data[system][file]), N)])
                    # total lost of CPU time should be equal to the nr of stalls increase

                    #
                    
            flen = len(system_data[system][file])
            if "promote" in file or "demote" in file:
                max_len = max(max_len,flen)
            print(max_len,  flen, file, "len setting...", system) # we have more LLC misses w/AsMEM... why?? 
        max_len_sys[system] = max_len
        try:
            _ = system_data[system]['hit_ratio_X']
        except:
            del system_data[system]
            continue
        _ = _ - _[0]
        _ = _ *  (max_len/_[-1])
        system_data[system]['hit_ratio_X'] =  _ 

    # scale the X axis to be in the range between 0 and, max_len 
    try:
        print("why", system_data['ASMEM']['hit_ratio_Y'])
        print(_)
        #for system in system_data:
        #    for file in system_data[system]:
        print(_)
        print("_[-1]", _[-1])
        print(len(system_data['ASMEM']['hit_ratio_X']))
    except:
        pass
    #print(len(_), "new leno!")
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

    NO_CLOCK = True
    def plot_migs():
        plt.figure()
        demo = plt
        #demo= plt.twinx()
        if not NO_CLOCK: 
            cl= plt.twinx()
            hit_ratio = plt.twinx()
        print('about to mig')
        for system in system_data:
            linestyle = "--" if "ASMEM" in system else "-"
            if len(system_data[system].keys()) == 0:
                continue
            len_time = len(get_partial('demo', system_data[system]))
            for file in system_data[system]:
                dps = len(system_data[system][file])
                x = dps
                print("IMPOS", system, file, np.sum(dps))
                if 'clock' in  file:
                    x = np.linspace(0, len_time, len(system_data[system][file]))
                def def_color():
                    if "hit_ratio" in file:
                        return 'blue','Hit Ratio'
                    if "stalls" in file:
                        return 'orange','Stalls'
                    if "prom" in file:
                        return 'green','Promotions'
                    if "demo" in file:
                        return 'red','Demotions'
                    return 'black', 'BALLK'
                color,lab = def_color()
                if "clock" in file:
                    if NO_CLOCK: 
                        continue
                    ax = cl
                else: 
                    ax = demo
                if "prom" in file or "demo" in file:
                    demo.plot(np.linspace(0, dps, dps ),system_data[system][file],   color=color, linestyle=linestyle, label=lab + " " + system) #label=file,
                    demo.legend()
                if "hit" in file and "X" in file and "Y" not in file:
                    x = get_partial("hit_ratio_X", system_data[system])
                    y = (get_partial("hit_ratio_Y", system_data[system]))
                    # convolve to have the haverage hit ratio of the last 3 entries
                    #y = np.convolve(y, np.ones(10)/10, mode='same')
                    #hit_ratio.plot(x,y/100,  label=file, color=color, linestyle=linestyle)
                if "clock" in file:
                    print(system_data[system][file], "ruuuuuu")
                    cl.plot( x,system_data[system][file],  label=file, color=color, linestyle=linestyle)
                    
                    #plot_interpol(plt, system_data[system][file], linestyle, color, max_len_sys[system])
        plt.legend()
        print("oover_timemmmigrations_over_time.png SAVED")
        plt.title("BUU")
        plt.savefig("oover_timemmmigrations_over_time.png")
        #exit(0)
    def plot_hit_ratio():
        plt.figure()
        k=[ "taskclock", "stalls_l3_miss", "time", "hit" ]
        s=[
           "ASMEM"
            , 
            "MEMTIS-1"
           ]
        label=['Blocked time', "LLC stall cycles", "Run time", 
               "Hit Ratio"]

        results = []
        i=0
        for key in k:
            i+=1
            vals = []
            for sys in s:
                if 'taskclock' in key:
                    r = np.loadtxt("_" + sys + "_" "taskclock-overtimeTOTAL")
                elif 'time' in key:
                    r = np.loadtxt("_" + sys + "_" + "time")
                elif 'hit' in key:
                    r = np.loadtxt("_" + sys + "_" + "hit_ratioTOTAL")
                    print("HITT", r)
                else:
                    r = np.sum(get_partial( key,system_data[sys]))
                
                #if "taskcl" in key: r=r-1000
                #r=r-1000

                vals.append(
                    r
                    # np.sum(r)
                )
            #print(key)
            results.append(vals[0]/vals[1])

        plt.bar(label, results)
        plt.title("")
        plt.ylim(0.5,1.5)
        plt.ylim(0.5,1)
        plt.ylim(0,1.5)
        plt.title("ASMEM performance metrics against non weighted sampling")
        plt.ylabel("Change (%)")
        plt.savefig("ooverhit_ratioNICE_BARS.png")
        
        exit(0)





        #if system not in system_data_cum: #system_data_cum[system] = {} "system_data_cum[system][file] = np.sum(system_data[system][file] )
        for system in system_data:
                    if len(system_data[system].keys()) == 0:
                        continue
                    #x = get_partial("hit_ratio_X", system_data[system])
                    y = (get_partial("hit_ratio_Y", system_data[system]))
                    y =np.mean(y)
                    plt.bar(system, y)
                    
        plt.savefig("ooverhit_ratio.png")
        pass

    plot_migs()
    plot_hit_ratio()


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
            print("SAVED",("over_time_" + p + ".png"))
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
    RESULT_FOLDER="multiIII"
    for MODE in "-": # "-freq_weighted" "":
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
                        'o1' : [],
                        'o2' : [],
                        'Frequency': []
                    }
                    for line in lines:
                        v = line.split(" ")
                        d['address'].append(v[0])
                        d['Access time'].append(int(v[1]))
                        d['Stall Cycles'].append(int(v[2]))
                        d['Stall Cycles/MLP'].append(int(v[4]))
                        d['o1'].append(int(v[-2]))
                        d['o2'].append(int(v[-3]))
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
            f = (f"{FIGS_FOLDER}/{RESULT_FOLDER}/{file}_stallsmlp_freqNEW.png")
            print("saved",  f)
            plt.savefig(f)
            plt.close()

            

            plt.title("CDF of instruction metrics for " + file.split("-")[1])
            plt.xlabel("Metric")
            for i in ['Stall Cycles', 'Access time','Stall Cycles/MLP']:
                sorted_data, cdf = get_cdf_array(d[i])
                plt.plot(sorted_data, cdf, label=i)
            plt.ylabel("CDF")
            plt.legend()
            f = (f"{FIGS_FOLDER}/{RESULT_FOLDER}/{file}{MODE}NEW.png")
            print("saved",  f)
            plt.savefig(f)
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

                
            

def _m(*args):
    return np.mean(np.array(args))
def mago():
    #./plot.sh runn do_soar_static cg

    # memtis stock.. 
    bench = "mg.C"
    bench = "bck"
    bench = "bcu"

    params = {
        'mg.C' : {
            'RSS' : 3570,
            'max_y': 10,
            'OBJ_DRAMS': [1186, 2372, 3458, 3570], # 112MB
            'SYSTEM_COL': "6",
            'soargrep': 'mg.C',
            'all_fast' : _m([77.81]) ,
            'all_slow': _m([213.11]), # 213.00  219.06 ##  252.57
            'STOCK': 
                { 
                 '1': 
                                        _m(139.37, 132.70, 141.23),  
                    '2': 87.705,
                    '3': 20 # FILL
                },
                #./plot.sh runn do_soar_static mg
                #ana_soar
                #do_soar
                #static_soar
                #do_soar_static

            'SOAR' : {
                #'1' :  
                '1186' :  
                  np.mean(
                    np.array([150.35])
                  ),

                  #'2' :
                  "2372":
                  np.mean(
                    np.array([77.53]) #'147.36])
                  ),
                  #"2372":
                  #'3': np.mean(
                  #    np.array([100])
                  #)
            },


            'TPP' : {
                #'1186' :  #'1000': 10000, # FILL  

                '1186' :  
                #'2000':
                        np.mean(np.array([
                            4451.85 ,
                            4471.56, # hot set is > than fast tier. mem trashing
                            4483.79])),
                  "2372":
                  #          '3458':
                        #'3000': 
                        # TPP w/3GB + 2GB --> while ASMem has less than 2372...
                        np.mean(np.array([   84.06, 78.30, 78.72 , 78.79 , 78.93 , 78.95 , 78.99 , 79.02 , 79.03 , 79.04 , 79.06 , 79.07 , 79.07 , 79.13 , 79.16 , 79.17 , 79.20 , 84.06 ])) 
                       # stable all good!
                        
                
                },
            'Alto' : {
                #'1000' : 10000, # FILL
                '1186' :  
                #ran w/'2000' : 
                    np.mean(np.array([5330.72 , 5299.27])), # and some more!
                  "2372":
                # ran w/'3000' : 
                    np.mean(np.array([169.63, 204.03, 226.90, 210.53])),
                #'5000' : np.mean(np.array([])) # never stables!0
                '4000' : 0 # FAILS, catastrophic migration overhead
                          },
        },
        'XSBench' : {
            
        },
        'cg.D': {
            #'RSS':
            #'max_y': 
            #  644.08 fast 1 thread
            'SYSTEM_COL': "5"
        }, 
        'bck': {
            'RSS': 22000,
            'max_y': 10,
            'OBJ_DRAMS': [0, 512, 1536,               2560, 3072, 3584,                4096,                       20480, 2200, 2200, 2200],
            'SYSTEM_COL': "5",
            'soargrep': 'kron.sg', 
            'all_fast': np.array([59.35356]),
            'all_slow': np.array([130, 140.98495 ,140.97888 ]),
            'SOAR' : {
'1' : np.mean(np.array([                116.00079 ,115.70927 ])),
'2' : np.mean(np.array([96.10755 , 96.12919 ])),
'3' : np.mean(np.array([92.11573 , 92.08232 ])),
'4' : np.mean(np.array([91.91846 , 91.92936 ])),
'5' : np.mean(np.array([86.05287,])),
'6' : np.mean(np.array([85.99102 ,])),
            },
            'Alto': {
                #'1000' 
           #'3000'  : 216.39407 
           #5000 475.28171
            #'3000': np.mean(np.array([105.27236, 137.43331, 145.85061])),
            '7000' : np.mean(np.array([95.35302, 94.76675, 96.06376])),
                #'10000' : 401.28754, 462.40864, 449.20613 
            }
        },
        'bcu': {
            'RSS': 22000,
            'OBJ_DRAMS': [0, 512, 1536, 2560, 3072, 3584, 4096, 20480, 2200, 2200, 2200],

            'soargrep': 'urand.sg',

            'SYSTEM_COL': "5",

            'RSS': 22000,
            'max_y': 4,
            #  cat ~/all_results | grep bcu | grep MEMTIS-1
            #  cat ~/all_results | grep bcu | grep ASMEM
            'OBJ_DRAMS': [0, 512, 1536,               2560, 3072, 3584,                4096,                       20480, 2200, 2200, 2200],
            'SYSTEM_COL': "5",
            'soargrep': 'kron.sg', 
            'all_fast':  122, #np.array([59.35356]),
            'all_slow':  240, # vs 223.. np.mean(np.array([480.74,496.52, 480.47380,  477.56586])), # ALL 223 SLOW = 480
            # cat ~/all_results | grep ALTO | grep urand.sg__ |  grep 1000 | tail -n 5 | awk '{ print $0 ;a+=1; b+=$1; } END {print b/a}'
            # cat ~/all_results | grep ALTO | grep urand.sg__ |  grep 2000 | tail -n 5 | awk '{ print $0 ;a+=1; b+=$1; } END {print b/a}'
            # cat ~/all_results | grep ALTO | grep urand.sg__ |  grep 3000 | tail -n 5 | awk '{ print $0 ;a+=1; b+=$1; } END {print b/a}'
            # cat ~/all_results | grep ALTO | grep urand.sg__ |  grep 4000 | tail -n 5 | awk '{ print $0 ;a+=1; b+=$1; } END {print b/a}'
            # cat ~/all_results | grep ALTO | grep urand.sg__ |  grep 5000 | tail -n 5 | awk '{ print $0 ;a+=1; b+=$1; } END {print b/a}'
            # cat ~/all_results | grep ALTO | grep urand.sg__ |  grep 10000 | tail -n 5 | awk '{ print $0 ;a+=1; b+=$1; } END {print b/a}'

            # cat ~/all_results | grep ALTO | grep urand.sg__ |  grep 1000 | tail -n 5 | awk '{ print $0 ;a+=1; b+=$1; } END {print b/a}'
            # cat ~/all_results | grep ALTO | grep urand.sg__ |  grep 2000 | tail -n 5 | awk '{ print $0 ;a+=1; b+=$1; } END {print b/a}'
            # cat ~/all_results | grep ALTO | grep urand.sg__ |  grep 3000 | tail -n 5 | awk '{ print $0 ;a+=1; b+=$1; } END {print b/a}'
            # cat ~/all_results | grep ALTO | grep urand.sg__ |  grep 4000 | tail -n 5 | awk '{ print $0 ;a+=1; b+=$1; } END {print b/a}'
            # cat ~/all_results | grep ALTO | grep urand.sg__ |  grep 5000 | tail -n 5 | awk '{ print $0 ;a+=1; b+=$1; } END {print b/a}'
            # cat ~/all_results | grep ALTO | grep urand.sg__ |  grep 10000 | tail -n 5 | awk '{ print $0 ;a+=1; b+=$1; } END {print b/a}'

            # 341.898 1GB
            # 263.233 2GB 2r old
            # 189.389 3gb 3r old
            # 244.228  4gb 2r old
            # 172 5GB ok
            # 160 10G  3r (1 old, do more)
            'DR': [                512, 1536, 2560, 3072, 3584],
             "ASMEM-1": {
                
                #'512': np.mean(np.array([99.78613])),
#'1536': np.mean(np.array([77.32546])),
#'2560': np.mean(np.array([59.07058])),
#
#'3072': np.mean(np.array([0])),
#'3584': np.mean(np.array([0])),
#
############################################## OBTAIN MORE DATA
'512': np.mean(np.array([106.10142])),
#'1024': np.mean(np.array([139.76748])),
'1536': np.mean(np.array([77.83255])),
#'2048': np.mean(np.array([71.45235])),
'2560': np.mean(np.array([112.3854])),
'3072': np.mean(np.array([0])),
'3584': np.mean(np.array([0])),
#'4096': np.mean(np.array([96.84782])),

                }, 
            "ASMEM": {
                '512': np.mean(np.array([99.78613])),
'1536': np.mean(np.array([77.32546])),
'2560': np.mean(np.array([59.07058])),

'3072': np.mean(np.array([10])),
'3584': np.mean(np.array([10])),

#                '500': np.mean(np.array([99.78613])),
#'1400': np.mean(np.array([77.32546])),
#'2500': np.mean(np.array([59.07058])),
#'1536': np.mean(np.array([73.09880])),
#'2560': np.mean(np.array([58.83784])),
                
                },

            "SOAR" : {
              '512': np.mean(np.array([185.16612])),   # column 2 = 1
                '1536': np.mean(np.array([150.632415])),  # column 2 = 2
                '2560': np.mean(np.array([137.54195])),   # column 2 = 3
                '3072': np.mean(np.array([137.210175])),  # column 2 = 4
                '3584': np.mean(np.array([133.697065])),  # column 2 = 5
             #    '4096': np.mean(np.array([133.661825])),  # column 2 = 6
            }, 


            # for i in 500 1000 2000 3000 4000 5000 6000 7000 8000 9000 1000; ^C echo $i; cat ~/all_results | grep " TPP " | grep urand.sg__ |  grep $i | tail -n 10 | awk '{ print $0 ;a+=1; b+=$1; } END {print b/a}' | tail -n 1; done
'TPP':{
        # 1343.48 3GB
    # 901.849 5GB


            #183.88148 0 3000 TPP-ALTO #192.56566 0 3000 TPP-ALTO #191.71885 0 3000 TPP-ALTO #144.29273 0 10000 TPP-ALTO
            #KRON #105.27236 0 3000 TPP-ALTO #137.43331 0 3000 TPP-ALTO #145.85061 0 3000 TPP-ALTO #95.35302 0 7000 TPP-ALTO #94.76675 0 7000 TPP-ALTO #96.06376 0 7000 TPP-ALTO 
                
            }, 'Alto':{
    #'3000': np.mean(np.array([183.88148, 192.56566, 191.71885])), '1000': np.mean(np.array([144.29273])),
                
            }

    }
    }
    #bench = "bck"
    bench = "mg.C"
    bench = "bcu"

    pre = "cat ~/nas/all_results  | grep -v '^0' | grep " 
    memtis_versions = pre + bench + " | grep -v '^0 ' | grep -E 'MEMTIS|ASMEM|AsMem|ASMEM' | awk '{print $COLUMN}'"
    import os
    import subprocess
    to_ignore = []
    def do(cmd, type=np.float64, f=lambda x : True):
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        r = []
        i = 0
        for line in result.stdout.strip().split('\n'):
            i += 1
            if not line:
                continue
            _ = line.strip()
            if i in to_ignore or not f(_): 
                to_ignore.append(i)
                continue
                
            r.append(_) 
        #lines = [line.strip() for line in if (line and f(line) and (True or ) )]
        lines = np.array(r,dtype=type) # np.fromstring(strr, dtype=type, sep='\n')
        return lines
    MEMTIS_DRAMS = do(memtis_versions.replace("COLUMN",str(int(params[bench]['SYSTEM_COL'])-2)), f= lambda x : int(x) < params[bench]['RSS'] )
    MEMTIS_TIMES = do(memtis_versions.replace("COLUMN","1"))
    MEMTIS_SYSTEMS = do(memtis_versions.replace("COLUMN",params[bench]['SYSTEM_COL']), object)
    to_ignore = []
    DRAMS_BY_OBJ = np.array(params[bench]['OBJ_DRAMS'] ,dtype=np.float64)
    # cat ~/nas/all_results  | grep mg.C | grep TPP | awk '{print $1 " "  $3}' #TPPS
    # 2000 mb for 
    # add TPP
    # add SOAR
    # 
    #DRAMS_BY_OBJ[do("cat ~/nas/all_results  | grep mg.C | grep SOAR | awk '{print $8 }'").astype(int)]


    RSS = params[bench]['RSS']
    norm = params[bench]['all_fast']
    # draw horizontal line in the all slow

    def convert_dram_to_obj(drams, drams_objs):
        new_dram = []
        for d in drams:
            # find the closest value in drams_objs to d
            closest = np.inf
            clost_d = -1
            for OBJ in drams_objs:
                if abs(OBJ - d) < closest:
                    closest = abs(OBJ - d)
                    clost_d = OBJ
            new_dram.append(clost_d)
        return np.array(new_dram)

    MEMTIS_DRAMS = convert_dram_to_obj(MEMTIS_DRAMS, DRAMS_BY_OBJ)
    def do_mean_by_system(systems, times, drams):
        u = np.unique(systems)
        d = np.unique(drams)
        new_drams = []
        new_times = []
        new_systems = []
        for dr in d:
            for k in u:
                mask = (systems == k) & (drams == dr)
                new_drams.append(dr)
                new_times.append(np.mean(times[mask]))
                new_systems.append(k)
        return np.array(new_drams), np.array(new_times), np.array(new_systems)
    MEMTIS_DRAMS, MEMTIS_TIMES, MEMTIS_SYSTEMS = do_mean_by_system(MEMTIS_SYSTEMS, MEMTIS_TIMES, MEMTIS_DRAMS)
    unique_systems = np.unique(MEMTIS_SYSTEMS)

    print(params[bench].keys())
    if 'DR'in params[bench]:
        unique_drams = np.array(np.unique( params[bench]['DR']), dtype=np.float64)
    else:
        unique_drams = np.unique(MEMTIS_DRAMS)

    colors = ["blue", "orange", "red", "green"]

    x = np.arange(len(unique_drams))
    width = 0.1

    plt.figure()
    # horizontal line  Y = 
    #plt.bar(MEMTIS_TIMES, MEMTIS_DRAMS, label=MEMTIS_SYSTEMS, color=["blue","orange","red","green"])
    plt.axhline(y=params[bench]['all_slow']/norm, color='grey', linestyle='--', linewidth=2, label="Full slow tier slowdown") # JC
    i=0
    def auto_system():
        for i, system in enumerate(unique_systems):
            mask = (MEMTIS_SYSTEMS == system) # & ( MEMTIS_DRAMS < params[bench]['RSS']) 
            times_for_system = MEMTIS_TIMES[mask]
            drams_for_system = MEMTIS_DRAMS[mask]
            
            # Sort by dram value for proper alignment
            sorted_indices = np.argsort(drams_for_system)
            drams_sorted = drams_for_system[sorted_indices]
            times_sorted = times_for_system[sorted_indices]
            #mask = drams_sorted < params[bench]['RSS'] 
            #times_sorted = times_sorted
            #
            
            
            plt.bar(x + i*width, np.array(times_sorted)/norm, width, label=system, color=colors[i % len(colors)])
                    
    """                
    if bench == "mg.C":
        SOAR_TIMES = [212.86, 147.36] # 77.10]
        SOAR_DRAMS = DRAMS_BY_OBJ #[:-1]
    else:
        #cat ~/all_results | grep "kron.sg" | grep -v "^0 "  | grep "SOAR"
        SOAR_TIMES = do(pre + params[bench] ['soargrep'] + " | grep SOAR | awk '{print $1 }'")
        _ =  do(pre + params[bench] ['soargrep'] + " | grep SOAR | awk '{print $1 }'")
        SOAR_DRAMS = [  DRAMS_BY_OBJ[i] for i in    do("cat ~/nas/all_results  | grep " + params[bench] ['soargrep'] + " | grep SOAR | awk '{print $7 }'").astype(int)]
    
    i+=1
    plt.bar(x + i*width, np.array(SOAR_TIMES)/norm, width, label="SOAR", color="black")
    """
    ################

    def manual(system,color="Brown"):

        #dram = '3000'
        # CONLCUSION
        # Alto was ran with 3GB. and had outlier with 10x slow down. lower configurations yield consistently 10x worst
        # all TPP systems had, at least one outlier, with 10x slow down
        # holding of promotions seems to make the system unable to stabilize.  WE RAN TPP WITH 5GB
        # they have rougly the same size but TPP can't detect which is more relevant. Freq based systems, however, can.

        # TPP has free memory available, but decides not to use it! 
        s = params[bench][system]
        print(s)
        times = []
        drams = list(sorted(list(
            np.array(list(s.keys()), dtype=int)
            ))) #, reverse=True)
        print(drams)
        print(drams)
        print(drams)
        for dram in drams:
            times.append(s[str(dram)])
        #drams = DRAMS_BY_OBJ
        #[212.86, 147.36]
        if len(drams) == 0:
            print("NO DATA FOR", system)
            return

        

        print(system, times, x + i*width, "...", drams)
        print(system, times, x + i*width, "...")
        print(system, times, x + i*width, "...")
        print(system, times, x + i*width, "...")
        #print(dram)

        print("bench", bench, "system", system, "DRAMS", drams)

        print("params[bench][system] = ", params[bench][system])
        print("params[bench][system][drams[0]] = ", params[bench][system][str(drams[0])])
        print("params[bench][system][drams[0]]/norm = ", params[bench][system][str(drams[0])]/norm)
        print(x)
        plt.bar(x + i*width, 

            [
params[bench][system][str(v)]/norm for v in drams
#                1,1 
 #, 0 #  params[bench][system][dram]/norm

            ]
               , width, 
                label=system, color=color)
    
    manual("ASMEM", 'blue')
    i+=1
    manual("ASMEM-1", 'orange')
    i+=1
    manual("SOAR", 'Black')
    i+=1
    manual('Alto','Brown')
    i+=1
    manual('TPP', "Magenta")
    def TPPs():
        TPP_TIMES =  do(pre + bench + " | grep 'TPP ' | awk '{print $1 }'")
        TPP_DRAMS =  convert_dram_to_obj(do(pre + bench + " | grep 'TPP ' | awk '{print $3 }'"), DRAMS_BY_OBJ)
        #TPP_TIMES, TPP_DRAMS, TPP_SYSTEMS = do_mean_by_system(np.full( len(TPP_TIMES),"TPP"), TPP_TIMES, TPP_DRAMS)
        times, drams, systems = do_mean_by_system(np.full( len(TPP_TIMES),"TPP"), TPP_TIMES, TPP_DRAMS)
        i+=1
        plt.bar(x + i*width, np.array(times)/norm, width, label="TPP", color="yellow")

        TPP_ALTO_TIMES =  do(pre + bench + " | grep 'TPP-A' | awk '{print $3 }'")
        TPP_ALTO_DRAMS =  convert_dram_to_obj(do(pre + bench + " | grep 'TPP-A' | awk '{print $3 }'"), DRAMS_BY_OBJ)
        #TPP_ALTO_TIMES, TPP_ALTO_DRAMS, TPP_ALTO_SYSTEMS = do_mean_by_system(np.full(len(TPP_ALTO_TIMES),"TPP-A"), TPP_ALTO_TIMES, TPP_ALTO_DRAMS)
        times, drams, systems = do_mean_by_system(np.full(len(TPP_ALTO_TIMES),"TPP-A"), TPP_ALTO_TIMES, TPP_ALTO_DRAMS)
        i+=1
        plt.bar(x + i*width, np.array(times)/norm, width, label="Alto", color="Orange")



    print(RSS, unique_drams, "TICKS", unique_drams*100/RSS)
    plt.xticks(x + width*1.5, np.round(((unique_drams*100/RSS))).astype(int))
    

    #plt.bar(DRAMS, TIMES, label=SYSTEMS)
    plt.xlabel("DRAM")
    plt.ylabel("Normalized runtime")
    #print("LAST", 
    

    #np.sort(MEMTIS_DRAMS[MEMTIS_DRAMS < RSS ])[-1]*100 /RSS )
    #plt.xlim(-1, 1.5)
    plt.ylim(0,params[bench]['max_y'])
    handles, labels = plt.gca().get_legend_handles_labels()
    print(labels)
    labels = ['ASMEM-1' if lbl == 'MEMTIS-1' else lbl for lbl in labels]

    plt.legend(handles, labels)
    plt.title("Workload performance in function of DRAM")
    #plt.legend()
    
    ext= ".png"
    ext= ".svg"
    plt.savefig("mago "+bench + ext)
    print(("mago "+bench + ext))
    plt.close()
    

def backup_files(*files):
    import os
    import shutil
    from pathlib import Path
    from datetime import datetime
    """
    Copy each file in `files` to a backup directory, with its modified time in the filename.
    
    Args:
        *files: variable number of file paths (strings or Path objects).
                Example: backup_files('config.txt', 'data.csv', 'notes.md')
    """
    # Define the backup directory (relative to current dir)
    backup_dir = Path("backup")
    backup_dir.mkdir(exist_ok=True)  # Create if it doesn't exist

    for file_path in files:
        src = Path(file_path)
        if not src.exists():
            print(f"Warning: {src} does not exist, skipping.")
            continue
        if not src.is_file():
            print(f"Warning: {src} is not a regular file, skipping.")
            continue

        # Get last modified time and format it as YYYY-MM-DD_HH-MM-SS
        mtime = src.stat().st_mtime
        mod_time_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d_%H-%M-%S")

        # Build new filename: original_stem + _ + timestamp + original_suffix
        stem = src.stem
        suffix = src.suffix
        new_filename = f"{stem}_{mod_time_str}{suffix}"
        dst = backup_dir / new_filename

        # Copy the file (preserves metadata like timestamps)
        shutil.copy2(src, dst)
        print(f"Backed up: {src} → {dst}")

    
def quinta():
    system = []
    time = []
    arand = []
    aptr = []
    ratio = []
    dram = []
    benched = []
    DRAM=3; ARAND=2; APTR=1; SYSTEM=3; BENCHED=5; TIME=0
    folder="/home/ist196723/nas/"
    bench_file="q"
    file = os.path.join(folder, bench_file)
    backup_files(file)
    with open(file, 'r') as f:
        lines = f.readlines()
        sy_results = {}
        for line in lines:
            v = line.split(" ")
            try:
                s = v[SYSTEM].strip()
                d = int(v[DRAM].strip())
                #b = v[#BENCHED].strip()
                #b = b.split("/")[-1].split("_")[0]
                ar = int(v[ARAND])
                ap = int(v[APTR])
                s_name = " ".join(v[5:8]).strip()
                #if not any([ h in  s_name for h  in [ "STATIC-2", "STATIC-3", "STATIC-0"]]): #, "SCALED", "ASMEM","MEMTIS-1"] ]): #STATIC-4
                #continue

                if "ASMEM" in v[5] :
                    s_name = " ".join(v[5:8]).strip()
                else:
                    s_name = v[5].strip()
                if  any([ h in  s_name for h in ["STATIC-4", "ALL","./outa", "NULL", "ALL"]]):
                    #pass
                    continue
                if  any([ h in  s_name for h in ["STATIC-4", "./outa", "NULL", "SCALED", "ALL"]]):
                    pass
                    #continue
                if False and any([ h in  s_name for h in ["STATIC-4", "./outa", "NULL", "SCALED"]]):
                    continue
                    
                #print("OUT_LINE", s,int(d),b,t)
                t = float(v[TIME])
                if t > 2000:
                    continue
                dram.append(d)
                #system.append(s)
                aptr.append(ap)
                arand.append(ar)
                print("s_name", s_name)
                system.append(s_name)
                #benched.append(b)
                time.append(float(t))
            except Exception as e:
                print(e)
                continue
    print(f"len system: {len(system)}")
    print(f"len time: {len(time)}")
    print(f"len arand: {len(arand)}")
    print(f"len aptr: {len(aptr)}")
    print(f"len dram: {len(dram)}")
    system = np.array(system); time = np.array(time); arand = np.array(arand); aptr = np.array(aptr); dram = np.array(dram);
    df = pd.DataFrame({'System': system, 'time': time, 'arand': arand, 'aptr': aptr, 'dram': dram})
    df = df.groupby(['System', 'aptr', 'arand', 'dram'])  .agg({'time': 'mean'}).reset_index() #drop=True
    # drop=True
    #.filter(lambda x: len(x) >= 1)
    # . reset_index()   #df = df.groupby(['System', 'aptr', 'arand', 'dram'])
    print(len(df), df)
    systems_to_ignore = [        'MEMTIS-SCALED', 'MEMTIS-S']
    df = df[~df['System'].isin(systems_to_ignore)]
    """
    for aptr in np.unique(aptr):
        for arand in np.unique(arand):
            _ = (df['arand'] == arand ) & ( df['aptr'] == aptr) & (df['system'] == 'STATIC-0')
            t = np.mean(df['time'][_])
            for s in np.unique(system):
                if t :
                    pass
                    #___ = (df['arand'] == arand ) & ( df['aptr'] == aptr) & (df['system'] == s)
                    #df.loc[___, 'time'] = df.loc[___, 'time'] / t
                    #df['time'][___] = df['time'][___]/t

    """

        
    humanS = {
        'STATIC-0': "All fast",
        'STATIC-1': "All slow",
        'STATIC-2': 
"Seq Read fast",
            #"Ptr Chase in slow tier",
        'STATIC-3': 
            "Ptr Chase fast ",
            #"Ptr Chase in fast tier",
            
        'ASMEM': "ASMEM (Stall Cycles/MLP)",

        'ASMEM-299': "(NORMAL) ASMEM (Stall Cycles/MLP)",
        'ASMEM-299 20_120': "(NORMAL) ASMEM (∆ Stall cycles/MLP)",
        'MEMTIS-1-299': "(NORMAL) MEMTIS-1",

        'ASMEM-11': "(HIGH) ASMEM (Stall Cycles/MLP)",
        'ASMEM-11 20_120': "(HIGH) ASMEM (∆ Stall cycles/MLP)",
        'ASMEM 20_120': "ASMEM (∆ Stall cycles/MLP)",
        'MEMTIS-1': "MEMTIS-1",
        'MEMTIS-1-11': "(HIGH) MEMTIS-1",
        'MEMTIS-SCALED': "MEMTIS-Sapo",
        
    }
    cols = {
        'STATIC-0' : 'green',
        'STATIC-1': 'red',
        'STATIC-2': 'brown',
        'STATIC-3': 'magenta',
        
        'ASMEM' : 'purple',
        'ASMEM 20_120' : 'blue',
        'MEMTIS-1' : 'orange',
        'MEMTIS-SCALED' : 'black',

        'ASMEM-11': 'cyan',
        'ASMEM-11 20_120': 'olive',

        'ASMEM-299': 'cyan',
        'MEMTIS-1-299': 'lime',
        'ASMEM-299 20_120': 'olive',

        'MEMTIS-1-11': 'lime',
    }
    allow = {
        'STATIC-0': "All fast",
        'STATIC-1': "All slow",
        'STATIC-2': 
"Seq Read fast",
            #"Ptr Chase in slow tier",
        'STATIC-3': 
            "Ptr Chase fast ",
            #"Ptr Chase in fast tier",
            
        'ASMEM': "ASMEM (Stall Cycles/MLP)",

        'ASMEM 20_120': "ASMEM (∆ Stall cycles/MLP)",
        'MEMTIS-1': "MEMTIS-1",
        
    }

    cols = {humanS[k]:v for k,v in cols.items()}
    other_colors = ['red', 'orange', 'red', 'green', 'blue', 'yellow', 'pink', 'purple', 'brown', 'magenta']
    for s in np.unique(df['System']):
        if s not in cols.keys():
            if len(other_colors) == 0:
                other_colors = ['red', 'orange', 'red', 'green', 'blue', 'yellow', 'pink', 'purple', 'brown', 'magenta']
            cols[s] = other_colors.pop()

    

    for r in [1,10,100]:#np.unique(aptr):
        #static_0 = df[(df['aptr'] == r) & (df['arand'] == 50) & (df['dram'] == 185) & (df['system'] == 'STATIC-0')]
        df_plot = df[(df['aptr'] == r) & (df['time'] < 300) & (df['dram'] == 185)].copy()
        df_plot['System'] = df_plot['System'].map(lambda s: humanS[s] if s in humanS else s)
        #df_plot['time'] = df_plot['time'] / static_0['time'].values[0]

        df_s = df_plot[df_plot["System"] ==  humanS['STATIC-2']]
        # THE RATIO IS 2... but where do they intersect
        df_s_other = df_plot[df_plot["System"] == humanS['STATIC-3']]
        p1 = np.polyfit(df_s_other['arand'], df_s_other['time'], deg=1) 
        p2 = np.polyfit(df_s['arand'], df_s['time'], deg=1)
        ratio = p1[0]/p2[0]
        
        a1, b1 = p1
        a2, b2 = p2
        x = (b2 - b1) / (a1 - a2)


        import seaborn as sns
        plt.figure(figsize=(10, 6))
        #lineplot
        #sns.lmplot(data=df_plot, x='arand', y='time', hue='system') #, errorbar=None)
        """
        sns.lmplot(data=df_plot, x='arand', y='time', hue='System',
                   hue_order=list(cols.keys()), 
                   ci=None,  fit_reg=False, scatter_kws={'s': 3,
                                                        # 'color': [cols[s] for s in df_plot['System']]
                                                         })
        """                                                         

        for s, color in list(cols.items()): # ("STATIC-0", "C0"), ("STATIC-3", "C1")]:
            if s not in allow.values():
                continue
            if s not in ["All fast", "All slow", "Seq Read fast", "Ptr chase fast", "ASMEM", "ASMEM Delta MLP", "MEMTIS-1"]:
                pass
                #continue

            df_s = df_plot[df_plot["System"] == s]
            if len(df_s) == 0:
                continue
            sns.scatterplot(
                data=df_s,
                x='arand',
                y='time',
                color=color,
                s=15,
                
            )
            sns.lineplot(

                data=df_s,
                x='arand',
                y='time',
                ci=None,
                color=color,
                label=s
            )

            """
            sns.regplot(
                data=df_s,
                x="arand",
                y="time",
                scatter=False, ci=False,
                color=color, line_kws={'linewidth': 1}
            )
            """

        plt.title(f'Performance in function of access distribution ({r} Pointer chasings)')
        #plt.title(f"Ratio static-2/static-3: {ratio:.2f} {x:.4f}")
        #plt.title(f"Performance  {r} ")
        plt.xlabel('Sequential reads')
        plt.ylabel('Time (mean)')
        #plt.ylim(0, 300)
        #plt.xlim(0, 750)
        if r == 1:
            plt.xlim(0, 55)
            plt.ylim(0, 10)
            pass
        if r == 10:
            plt.ylim(0,80)
            plt.xlim(0,550)
        if r == 100:    
            #plt.ylim(0,80)
            plt.xlim(0,1000)
        
        #plt.legend(title='system')
        plt.savefig(f"./_______MILLION{r}.png")
        plt.close()
    print(dram)
    print(np.unique(aptr) ) #dram)


    # aptr over ratio
    for r in [1,10,100]:#np.unique(aptr):
        idx = aptr == r
        print("Doing aptr R",r, np.sum(idx))
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
        x = np.arange(len(arands)) 

        print("MAXIMO", np.max(arands))
        x_i = 0
        per_system_xy = {}
        for i in range(len(arands)):
            current_arand = arands[idx_sort][i]
            DRAM_USED=185
            baseline_fast = 1
            k =     0
            #plt.bar(["Hello", "Hello", "There", "There", "yo", "yo"], [1,2,3,4,5,6], label=['System1','System2','System1','System2','System1' ,'System2'])
            #continue
            unique_labels =np.unique(system)
            palette = plt.cm.Set2(np.linspace(0, 1, len(unique_labels)))
            label2color = {lab: col for lab, col in zip(unique_labels, palette)}
            for  s in np.unique(system[idx]):
                if s not in per_system_xy:
                    #per_system_xy[s] = [[aptr],[idx_s]]
                    pass
                #                if not s == "ASMEM" and not s == "MEMTIS-1" and not s == "ASMEM 20_120":

                #    continue
                idx_s = (aptr == r) & (arand == current_arand) & (system == s) & (dram == DRAM_USED) #(dram[idx] == 320)
                o = i*2
                csys = ["ASMEM", "MEMTIS-1", "MEMTIS-NULL", "ASMEM 20_120", "STATIC-2", "STATIC-3", "STATIC-0"]
                ccolor = ["Orange", "blue", "red", "ASMEM 20_120"]
                bs = "MEMTIS-1" # "STATIC-0"
                baseline_fast = np.mean(
                                    time[
                        (aptr == r) & (arand == current_arand) & (system == bs) & (dram == DRAM_USED)
                                        ] #(dram[idx] == 320)
                )
                t = np.mean(time[idx_s])/1 # baseline_fast
                if not t:
                    continue


                width=0.2
                space_bet = 0.2
                print("SYSTEM", s)
                plt.bar(
                    x[x_i]*(1+width*5) + space_bet*k
                   # i+o+k
                    ,t , width=width, color=label2color[s])
                k+=1
                #plt.bar(i+o+0.5, np.mean(time[idx][idx_asm])/baseline_fast, width=0.5, color="orange")
                #xticks.append(i+o+0.25)
                #xticks_labels.append(str(current_arand))
                continue

            x_i +=1
            continue
                

            #print(dram, idx)
            idx_mem = (arand[idx] == current_arand) & (system[idx] == "MEMTIS-1-1\n") & (dram[idx] == DRAM_USED) #(dram[idx] == 320)
            idx_asm = (arand[idx] == current_arand) & (system[idx] == "ASMEM\n") & (dram[idx] == DRAM_USED) #(dram[idx] == 320)

            idx_all_fast = ( arand[idx] == current_arand) & ((system[idx] == "ALL_FAST\n") | (system[idx] == "ALL_FAST"))
            idx_all_slow = ( arand[idx] == current_arand) & (((system[idx] == "ALL_SLOW\n") | (system[idx] == "ALL_SLOW"))) 

            baseline_fast = np.mean(time[idx][idx_all_fast])
            baseline_fast = np.mean(time[idx][idx_all_slow])

            print("----------")
            print(len(time[idx][idx_mem]))
            print(len(time[idx][idx_asm]))
            print("----------")

            o = i*1.1
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
            #plt.xticks(xticks, xticks_labels)
            #plt.bar(i+0.25, 0, width=0, bottom=str(aptrs[i]))

            #plt.bar(system[idx][i] + aptr[idx][i], time[idx][i], label="Time")
            #plt.bar(system[idx][i], aptr[idx][i], bottom=time[idx][i], label="Ptr")

        from matplotlib.lines import Line2D

        # Color legend handles
        color_handles = [
            Line2D([0], [0],  color='blue', label='MEMTIS'),
            Line2D([0], [0],  color='orange', label='AsMem'),
        ]
        from matplotlib.patches import Patch
        legend_handles = [Patch(facecolor=label2color[lab], label=lab) for lab in unique_labels]
        plt.legend(handles=legend_handles)


        # Combine marker and color handles
        all_handles =  color_handles

        # Show legend with all handles
        #plt.legend(handles=all_handles, loc='best')
        #plt.legend()
        plt.title(f"Performance with {r} pointer chasings")
        plt.title(np.unique(system[idx]))
        plt.savefig(f"{FIGS_FOLDER}/../report/Haptr_{r}.png")
        print("Saved", (f"{FIGS_FOLDER}/../report/Haptr_{r}.png"))
    
        
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

        other_benchmode = True
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
                            return "SCALED" not in v[SYSTEM] and "STOCK" not in v[SYSTEM] and "ASMEM" not in  v[SYSTEM] and "TPP" not in v[SYSTEM] and "MEMTIS" not in v[SYSTEM] and "SOAR" not in v[SYSTEM] and "ALL_FAST" not in v[SYSTEM] and "ALL_SLOW" not in v[SYSTEM]
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
                            #exit(0)
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
                        bench = "bck"
                        bench = "mg.C"
                        bench = "bcu"
                        bench = "bck"
                        bench = "mg.C"
                        bench = "cg"
                        bench_sel = bench == benched[idx] 

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
                    idx_memtis_stock = ((system[idx] == "MEMTIS-STOCK")  & bench_sel )#plt.bar("MEMTIS", np.mean(time[])) #plt.bar("AsMem", np.mean(time[]))
                    idx_memtis_scaled = ((system[idx] == "MEMTIS-SCALED")  & bench_sel )#plt.bar("MEMTIS", np.mean(time[])) #plt.bar("AsMem", np.mean(time[]))
                    idx_memtis_scaled_16 = ((system[idx] == "MEMTIS-SCALED_16")  & bench_sel )#plt.bar("MEMTIS", np.mean(time[])) #plt.bar("AsMem", np.mean(time[]))
                    bench_sel = bench == benched[idx] 
                    PERCENT_DRAM = True
                    benchmarkss = {
                        'mg.C' : [4000+2000],
                        #'bck' : [20000],
                        'bck' : [7000],
                        'bcu' : [7000],
                        #'bcu' : [20000],
                        'cg' : [7000]
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
                        if len(time[idx][idx_memtis_stock]) != 0:
                            plt.scatter(percentage, np.mean(time[idx][idx_memtis_stock]/norm), color="purple", alpha=alfa)
                        if len(time[idx][idx_memtis_scaled]) != 0:
                            plt.scatter(percentage, np.mean(time[idx][idx_memtis_scaled]/norm), color="grey", alpha=alfa)
                        if len(time[idx][idx_memtis_scaled_16]) != 0:
                            plt.scatter(percentage, np.mean(time[idx][idx_memtis_scaled_16]/norm), color="black", alpha=alfa)
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
                #exit(0)
            print("bouto..")
            other_plot(bench)
            return

    #do_plot("__", 5, "JOINED", False)
    
    if False:
        LAST_SYN=False
        file = "/mnt/nas/inesc/ist196723/all_results"
        nr_args = 5
        do_plot(file, nr_args, bench, True)
        print("JJJJJJJJJJJJJJJJJJJJJJJJ")
        print(system, dram)

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
    
    #return
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

    "echo $run_time $aptr $arand $DRAM $memory $BASE $exec | tee -a ~/synthethic_results"
    with open("~/nas/synthethic_results", "r") as f:
        lines = f.readlines()
        run_times = []
        aptrs = []
        arands = []
        DRAMs = []
        memorys = []
        BASEs = []
        execs = []
        for line in lines:
            if "outa" not in line:
                continue
            run_time, aptr, arand, DRAM, memory, BASE, exec = line.split()
            run_times.append(float(run_time))
            aptrs.append(int(aptr))
            arands.append(int(arand))
            DRAMs.append(int(DRAM))
            memorys.append(memory)
            BASEs.append(BASE)
            execs.append(exec)
        run_times = np.array(run_times)
        aptrs = np.array(aptrs)
        arands = np.array(arands)
        DRAMs = np.array(DRAMs)
        memorys = np.array(memorys)
        BASEs = np.array(BASEs)
        execs = np.array(execs)

        BASEs == "STATIC-3"
        BASEs == "STATIC-2"



            

    pass
def plot_su():
    ptr_slow = 154.076404 
    ptr_fast = 81.705234
    seq_fast=  7.884400
    seq_slow = 16.413961
    benefit_ptr = ptr_slow - ptr_fast
    benefit_seq = seq_slow - seq_fast
    ptr_acc_time = [219]; seq_acc_time = [189 ]
    ptr_acc_time_slow = [420]; seq_acc_time_slow = [459 ]

    ptr_acc_time_fast = [219]; seq_acc_time_fast = [189 ]

    ptr_stall_cycles_weights_slow = [336.7307692307692]; 
    ptr_stall_cycles_slow = ptr_stall_cycles_weights_slow
    seq_stall_cycles_weights_slow = [278]
    seq_stall_cycles_slow = seq_stall_cycles_weights_slow
    ptr_stall_cycles_fast = [205]
    seq_stall_cycles_fast = [76]


    #ptr_mlp_stall_fast = [104]
    #seq_mlp_stall_fast = np.mean([6])
    ptr_mlp_stall_slow = [223]
    seq_mlp_stall_slow = [26]

    ptr_mlp_stall_fast = [102] #whyy
    seq_mlp_stall_fast = [5]
 


    ptr_by_mlp_avg_weights_slow = [116.8076923076923]; ptr_by_mlp_avg_weights_fast = [54.583333333333336]
    ptr_acc_time = np.array(ptr_acc_time); seq_acc_time = np.array(seq_acc_time)
    ptr_acc_time_fast = np.array(ptr_acc_time_fast); seq_acc_time_fast = np.array(seq_acc_time_fast)
    ptr_acc_time_slow = np.array(ptr_acc_time_slow); seq_acc_time_slow = np.array(seq_acc_time_slow)
    
    ptr_acc_time = np.mean(ptr_acc_time); seq_acc_time = np.mean(seq_acc_time)
    ptr_acc_time_fast = np.mean(ptr_acc_time_fast); seq_acc_time_fast = np.mean(seq_acc_time_fast)
    ptr_acc_time_slow = np.mean(ptr_acc_time_slow); seq_acc_time_slow = np.mean(seq_acc_time_slow)


    ptr_mlp_stall_fast = np.array(ptr_mlp_stall_fast); seq_mlp_stall_fast = np.array(seq_mlp_stall_fast)
    ptr_mlp_stall_fast = np.mean(ptr_mlp_stall_fast); seq_mlp_stall_fast = np.mean(seq_mlp_stall_fast)
    ptr_mlp_stall_slow = np.array(ptr_mlp_stall_slow); seq_mlp_stall_slow = np.array(seq_mlp_stall_slow)
    ptr_mlp_stall_slow = np.mean(ptr_mlp_stall_slow); seq_mlp_stall_slow = np.mean(seq_mlp_stall_slow)
    seq_stall_cycles_fast = np.array(seq_stall_cycles_fast); seq_stall_cycles_slow = np.array(seq_stall_cycles_slow)
    seq_stall_cycles_fast = np.mean(seq_stall_cycles_fast); seq_stall_cycles_slow = np.mean(seq_stall_cycles_slow)
    ptr_stall_cycles_slow = np.array(ptr_stall_cycles_slow); seq_stall_cycles_slow = np.array(seq_stall_cycles_slow)
    ptr_stall_cycles_slow = np.mean(ptr_stall_cycles_slow); seq_stall_cycles_slow = np.mean(seq_stall_cycles_slow)

    plt.figure(figsize=(12, 6))
    plt.title("Proportion between Pointer Chaseeeee and Streaming Reads metrics", pad=20)
    
    # Bar width and group spacing
    bar_width = 0.12
    group_spacing = 0.4
    # Group positions
    groups = {
        "Access time": 0,
        "Stall cycles/MLP": group_spacing,
        "Stall cycles": group_spacing * 2,
        "Iteration time": group_spacing * 3,
        "Benefit": group_spacing * 4,
        "∆Access Time":   group_spacing*4.5,
        "∆Stall cycles/MLP":   group_spacing*5.5,
        "∆Stall cycles":   group_spacing*6,
        "Degradation": group_spacing*7
    }

    xlabels = []
    xticks = []

    # Access time
    x = groups["Access time"]
    plt.bar(x, ptr_acc_time_fast/seq_acc_time_fast, width=bar_width, color="blue", label="Fast" if x == 0 else "")
    plt.bar(x + bar_width, ptr_acc_time_slow/seq_acc_time_slow, width=bar_width, color="orange", label="Slow" if x == 0 else "")
    xticks.append(x + bar_width/2)
    xlabels.append("Access time")

    # Stall cycles/MLP
    x = groups["Stall cycles/MLP"]
    plt.bar(x, ptr_mlp_stall_fast/seq_mlp_stall_fast, width=bar_width, color="blue")
    plt.bar(x + bar_width, ptr_mlp_stall_slow/seq_mlp_stall_slow, width=bar_width, color="orange")
    xticks.append(x + bar_width/2)
    xlabels.append("Stall cycles/MLP")

    # Stall cycles
    x = groups["Stall cycles"]
    plt.bar(x, ptr_stall_cycles_fast/seq_stall_cycles_fast, width=bar_width, color="blue")
    plt.bar(x + bar_width, ptr_stall_cycles_slow/seq_stall_cycles_slow, width=bar_width, color="orange")
    xticks.append(x + bar_width/2)
    xlabels.append("Stall cycles")

    # Iteration time
    x = groups["Iteration time"]
    plt.bar(x, ptr_fast/seq_fast, width=bar_width, color="blue")
    plt.bar(x + bar_width, ptr_slow/seq_slow, width=bar_width, color="orange")
    xticks.append(x + bar_width/2)
    xlabels.append("Iteration time")

    x = groups["Degradation"]
    plt.bar(x, ptr_slow/ptr_fast, width=bar_width, color="blue")
    plt.bar(x + bar_width, seq_slow/seq_fast, width=bar_width, color="grey")
    xticks.append(x + bar_width/2)
    xlabels.append("Degradation")

    # Benefit
    x = groups["Benefit"]
    plt.bar(x, benefit_ptr/benefit_seq, width=bar_width, color="grey", label="Both")
    xticks.append(x  )
    xlabels.append("Benefit")

    k = "∆Access Time"
    x = groups[k]
    plt.bar(x, (ptr_acc_time_fast-ptr_acc_time_slow) / (seq_acc_time_fast-seq_acc_time_slow), width=bar_width, color="grey")
    xticks.append(x)
    xlabels.append(k)
    x = groups[k]
    k =        "∆Stall cycles"
    plt.bar(x,  (ptr_stall_cycles_fast-ptr_stall_cycles_slow) / (seq_stall_cycles_fast-seq_stall_cycles_slow), width=bar_width, color="grey")
    xticks.append(x )
    xlabels.append(k)
    k =        "∆Stall cycles/MLP"
    x = groups[k]
    plt.bar(x,  (ptr_mlp_stall_slow-ptr_mlp_stall_fast) / (seq_mlp_stall_slow-seq_mlp_stall_fast), width=bar_width, color="grey")
    xticks.append(x)
    xlabels.append(k)

    #plt.bar("Access time",  color="grey")
    #plt.bar("Stall cycles/MLP ", (ptr_mlp_stall_fast-ptr_mlp_stall_slow) / (seq_mlp_stall_fast-seq_mlp_stall_slow), color="grey")
    #plt.bar("Stall cycles ", (ptr_stall_cycles_fast-ptr_stall_cycles_slow) / (seq_stall_cycles_fast-seq_stall_cycles_slow), color="grey")
    #plt.bar("Iteration time", (ptr_fast-ptr_slow) / (seq_fast-seq_slow), color="grey")

    # Add legend, labels, and adjust layout
    plt.xticks(xticks, xlabels, rotation=45, ha='right')
    plt.legend(title="Tier used to obtain metrics")
    plt.ylabel("Ratio (Pointer Chase / Streaming Reads)")
    plt.tight_layout()

    """
    plt.bar("Stall cycles/MLP ", ptr_mlp_stall_slow/seq_mlp_stall_slow , color="orange")
    plt.bar("Stall cycles ", ptr_stall_cycles_fast/seq_stall_cycles_fast , color="blue")
    plt.bar("Stall cycles ", ptr_stall_cycles_slow/seq_stall_cycles_slow , color="orange")
    plt.bar("Iteration time", ptr_fast/seq_fast, color="blue")
    plt.bar("Iteration time", ptr_slow/seq_slow, color="orange")
    plt.bar("Benefit", benefit_ptr/benefit_seq, color="grey")

    plt.bar("Access time", (ptr_acc_time_fast-ptr_acc_time_slow) / (seq_acc_time_fast-seq_acc_time_slow), color="grey")
    plt.bar("Stall cycles/MLP ", (ptr_mlp_stall_fast-ptr_mlp_stall_slow) / (seq_mlp_stall_fast-seq_mlp_stall_slow), color="grey")
    plt.bar("Stall cycles ", (ptr_stall_cycles_fast-ptr_stall_cycles_slow) / (seq_stall_cycles_fast-seq_stall_cycles_slow), color="grey")
    plt.bar("Iteration time", (ptr_fast-ptr_slow) / (seq_fast-seq_slow), color="grey")
    """



    # blue is fast tier orange is slow tier 
    plt.savefig("report/su.png")
    

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


        LIMIT=10
        mask_X = [inst == insts_unique[0] for inst in values['inst_weights'][:LIMIT][idx]]
        mask_O = [inst == insts_unique[1] for inst in values['inst_weights'][:LIMIT][idx]]
        #mask_O = [not cond for cond in mask_X]
        if not DO_DIFF:
            diff = np.zeros(len(values['arand'][idx][mask_X]))

        diff = diff if not DO_DIFF else np.array(values80['acc_time_weights'])[:LIMIT][idx][mask_X]
        plt.scatter(np.array(values['arand'])[:LIMIT][idx][mask_X],  np.abs(diff - np.array(values['acc_time_weights'])[:LIMIT][idx][mask_X]), 
                    label='Access time Stream', marker='X', color="blue")
        diff = diff if not DO_DIFF else np.array(values80['acc_time_weights'])[:LIMIT][idx][mask_O]
        plt.scatter(np.array(values['arand'])[:LIMIT][idx][mask_O], np.abs(diff - np.array(values['acc_time_weights'])[:LIMIT][idx][mask_O]), 
                    label='Access time Pointer Chase', marker='o', color="blue")
        
        diff = diff if not DO_DIFF else np.array(values80['stall_cycles_weights'])[:LIMIT][idx][mask_X]
        plt.scatter(np.array(values['arand'])[:LIMIT][idx][mask_X], np.abs(diff - np.array(values['stall_cycles_weights'])[:LIMIT][idx][mask_X]), 
                    label='Stall cycles Stream', marker='X', color="orange")
        diff = diff if not DO_DIFF else np.array(values80['stall_cycles_weights'])[:LIMIT][idx][mask_O]
        plt.scatter(np.array(values['arand'])[:LIMIT][idx][mask_O], np.abs(diff - np.array(values['stall_cycles_weights'])[:LIMIT][idx][mask_O]), 
                    label='Stall cycles Pointer Chase', marker='o', color="orange")
        diff = diff if not DO_DIFF else np.array(values80['by_mlp_avg_weights'])[:LIMIT][idx][mask_X]
        plt.scatter(np.array(values['arand'])[:LIMIT][idx][mask_X], np.abs(diff - np.array(values['by_mlp_avg_weights'])[:LIMIT][idx][mask_X]), 
                    label='Stall cycles/MLP Stream', marker='X', color="green")
        diff = diff if not DO_DIFF else np.array(values80['by_mlp_avg_weights'])[:LIMIT][idx][mask_O]
        plt.scatter(np.array(values['arand'])[:LIMIT][idx][mask_O], np.abs(diff - np.array(values['by_mlp_avg_weights'])[:LIMIT][idx][mask_O]), 
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
        ptr_slow = 154.076404 
        ptr_fast = 81.705234
        seq_fast=  7.884400
        seq_slow = 16.413961
        benefit_ptr = ptr_slow - ptr_fast
        benefit_seq = seq_slow - seq_fast
        plt.bar("Iteration time fast tier", ptr_fast/seq_fast, color="grey")
        plt.bar("Iteration time slow tier", ptr_slow/seq_slow, color="grey")
        plt.bar("Benefit", benefit_ptr/benefit_seq, color="grey")

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
        plt.bar("Hello",10)
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
    
        

from enum import IntEnum

class WEIGHT_FIELD(IntEnum):
    ADDR = 0
    TOTAL_TIME = 1
    STALL_TIME = 2
    MLP_WEIGHTED_PERCENT = 3
    MLP_BY_MEAN = 4
    HYPER_THREAD_WEIGHT = 5
    HYPER_THREAD_NO_MLP = 6
    LSTALL = 7
    FREQ = 8
    LITERAL_ONE = 9
    AVG_INST_COST = 10
    AVG_COST_PER_ACC = 11
    AVG_INST_COST_160 = 12
    AGG_STORE_COST = 13
    MLP_WEIGHTED_AGG = 14
    BMW_METRIC = 15

    @classmethod
    def get_name(cls, idx: int) -> str:
        base_field = next((member for member in cls if member.value == idx), None)
        base = ""
        if base_field is None:
            base_field = next((member for member in cls if member.value+16 == idx), None)
            base = "80"
        if base_field is None:
            return "UNKNOWN MAN..."
        return base_field.name +  base

    @classmethod
    def get_from(cls,   field_name: str, type_idx: int = 0) -> int:
        """
        Get the position for a field name in the given type (0=first line, 1=second line at +16).
        Usage: parts[RecordField.get_position("TOTAL_TIME", 1)]  # second type TOTAL_TIME
        """
        field = cls[field_name]
        return field.value + (type_idx * 16)



"""
python3 bin/python_parser.py "simple_weight()"
"""
writes=0
def psw___(): # plot syntehthic weights 
    RESULT_FOLDER="/mnt/nas/inesc/ist196723/osdi26/final_data/multiIII100/synthethic_extended-*-*"
    #reads = [int(i) for i in  ("1 2 4 8 16 32 64 128 256 512 " * 2 ).split(" ") ] # arand only , combined,

    _ = {}
    runs = glob.glob(RESULT_FOLDER)
    print("\n".join(runs))
    df = pd.DataFrame()
    aptr_inst = 14416; arand_inst = 13667
    #arand_inst= aptr_inst;
    for f in runs: 
        print(f)
        arand = int(f.split("extended-")[1].split("-")[0])
        aptr = int(f.split("extended-")[1].split("-")[1])
        if not aptr == arand:
            pass
            #continue
            
        f = open(f, 'r'); lines = f.readlines(); f.close()
        for l in lines:
            if not l.startswith(str(aptr_inst)) and not l.startswith(str(arand_inst)): 
                print(l) 
                continue
            #print(l, "PASS")
            row = {'aptr': aptr, 'arand': arand}
            for i,entry in enumerate(l.split(" ")):
                if entry == "\n" or entry == '':
                    continue 
                entry  = int(entry)
                row[WEIGHT_FIELD.get_name((i))] = entry 
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)  
            # CONCAT ON THE WRONG IDENTATION, ONLY GETTING ONE ROW PER FILE


        
        
        
        """
        def get_line(inst):
            return [ l if l.startswith(str(arand_inst)) for l in lines][0]
        def get_values():
            arand_line = get_line(arand_inst)
            sp = arand_line.split(" ")

            [WEIGHT_FIELD.TOTAL_TIME]
        aptr_line = get_line(aptr_inst)
        """

    #     
    #print(df)
    df = df.sort_values(by="arand")
    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', None):
        pass
        print(df)
    plt.figure()
    INSTS = [
        ["Ptr Chase", aptr_inst, "x"],
        ["Streaming", arand_inst, "."] , 
        ]
    weight_colors = [ 'blue','orange', 'purple']
    i = INSTS[0]
    inst_sel = (df["ADDR"] == (i[1]))
    climb = df[inst_sel]["arand"] == df[inst_sel]["aptr"]
    #inst_sel = inst_sel & ~climb
    df_inst1 = df[inst_sel].reset_index(drop=True)  
    i = INSTS[1]
    inst_sel = (df["ADDR"] == (i[1]))
    climb = df[inst_sel]["arand"] == df[inst_sel]["aptr"]
    #inst_sel = inst_sel & ~climb
    df_inst2 = df[inst_sel].reset_index(drop=True)  
    wc=0
    marker = 'x'#["x" if m else "." for m in climb] 
    # Compute climb AFTER reset_index so indices are aligned
    climb = df_inst1["arand"] == df_inst1["aptr"]  # boolean mask, index 0,1,2,...

    #"""
    wc = 0
    FIELDSSS = [  
        "AVG_INST_COST_160",
                #"MLP_WEIGHTED_AGG",
                           #MLP_BY_MEAN",
                           "TOTAL_TIME", "STALL_TIME"]

    
    impo = 1
    if impo % 2 == 0:
        for weight in FIELDSSS:
            _  = df_inst1
            
            for df_inst1    in [_, df_inst2]:
                color = weight_colors[wc]

                y1 = df_inst1[str(weight)] #/ df_inst2[str(weight)]
                y2 = (df_inst1[str(weight)+"80"] - df_inst1[str(weight)]) # / \ (df_inst2[str(weight)+"80"] - df_inst2[str(weight)])

                x = df_inst1["arand"]

                # Split into climb / non-climb and assign marker
                for mask, marker in [(climb, "x"), (~climb, "o")]:
                    marker = "x" if np.all(df_inst1 == _) else 'o'
                    # First scatter (raw ratio)
                    plt.scatter(x[mask], y1[mask],
                                label=weight if not mask.any() else "_nolegend_",
                                color=color, marker=marker)

                    # Second scatter (delta ratio)
                    plt.scatter(x[mask], y2[mask],
                                label="_nolegend_",
                                color=color, marker=marker, alpha=0.4)

            wc+=1
    #"""
    #"""
    for weight in FIELDSSS:
        #print(df[inst_sel], "DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD")
        plt.scatter(df_inst1["arand"], df_inst1[str(weight)]/df_inst2[str(weight)], 
                    #labelhh=weight + i[0],marker=i[2],
                    label=weight,
                    color=weight_colors[wc], 
                    marker=marker)
        plt.scatter(df_inst1["arand"], 
                    (df_inst1[str(weight)+"80"]-df_inst1[str(weight)] )/ (df_inst2[str(weight)+"80"]-df_inst2[str(weight)] )
                    , label=weight, color=weight_colors[wc], 
                    marker=marker)
                    
                    #marker='o')
        wc+=1
    #"""

    if False and True:
        for i in INSTS:
            inst_sel = (df["ADDR"] == (i[1]))
            climb = df[inst_sel]["arand"] == df[inst_sel]["aptr"]
            inst_sel = inst_sel & ~climb
            df_inst = df[inst_sel].reset_index(drop=True)  
            weight_colors = [ 'blue','orange', 'purple']
            wc = 0
            
            for n in np.unique(df_inst["arand"]):
                print(np.sum(df_inst["arand"] == n), "LENO")
            for weight in FIELDSSS:
                #print(df[inst_sel], "DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD")
                plt.scatter(df_inst["arand"], df_inst[str(weight)], 
                            #labelhh=weight + i[0],
                            marker=i[2],
                            color=weight_colors[wc] , #marker='.'
                            )
                if wc != -1:
                    plt.scatter(df[inst_sel]["arand"], df[inst_sel][str(weight)+"80"]-df[inst_sel][str(weight)] 
                                , color=weight_colors[wc], 
                                #marker=i[2],
                             marker='^'
                                )
                # one 

                #plt.plot(df[inst_sel][climb]["arand"], df[inst_sel][climb][str(weight)+"80"] - df[inst_sel][climb][str(weight)] , color=weight_colors[wc], marker=i[2])
                #climb =  ~climb
                #plt.plot(df[inst_sel][ climb]["arand"], df[inst_sel][climb][str(weight)+"80"] - df[inst_sel][climb][str(weight)] , color=weight_colors[wc], marker=i[2])


                wc+=1
                #df[inst_sel][str(weight)]-
                #print(df[inst_sel][str(weight)+"80"], "weightttttttttttttttyyy")

    #plt.plot(df["ADDR"] == str(aptr_inst))
    plt.title("Instruction weights in function of parameters")

    # --- LEGEND (3 separate sections) ---

    # Section 1: Access pattern (shapes)
    pattern_handles = [
        mlines.Line2D([], [], color='gray', marker='o', linestyle='None', markersize=9, label='Streaming'),
        mlines.Line2D([], [], color='gray', marker='x', linestyle='None', markersize=9, label='Ptr Chase'),
    ]

    # Section 2: Metric (colors)
    metric_handles = [
        mlines.Line2D([], [], color='blue',   marker='s', linestyle='None', markersize=9, label='MLP_BY_MEAN'),
        mlines.Line2D([], [], color='orange', marker='s', linestyle='None', markersize=9, label='TOTAL_TIME'),
        mlines.Line2D([], [], color='purple', marker='s', linestyle='None', markersize=9, label='STALL_TIME'),
    ]

    # Section 3: Measurement type (opacity)
    type_handles = [
        mlines.Line2D([], [], color='black', marker='s', linestyle='None', markersize=9, alpha=1.0, label='Raw'),
        mlines.Line2D([], [], color='black', marker='s', linestyle='None', markersize=9, alpha=0.3, label='Δ (vs baseline)'),
    ]

    # Combine with blank spacer titles using a "title-only" handle trick
    from matplotlib.patches import Patch
    spacer = Patch(color='none')  # invisible spacer

    all_handles = (
        [spacer] + pattern_handles +
        [spacer] + metric_handles +
        [spacer] + type_handles
    )
    all_labels = (
        ["── Access Pattern ──"] + ['Streaming', 'Ptr Chase'] +
        ["── Metric ──"] + ['MLP_BY_MEAN', 'TOTAL_TIME', 'STALL_TIME'] +
        ["── Measurement ──"] + ['Raw', 'Δ (vs baseline)']
    )
    """
    import matplotlib.lines as mlines
    # legend saying X is Ptr Chase
    # O is Streaming
    # and then , one color for Total Time, another for .... 
    # 1. Access Pattern Legend (Markers)
    pattern_handles = [
        mlines.Line2D([], [], color='black', marker='o', linestyle='None',
                    markersize=10, label='Streaming'),
        mlines.Line2D([], [], color='black', marker='x', linestyle='None',
                    markersize=10, label='Ptr Chase')
    ]

    # 2. Metric Legend (Colors)
    metric_handles = [
        mlines.Line2D([], [], color='blue', marker='s', linestyle='None', 
                    markersize=10, label='MLP_BY_MEAN'),
        mlines.Line2D([], [], color='orange', marker='s', linestyle='None', 
                    markersize=10, label='TOTAL_TIME'),
        mlines.Line2D([], [], color='purple', marker='s', linestyle='None', 
                    markersize=10, label='STALL_TIME')
    ]

    # Combine them or add separately
    # Option A: Single combined legend
    all_handles = pattern_handles + metric_handles
    plt.legend(handles=all_handles, loc='upper right', title="Legend")


    # Option B: Two separate legends (fancier)
    #leg1 = plt.legend(handles=pattern_handles, loc='upper left', title="Patterns")
    #plt.gca().add_artist(leg1) # Add first back manually
    #plt.legend(handles=metric_handles, loc='upper right', title="Metrics")

    #plt.title("
    """

    plt.legend(all_handles, all_labels, loc='upper right', framealpha=0.9)

    plt.xlabel("Number of reads")
    plt.ylabel("Weight")
    #plt.legend()
    plt.xlim(0,130)
    #plt.ylim(0)

    plt.savefig("./good_weights.svg")
    print("./good_weights.svg")
    print(df)
    print("bru")



    
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

    #print("Doing simple_weight")
    #exit(0I#)
    MULTI=True
    TARGET_BIN = "cg.D"
    TARGET_BIN = "sp.B"
    TARGET_BIN = None
    #MULTI=False
    if MULTI:
        RESULT_FOLDER="_mu"
    def simp(data,r):
        global writes
        EIGHT_MODE=False
        this_binary = data[r]['0']['bench'].split("/")[-1]
        print(this_binary, "THI SBINARY")
        if TARGET_BIN and TARGET_BIN not in this_binary:
            print("WOW")

            return
        benchset = data[r]['0']['benchset']
        if benchset != "npb_result-iter":
            print("skip")
        else:
            print("Found", TARGET_BIN)
            
        #exit(0)

        ignore_inst = True
        if not ignore_inst:
            i = load_inst_fields(data, r)
            if EIGHT_MODE:
                i = load_inst_fields(data, r, '80')   # i80 = ... instead of i = ... <--------- HOURS LOST !
        else:
            i = 0
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
        if not ignore_inst:
            for k in keys_used:
                print(len(i[k][SKIP_START:]),k, "lol")
                i[k] = i[k][SKIP_START:]
        
        agg_keys = ['count', 'address', 'accessBracket', 'stallCyclesMLPLoad',  'totalTime', 'stallTime', 'lastStallTime']
        agg = load_aggregate_fields(data, r)
        #agg = load_aggregate_fields(data, r, '80')
        for k in agg_keys:
            agg[k] = agg[k]

        if(len(load_inst_fields(data, r )['totalTime']) != len(load_inst_fields(data, r )['address']) ):
                        print("big mistake!!")
                        return
            
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

                if binary == this_binary: #and data[ru]['0']['benchset'] == data[r]['0']['benchset']:

                    try:
                        for k in keys_used: 
                            if(len(load_inst_fields(data, r )['totalTime']) != len(load_inst_fields(data, r )['address']) ):
                                            print("big mistake!!")
                                            raise Exception("Bad binary...")
                                            return
                            load_inst_fields(data, ru )[k][SKIP_START:] # test that it works
                        for k in agg_keys:
                            load_aggregate_fields(data, r)[k]
    
                        
                    except:
                        continue


                    rs.append(ru)
                    for k in keys_used:
                        try:

                            v =  np.concatenate((i[k], load_inst_fields(data, ru )[k][SKIP_START:]))
                            i[k] = v
                        except :
                            if not ignore_inst:
                                print("FAILED??")
                                exit(0)
                    for k in agg_keys:
                        v =  np.concatenate((agg[k], load_aggregate_fields(data, ru)[k]))
                        agg[k] = v
                        ####### WHY BREAK break
                
            print("Used", len(rs), "for ", data[r]['0']['bench'].split("/")[-1])
            if len(rs) == 1:
                pass
                #return
        else:
            return
            pass
            #return

        for k in keys_used:
            if not ignore_inst:
                print(len(i[k][SKIP_START:]),k)


        bio = data[r]['0']['bench']
        print('benchname is ', bio)
        if not ignore_inst:
            sel = i['totalTime'] != 0
            add = i['address'][sel]
        else: 
            sel = None
            add = None
        """
        sel = i['totalTime'] != 0
        add = i['address'][sel]
        """
        if not ignore_inst:
            print("Unique addresses:", np.unique(i['address']))
        #agg = load_aggregate_fields(data, r) ---- if multi is being used no need to use this.. 
        #agg = load_aggregate_fields(data, r,'80')
        #uniq_add = np.sort(np.unique(add[add < 140000000000335 ]))
        uniq_add = np.sort(np.unique(agg['address'][agg['address'] < 140000000000335 ]))
        #uniq_add = np.sort(np.unique(i['address'])) # np.unique(agg['address'][agg['address'] < 140000000000335 ]))
        if not ignore_inst:
            if( len(np.unique(i['address'])) != len(np.unique(agg['address']))):
                print("SADLY DIFF IS ", len(np.unique(i['address'])) - len(np.unique(agg['address'])), bio)



        # <------------------------------------------- WAS SKIPPING BECAUSE OF PARTIAL ( the original constrains were alliviated for higher iteration time!)
        j=0
        #print("uniq insts", len(uniq_add))
        #if len(uniq_add) > 50:
        #return
        out = "" 
        ints_1 = []
        ints_2 = []
        inst_priority = []
        import math 
        print( "Shared lib importance", np.sum(agg['count'][agg['address'] > 154139636 ]) / np.sum(agg['count']))
        nr_stores = 0; skipped = 0; actually_added = 0
        def process_inst(addr):
            sanity = []
            def _proccess_inst(addr, aggi):
                """
                sel = i['address'] == addr # & i['totalTime']  != 0
                """

                #print(aggi, "AGGI")
                sanity.append(aggi)
                if len(sanity ) != 1:
                    """
                    print(sanity[0] == sanity[-1])
                    if (sanity[0] == sanity[-1]):
                        print("EXODUS")
                        exit(0)
                    """
                    pass
                agg_sel = aggi['address'] == addr
                isStore = np.sum(aggi['totalTime'][agg_sel]) == 0

                if isStore:
                    pass
                    #nr_stores += 1

                def overloaded_cost(bracket):
                    hidden_cost = (aggi['address'] == addr) & (aggi['accessBracket'] <= bracket)
                    llc_misses = (aggi['address'] == addr) & (aggi['accessBracket'] > bracket)
                    n_llc_misses = np.sum(aggi['count'][llc_misses])
                    n_llc_misses = n_llc_misses if n_llc_misses != 0 else 1
                    n_hidden = np.sum(aggi['count'][llc_misses])
                    n_hidden = n_hidden if n_hidden != 0 else 1
                    return (np.sum(aggi['stallCyclesMLPLoad'][hidden_cost])/n_llc_misses) + np.sum(aggi['stallCyclesMLPLoad'][llc_misses]/n_llc_misses)
                def inst_cost(bracket, fun):
                    hidden_cost = (aggi['address'] == addr) & (aggi['accessBracket'] <= bracket)
                    llc_misses = (aggi['address'] == addr) & (aggi['accessBracket'] > bracket)
                    n_llc_misses = np.sum(aggi['count'][llc_misses])
                    n_llc_misses = n_llc_misses if n_llc_misses != 0 else 1
                    n_hidden = np.sum(aggi['count'][llc_misses])
                    n_hidden = n_hidden if n_hidden != 0 else 1
                    return fun(llc_misses, hidden_cost, n_llc_misses)


                average_inst_cost = overloaded_cost(4) # 68 
                average_inst_cost_160 = overloaded_cost(10) # 160 of latency

                aggCost =       np.sum((aggi['stallCyclesMLPLoad'][agg_sel]))/np.sum(aggi['count'][agg_sel])
                aggCost = np.where(aggCost == 0, 0, aggCost)
                aggStoreCost = np.sum((aggi['lastStallTime'][agg_sel]))/np.sum(aggi['count'])

                aggStoreCost = np.where(aggStoreCost == 0, 0, aggStoreCost)
                aggStoreCost = np.where(aggStoreCost > 700, 100, aggStoreCost)

                

                #delta_average
                #average_inst_cost_160 = overloaded_cost(11) # 160 of latency



                all_accesses = np.sum(aggi['count'][agg_sel])
                avg_cost_per_acc = np.sum(aggi['stallCyclesMLPLoad'][agg_sel])/all_accesses
                avg_cost_per_acc = np.where(all_accesses == 0 , 0, avg_cost_per_acc)

                _s = agg_sel & (aggi['accessBracket'] >= 4 ) & (aggi['count'] >= 1) # accessBracket must be != 0 , otherwise we will grab also store instructions ! 
                if not np.sum(_s):
                    mlpWeightedAgg = 0
                else:
                    mlpWeightedAgg = np.sum(aggi['stallCyclesMLPLoad'][_s])/np.sum(aggi['count'][_s]) 
                    mlpWeightedAgg = np.where(np.sum(aggi['count'][_s]) == 0, 0, mlpWeightedAgg)
                #= avg_cost_per_acc 


                # Store 
                #print('Did over cost')




                #j+=1
                def toi(n):
                    return int(n if not np.isnan(n) else 0)
                mlpWeighted = 0 if ignore_inst else toi(np.mean(i['stallCyclesMLPLoad'][sel])) # if not np.isnan(np.mean(i['stallCyclesMLPLoad'][sel])) else 0
                freq = sel.sum() if not ignore_inst else inst_cost(4, lambda llc_misses,hidden_cost,n_llc_misses: n_llc_misses)  

                totTime = inst_cost(4, lambda llc_misses,hidden_cost,n_llc_misses: int(np.sum(aggi['totalTime'][llc_misses]/n_llc_misses)) )
                if(totTime < 250):
                    pass
                    #print('sad..')
                    #exit()
                sTime = inst_cost(4, lambda llc_misses,hidden_cost,n_llc_misses: int(np.sum(aggi['stallTime'][llc_misses]/n_llc_misses)) )
                mlpWeighted = inst_cost(4, lambda llc_misses,hidden_cost,n_llc_misses: int(np.sum(aggi['stallCyclesMLPLoad'][llc_misses]/n_llc_misses)) )

                if not OLD_V4 and not ignore_inst:
                    exit(0)
                    mlpWeighted /= 1024
                    mlp_by_mean = toi(np.mean(i['stallTime'][sel]/(i['average_mlp'][sel]+1)))
                    hyper = i['stallTime'][sel] - (i['totalTime'][sel] - i['stallTime'][sel])
                    hyper = np.mean( np.where(hyper > 0, hyper, 0) ) 
                    #max(0, hyper)
                    hyper_thread_weight = toi(np.mean((hyper) /(i['average_mlp'][sel]+1))) # aka 2x stall time - total time
                    hyper_thread_no_mlp = toi(np.mean((hyper))) # aka 2x stall time - total time
                else:
                    mlp_by_mean = mlpWeighted
                    hyper_thread_weight = mlpWeighted
                    hyper_thread_no_mlp = mlpWeighted
                # int(np.mean(i['average_mlp'][sel])), "--->", 

                # IS BY AGG VERY DIFF THAN BY INST? 

                totTime = totTime if ignore_inst else np.mean(i['totalTime'][sel])
                sTime = sTime if ignore_inst else np.mean(i['stallTime'][sel])
                #toi(totTime) + toi(sTime)  + toi(aggCost) + toi(aggStoreCost) + toi(mlpWeighted) +
                bmw_metric = mlpWeightedAgg + aggStoreCost #aggCost 
                relevant_costs =  toi(mlp_by_mean) + toi(mlpWeightedAgg) + toi(bmw_metric)
                #print("beff")
                if relevant_costs == 0:
                    return ""
                    skipped += 1
                #print("RELEVANT COSTS", relevant_costs)
                def si(_):
                    return str(toi(_)) + " "
                lstall = toi(len(i['stallTime'][sel])) if not ignore_inst else 0    # makes no sense but okay
                res =  str(addr) + " " + \
                str(toi(totTime)) + " " + \
                str(toi(sTime)) + " " +\
                str(toi(mlpWeighted*100))  + " " + \
                str(mlp_by_mean) + " " + \
                str(hyper_thread_weight) + " " + \
                str(hyper_thread_no_mlp) + " " + \
                str(lstall) +  " " + \
                str(freq) + " " + \
                str(1) +  " " +  \
                str(toi(average_inst_cost))  +  " " + \
                str(toi(avg_cost_per_acc)) + " " + \
                str(toi(average_inst_cost_160)) +  " " + \
                si(aggStoreCost) + \
                si(mlpWeightedAgg)  +  \
                si(bmw_metric) + "\n"
                #actually_added += 1
                return res
                """
                ints_1.append(mlp_by_mean)
                ints_2.append(toi(mlp_by_mean/2))
                if mlpWeighted >= 1: 
                    inst_priority.append(2**(toi((mlp_by_mean)/(2))))

                else:
                    inst_priority.append(mlpWeighted)
                """

            #agg = load_aggregate_fields(data, r) from MULTI ple runs 
            #gu = load_global_fields(data, r)
            #slowdown = np.mean(load_global_fields(data, r, '80')['cycles'])*100/np.mean(load_global_fields(data, r, '0')['cycles'])
            agg80 = load_aggregate_fields(data, r, '80')  # was not passing the 80 here...
            #print(data[r]['80']['line'])
            try:
                zero = _proccess_inst(addr,agg)
                eighty = _proccess_inst(addr,agg80)
            except Exception as e:
                print(e)
                import traceback
                traceback.print_exc()
                return ""

            if not zero:
                return ""
            return zero[:-2] + " " + eighty
                



        from pathos.multiprocessing import Pool
        #from multiprocessing import Pool
        with Pool(30) as p:
            results = p.map(process_inst, uniq_add)
        """
        for addr in uniq_add:
            out += process_inst(addr)
        """
        actually_added = len(list(filter(lambda x: x != "", results)))
        out = "".join(results)


        
        header = (str(actually_added+1) + " ") * 10 + "\n"
        out = header + out
        bench = data[r]['0']['bench'].split("/")[-1]
        extra = ""
        extra += "_80" if EIGHT_MODE else ""
        if OLD_V4:
            extra += "_v4"
        extra += str(writes) + "-" + str(len(rs))
        writes+=1
        fname=f"{FIGS_FOLDER}/{RESULT_FOLDER}/{benchset}-{bench}{extra}"
        print("WRITE TO", fname, nr_stores)
        with open(fname, "w") as f:
                print(fname)
                f.write(out)
        return        
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
    return iterate_over_benches(data, simp)

    iterate_over_benches(data, simp ,
                         reject= lambda data,r :  all( [ a not in data[r]['0']['line'] for a in [ 
                             'synt'
                                                                                                # 'syn'
                                                                                                 ]])#'sp.B' ]] ) # sroms', 'pr', 'lbm','cact',  'bc']])
                         )  # 'bwaves'
    # 'bwaves' not in data[r]['0']['line'] and

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



    


def iterate_over_benches(data, function, reject=lambda x,y:False):
    global bench_nr
    global bench_name
    
    ok_runs = 0 
    okay_names = []
    okay_nrs =  []
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
        except Exception as e:
            print("Skipped run", list(data[r].values())[0]['benchnr'], e)
            continue

        try:

            if reject(data,r):
                raise Exception("Unwanted bench")

            function(data, r)
            ok_runs += 1
            okay_names.append(bench_name)
            okay_nrs.append(bench_nr) 
            if ok_runs > TRACE_MODE:
                break

        except Exception as e:
            bad_runs += 1
            print(e)
            print(e)
            print(e)
            
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
                    print("\n\n\n")
                else:
                    print("ITERATE_FAILED Error", e)
                print(f"---  {str(last_error)} x {bad_runs} ({ok_runs+bad_runs}/{total_runs})", end='\r')
                last_error = e
            continue
    print(f"ITERATE ENDED, ok runs: {ok_runs}, bad runs: {bad_runs}, total: {ok_runs+bad_runs}")
    print('OKAY_NAMES', okay_names)
    print('OKAY_NRs', okay_nrs)
    print('Unique names:', len(np.unique(np.array(okay_names))), "Total: ", len(np.array(okay_names)))

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
            all_data_weight = winsorize(all_data_weight, limits=[0.1, 0.1])
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



############################################################################ 
def load_bench_data():
    global inst_types
    global DATASET_S
    global OVERRIDE_PID_ONLY
    global OVERRIDE_RUN_FOLDER
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

    #DATASET_1 
    # 2 all the ones with AccTime and Inst soar and MLP implementation
    # 3 --- most recent run, with all benchmarks, store implemented
    DATASET=3
    DATASET=2
    DATASET=3
    DATASET=1
    DATASET=3
    DATASET=1
    DATASET=1 # only all older than day 7
    DATASET=5
    DATASET=4
    DATASET=1
    DATASET=4
    DATASET=4

    DATASET=0

    DATASET=4
    DATASET=1
    if OVERRIDE_DATASET:
        DATASET=OVERRIDE_DATASET

    GET_BIGGEST=True
    GET_BIG_DATASET = True

    GET_BIG_DATASET = False ########### CHANGE
    GET_BIGGEST=False
    DATASET_S = "__" + str(DATASET) + "_SUS_"
    
    def __l(run_meta):
        old_runs = 0
        new_runs = 0
        kkk = 0
        with open(run_meta, 'r') as file:
            for line in file:
                all_lines.append(line)


            for line in all_lines[GEM5_PIDS_TAIL:]:
                if len(line.split(" ")) < 2:
                    continue
                is_new_run = False
                try:
                    _  = build_run_data(line)
                    _['line'] = line
                    try:
                        __ = int(_['pid'])
                    except:
                        print(_['pid'], "FAIL TO CONVERT TO INT", line)
                        continue
                    date =  int(line.split(" ")[-1])
                    december_day_7_2025_mid_night =  1765065600 # WHEN NEW BATCH WITH SOAR INST 
                    december_store_implemented = 1765969399
                                                # 765247870
                                                #1765970398
                                                #1765315488
                                                #1765315104
                                                #1765010844
                                                 #1764920331
                    if DATASET == 5:
                        if (date -december_day_7_2025_mid_night < 0):
                            continue

                    if DATASET == 4:

                        #if (date - december_day_7_2025_mid_night ) < 0:
                        if (date - december_store_implemented) < 0:
                            continue
                    if DATASET == 1 and (date - december_store_implemented) >= 0:
                        continue
                    """
                    if (date - december_store_implemented) > 0:
                        if DATASET == 1:
                            continue
                        if DATASET == 2:
                            continue # ONLY ALLOW PASS THOROUGH OF THE RUNS SHOWN IN DISCROD REGARDING SOAR INST
                    else:
                        if DATASET == 3: # se é negativo e é o 3 SKIP (i.e. ignora antigos)
                            continue

                        
                    if (date - december_day_7_2025_mid_night) < 0:  
                        if DATASET == 2: ######## SE é suposto ter o SOAR, skip!
                            continue
                        old_runs +=1
                            
                        if SOURCE_INST_DATA == OFULL:
                            #continue # ingore old RUNS
                            pass
                    else:
                        new_runs += 1
                        is_new_run = True
                        if DATASET == 1: # se é > 0, é mt recente.
                            continue
                    """
                except Exception as e:
                    print(e)
                    print(line)
                    continue

                r_number = _['benchnr']
                if not r_number in all_data:
                    all_data[r_number] = {}

                #print(line, "PID", "pid", line.split("pid: ")[1].split(" ")[0].strip(), "OOOOOO")
                if _['increase'] in all_data[r_number]: 
                    print("WARNING: Duplicate increase", line)
                    print("huuu")
                    if not GET_BIG_DATASET:
                        all_data[r_number][_['increase']] = _ 
                        continue
                    #continue

                    #if not is_new_run:
                    #    continue
                    try:
                        g = load_global_fields({r_number: {_['increase'] : _}}, r_number, _['increase'])
                        go = (g['currentCycle'])
                    except:
                        continue
                    try:
                        g_old = load_global_fields(all_data, r_number, _['increase'])
                        #all_data[r_number]
                        print(len(g_old['currentCycle']) - len(g['currentCycle']))
                        kkk +=1
                        #if kkk == 20: break

                        if (len(g_old['currentCycle']) - len(g['currentCycle']) > 0):
                            #and not is_new_run:
                            print("Is nto new run..")
                            continue
                        
                        #print(g['currentCycle'])
                        #print("done")
                        #exit(0)

                        #glob_80 = load_global_fields(data_v4, r, "80", PID_ONLY=True, run_folder=RUN_DATA_FOLDER_V4)
                    except Exception as e:
                        print("RIP",e)
                        #exit(0)
                        #continue
                        #print('blo')
                        #print(e)
                        #continue
                    print("i")
                    #exit(0)
                

                all_data[r_number][_['increase']] = _ 
                print("OLD_TRACK", old_runs, new_runs)
                #def get_run_name(run):
                #    return os.path.basename(run['0']['bench']).split('.')[0]

                #_['global'] = load_struct(GlobalStatsss,glob.glob(f"/mnt/nas/inesc/ist196723/osdi26/results_gem5/global_{_['pid']}_{_['host']}*.bin")[0])
                #_['inst'] = load_struct(InstructionData,glob.glob(f"/mnt/nas/inesc/ist196723/osdi26/results_gem5/aggregate_{_['pid']}_{_['host']}*.bin")[0])
                #_['final'] = load_struct(FinalMetrics,glob.glob(f"/mnt/nas/inesc/ist196723/osdi26/results_gem5/inst_{_['pid']}_{_['host']}*.bin")[0])
                    #f"/mnt/nas/inesc/ist196723/osdi26/results_gem5/output_{rdata["host"]}.bin")


    if DATASET == 0:
        __l("/mnt/nas/inesc/ist196723/osdi26/v4/results_gem5/gem5_pids.txt")
        RUN_DATA_FOLDER="/mnt/nas/inesc/ist196723/osdi26/v4/results_gem5"
        OVERRIDE_PID_ONLY=True
        OVERRIDE_RUN_FOLDER="/mnt/nas/inesc/ist196723/osdi26/v4/results_gem5"
    else:
        __l(run_meta)
    for f in ['gem5_pids_before_modify_big_manuals', 'gem5_pids.txt_about_to_clean' ]:
        continue
        __l(f)
    import traceback
    traceback.print_exc()
    return all_data

import numpy as np
import matplotlib.pyplot as plt





def get_field(run, struct,field_name, type_, convolve_skip=False, PID_ONLY=False, run_folder=None):
    if run_folder is None:
        run_folder = RUN_DATA_FOLDER
    if OVERRIDE_RUN_FOLDER:
        run_folder = OVERRIDE_RUN_FOLDER
    if (run['pid'], struct, field_name) in cached_fields:
        return cached_fields[(run['pid'], struct, field_name)]
    if PID_ONLY or OVERRIDE_PID_ONLY:
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
    field_path = f"{folder_chosen}/_{struct}_{field_name}_{run['pid']}.txt"
    if not os.path.exists(field_path):
        raise FileNotFoundError(f"Field file not found: {field_path} (pid={run['pid']}, struct={struct}, field={field_name})")
    arr =  np.fromfile(field_path, dtype=type_)
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
#slowdown/l3stall_cyles = 1/(a+b/AOL)
def obtain_soar_mlp_aware_slowdown(unadjusted, AOL, out,ALL):
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
    
    target = ALL['Slow Cycles/Fast LLC Stall Cycles']
    def model(AOL, a, b, unadjusted):
        #return unadjusted * 1.0 / (a + b / AOL)
        return 1.0 / (a + b / AOL)

    # We need a wrapper that takes AOL and parameters a, b, then uses unadj inside
    def fit_func(AOL, a, b):
        return model(AOL, a, b, unadjusted) # in this fitting.. where is the slow cycles?? 


    # Initial guesses for a and b
    initial_guess = [0.78, 0.231]

    # Perform the curve fit
    popt, pcov = curve_fit(fit_func, AOL, target, p0=initial_guess)

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
    #exit(0)
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

from sklearn.linear_model import RANSACRegressor
from sklearn.base import BaseEstimator, RegressorMixin
UNunadjusted_slowdown= None

class NonLinearModel(BaseEstimator, RegressorMixin):
    """Wrapper for non-linear model to work with sklearn's RANSACRegressor"""
    
    def __init__(self):
        self.a_ = None
        self.b_ = None
    
    def fit(self, X, y):
        # X is AOL values, y is real values
        if MINIMIZE_SLOW_ERROR:
            def model(AOL, a, b):
                return AOL[:,0] / (a + b / AOL[:,1])

        else:
            def model(AOL, a, b):
                return 1.0 / (a + b / AOL)
        
        # Fit the model
        from scipy.optimize import curve_fit
        try:
            popt, _ = curve_fit(model, X.ravel(), y, 
                               p0=[24.67, 0.87],
                               bounds=[(-1, -1), (50 , 50)],
                               maxfev=5000)
            self.a_, self.b_ = popt
        except Exception as e:
            print(e)
            self.a_, self.b_ = 24.67, 0.87
        
        return self
    
    def predict(self, X):
        if self.a_ is None:
            raise ValueError("Model not fitted")
        return 1.0 / (self.a_ + self.b_ / X.ravel())

def ransac_sklearn(AOL, real, **kwargs):
    """Use sklearn's RANSACRegressor with custom non-linear model"""
    
    X = AOL.reshape(-1, 1)  # sklearn expects 2D array
    
    model = NonLinearModel()
    ransac = RANSACRegressor(
        estimator=model,
        min_samples=max(14, int(0.2*len(AOL))),
        max_trials=1000,
        random_state=42,
        **kwargs
    )
    
    ransac.fit(X, real)
    
    inlier_mask = ransac.inlier_mask_
    predicted = ransac.predict(X)
    
    print(f"RANSAC-sklearn: {np.sum(inlier_mask)}/{len(AOL)} inliers")
    print(f"  Parameters: a={ransac.estimator_.a_:.6f}, b={ransac.estimator_.b_:.6f}")
    
    return ransac.estimator_.a_, ransac.estimator_.b_, inlier_mask, predicted

MINIMIZE_SLOW_ERROR = True
def obtain_soar_mlp_aware_slowdown(unadjusted, AOL, out, weight, ALL):
    global OPTIMAL_A
    global OPTIMAL_B
    global MINIMIZE_SLOW_ERROR
    global UNunadjusted_slowdown
    import numpy as np
    from scipy.optimize import curve_fit, differential_evolution, shgo
    # Example data arrays; replace these with your actual data
    # AOL: array of AOL values
    # unadj: array of unadjusted_slowdown values
    # real: array of real_slow_down values
    MINIMIZE_SLOW_ERROR=False
    if MINIMIZE_SLOW_ERROR:
        real = out
        UNunadjusted_slowdown = unadjusted
        x =  np.column_stack([ UNunadjusted_slowdown,AOL])
    else:
        #real = ALL['Slow Cycles/Fast LLC Stall Cycles']
        real = ALL['Slow Cycles/Mem Stall Cycles']
        x = AOL
    # Define the fitting function:
    # f(AOL, a, b) = unadjusted_slowdown * 1 / (a + b / AOL)

    def model(AOL, a, b, unadjusted):
        #return unadjusted * 1.0 / (a + b / AOL)
        return  1.0 / (a + b / AOL)
    # We need a wrapper that takes AOL and parameters a, b, then uses unadj inside
    def fit_func(AOL, a, b):
        return model(AOL, a, b, unadjusted)
    
    # Objective function for global optimization
    def objective(params):
        a, b = params
        predicted = fit_func(AOL, a, b)
        return np.sum((predicted - real) ** 2)
    # Initial guesses for a and b
    initial_guess = [24.67, 0.87]
    
    # Bounds for parameters
    bounds = [(-1000, -1000), (1000, 1000)]

    a=2.838233; b=10.074349
    fitted_real = 1/(a + b/AOL) 
    residuals = np.abs(real - fitted_real)
    # Auto-calculate threshold
    threshold = np.median(residuals) + 3.5 * np.median(np.abs(residuals - np.median(residuals)))
    a_opt, b_opt, inlier_mask, predicted = ransac_sklearn(x, real, residual_threshold= threshold) # , 
    print("Ranksac", a_opt, b_opt)
    # nr of outliers
    print("Outliers", np.sum(~inlier_mask))
    #exit(0)

    
    # Perform the curve fit with increased maxfev
    popt, pcov = curve_fit(fit_func, AOL, real, p0=initial_guess, bounds=bounds, maxfev=100000)
    a_opt, b_opt = popt
    print('OPTIMAL A AND B (curve_fit):', a_opt, b_opt)
    
    # Global optimization using differential_evolution
    result_de = differential_evolution(objective, bounds)
    print('OPTIMAL A AND B (differential_evolution):', result_de.x[0], result_de.x[1])
    
    # Global optimization using shgo
    result_shgo = shgo(objective, bounds)
    
    # Extract the optimal parameters
    # Compute standard deviations (uncertainties) of the parameters
    a_err, b_err = np.sqrt(np.diag(pcov))
    #print(f"Fitted parameters:")
    #print(f" a = {a_opt:.6f} ± {a_err:.6f}")
    #print(f" b = {b_opt:.6f} ± {b_err:.6f}")
    # Optional: compute the fitted real_slow_down values
    fitted_real = fit_func(AOL, a_opt, b_opt)
    print('OPTIMAL A AND B (curve_fit):', a_opt, b_opt)
    print('OPTIMAL A AND B (differential_evolution):', result_de.x[0], result_de.x[1])
    print('OPTIMAL A AND B (shgo):', result_shgo.x[0], result_shgo.x[1])

    OPTIMAL_A = a_opt
    OPTIMAL_B = b_opt
    def calc_error(a,b):
        pass
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

"""
python3 bin/python_parser.py "viz_accesses_over_time()"
"""
def viz_accesses_over_time():
    file = "perf.txt"
    file ="/mnt/nas/inesc/ist196723/latency_benchmark/tests_syn/plot_time_math/sinos/perf.txt"
    return
    
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
    print("about ot do.")
    plt.figure(figsize=(14, 8))
    plt.imshow(heatmap.T, aspect='auto', origin='lower', 
               #norm=LogNorm(vmin=heatmap[heatmap>0].min(), vmax=heatmap.max()),
               #norm=LogNorm(vmin=heatmap[heatmap>0].min(), vmax=heatmap.max()),
               cmap='YlOrRd')
    plt.xlabel('Time (μs)')
    plt.ylabel('Page Number')
    plt.title('L3 Cache Miss Heatmap Over Time')
    plt.colorbar(label='Miss Count')
    plt.tight_layout()
    plt.savefig('access_heatmap.png', dpi=150)
    # plot CDF of total nr of accesses per page 
    plt.figure(figsize=(14, 8))
    plt.plot(np.sort(heatmap.sum(axis=0)))
    plt.xlabel('Page Number')
    plt.ylabel('Total Access Count')
    plt.title('Total Access Count per Page')
    plt.tight_layout()
    plt.savefig('access_count.png', dpi=150)
    print("saved .. to acc")



"""
sudo perf record -c 997 -e mem_load_retired.l3_miss:uppp -d --  /mnt/nas/inesc/ist196723/latency_benchmark/tests_syn/plot_time_math/outa 0 0 4 100 0 100 100 200 10000000 2 0 0 0 000000 0 splitted optimal
sudo perf script -i ./perf.data > perf.txt
"""
extra=""
file = "perf.txt"
file ="/mnt/nas/inesc/ist196723/latency_benchmark/tests_syn/plot_time_math/sinos/perf.txt"
def vio(e, file_input):
    global extra, file
    file = file_input
    extra = e
    viz_accesses_over_time()


def viz_accesses_over_time():
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    from matplotlib.colors import LogNorm
    
    timestamps = []
    addresses = []
    
    with open(file, 'r') as f:
        for line in f:
            parts = line.split()
            # read all parts of 5 asnumber base 16
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
                """
                for i in range(timestamp_idx + 3, min(timestamp_idx + 6, len(parts))):
                    if parts[i].startswith(('7f', '55', '40', '3f')):  # Common address ranges
                        try:
                            addr = int(parts[i], 16)
                            if addr > 0:
                                address_idx = i
                                break
                        except ValueError:
                            continue
                
                """
                try:
                    addr = int(parts[5], 16)
                    if addr > 0:
                        address_idx = 5
                except ValueError:
                    pass
                if address_idx is None or not parts[address_idx].startswith('7f'):
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
    
    # keep only the first 10% of the page indices
    percent = 0.3
    page_indices = page_indices[:int(int(len(page_indices) * percent))]
    timestamps = timestamps[:int(int(len(timestamps) * percent))]

    # Create
    # Create 2D histogram
    timestamps = timestamps - timestamps.min()
    n_time_bins = int(timestamps[-1]) #min(100, len(np.unique(timestamps)))
    n_page_bins = int(int(page_indices.max())) #/100000)
    
    print(f"Creating heatmap: {n_time_bins} time bins x {n_page_bins} page bins")
    # save all of this as numpy array
    """
    np.save("timestamps.npy", timestamps)
    np.save("addresses.npy", addresses)
    np.save("page_indices.npy", page_indices)
    np.save("heatmap.npy", heatmap)
    np.save("time_edges.npy", time_edges)
    np.save("page_edges.npy", page_edges)
    """
    
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
    plt.ylim(0,50)
    plt.xlim(60,180)
    plt.xlabel('Time (seconds)')
    plt.ylabel('Page Number')
    plt.title('L3 Cache Miss Heatmap Over Time')
    plt.colorbar(label='Miss Count')
    plt.tight_layout()
    plt.savefig(FIGS_FOLDER + "/" +  'access_heatmap' + extra + '.png', dpi=150)
    #plt.show()
    
    print(f"\nSummary:")
    print(f"  Total L3 misses: {len(addresses)}")
    print(f"  Unique pages: {len(np.unique(page_indices))}")
    print(f"  Heatmap saved to: access_heatmap.png")

    plt.figure(figsize=(14, 8))
    plt.plot(np.sort(heatmap.sum(axis=0)))
    plt.xlabel('Page Number')
    plt.ylabel('Total Access Count')
    plt.title('Total Access Count per Page')
    plt.tight_layout()
    plt.savefig(FIGS_FOLDER + "/" +  'access_count' + extra + '.png', dpi=150)
    plt.close()
    print("saved .. to acc")



    


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
SKIP_REGRESS = False

def should_skip_key(k):
    return False
    if len(SET_KEYS):
        print("GOING TO SKIP ACCORDING TO SET_KEYS")
        return not any([ i in k for i in SET_KEYS])

        
    s =  "SOAR" in k
    if "LLC" in k and "%" in k or s:
        return False
    return True
    if "MLP" in k or "Soar"  in k or "SOAR" in k:
        return False
    if "Squashed" in k or "Active" in k:
        return False
    return True
    if "Soar" not in k:
        return True
    return False
def should_scatter(k):
    return False

def should_load_cached():
    return False


"""
rm -r ~/deskk/MATRICAS
mkdir ~/deskk/MATRICAS
mkdir ~/deskk/MATRICAS/user
mkdir ~/deskk/MATRICAS/pebs
mkdir ~/deskk/MATRICAS/tpp
mkdir ~/deskk/MATRICAS/STALL
mkdir ~/deskk/MATRICAS/average_mlp
scp ist196723@10.15.0.17:/home/ist196723/nas/osdi26/_finos/fii/*user* ~/deskk/MATRICAS/user & 
scp ist196723@10.15.0.17:/home/ist196723/nas/osdi26/_finos/fii/*PEBS* ~/deskk/MATRICAS/pebs &
scp ist196723@10.15.0.17:/home/ist196723/nas/osdi26/_finos/fii/*TPP* ~/deskk/MATRICAS/tpp & 
scp ist196723@10.15.0.17:/home/ist196723/nas/osdi26/_finos/fii/*STALL* ~/deskk/MATRICAS/STALL &
rm ~/deskk/MATRICAS/*/*average*mlp*
scp ist196723@10.15.0.17:/home/ist196723/nas/osdi26/_finos/fii/*average*mlp* ~/deskk/MATRICAS/average_mlp &
"""

def mode_bars():
    global NORM
    global BY_MOMENT
    global INTENSITY_metric
    BY_MOMENT = False

SET_KEYS = []
DEST=""
SLOWP = 'Slow down (%)'
OTHER_X_KEYS = [SLOWP]
def mode_soar():
    global SKIP_REGRESS
    global SET_KEYS
    global INTENSITY_metric
    global DEST
    global NORM
    global OTHER_X_KEYS
    global BY_MOMENT
    BY_MOMENT = False
    NORM = "user"
    SET_KEYS = ["∆ Core Stalls Cycles", "Core Stalls Cycles (during LLC misses)" ,"bound", "Soar",] # "Soar", "SOAR",
    SKIP_REGRESS = False
    INTENSITY_metric = None
    DEST = "NU/"


    BY_MOMENT = False
    SET_KEYS = ["Soar"]
    OTHER_X_KEYS = [SLOWP]

def mode_global():
    global SKIP_REGRESS
    global SET_KEYS
    global INTENSITY_metric
    global BY_MOMENT
    global DEST
    global NORM
    global OTHER_X_KEYS
    BY_MOMENT = True
    BY_MOMENT = False
    NORM = "user"
    SET_KEYS = [ "bound", "Memory", "Squash","Soar", "SOAR"]
    SKIP_REGRESS = True
    INTENSITY_metric = None
    DEST = "NU/"
    #OTHER_X_KEYS = ['Absolute increase in cycles']
    OTHER_X_KEYS = [SLOWP]
    return

    
def mode_squash():
    global SKIP_REGRESS
    global SET_KEYS
    global INTENSITY_metric
    global BY_MOMENT
    global DEST
    global NORM
    global OTHER_X_KEYS
    BY_MOMENT = True
    BY_MOMENT = False
    NORM = "NONE"
    SET_KEYS = [ "bound", "Memory", "Squash","Soar", "SOAR"]
    SKIP_REGRESS = True
    INTENSITY_metric = None
    DEST = "NU/"
    #OTHER_X_KEYS = ['Absolute increase in cycles']
    OTHER_X_KEYS = [SLOWP]

ABS='Absolute increase in cycles'


OFULL="OLD_COMPLETE"
SOURCE_INST_DATA=OFULL
def mode_cores():
    global SKIP_REGRESS
    global SET_KEYS
    global INTENSITY_metric
    global BY_MOMENT
    global DEST
    global NORM
    global OTHER_X_KEYS
    BY_MOMENT = True
    #SET_KEYS = ["Instruction Stall cycles/MLP", "non_memory_stalls"] #"bound", "Memory", "Squash","Soar", "SOAR"]
    SET_KEYS= [ "Core", "Squashed","Active" ,"∆ Instruction Stall cycles/MLP"]


    SKIP_REGRESS = True
    INTENSITY_metric = None
    DEST = "NU/"
    NORM = "user"
    OTHER_X_KEYS = [SLOWP]

    NORM = "NONE"
    OTHER_X_KEYS = [ABS]

    SET_KEYS= [ "Core"]
    BY_MOMENT = True
    NORM = "user"
    OTHER_X_KEYS = [SLOWP]

    SET_KEYS= [ "Instruction"]
    SET_KEYS= [ "Instruction"]
    BY_MOMENT = True
    NORM = "NONE"
    OTHER_X_KEYS = [ABS]
    NORM = "user"
    OTHER_X_KEYS = [SLOWP]

    SET_KEYS= [ "Instruction"]
    NORM = "user"
    OTHER_X_KEYS = [SLOWP]
    

POINT_VARIABLES = {}

def robust_regress(k, all_together, REGRESS_MODE=SLOWP):
                #def r_errors(k, REGRESS_MODE=SLOWP):
                    #x_key = "Absolute increase in cycles"
                    r = all_together[k]
                    #if k.endswith("Instruction Stall Cycles") or k.endswith("Instruction Stall cycles"):
                    if REGRESS_MODE == SLOWP:
                        x_axis = all_together[SLOWP]
                    else:
                        x_axis = all_together[ABS]
                    y_axis = all_together[k]

                    min_x = np.min(x_axis)
                    max_x = np.max(x_axis)
                    bin_sizex = (max_x - min_x)*0.99999

                    min_y = np.min(all_together[k])
                    max_y = np.max(all_together[k])
                    bin_sizey = (max_y - min_y)*0.99999
                    # discretize results to the bins
                    new_x = ( (x_axis // bin_sizex) *bin_sizex) + bin_sizex*0.5
                    new_y = (y_axis // bin_sizey)*bin_sizey + bin_sizey*0.5
                    from scipy.stats.mstats import winsorize
                    new_x = x_axis # winsorize(x_axis, limits=[0.01, 0.01])
                    new_y = winsorize(y_axis, limits=[0.01, 0.01])
                    def obt_limo(a):
                        min_a = np.min(a)
                        max_a = np.max(a)
                        dif = max_a - min_a
                        percent_scale = a/dif
                        return percent_scale
                    #new_x = obt_limo(new_x)
                    #new_y = obt_limo(new_y)
                    #new_x = x_axis
                    #new_y = y_axis
                    # for each percent in percent scale, average 
                        
                        # Counting all instructions stall cycles leads to severe over count. However, when MLP is con
                        # 
                        # Instruction stall cycles is WORST than LLC count. Despite providing mroe informtion, the overlaps are bad.
                        # 





                    

                    SCALE=1
                    try:
                        regress, residuals, rank, singular_values, rcond  = np.polyfit(new_y*SCALE, new_x, 1, full=True)
                        correlation, pvalue = np.corrcoef(new_y*SCALE, new_x)
                    except Exception as e:
                        print(e)
                        raise Exception("Blackkk")
                    # calculate results from poly
                    ru = np.array((new_y*SCALE))* regress[0]  + regress[1]
                    #ru = np.clip(ru, -0.30,300)
                    BY_MEAN = len(new_x)
                    BY_MEAN = 1
                    ru = np.abs( (ru - new_x)/BY_MEAN) # **2 <-- not squared.. 
                    if correlation[0] > 1:
                        print("WHY?=")
                        exit(0)
                    out1,out2,out3 = new_y*SCALE,correlation[1], ru

                    SSE = np.sum( (ru - new_x)**2 )
                    #SSE = residuals[0]
                    SSE = np.sum( np.abs((ru - new_x)) )
                    #MSE = SSE / len(x)  # Mean Squared Error
                    #RMSE = np.sqrt(MSE) /SCALE

                    # cat regress_errors  | grep REGRESS | awk '{print $NF " " $0 }' | sort  -n | grep "%"
                    #print("REGRESS ERROR ", k, x_key, SSE/SCALE, "MSE", MSE/SCALE, "RMSE", RMSE, SSE)
                    return out1,out2,out3

def find_outlier():
    global SKIP_REGRESS
    global SET_KEYS
    global INTENSITY_metric
    global DEST
    global NORM
    global OTHER_X_KEYS
    #NORM = "active"
    NORM="user"
    BY_MOMENT = False
    #INTENSITY_metric = "commitedL3Misses"
    SET_KEYS = ['non_memory_stalls']   #'Instruction Stall cycles/MLP' , "Active", "Squash" ]
    #globy['RatioStoreLLC'] = aggregate_op(glob_0['commitedL3Misses'][:last_idx])/aggregate_op(glob_0['commitedStores'][:last_idx]) 
    OTHER_X_KEYS = ['Slow down (%)'    ]
    # [           '∆ Active cycles']
    
# get_last_idx_agg
def moment_metric():
    global NORM
    global BY_MOMENT
    global INTENSITY_metric
    global OTHER_X_KEYS
    BY_MOMENT = True

    NORM = "NONE"

    #NORM = "NONE"
    OTHER_X_KEYS = [ABS]


    NORM = "user"
    OTHER_X_KEYS = [SLOWP]

    #NORM = "NONE"
    
    #OTHER_X_KEYS = [ABS]

    metric_eval()

    BY_MOMENT = True
    NORM = "NONE"
    metric_eval()

    exit(0)

def erview():
    global ERROR_VIEW
    global NORM
    global BY_MOMENT
    global INTENSITY_metric
    global OTHER_X_KEYS
    global SHOULD_PLOT_KEY
    global OVERRIDE_DATASET
    ERROR_VIEW = True
    OTHER_X_KEYS= [SLOWP]
    BY_MOMENT = True
    #SHOULD_PLOT_KEY = lambda x : all(v in x for v in ['LLC','change'])
    SHOULD_PLOT_KEY = lambda x : all(v in x for v in ['Core Stall']) # ['Core Memory bound'])

    #for i in [4]:
    NORM = "user"
    #NORM = "NONE"
    metric_eval()
    BY_MOMENT = False
    metric_eval()
    exit(0)
def soari():
    global NORM
    global BY_MOMENT
    global INTENSITY_metric
    global OTHER_X_KEYS
    global SHOULD_PLOT_KEY
    global OVERRIDE_DATASET
    OTHER_X_KEYS= [SLOWP]
    BY_MOMENT = True
    SHOULD_PLOT_KEY = lambda x : all(v in x for v in ['LLC','change'])
    #SHOULD_PLOT_KEY = lambda x : all(v in x for v in ['SOAR', 'LLC']) #['Core Store'])

    #for i in [4]:
    NORM = "user"
    #NORM = "NONE"
    metric_eval()
    BY_MOMENT = False
    metric_eval()

    exit(0)


def stori():
    global NORM
    global BY_MOMENT
    global INTENSITY_metric
    global OTHER_X_KEYS
    global SHOULD_PLOT_KEY
    global OVERRIDE_DATASET
    OTHER_X_KEYS= [SLOWP]
    BY_MOMENT = True
    #SHOULD_PLOT_KEY = lambda x : all(v in x for v in ['LLC','change'])
    SHOULD_PLOT_KEY = lambda x : all(v in x for v in ['Load bound']) #['Core Store'])

    #for i in [4]:
    NORM = "user"
    #NORM = "NONE"
    metric_eval()
    BY_MOMENT = False
    metric_eval()
    exit(0)

def mmoments():
    global NORM
    global BY_MOMENT
    global INTENSITY_metric
    global OTHER_X_KEYS
    global SHOULD_PLOT_KEY
    global OVERRIDE_DATASET
    global BY_HOT
    BY_HOT=False
    OTHER_X_KEYS= ['Average LLC MLP', 'Average MLP', SLOWP]
    OTHER_X_KEYS= [ SLOWP]
    BY_MOMENT = False
    SHOULD_PLOT_KEY = lambda x : "ransac" in x # True # all(v in x for v in ["MLP", "Average"])
        #all(v in x for v in ["LLC change", "Average"])
                                     #['non_memory','stalledCyclesWithMemRequests'])
                                     #['LLC','change'])

    #for i in [4, #1]: ]:
    NORM = "user"
    metric_eval()
    BY_MOMENT = True
    metric_eval()
    exit(0)

    

    NORM = "NONE"
    #NORM = "NONE"
    metric_eval()
    NORM = "user"
    metric_eval()
    BY_MOMENT = True
    metric_eval()
    NORM = "NONE"
    metric_eval()


    

def point_metric():
    global NORM
    global BY_MOMENT
    global INTENSITY_metric
    global OTHER_X_KEYS
    BY_MOMENT = False
    NORM = "user"

    OTHER_X_KEYS = ['average_mlp']
    NORM = "NONE"
    NORM = "user"
    OTHER_X_KEYS = [ABS]
    OTHER_X_KEYS = [SLOWP]

    metric_eval()
    exit(0)


def metric_evalit():
    global NORM
    global BY_MOMENT
    global INTENSITY_metric
    global OTHER_X_KEYS

    for b in [     True, False]:
        BY_MOMENT = b
        for i in ['average_mlp', 'average_l3mlp', None ]: # 'average_l3mlp', 'average_mlp']: #   'average_l3mlp', None, 'average_mlp']: # None,, 'average_mlp']: # None,
            INTENSITY_metric = i
            print("intensity is", i, INTENSITY_metric)
            #for n in ["NONE", "user", "fast_cycles", "NONE"] :  #"user"]: #"NONE",  "user",]: # "PEBS","TPP", "STALL" ] : #  , "TPP" ]: #, "TPP", "PEBS"]:
            for n in [ "user", "NONE"]: # "fast_cycles", "NONE", "PEBS"] :  #"user"]: #"NONE",  "user",]: # "PEBS","TPP", "STALL" ] : #  , "TPP" ]: #, "TPP", "PEBS"]:
                NORM = n
                #find_outlier()
                #mode_squash()
                #mode_global()
                #mode_soar()
                #mode_cores()

                metric_eval()
                exit(0)
                print("intensity is", i, INTENSITY_metric)

def get_color(data,r):
    benchname = data[r]['0']['bench']
    benchsets =  [ "cpu2017", "gapbs",   "NPB-CPP",            ] # ]/apps",   "pkgs/kernels" , "pkgs/splash"]
    benchsetsHUMAN =  [ "CPU2017", "GAPBS",   "NPB", "Others"] # ,   "PARSEC-kernels" , "PARSEC-splash"]
    colors = ['blue', 'orange', 'purple',  'grey']
    for i in range(len(benchsets)):
        if benchname in benchsets[i]:
            return colors[i]
    return colors[-1]
def freq_stall():
    freqs = []
    totals = []
    colors = []
    def d(data,r):
        #ag80 =  load_aggregate_fields(data,r,'80')
        ag0 =  load_aggregate_fields(data,r)
        inst = np.unique(ag0['address'])
        benchname = data[r]['0']['bench']
        global_cost = np.sum(ag0['stallCyclesMLPLoad'])
        global_freq = np.sum(ag0['count'])

        for i in inst: 
            sel = (ag0['address'] == i)  & (ag0['accessBracket'] < 14 )
            tot = np.sum(ag0['count'][sel])
            avg_stall = np.sum(ag0['stallCyclesMLPLoad'][sel])/tot
            totals.append(np.sum(ag0['stallCyclesMLPLoad'][sel])*100000/global_cost) #*1000000/tot )
            freqs.append(tot*100000/global_freq)
            # color by average 
            
            if avg_stall > 50:
                avg_stall = 50
            colors.append((avg_stall/50,0,0) )
            #colors.append(get_color(data,r))
    iterate_over_benches(data, d)
    plt.figure(figsize=(14, 8))
    # do log scale on the x axis
    plt.scatter(
        np.log(np.array(freqs)),
        np.log(np.array(totals)),
        #np.array(totals)),
        c=colors)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Total MLP Stalls')
    plt.title('MLP Stalls vs Frequency')
    print(len(freqs), "total insts...")
    plt.tight_layout()
    plt.savefig('mlp_stalls_vs_frequency.png', dpi=150)
    plt.show()
    

def metric_eval():
    global total_sim_time
    global NORM
    global BY_MOMENT
    per_bench = []
    benchset  = []
    benchname = []
    benchnrrr = []

    _EDGE_normal_slow = []
    _EDGE_due_to_squash = []
    sq__EDGE_normal_slow = []
    sq__EDGE_due_to_squash = []
    _EDGE_bench = []
    _EDGE_benchset = []
    total_sim_time = 0
    
    x_keys = ['Slow down (%)', 'Absolute increase in cycles','Core Stall Cycles', '∆ Core Stalls Cycles',  'average_mlp']
    #OTHER_X_KEYS = []
    if OTHER_X_KEYS:
        x_keys = OTHER_X_KEYS
    mode = "LLC_SHOW"
    mode = "PERCENT_SQUASH"
    def valo(data, r):
        global total_sim_time
        print(data[r]['0']['line'])
        if is_miss_aligned(data,r):

            raise Exception("Unaligned execution detected!!")
            return
        benchsett = data[r]['0']['benchset']
        if benchsett != "benches_final":
            print("Non analysis bench run", benchsett, data[r]['0']['bench'])
            raise Exception("Non analysis bench run") 
            return
            #raise Exception("Unaligned execution detected!!")
            #r
    
        #glob_80 = load_global_fields(data_v4, r, "80", PID_ONLY=True, run_folder=RUN_DATA_FOLDER_V4)
        #glob_0 = load_global_fields(data_v4, r, "0", PID_ONLY=True, run_folder=RUN_DATA_FOLDER_V4)
        #total_sim_time += np.sum(glob_0['currentCycle'][:get_last_idx_of_smallest_vector(glob_80['currentCycle'],glob_0['currentCycle']) ])
        #return


        def checks():
            commited_instructions = load_global_fields_crescendo(data,r)['commitedInstructions'][0]
            commited_instructions_80 = load_global_fields_crescendo(data,r, "80")['commitedInstructions'][0]
            if commited_instructions != commited_instructions_80:
                raise Exception("Unaligned execution. Runs from different report intervals.")
            print("COMMMM", commited_instructions, commited_instructions_80, commited_instructions == commited_instructions_80)
        checks()

        glob_0 = load_global_fields(data,r) #convolve=500)
        if "80" not in data[r]:
            print("No 80 run", benchset, data[r]['0']['bench'])
            if r in data_v4 and "80" in data_v4[r]:
                print("BUT V4 COULD SAVE!")
                raise Exception("V4 won't save")
                glob_80 = load_global_fields(data_v4, r, "80", PID_ONLY=True, run_folder=RUN_DATA_FOLDER_V4)
                glob_0 = load_global_fields(data_v4, r, "0", PID_ONLY=True, run_folder=RUN_DATA_FOLDER_V4)
                total_sim_time += np.sum(glob_0['currentCycle'][:get_last_idx_of_smallest_vector(glob_80['currentCycle'],glob_0['currentCycle']) ])
            else:
                raise Exception("Unaligned execution detected!!")
                return
        else:
            glob_80 = load_global_fields(data,r,"80") # convolve=500)
        #data_v4
        if( (len(glob_0['currentCycle']) - len(glob_80['currentCycle'])) != 0 ):
            print("Did not run to completion")
            

        date =  int(data[r]['0']['line'].split(" ")[-1])
        december_day_7_2025_mid_night =  1765065600
        if (date - december_day_7_2025_mid_night) < 0:  
            pass
            #return
            #raise Exception("Run from an old binary!")
            #return
            
            
            

        if len(glob_0['currentCycle']) < 400:
            print("Not enough execution time..." , len(glob_0['currentCycle']),   data[r]['0']['benchset'], data[r]['0']['bench'])
            raise Exception("Not enough execution time...")
            return


        last_idx = get_last_idx_of_smallest_vector(glob_80['currentCycle'],glob_0['currentCycle']) 
        def get_last_idx_agg(_last_idx) :
            agg80 = load_aggregate_fields(data, r, "80")
            agg0 = load_aggregate_fields(data, r)
            rrr = _last_idx
            if np.sum(agg0['count']==0) != len(glob_0['currentCycle'][:_last_idx]):
                print("WARNING: different sizes", np.sum(agg0['count']==0), len(glob_0['currentCycle']))
                a = np.sum(agg0['count']==0) 
                if (agg0['count'] == 0)[-1] == True:
                    a -= 1  # the last won't have any data...! it can't count! 

                b = len(glob_0['currentCycle'][:_last_idx])
                rrr = min(a,b)
                    
                if np.sum(agg0['count']==0)/ len(glob_0['currentCycle'][:_last_idx]) < 0.5:
                    pass
                    #raise Exception("Not enough aggregate data for some reason")

                #print("LAST IDX is", last_idx, _last_idx)
                if  np.abs(a - b) > 100:
                    if a > b:
                        pass
                    else:
                        pass
            return rrr
        try:
            # 
            if LIMIT_BY_AGG:
                last_idx = get_last_idx_agg(last_idx)
        except FileNotFoundError:
            raise Exception("Aggregate data not found...")
        except Exception as e:
            print("WARNING: different sizes")
            print(e)
            exit(0)
            raise e
                


        if last_idx < 400:
            print("Survived on fast only.. but dead")
            return
        globy = {}
        def aggregate_op(array, positive=True):
            if BY_MOMENT:
                array = array.astype(np.int64)
                # do the mean of 2
                #return np.convolve(array, np.ones(2)/2, mode='valid')
                return np.where(array == 0, 1 if positive else 0, array)
            r = np.sum( array.astype(np.int64), dtype=np.int64)
            return r if not positive or (positive and r != 0) else 1
        def norm_function():
            if NORM == "active": # (get('currentCycle') - get('stalledCycles'))/,
                return aggregate_op(glob_0["currentCycle"][:last_idx]) -aggregate_op(glob_0["stalledCycles"][:last_idx]) # user
            if NORM == "fast_cycles":
                return  aggregate_op(glob_0['currentCycle'][:last_idx]) - aggregate_op(glob_0['stalledCycles'][:last_idx]) # user
            if NORM == "NONE":
                return 1
            if NORM == "STALL":
                return  aggregate_op(glob_0['stalledCycles'][:last_idx]) # user
            if NORM == "TPP":
                return  aggregate_op(glob_0['commitedLoads'][:last_idx]) # user
            if NORM == "PEBS":
                return  aggregate_op(glob_0['commitedL3Misses'][:last_idx]) # user
            if NORM  == "user":
                return  aggregate_op(glob_0['currentCycle'][:last_idx]) # user
            if NORM  == "stores":
                return  aggregate_op(glob_0['commitedStores'][:last_idx]) # user
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
        if np.mean(global_slowdown) < 0.98:
            print("global_slowdown is SPEED UP!!!")
            #raise Exception("global_slowdown is SPEED UP!!!")
            #return
            pass
        if np.sum(glob_80["currentCycle"][:last_idx])/np.sum( glob_0["currentCycle"][:last_idx]) < 0.98:
            print("global_slowdown is SPEED UP!!!")
            raise Exception("global_slowdown is SPEED UP!!!")
            #return
            #pass


        agg0 = load_aggregate_fields(data, r)
        #print("LST", get('lastStallTime') )
        #print(agg0['lastStallTime'])
        #agg80 = load_aggregate_fields(data, r, '80')
        #if np.mean(get('lastStallTime')/get('stalledCyclesWithMemRequests')) >= 50:
        #    raise Exception("Store bound")
        #if( (np.sum(agg0['count']) - get('commitedLoads') + get('commitedStores')) > 100): # 69 okay runs to --> 
        #    raise Exception("Not cool!")
            
        globy = {
            'Slow down (%)': 100*(global_slowdown-1),
            'Absolute increase in cycles': getSLOW('currentCycle') - get('currentCycle') ,
           # 'global_slowdown': #global_slowdown-1, #getSLOW('currentCycle') - get('currentCycle') ,
            #'delta_cycles' : global_slowdown-1,
                '∆ Active cycles': (getSLOW('currentCycle') - getSLOW('stalledCycles') - ( get('currentCycle') - get('stalledCycles') ))/norm,
                'Active cycles slow': (getSLOW('currentCycle') - getSLOW('stalledCycles'))/norm,
                'Active cycles fast': (get('currentCycle') - get('stalledCycles'))/norm,
                        'commitedStores' : get('commitedStores')/norm,
                        'Cycles' : get('currentCycle'),

                        

                        #'AggStore bound cycles' :  np.sum(agg0['lastStallTime']*agg0['count'])/norm, # get('lastStallTime')/norm,
                        #'Agg∆ Store bound cycles' : (np.sum(agg80['lastStallTime']*agg80['count']) - np.sum(agg0['lastStallTime']*agg80['count'] ))/norm,
                            
                            #(getSLOW('lastStallTime') - get('lastStallTime'))/norm,

                        #'commitedLoads' : get('commitedStores')
                    
                
            # the increase in fast cycles is harder ... than obtaining the slow down percentually  
            # i.e. there are scenarios where, for any of the metrics, 
            #  there is not a linear relationship between the metrics and the absolute increase in run time
            # This non lineary is hidden, when slow down is calculated as the percentual increase in stall cycles
            # i.e. they have higher run time (and slow down), for simlar metrics (i.e. a small increase in the stall latency = big increase in the number of slowdowns) 
            # this makes sense for high MLP, 
            # fast cycles must be shorter and shorter, because as the 

            # at first, + L is hidden, and there is no degradation.
            # then L becomes great enough +X > 0
            # at first, +X is highly dilluted in the rest of the execution cost (both compute and memory access)
            # then, +X starts to become substantial.
            
            # this is equivalent to the rate of cost for fast tier metrics. 
            # the higher the rate, the higher the slow down percentually, in linear proportions
            # however, +X of stalls is not +X  of delay
            # in some scenarios, +X implies a >> greater increase in delay
            # ()

            # it must be being divided by a lower value in order to rise up to linear corr
            # thus, the higher the difference, the lower the stall cycles in the fast tier
            # stall cycles originate from toerh things 
            # 
            # (the diff is greater.. thus, in proportion to slow down, the slow cycles are much greater)
            # slow cycles/ fast_cycles          
            # --> +X 
            
            # lets assume that +X is indeed the cost observed
            # at first, +X is highly dilluted in the rest of the cost
            
            # this means that for any metric, +X of it does not correspond to a +X of delay, even though they are in the same unit
            # the rate of stalls.. correlates better.
            # intuitively, the higher the rate of memory acces cost, the harder can the CPU amortize it. (i.e. the active cycles become less and less in proportion, thus 10 to fetch and 20 to process is very different than 20/20, or 40/20..) 
            # using these metrics in an online fashion... will be less accurate because of this
            
            #  INDEED, since stall cycles and global cycles vary non trivially, considering them as units.,.. breaks
            # higher diffs = 
        }

        print("Going to do core cycles") 
        globy['Core Stall Cycles'] = aggregate_op(glob_0['stalledCycles'][:last_idx]) /norm
        globy['Core MLP Stall Cycles'] = aggregate_op(glob_0['stallCyclesMLPLoad'][:last_idx]) /norm
        benchsett = data[r]['0']['benchset'] 
        benchnamee = data[r]['0']['bench']
        try:
            benchsett = data[r]['0']['benchset'] 
            benchnamee = data[r]['0']['bench']
        except Exception as ee :
            print(f"Error accessing benchset/bench for {r}", e)
        bench_nr = data[r]['0']['benchnr']
        def complete():
            print("Trying to complete")
            try:
                per_bench.append(globy)
                benchset.append(benchsett)
                benchname.append(benchnamee)

                benchnrrr.append(bench_nr)
            except Exception as e:
                print(e)
                
            print("COMPLETED")

        a = 1.0155768028621026
        b = -0.2562029379967975
        cycles_with_demand_read_0 = get('cyclesWithMemrequests',False) #aggregate_op(glob_0['cyclesWithMemrequests'][:last_idx])
        globy['cyclesWithMemrequests'] = cycles_with_demand_read_0

        globy['Core Load bound stalls'] = get("stalledCyclesWithMemRequests") /norm
        globy['Core Load and Store bound stalls'] = (get("stalledCyclesWithMemRequests") + get('lastStallTime'))/norm
        #complete()
        #return
        number_of_demand_reads_0 = get('commitedLoads', False) #aggregate_op(glob_0['commitedLoads'][:last_idx])

        globy['average_mlp'] =  get('totalMLPsummed', False)/cycles_with_demand_read_0
        globy['Average MLP'] =  get('totalMLPsummed', False)/cycles_with_demand_read_0
        globy['Average MLP'] = np.where(cycles_with_demand_read_0 == 0, 0, globy['Average MLP']) 
        avgSlow = getSLOW('totalMLPsummed', False)/getSLOW('cyclesWithMemrequests',False) 
        avgSlow = np.where(getSLOW('cyclesWithMemrequests',False)  == 0, 0, globy['Average MLP']) 
        globy['Average MLP (Slow)'] = avgSlow 
        globy['∆Average MLP'] =  globy['Average MLP'] -  avgSlow


        #print(np.histogram(globy['average_mlp']))
        globy['average_l3mlp'] = get('totalL3MLPsummed', False)/get('L3cyclesWithMemrequests')
        globy['Average LLC MLP'] = get('totalL3MLPsummed', False)/get('L3cyclesWithMemrequests', False)
        globy['Average LLC MLP'] = np.where(get('L3cyclesWithMemrequests', False) == 0, 1, globy['Average LLC MLP']) 
        #print("l3", np.histogram(globy['average_l3mlp']))
        print("AVG MLP DONE") 
        def make_safe(d, key, prob_data,sub=0):
            d[key] = np.where((prob_data == 0), sub, d[key])
            # cap
            d[key] = np.where((d[key] < 0), 0, d[key])
        slowdooo = (getSLOW('currentCycle')-get('currentCycle'))/get('currentCycle') 
        P = get('L3stalledCycles', False)/get('currentCycle')
        P = get('L3stalledCycles', False)/getSLOW('L3stalledCycles')
        globy['Fast LLC Stall Cycles/Slow Cycles'] =  slowdooo/P
        make_safe(globy, 'Fast LLC Stall Cycles/Slow Cycles', P)

        P = get('stalledCyclesWithMemRequests', False)/get('currentCycle')
        P = get('stalledCyclesWithMemRequests', False)/get('stalledCyclesWithMemRequests')
        globy['Slow Cycles/Mem Stall Cycles'] = slowdooo/P
        make_safe(globy, 'Slow Cycles/Mem Stall Cycles', P)
        # getSLOW('currentCycle')/get('stalledCyclesWithMemRequests', False)



        AOL = cycles_with_demand_read_0/number_of_demand_reads_0 
        #AOL = np.where(number_of_demand_reads_0 == 0 | np.isnan(AOL)|  cycles_with_demand_read_0 == 0, 1, AOL)# 
        globy['AOL (All accesses)'] = np.where((number_of_demand_reads_0 == 0) | (np.isnan(AOL)) | (cycles_with_demand_read_0 == 0), 0, AOL) 
        AOL = np.where((number_of_demand_reads_0 == 0) | (np.isnan(AOL)) | (cycles_with_demand_read_0 == 0), 0, AOL) 

        

        unadjusted_slowdown =  get("stalledCyclesWithMemRequests")/aggregate_op(glob_0['currentCycle'][:last_idx])
        a=12.68203862081165 
        b=-8.91028953019958
        globy['Soar slowdown (unormallll)'] = aggregate_op(glob_0['stalledCyclesWithMemRequests'][:last_idx]) * (1/(a + b/AOL))
        a=18.498574928747963 
        b=0.8699999999631827 
        globy['Soar slowdown (unormalSANO)'] = aggregate_op(glob_0['stalledCyclesWithMemRequests'][:last_idx]) * (1/(a + b/AOL))

        a = 1.0155768028621026
        b = -0.2562029379967975
        globy['Soar slowdown ALL_STALLS'] = unadjusted_slowdown * (1/(a + b/AOL))

        if False and  ALL_DESIRED_KEYS(globy):
            complete()
            print("Yupoyy")
            return
        #return
        mean_non_stall =  np.mean(

             (get("stalledCycles")- get('stalledCyclesWithMemRequests'))
            /get("stalledCycles")) # get("currentCycle"))
        print("MEANNONN", mean_non_stall)
        if mean_non_stall > 0.25:
            pass
            #return
        ck = [
            'commitedStores', 'commitedAtomic', 'commitedLoads'
        ]
        okay = True

        for ku in ck:
            continue
            diff = np.abs(getSLOW(ku)- get(ku))
            ruuminante = np.sum(diff < 10)
            print(f"Checking ali alignment for {ku}...", r, "/", len(diff), "max_diff:", np.max(diff),"\n")
            print(f"Checking alignment for {ku}...", r, "/", len(diff), "max_diff:", np.max(diff),"\n")
            print(f"Checking alignment for {ku}...", r, "/", len(diff), "max_diff:", np.max(diff),"\n")
            okay = okay and ruuminante == len(diff)
        if(not okay):
            print("UNALIGNED")
            #exit(0)

        
        ratio = aggregate_op(glob_0['totalSquashed'][:last_idx]) / aggregate_op(glob_80['totalSquashed'][:last_idx])
        diff_squash = aggregate_op(glob_0['totalSquashed'][:last_idx]) - aggregate_op(glob_80['totalSquashed'][:last_idx])
        globy['ratio_stalls']  = ratio 
        globy['Squashed instructions'] = aggregate_op(glob_0['totalSquashed'][:last_idx]) /norm
        globy['∆ Squashed'] = getSLOW('totalSquashed')-  get('totalSquashed') /norm #aggregate_op(glob_0['totalSquashed'][:last_idx])
        globy['Squashed instructions slow'] = aggregate_op(glob_80['totalSquashed'][:last_idx]) /norm

        # 1278 seconds  ALL
        # 1191 seconds (only until last IDX) =  19 minutes of real runtime 1191 * 11000 = 209 000 minutes = 3 450 horas /  27 h of compute if split across 128 cores 

        globy['Instruction Soar'] = get("L3stallCyclesMLPBoth")
        globy['Instruction Stall Cycle/MLP Start'] = get("L3stallCyclesMLPStore")
        globy['Instruction Stall Cycles/MLP Middle'] = get("stalledCyclesDuringStore")
        globy['Instruction Stall Cycles/MLP End'] = get("L3stalledCyclesDuringStore")
        globy['Instruction Stall Cycles/MLP Average'] = get("stallCyclesMLPStore")
        globy['non_memory_stalls']  =  (get("stalledCycles")- get('stalledCyclesWithMemRequests') ) / norm
        globy['Non Memory Stalls (LLC)']  =  (get("stalledCycles")- get('L3stalledCycles') ) / norm
        globy['Non Load/Store bound cycles']  = (get("stalledCycles")- get('stalledCyclesWithMemRequests')- get('lastStallTime'))/norm
        globy['Non Load LLC/Store bound cycles']  = (get("stalledCycles")- get('L3stalledCycles')- get('lastStallTime'))/norm
        globy['∆ Non Load/Store bound cycles']  =(getSLOW("stalledCycles")- getSLOW('stalledCyclesWithMemRequests')- getSLOW('lastStallTime'))/norm -  globy['Non Load/Store bound cycles']  
        globy['∆ Non Load LLC/Store bound cycles']  =(getSLOW("stalledCycles")- getSLOW('L3stalledCycles')- getSLOW('lastStallTime'))/norm -  globy['Non Load/Store bound cycles']  

        globy['Core Store+Load bound cycles']  = (get("lastStallTime")+ get('stalledCyclesWithMemRequests'))/norm
        globy['Core Store+LLC bound cycles']  = (get("lastStallTime")+ get('L3stalledCycles'))/norm

        globy['∆ Load/Store bound cycles']  = (get('L3stalledCycles')+ get('lastStallTime'))/norm
        print("Before...")
        globy['LLC bound stall cycles'] = get('L3stalledCycles')/norm 
        globy['∆ LLC bound stall cycles'] = getSLOW('L3stalledCycles')/norm - globy['LLC bound stall cycles']
        globy['L3stalledCycles'] =  get('L3stalledCycles')
        globy['Store bound cycles'] =  get('lastStallTime')/norm
        globy['Store bound cycles Slow'] =  getSLOW('lastStallTime')/norm
        globy['∆ Store bound cycles'] = (getSLOW('lastStallTime') - get('lastStallTime'))/norm
        globy['RatioStoreLLC'] = aggregate_op(glob_0['commitedL3Misses'][:last_idx])/aggregate_op(glob_0['commitedStores'][:last_idx]) *  (get("stalledCycles")- get('stalledCyclesWithMemRequests')) 
        globy['RatioStoreLLC*Squash'] = aggregate_op(glob_0['commitedL3Misses'][:last_idx])/aggregate_op(glob_0['commitedStores'][:last_idx]) *  (get("stalledCycles")- get('stalledCyclesWithMemRequests'))  * get('totalSquashed')
        globy['LLC count'] = aggregate_op(glob_0['commitedL3Misses'][:last_idx])/norm


        average_time = np.max(np.sum(glob_0['currentCycle']/3e9)) # get('currentCycle')/3e9 # 3Ghz per second
        average_time = get('currentCycle')/3e9 # 3Ghz per second
        globy['average_time'] = (average_time)
        # print("AVG Time ",  (average_time), (np.max(glob_0['currentCycle'][:last_idx])/3e9))

        THRESHOLD_SPEEDUP = 0.99
        THRESHOLD_SLOWDOWN = 1.01

        THRESHOLD_SPEEDUP = 0.95
        THRESHOLD_SLOWDOWN = 1.05
        commitedL3Misses = aggregate_op(glob_0['commitedL3Misses'][:last_idx])
        commited_slow = getSLOW('commitedL3Misses')

        #globy['average_mlp'] =  get('totalMLPsummed', False)/cycles_with_demand_read_0
        ##print(np.histogram(globy['average_mlp']))
        #globy['average_l3mlp'] = get('totalL3MLPsummed', False)/get('L3cyclesWithMemrequests')

        if np.sum(global_slowdown < THRESHOLD_SPEEDUP) >= 1:
            if(not okay):
                print("aligned UNALIGNED YOUR FAULT BRO\n")
                #exit(0)
            print("Negative slowdown detected!!") #, np.sum(global_slowdown<1),  np.sum(global_slowdown<1)/len(global_slowdown) ,  data[r]['0']['benchset'], data[r]['0']['bench']) 
            gs = (global_slowdown < THRESHOLD_SPEEDUP)

        if np.sum(global_slowdown < THRESHOLD_SPEEDUP) >= 1 and BY_MOMENT:
            try:
                #sss = np.sum(aggregate_op(glob_0['currentCycle'][:last_idx]))
                sss = aggregate_op(glob_0['stalledCycles'][:last_idx]) 
                sss80 = aggregate_op(glob_80['stalledCycles'][:last_idx])
                squash = aggregate_op(glob_0['totalSquashed'][:last_idx]) /aggregate_op(glob_80['totalSquashed'][:last_idx])
                #due_to_squash = (100*np.sum((1-( aggregate_op(glob_0['totalSquashed'][:last_idx]) /aggregate_op(glob_80['totalSquashed'][:last_idx])) ) > 1-global_slowdown) & (global_slowdown < 1)) )/ np.sum((global_slowdown < 1))

                # 2. Calculate "due_to_squash" (When Speedup: slowdown < 1)
                # We count where (Ratio > 1) AND (Slowdown < 1), then divide by total count of (Slowdown < 1)
                due_to_squash = 100 * np.sum((ratio > 1) & (global_slowdown < 1)) / np.sum(global_slowdown < 1)
                """
                due_to_squash_precise = 100 * np.sum((  
                    # the unexpected increase in ratio
                                                      (1-ratio[gs]) >= 
                                                      # > than the unexpected decrease in slow down
                                                      (1-global_slowdown[gs])) & (global_slowdown[gs] < 1)) / np.sum(global_slowdown[gs] < 1)
                """

                # 3. Calculate "in_general" (When Slowdown: slowdown >= 1)
                # We count where (Ratio > 1) AND (Slowdown >= 1), then divide by total count of (Slowdown >= 1)
                DELTA=1000
                due_to_squash_diff = 100 * np.sum((diff_squash > DELTA) & (global_slowdown < THRESHOLD_SLOWDOWN)) / np.sum(global_slowdown < THRESHOLD_SLOWDOWN)
                in_general_diff = 0 # 100 * np.sum((diff_squash > DELTA) & (global_slowdown >= SLOW_THRESHOLD)) / np.sum(global_slowdown >= SLOW_THRESHOLD)
                in_general_mask = (global_slowdown > THRESHOLD_SLOWDOWN)
                speedup_mask  = (global_slowdown < THRESHOLD_SPEEDUP)
                mean_squash = np.sqrt(np.mean( diff_squash[speedup_mask]**2) )
                mean_general = np.square(np.mean( diff_squash[in_general_mask]**2) )

                in_general = 100 * np.sum((ratio > 1) & (global_slowdown > THRESHOLD_SLOWDOWN)) / np.sum(global_slowdown > THRESHOLD_SLOWDOWN)
                ingen_stalls =  sss /sss80
                #_EDGE_normal_slow.append(in_general_diff)
                #_EDGE_due_to_squash.append(due_to_squash_diff)

                gen_llc = np.mean(commitedL3Misses[in_general_mask])
                if gen_llc == 0:
                    gen_llc = 1
                up_llc = np.mean(commitedL3Misses[speedup_mask])
                up_llc = up_llc if up_llc else 1


                in_general_greater = np.sum(diff_squash[in_general_mask] < 0) / len(diff_squash[in_general_mask]) *100
                speedup_greater =  np.sum(diff_squash[speedup_mask] <= 0) / len(diff_squash[speedup_mask]) * 100 # CHANGE
                
                
                # AVERAGE MEAN OF INCREASE/ DECREASE OF INSTS
                #_EDGE_normal_slow.append(0) #/gen_llc)
                #_EDGE_due_to_squash.append(mean_squash) #/up_llc)

                ############################### 
                #if mode == "LLC_SHOW":
                #_EDGE_normal_slow.append(np.mean( getSLOW('commitedL3Misses')[in_general_mask]/commitedL3Misses[in_general_mask] )) # have almost no LLC misses. 
                #_EDGE_due_to_squash.append(np.mean( getSLOW('commitedL3Misses')[in_general_mask]/commitedL3Misses[speedup_mask]))

                _EDGE_normal_slow.append(np.mean( commitedL3Misses[in_general_mask] )) # have almost no LLC misses. 
                _EDGE_due_to_squash.append(np.mean(commitedL3Misses[speedup_mask]))
                sq__EDGE_normal_slow.append(in_general_greater) #/gen_llc)
                sq__EDGE_due_to_squash.append(speedup_greater) #/up_llc)

                

                print("ali DIFF SQUASH", due_to_squash_diff)
                n = data[r]['0']['bench'].split("/")[-1]
                n = n.split(".NOavx")[0]
                i = 0
                for b in _EDGE_bench:
                    if b == n:
                        i += 1
                if i > 0:
                    n += "-" + str(i)
                _EDGE_bench.append(n)
                _EDGE_benchset.append(data[r]['0']['benchset'])

                sss = aggregate_op(glob_0['stalledCycles'][:last_idx]) 
                sss80 = aggregate_op(glob_80['stalledCycles'][:last_idx])
                """
                due_to_squash = (100*np.sum((aggregate_op(glob_0['totalSquashed'][:last_idx]) /aggregate_op(glob_80['totalSquashed'][:last_idx]))  > 1) & (global_slowdown < 1))/ np.sum((global_slowdown < 1))
                in_general =  (
                    100*
                    np.sum( (
                            aggregate_op(glob_0['totalSquashed'][:last_idx]) /aggregate_op(glob_80['totalSquashed'][:last_idx])  > 1) )
                    & (global_slowdown >= 1)  /
                    np.sum((global_slowdown >= 1))

                )
                """


                print("In general", in_general, " when we have speed up:", due_to_squash )
                print("In general", in_general, " when we have speed up:", due_to_squash )
                print("In general", in_general, " when we have speed up:", due_to_squash )
                print("In general", in_general, " when we have speed up:", due_to_squash )
            except Exception as e:
                print(e)
                print(e)
                print(e)
                print(e)
                print(e)
                print(e)
                print(e)
                print(e)
                print(e)
                print(e)
                print(e)
                print(e)
                print(e)
                #return
            # since the CPU can access memory faster.. it can also speculate faster...
            """
            print("Negative slowdown detected!!",  due_to_squash, data[r]['0']['benchset'], data[r]['0']['bench']) 
            print("Negative slowdown detected!!", due_to_squash,  data[r]['0']['benchset'], data[r]['0']['bench']) 

            print("When stalls were fewer", np.sum(sss80-sss < 1))
            print("When stalls were fewer", np.sum((sss80[gs]-sss[gs]) < 1))
            neg_indices = np.where(global_slowdown < 0.98)[0]
            # worse prefetching -> resources are more devoted to demand reads --> 
            #_ Higher latency actually enhances prefetcher effectiveness by providing a larger temporal window for the prefetcher to work effectively.
            commitedL3Misses80 = aggregate_op(glob_80['commitedL3Misses'][:last_idx])
            # the number of LLC misses, in percentage on the slow tier, is lower than 100%. in fact, it is lower than the speed up (i.e. each % LLC miss contributes to less than % of slowdown)
            # CPU archiecture is so complex, that no heuristic holds true at enough granularity.
            # accross all workloads, these datapoints represent less than 5% of the moments. 
            # this constrasts witht the exact opposite reasoning 
            print("When MISSES are fewer", int(100*np.sum((1-(commitedL3Misses80[gs]/commitedL3Misses[gs])) <  (1-global_slowdown[gs]) )/np.sum(gs)))
            print("When MISSES are fewerrr", int(100*np.sum((commitedL3Misses80[gs]-commitedL3Misses[gs])  < 0 ) /np.sum(gs)))
            # we have less LLC misses.. 

            j = 0
            for i in neg_indices:
                prev_val = global_slowdown[i-1] if i > 0 else np.nan
                curr_val = global_slowdown[i]
                next_val = global_slowdown[i+1] if i < len(global_slowdown)-1 else np.nan

                

                print(f"Index {i}: prev={prev_val:.4f}, curr={curr_val:.4f},{squash[i]} {sss80[i]/sss[i]} next={next_val:.4f}")
                # sometimes it has mroe, sometimes it has less stall cycles...
                j +=1
                if (j > 20):
                    break
            """    

            #raise Exception("Negative slowdown detected!!")
            #return
        print("Hoooo")    
            
        print("HIII")

        if benchsett != "benches_final":
            print(benchsett)
            print("Not an instruction aligned execution ")
            raise Exception("Unaligned execution detected!!")
            return
        if ( np.sum(np.abs( getSLOW('commitedLoads') - get('commitedLoads')) > 50) > 2):
            print("Unaligned execution detected!! ", benchsett, benchnamee)
            o = np.abs( getSLOW('commitedLoads') - get('commitedLoads'))
            print("AAAA", np.max(o), np.min(o), np.mean(o), np.percentile(o, 95), np.percentile(o, 5), np.percentile(o, 50))
            if np.percentile(o, 50) > 100:
                raise Exception("Unaligned execution detected!!")
                
            # CHANGE
        if ( np.sum(np.abs( getSLOW('commitedLoads') - get('commitedLoads')) > 200) > 10):
            print("BAD unaligned")
            raise Exception("Unaligned execution detected!!")

            #return

        #return complete()
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
        globy['Core MLP Stall Cycles (during LLC misses)'] = aggregate_op(glob_0['L3stallCyclesMLPLoad'][:last_idx]) /norm
        globy['Core Stall Cycles (during LLC misses)'] = aggregate_op(glob_0['L3stalledCycles'][:last_idx]) /norm

        #globy['Delta  Cycles'] = aggregate_op(glob_0['stalledCycles'][:last_idx]) /norm

        print("Doing core deltas")
        norm_diff =  aggregate_op(glob_0['stalledCycles'][:last_idx])
        norm_diff =  aggregate_op(glob_0['currentCycle'][:last_idx])
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
        globy['Core LLC stalls'] = get("L3stalledCycles") /norm

        globy['Core Load bound stalls'] = get("stalledCyclesWithMemRequests") /norm_diff
        globy['∆ Core Load bound stalls'] = getSLOW("stalledCyclesWithMemRequests") /norm_diff - get("stalledCyclesWithMemRequests") /norm_diff  

        """ CHANGE
        summedKeys = ['totalAccessTimeSummed' ] #, 'average_mlp', 'average_l3mlp']
        for k in summedKeys:
            globy[k] = get(k)/norm
        diffKeys = ['totalAccessTimeSummed']
        for k in diffKeys:
            norm_diff = get(k)
            globy['diff_'+k] = (getSLOW(k) - get(k)) /norm_diff
        """






        print("Doing total instructions")
        tot_keys = ['totalL3MLPStalledCyclesSummed', 'totalL3StalledCyclesSummed', 'totalStalledCyclesSummed', 'totalMLPStalledCyclesSummed']
        for k in tot_keys:
            globy['k'] = get(k)/norm

        globy['Instruction Stall cycles/MLP (LLC misses)'] = (aggregate_op(glob_0['totalL3MLPStalledCyclesSummed'][:last_idx]))/norm 
        globy['Instruction Stall cycles (LLC misses)'] = (aggregate_op(glob_0['totalL3StalledCyclesSummed'][:last_idx]))/norm 
        globy['Instruction Stall cycles'] = (aggregate_op(glob_0['totalStalledCyclesSummed'][:last_idx]))/norm 
        globy['Instruction Stall cycles/MLP'] = (aggregate_op(glob_0['totalMLPStalledCyclesSummed'][:last_idx]))/norm 
        #globy['Instruction Stall cycles/MLP (LLC misses)'] = (aggregate_op(glob_0['totalL3MLPStalledCyclesSummed'][:last_idx]))/norm 

        globy['Slow Instruction Stall cycles/MLP (LLC misses)'] = (aggregate_op(glob_80['totalL3MLPStalledCyclesSummed'][:last_idx]))/norm 
        globy['Slow Instruction Stall cycles (LLC misses)'] = (aggregate_op(glob_80['totalL3StalledCyclesSummed'][:last_idx]))/norm 
        globy['Slow Instruction Stall cycles'] = (aggregate_op(glob_80['totalStalledCyclesSummed'][:last_idx]))/norm 
        globy['Slow Instruction Stall cycles/MLP'] = (aggregate_op(glob_80['totalMLPStalledCyclesSummed'][:last_idx]))/norm 

        globy['∆ Instruction Stall cycles/MLP (LLC misses)'] = (aggregate_op(glob_80['totalL3MLPStalledCyclesSummed'][:last_idx]) - aggregate_op(glob_0['totalL3MLPStalledCyclesSummed'][:last_idx]))/norm 
        globy['∆ Instruction Stall cycles (LLC misses)'] = (aggregate_op(glob_80['totalL3StalledCyclesSummed'][:last_idx]) - aggregate_op(glob_0['totalL3StalledCyclesSummed'][:last_idx]))/norm 
        globy['∆ Instruction Stall cycles'] = (aggregate_op(glob_80['totalStalledCyclesSummed'][:last_idx]) - aggregate_op(glob_0['totalStalledCyclesSummed'][:last_idx]))/norm 
        globy['∆ Instruction Stall cycles/MLP'] = (aggregate_op(glob_80['totalMLPStalledCyclesSummed'][:last_idx]) - aggregate_op(glob_0['totalMLPStalledCyclesSummed'][:last_idx]))/norm 

        globy['∆ (Instruction Store Bound + Load Stall Cycles/MLP)'] =  globy['∆ Instruction Stall cycles/MLP'] + globy['∆ Store bound cycles']
        globy['Instruction Store Bound + Load Stall Cycles/MLP'] =  globy['Instruction Stall cycles/MLP'] + globy['Store bound cycles']
        if ALL_DESIRED_KEYS(globy):
            #complete()
            pass
            #return
        # the number of in-flight requests is N. bound stalls * N /N = bound stalls

        globy['Access Time'] = get("totalAccessTimeSummed") / norm
        globy['∆ Access Time'] = (getSLOW("totalAccessTimeSummed") - get("totalAccessTimeSummed")) /norm

        print("Deltas done") 
        WIDE_80_USE = False
        if WIDE_80_USE:
            i80 = load_inst_fields(data,r,"80")
            globy['DIFFtotalStalledCyclesSummed'] = (aggregate_op(glob_80['totalStalledCyclesSummed'][:last_idx])-aggregate_op(glob_0['totalStalledCyclesSummed'][:last_idx]))/norm 
            globy['DIFFtotalL3MLPStalledCyclesSummed'] = (aggregate_op(glob_80['totalL3MLPStalledCyclesSummed'][:last_idx])-aggregate_op(glob_0['totalL3MLPStalledCyclesSummed'][:last_idx]))/norm 

        print("Bout to commit")
        globy['Commited loads'] = aggregate_op(glob_0['commitedLoads'][:last_idx])/norm # should be the same for each of them..
        globy['Commited loads (LLC misses)'] = aggregate_op(glob_0['commitedL3Misses'][:last_idx])/norm
        print("Commited loads done")
        #globy['norma'] =  norm

        b = 24.67
        a = 0.87 

        

        unadjusted_slowdown = aggregate_op(glob_0['stalledCyclesWithMemRequests'][:last_idx])/aggregate_op(glob_0['currentCycle'][:last_idx])
        a=0.18107765333475537 
        b=-0.15584940179654744

        globy['Soar slowdown1'] = unadjusted_slowdown * (1/(a + b/AOL))
        a=0.020198280396840813 
        b=-0.00890232139828185
        globy['Soar slowdown2'] = unadjusted_slowdown * (1/(a + b/AOL))
        a = 1.0155768028621026
        b = -0.2562029379967975
        globy['Soar slowdown3'] = unadjusted_slowdown * (1/(a + b/AOL))

        a=18.498574928747963 
        b=0.8699999999631827 
        globy['Soar slowdown4'] = unadjusted_slowdown * (1/(a + b/AOL))

        a=15.368852144089956 
        b=0.87
        globy['Soar slowdown4000000prop'] = unadjusted_slowdown * (1/(a + b/AOL))


        globy['L3cyclesWithMemrequests'] =  get('L3cyclesWithMemrequests', positive=False)
        globy['commitedL3Misses'] =  get('commitedL3Misses', positive=False)
        #glob_0['commitedL3Misses'][:last_idx] #, positive=False)

        real_slow =  getSLOW('currentCycle')/get('currentCycle')
        #print(len(unadjusted_slowdown), print(len(AOL)))
        """
        #try:
        #except:
            #exit(0)
        """
                        #raise Exception("Can't do aggregate compute")
                        
                    #exit(0)


        def aggregate_compute(last_idx):
            _last_idx = last_idx
            for n in range(0,16):
                #print("DOING RANGE", n)
                agg80 = load_aggregate_fields(data, r, "80")
                agg0 = load_aggregate_fields(data, r)
                if BY_MOMENT:
                    if np.sum(agg0['count']==0) != len(glob_0['currentCycle'][:_last_idx]):
                        print("WARNING: different sizes", np.sum(agg0['count']==0), len(glob_0['currentCycle']))
                        a = np.sum(agg0['count']==0) 
                        if (agg0['count'] == 0)[-1] == True:
                            a -= 1  # the last won't have any data...! it can't count! 

                        b = len(glob_0['currentCycle'][:_last_idx])
                        last_idx = min(a,b)
                            
                        if np.sum(agg0['count']==0)/ len(glob_0['currentCycle'][:_last_idx]) < 0.5:
                            pass
                            #raise Exception("Not enough aggregate data for some reason")

                        print("LAST IDX is", last_idx, _last_idx)
                        if  np.abs(a - b) > 100:
                            if a > b:
                                pass
                            else:
                                pass
                                #raise Exception("Can't do aggregate compute")
                                
                            #exit(0)

                arr = agg0
                s = (arr['count'] == 0) & (arr['accessBracket'] == 0) & (arr['stallCyclesMLPLoad'] == 0)
                if s[-1] != True:
                    agg0['count'] = np.concatenate([agg0['count'], [0]])
                    agg0['accessBracket'] = np.concatenate([agg0['accessBracket'], [0]])
                    agg0['stallCyclesMLPLoad'] = np.concatenate([agg0['stallCyclesMLPLoad'], [0]])

                def get_idx_end(arr):
                    #en(arr['count'])
                    if not BY_MOMENT:
                        #exit(0)
                        return len(arr['count'])
                    s = (arr['count'] == 0) & (arr['accessBracket'] == 0) & (arr['stallCyclesMLPLoad'] == 0)
                    
                        
                    print(np.cumsum(s)[-1], "TOTAL", last_idx)
                    #print(np.cumsum(s), last_idx, np.argmax(np.cumsum(s) > last_idx+1) )
                    print("Res",np.argmax( np.cumsum(s) > last_idx)+1,  np.cumsum(s))
                    r = np.argmax(np.cumsum(s) == (last_idx+1+1)) #  +1 to convert index to count, +1 to grab the next start, thus including ALL the data about the last histo desired.      +1 outside woudl only include another entry of the current histo, not the next histo # when the Nth appears, we are at the start of this N's data # this will include the NULL value from the next moment.

                    r2 = np.argmax(np.cumsum(s) == (last_idx+2)) # +1 outside woudl only include another entry of the current histo, not the next histo # when the Nth appears, we are at the start of this N's data # this will include the NULL value from the next moment.
                    print("Errrr, r", r)

                    print("UNO MOMENTITO", np.sum(s[:r]) ,np.sum(s[:r2]) ,  np.sum(s))
                    if r == 0: # aka there is no next dude

                        r = len(arr['count'])

                    print("UNO MOMENTITO PLI", np.sum(s[:r]), np.sum(s), s[-1])
                    return r

                def get_idx_start(arr):
                    s = (arr['count'] == 0) & (arr['accessBracket'] == 0) & (arr['stallCyclesMLPLoad'] == 0)
                    return 0
                    if not BY_MOMENT:
                        return 0
                    else:
                        return np.argmax(np.cumsum(s) >= last_idx) # this will include the NULL value from the last_idx moment

                    #s = (arr['count'] == 0) & (arr['accessBracket'] == 0) & (arr['stallCyclesMLPLoad'] == 0)

                idx_start8 = get_idx_start(agg80)
                idx_end8 = get_idx_end(agg80)
                
                idx_start = get_idx_start(agg0)
                idx_end = get_idx_end(agg0)
                
                print(idx_start, idx_end, "----", idx_start8, idx_end8)
                def get_slice(v,key, idx_start, idx_end):
                    r = v[key][idx_start:idx_end]
                    return r

                agg80['stallCyclesMLPLoad'] =  get_slice(agg80,'stallCyclesMLPLoad', idx_start8, idx_end8)
                agg0['stallCyclesMLPLoad'] =  get_slice(agg0,'stallCyclesMLPLoad', idx_start, idx_end)

                agg80['accessBracket'] =  get_slice(agg80,'accessBracket', idx_start8, idx_end8)
                agg0['accessBracket'] =  get_slice(agg0,'accessBracket', idx_start, idx_end)
                #print(np.unique(agg0['accessBracket']), "ooo")

                agg0['count'] =  get_slice(agg0,'count', idx_start, idx_end)
                agg80['count'] =  get_slice(agg80,'count', idx_start8, idx_end8)


                sel80 = agg80['accessBracket'] >= n
                sel0 = agg0['accessBracket'] >= n
                #print("HUM NITO", n, np.sum(sel0),np.unique(agg0['accessBracket']), np.sum(agg0['count'][sel0]))
                def sum_by_moment(arr, key, cond):
                    #return np.sum(arr[key][cond])
                    if not BY_MOMENT:
                        return np.sum(arr[key][cond])
                    moments = (arr['count'] == 0) #| (cond)
                    print(np.sum(moments), "MOMENTS HERE!!|")
                    # Identify block boundaries
                    #print(np.sum(moments), "nUU")
                    #print(f"moments shape: {moments.shape}, sum: {np.sum(moments)}")
                    #print(f"moments: {moments[:20]}")  # First 20 elements
                    # is there the edge case where there are 2 consecutive arr['count'] == 0?

                    has_consecutive_true = np.any(moments[:-1] & moments[1:])
                    if(has_consecutive_true):
                        print("THIS EDGE CASE REALLY EXISTS!!", np.sum(moments[:-1] & moments[1:]))
                        #exit(0)
                        
                    #np.diff(moments.astype(int))
                    #diff = np.diff(np.concatenate([[True], moments, [True]]).astype(int))
                    #starts = np.where(diff == 1)[0]


                    #if moments[-1] != True: #  if this is not an end... we need an end!
                    #moments = np.concatenate([moments, [True]])
                    #pass
                    #starts = np.where(moments )[0]
                    #else:
                    starts = np.where(moments )[0][:-1] # last is not a start/end.. BUT only if .. 
                    ends = np.where(moments )[0][1:] # first is not a end
                    
                    #starts = np.concatenate([False], moments[:-1])
                    #ends = np.concatenate([moments[1:], False])
                    #ends = np.where(diff == -1)[0]

                    #print(f"starts: {starts}, len: {len(starts)}")
                    #print(f"ends: {ends}, len: {len(ends)}")
                    cp = arr[key] #* arr['count'] #.copy()
                    #print(f"cp before where: shape={cp.shape}, dtype={cp.dtype}")
    
                    #print("weird", np.sum(arr['accessBracket'] >= n), len(arr['accessBracket']))
                    cp = np.where( (~cond) & (arr['count'] != 0 ),0 , cp)
                    #print(f"cp after where: shape={cp.shape}, dtype={cp.dtype}, type={type(cp)}")

                    #cp = np.where(~cond, cp, 0)
                    
                    # Cumsum for O(n) block sums
                    cumsum = np.concatenate([np.cumsum(cp)])
                    print(f"cumsum shape: {cumsum.shape}")
                    print(f"cumsum shape: {cumsum}")

                    #print(ends, starts, len(cumsum))
                    return cumsum[ends] - cumsum[starts]  # O(n) total





                
                kkey =  'stallCyclesMLPLoad'
                try:
                    ril = sum_by_moment(agg0,kkey, sel0)
                    print("RANGEIO" , n , len(sel0), 'k',np.sum(agg0['accessBracket'] >= n), np.sum(~(agg0['accessBracket'] >= n)),  len(agg0['accessBracket']) , np.sum(agg0[kkey][sel0]), np.sum(ril))
                    if not BY_MOMENT:
                        ril = np.sum(ril)
                except Exception as e:
                    print("EXCEPTION IN SUM BY MOMENT")
                    import traceback
                    traceback.print_exc()
                    print(e)

                    exit(0)
                    

                if last_idx == 0: #or len(ril) == 0:
                    pass
                    #raise Exception("blow")
                    
                if BY_MOMENT:
                    globy['mlpCost' + str(n)] =  ril[:-1]
                    print(ril)
                    diff_size = _last_idx - len(ril)
                    print("DUVIDOSO", last_idx, len(globy['mlpCost' + str(n)]), _last_idx)
                    if diff_size > 0:
                        #ril = np.pad(ril, (np.mean(ril), diff_size), 'constant', constant_values=0)
                        pass
                    if diff_size < 0:
                        print(ril, diff_size, "DIFFO SIZE")
                        ril = ril[:diff_size]
                        #pass
                    globy['mlpCost' + str(n)] =  ril/norm[:last_idx] #(glob_0['currentCycle'][:last_idx]) #get('currentCycle') #/norm
                    if n == 0:
                        print("A_MLP_COST" ,globy['mlpCost' + str(n)][0:10] )
                        print("G_MLP_COST", (glob_0['totalMLPStalledCyclesSummed'][:last_idx]/norm[:last_idx])[0:10])
                        print("A_MLP_COST" ,globy['mlpCost' + str(n)][-10:] )
                        print("G_MLP_COST", (glob_0['totalMLPStalledCyclesSummed'][:last_idx]/norm[:last_idx])[-10:])

                    globy['fcount' + str(n)] = sum_by_moment(agg0, 'count', sel0)   #np.sum(agg0['count'][sel0])
                    globy['scount' + str(n)] = sum_by_moment(agg80, 'count', sel80)  #np.sum(agg80['count'][sel0])
                else:
                    globy['mlpCost' + str(n)] =  ril/(np.sum(glob_0['currentCycle'][:last_idx])) #get('currentCycle') #/norm
                    globy['fcount' + str(n)] = np.sum(sum_by_moment(agg0, 'count', sel0))   #np.sum(agg0['count'][sel0])
                    globy['scount' + str(n)] = np.sum(sum_by_moment(agg80, 'count', sel80))  #np.sum(agg80['count'][sel0])
                continue
                arr_80 = sum_by_moment(agg80,kkey, sel80)
                arr_0 = sum_by_moment(agg0,kkey, sel0)
                if BY_MOMENT:
                    if len(arr_80) < len(arr_0):
                        arr_80 = np.pad(arr_80, (0, len(arr_0) - len(arr_80)), 'constant', constant_values=0)
                    elif len(arr_0) < len(arr_80):
                        arr_0 = np.pad(arr_0, (0, len(arr_80) - len(arr_0)), 'constant', constant_values=0)
                globy['DeltamlpCost' + str(n)] = arr_80 - arr_0
                #print("WENT WELL!")
                #np.sum(agg80['count'][sel0])
                """
                POINT_VARIABLES['mlpCost' + str(n)] = np.sum(agg0['stallCyclesMLPLoad'][sel0]) 
                POINT_VARIABLES['fcount' + str(n)] = np.sum(agg0['count'][sel0])
                POINT_VARIABLES['scount' + str(n)] = np.sum(agg80['count'][sel0])
                POINT_VARIABLES['DeltamlpCost' + str(n)] = int(np.sum(agg80['stallCyclesMLPLoad'][sel80])) - int(np.sum(agg80['stallCyclesMLPLoad'][sel0]))
                """
            #exit(0)





        print("SOAR normal done")
        globy['LLC change (%)']  =  (commited_slow )*100/np.where( commitedL3Misses == 0, 1,commitedL3Misses) #/globy['average_l3mlp'] - commitedL3Misses
        print(benchnamee, "-- CHANGO" , np.mean(np.abs((commited_slow  - commitedL3Misses)*100/np.where( commitedL3Misses == 0, 1,commitedL3Misses)))) #/globy['average_l3mlp'])

        # point fit all 15.368852144089956 0.87
        # point  fit L3 
        cycles_with_demand_read_0 = get('L3cyclesWithMemrequests', positive=False) #aggregate_op(glob_0['cyclesWithMemrequests'][:last_idx])
        number_of_demand_reads_0 =commitedL3Misses #aggregate_op(glob_0['commitedLoads'][:last_idx])
        AOL = cycles_with_demand_read_0/number_of_demand_reads_0 
        #AOL = np.where(number_of_demand_reads_0 == 0 | np.isnan(AOL)|  cycles_with_demand_read_0 == 0, 1, AOL)# 
        globy['AOL'] = np.where((number_of_demand_reads_0 == 0) | (np.isnan(AOL)) | (cycles_with_demand_read_0 == 0), 0, AOL) 
        AOL = np.where((number_of_demand_reads_0 == 0) | (np.isnan(AOL)) | (cycles_with_demand_read_0 == 0), 1, AOL) 

        a=18.498574935185832 
        b=0.869721403503706
        unadjusted_slowdown = aggregate_op(glob_0['stalledCyclesWithMemRequests'][:last_idx])/aggregate_op(glob_0['currentCycle'][:last_idx])


        a=2.834606019375835 
        b=9.84061672967524
        globy['SOAR'] = unadjusted_slowdown * (1/(a + b/AOL))
        globy['SOAR Abs'] = aggregate_op(glob_0['stalledCyclesWithMemRequests'][:last_idx]) * (1/(a + b/AOL))

        unadjusted_slowdown = aggregate_op(glob_0['L3stalledCycles'][:last_idx])/aggregate_op(glob_0['currentCycle'][:last_idx])
        globy['Soar slowdown ALL_STALLS (LLC misses)'] = unadjusted_slowdown * (1/(a + b/AOL))
        a=3.039685
        b=7.067997
        globy['LLC SOAR'] = unadjusted_slowdown * (1/(a + b/AOL))
        a=2.838233
        b=10.074349
        globy['LLC SOAR (moment regressed)'] = unadjusted_slowdown * (1/(a + b/AOL))
        #RANSAC-sklearn: 3472095/4964064 inliers
        # Parameters: 
        a=2.746450 
        b=13.217005 # custom threshold
        globy['LLC SOAR (ransac)'] = unadjusted_slowdown * (1/(a + b/AOL))
        a=3.968082326935735 
        b=11.585229969197693
        globy['LLC SOAR (storng ransac)'] = unadjusted_slowdown * (1/(a + b/AOL))


        # proper SLOW
        a=0.014277438933830476 
        b=0.7032630357861712
        globy['Soar slowdown ALL_STALLS (improper fit)'] = unadjusted_slowdown * (1/(a + b/AOL))
        a=18.498575242341495 
        b=0.8680555888755302
        globy['Soar slowdown ALL_STALLS_REP.. (improper fit)'] = unadjusted_slowdown * (1/(a + b/AOL))

        # proper w/SLOW
        a=12.68203862081165 
        b=-8.91028953019958
        globy['Soar slowdown (proper fit NON NORMAL)'] = aggregate_op(glob_0['L3stalledCycles'][:last_idx])* (1/(a + b/AOL))


        globy['Soar slowdown (proper fit)'] = unadjusted_slowdown * (1/(a + b/AOL))


        a=14.67883381610677 
        b=-6.745728720038567 # point fit

        globy['Soar Slowdown'] = unadjusted_slowdown * (1/(a + b/AOL))



        #soo =  obtain_soar_mlp_aware_slowdown(unadjusted_slowdown, AOL, real_slow)
        a = 0.2510135018070131 
        b = -2.1375780816928165 
        # for ABS increase
        a = 0.43693970453381986 
        b = -2.7944993991898
        # for % increasese ( in point mode only)
        # 
        a=  0.006540343223713865 
        b= -0.029886809540104652
        a= 0.0475846790957141
        b = -0.3086124557900186 

        unadjusted_slowdown = aggregate_op(glob_0['L3stalledCycles'][:last_idx])
        a=18.498574928747963 
        b=0.8699999999631827 
        globy['Soar Slowdown (LLC MISSES)'] = unadjusted_slowdown * (1/(a + b/AOL))
        a = 0.43693970453381986 
        b = -2.7944993991898
        globy['Soar Slowdown (LLC MISSESSSS)'] = unadjusted_slowdown * (1/(a + b/AOL))
        print("SOAR L3 done")



        try:
            if True:
                print("About to do agg")
                if LIMIT_BY_AGG:
                    aggregate_compute(last_idx)
                print("Did agg")
                pass
            pass
        except Exception as e:
            print("AGREGATE MADE US FAIL")
            print(e)
            import traceback
            print(traceback.print_exc())
            exit(0)
        print("Completed")
        complete()
        total_sim_time += np.sum(glob_0['currentCycle'][:last_idx]) + np.sum(glob_80['currentCycle'][:last_idx]) # [:last_idx])
        return

        """
        L3stalledCycles


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
            complete()
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
            globy['inst_stalls_MEANdiffDastCycles'] = (np.mean(i80['stallTime'][sel80]) - np.mean(i['stallTime'][sel0])) / norm
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


    #
    
    
    

    all_together = {}
    benchsets =  [ "cpu2017", "gapbs",   "NPB-CPP",            "pkgs/apps",   "pkgs/kernels" ,"XSBench", "liblinear", "pkgs/splash"]
    benchsetsHUMAN =  [ "CPU2017", "GAPBS",   "NPB",            "PARSEC-apps",   "PARSEC-kernels" ,"XSBench", "liblinear", "PARSEC-splash"]


    benchsets =  [ "cpu2017", "gapbs",   "NPB-CPP",            "pkgs" ] # ]/apps",   "pkgs/kernels" , "pkgs/splash"]
    benchsetsHUMAN =  [ "CPU2017", "GAPBS",   "NPB",        "PARSEC", "Others"] # ,   "PARSEC-kernels" , "PARSEC-splash"]
    colors = ['blue', 'orange', 'purple', 'green', 'grey']

    benchsets =  [ "cpu2017", "gapbs",   "NPB-CPP",            ] # ]/apps",   "pkgs/kernels" , "pkgs/splash"]
    benchsetsHUMAN =  [ "CPU2017", "GAPBS",   "NPB", "Others"] # ,   "PARSEC-kernels" , "PARSEC-splash"]
    colors = ['blue', 'orange', 'purple',  'grey']
    if not should_load_cached():

        iterate_over_benches(data, valo)
        print("Total sim time", total_sim_time, total_sim_time/3e9)
        #exit(0)
        #return
        print("about do do globaos de outrs" )
        #exit(0)

        #kprint("per_bench", per_bench)
        #kprint("per_bench", per_bench[0])
        for b in per_bench:
            for k in b:
                if k not in all_together:
                    all_together[k] = []
                all_together[k].append(b[k])
                #print(b[k])
        #print("all_together", all_together)

        def plot_latency_chosen():
            print("going to do plot_latency_chosen")
            #, all_together[ABS]
            corABS = []
            corSLOW = []

            corDeltaABS = []
            corDeltaSLOW = []
            fcount = []
            scount = []
            x = np.array([n for n in range(0,16)])*16
            for n in range(0,16):
                #print((all_together['mlpCost' + str(n)]))
                #continue
                
                try:
                    mlpCost = np.array(all_together['mlpCost' + str(n)])
                except:
                    print("MLP cost key not present in the dictionary..!")
                    return
                print(mlpCost)
                #fc= np.array(all_together['fcount' + str(n)])
                #sc= np.array(all_together['scount' + str(n)])
                #DeltamlpCost = np.array(all_together['DeltamlpCost' + str(n)])
                def cor(a,b, vector):
                    
                    v = ABS
                    v= SLOWP
                    from scipy.stats.mstats import winsorize
                    y_axis =  winsorize(mlpCost, limits=[0.01, 0.01])
                    regress, residuals, rank, singular_values, rcond  = np.polyfit(y_axis, 
                    all_together[v], 1, full=True)

                    ru = np.array((y_axis))* regress[0]  + regress[1]
                    #ru = np.clip(ru, -0.30,300)
                    SSE = np.sum( np.abs((ru - all_together[v])) )
                    vector.append(SSE)
                    r = SSE
                    return r


                    r = np.corrcoef(a,b)[0,1]
                    vector.append(r*r*100)
                    return r
                def ad(v, vector):
                    vector.append(np.sum(v))
                cor(all_together[ABS],mlpCost, corABS)
                cor(all_together[SLOWP],mlpCost, corSLOW)
                #cor(all_together[ABS],DeltamlpCost, corDeltaABS)
                #cor(all_together[SLOWP],DeltamlpCost, corDeltaSLOW)
                #ad(fc,fcount)
                #ad(sc,scount)
                #print("mlpCost", mlpCost) print("fcount", fcount) print("scount", scount) print("DeltamlpCost", DeltamlpCost)
                pass
            plt.figure()
            plt.plot(x,  np.array(corABS), label="Absolute")
            #plt.plot(x, corSLOW, label="Slowdown")
            #plt.plot(x, corDeltaABS, label="Absolute Delta")
            #plt.plot(x, corDeltaSLOW, label="Slowdown Delta")
            #plt.plot(x, fcount, label="Fast LLC count")
            #plt.plot(x, scount, label="Slow LLC count")
            plt.legend()

            plt.xlabel("Access detection threshold")
            plt.ylabel("Explained Slow down (%)")
            plt.savefig("./____________BIG_COOL_CDF2.png")



            #all_together
            #

            #POINT_VARIABLES['mlpCost' + str(n)] = np.sum(agg0['stallCyclesMLPLoad'][sel0]) 
            #POINT_VARIABLES['fcount' + str(n)] = np.sum(agg0['count'][sel0])
            #POINT_VARIABLES['scount' + str(n)] = np.sum(agg80['count'][sel0])
            #POINT_VARIABLES['DeltamlpCost' + str(n)] = int(np.sum(agg80['stallCyclesMLPLoad'][sel80])) - int(np.sum(agg80['stallCyclesMLPLoad'][sel0]))

        if LIMIT_BY_AGG: #and not KEY_PLOT:
            plot_latency_chosen()
        

        

        def calculate_point_colors(metric=None):
            benchset_colors = []
            #col_idxes = []

            
            for b in benchname:
                found = False
                for name in benchsets:
                    #print(name in b , name, b)
                    if name in b:
                        benchset_colors.append(benchsets.index(name))
                        found = True
                        break
                if found:
                    continue
                benchset_colors.append(-1) # other
                #print("other is ", b)
            final_colors = []
            for c in benchset_colors:
                final_colors.append(colors[c])
            return final_colors
        final_colors = calculate_point_colors()


    #final_colors = np.load("./_finos/npys/colors_of_each.npy")
    if should_load_cached():
        final_colors = np.load("./_finos/npys/colors_of_each.npy")
    else:
        colors_of_each = []
        if BY_MOMENT and INTENSITY_metric:
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
        elif BY_MOMENT: #??
            for k in all_together:
                for i in range(len(all_together[k])):
                    #break print(k, i, "BOUT TO ERROR")
                    colors_of_each.append(np.full(len(all_together[k][i]), final_colors[i]))
                break
        if BY_MOMENT:
            colors_of_each = np.concatenate(colors_of_each)
            final_colors = colors_of_each
        #np.save("./_finos/npys/colors_of_each.npy", colors_of_each)


        for k in all_together: ### THIS IS SHARED ACROSS BOTH OF THE ABOVE PATHS <-- 
            #print(k)
            try:
                if BY_MOMENT:
                    all_together[k] = np.concatenate(all_together[k])
                if not BY_MOMENT:
                    plt.figure() # figsize=(100,100)
                    plt.title(k)
                    #print(bench_name)

                    def t(s):
                        b = s.split("/")[-1].split("NOavxprota")[0]
                        ex = ""
                        if "test" in b:
                            ex = "(test)"
                        if "bwaves" in b:
                            b = "bwaves"
                        if "bench_btree" in b:
                            b = "btree_mt"
                        else:
                            if "pr_spmv" not in b:
                                b = b.split("_")[0]
                        b += ex
                        return b
                    # [b.split("/")[-1] for b in benchname]
                    plt.bar([t(s) for s in benchname], all_together[k])
                    plt.ylim(80,360)

                    plt.xticks(rotation=45, ha='right')
                    plt.tight_layout()
                    plt.savefig(f'./_finos/_BARS/A1__ - {NORM} globos de ouro' + k.replace("/", "D")   + '.png')
                    print("SAVED bars")

                    plt.close()
                    #plt.save_fig("bars/" +k)
                #print("BAAAA")
            except Exception as e:
                print(e)
                pass
                #print("BUUUUU")
                

    #MARKER latency
    #if not LIMIT_BY_AGG: # register function to configuration.. we then would cann this whenever AGG metrics are defined!
    #    plot_latency_chosen()
    #exit(0)
    #exit(0)
    
        #print(benchsets, all_together.keys())

        

    def plot_keypair(k, all_together, BY_MOMENT, x_key, EXTRA={}, KEY_PLOT=True):
            if not SHOULD_PLOT_KEY(k):
                return

            if "Soar" not in k: # or "prop" not in k: 
                pass
                #return

         
            """

            commitedL3Misses = np.array(all_together['commitedL3Misses'])
            cycles_with_demand_read_0 = np.array(all_together['L3cyclesWithMemrequests']) #aggregate_op(glob_0['cyclesWithMemrequests'][:last_idx])
            number_of_demand_reads_0 = commitedL3Misses #aggregate_op(glob_0['commitedLoads'][:last_idx])
            AOL = cycles_with_demand_read_0/number_of_demand_reads_0 
            unadjusted_slowdown = np.array(all_together['L3stalledCycles'])/np.array(all_together['Cycles'])
            # OPTIMAL A AND B  0.43693970453381986 -2.7944993991898

            

            soo =  obtain_soar_mlp_aware_slowdown(unadjusted_slowdown, AOL, 
np.array(all_together['Slow down (%)'])) 
                                                  #np.array(all_together['Absolute increase in cycles'])) # /all_together['Cycles'])
            #exit(0)
            print("Moment interval",1000*np.mean(np.array(all_together['Cycles'])/3e9), 1000*np.max(np.array(all_together['Cycles'])/3e9),1000*np.min(np.array(all_together['Cycles'])/3e9))
            #exit(0)
            commitedL3Misses = np.array(all_together['Commited loads'])
            cycles_with_demand_read_0 = np.array(all_together['cyclesWithMemrequests']) #aggregate_op(glob_0['cyclesWithMemrequests'][:last_idx])
            number_of_demand_reads_0 = commitedL3Misses # aggregate_op(glob_0['commitedLoads'][:last_idx])
            AOL = cycles_with_demand_read_0/number_of_demand_reads_0 
            # OPTIMAL A AND B  0.43693970453381986 -2.7944993991898
            # 0.020198280396840813 -0.00890232139828185
            soo =  obtain_soar_mlp_aware_slowdown(unadjusted_slowdown, AOL, 
np.array(all_together['Slow down (%)']), 

np.array(all_together['commitedL3Misses']), all_together

) 
            

            """
            if REGRESS_SOAR:
                unadjusted_slowdown = np.array(all_together['Core Load bound stalls'])/np.array(all_together['Cycles'])
                commitedL3Misses = np.array(all_together['commitedL3Misses'])
                cycles_with_demand_read_0 = np.array(all_together['L3cyclesWithMemrequests']) #aggregate_op(glob_0['cyclesWithMemrequests'][:last_idx])
                number_of_demand_reads_0 = commitedL3Misses #aggregate_op(glob_0['commitedLoads'][:last_idx])
                AOL = cycles_with_demand_read_0/number_of_demand_reads_0 
                AOL = np.nan_to_num(AOL, nan=1, posinf=1, neginf=1) 
                print("L3 version")
                # 3.0395898375259094 7.071662176080066 point 
                #  2.834606019375835 9.84061672967524
                soo =  obtain_soar_mlp_aware_slowdown(unadjusted_slowdown, AOL, 
    np.array(all_together['Slow down (%)']), 

    np.array(all_together['commitedL3Misses']), all_together

    ) 

            #exit(0)
            #"""
            #exit(0)
            
            #"""
            print("Thinking about plotting", k )
            if KEY_PLOT:
                if not HIGH_PRIORITY_KEYS(k):
                    return
            AGG_FUNCTIONS = []
            folder = DEST
            if 'folder' in EXTRA:
                folder=EXTRA['folder']
            sf = EXTRA['sf']  if 'sf' in EXTRA else ''
            title = "" if not 'title' in EXTRA else EXTRA['title']
                
        
            print("About to plot", k )
            x_axis = np.array(all_together[x_key])
            if ERROR_VIEW:
                x_key='Non Load/Store bound cycles'
                x_key='non_memory_stalls'
                #x_axis = all_together[]

                x_axis = all_together[x_key]

            y_axis = np.array(all_together[k])

            
            

            # do cdf of slow down (plot global_slwo down in black, and the metric in white) 
            COLOR_BY_LLC = False
            def plot_access_count_over_latency():
                lat_threshold = []
                count = []
                #fcount = []
                #scount = []
                color = []
                for n in range(0,16):
                    lat_threshold.append(n*16)
                    lat_threshold.append((n+0.5)*16)
                    count.append(np.sum(all_together['fcount' + str(n)])) # includes all accesses above threshold
                    color.append('blue')
                    count.append(np.sum( all_together['scount' + str(n)] ))
                    color.append('orange')
            
                plt.xticks([n*16 for n in range(0,16)])


                
                def p(unit):
                    plt.xlabel("Access detetection threshold")
                    plt.ylabel("Number of accesses" + unit)
                    plt.title("Number of accesses in function of sampling threshold")
                    plt.legend()
                    import matplotlib.patches as mpatches
                    legend_patches = [
                mpatches.Patch(color='orange', label='Slow tier' ),
                mpatches.Patch(color='blue', label='Fast tier' )
                    ]
                    plt.legend(handles=legend_patches, loc='upper left')

                    file = (
                        f'./_finos/fii/{folder}/{sf}_ACCESS_DIST_' + unit + DATASET_S +    ".svg"
                    )
                    print("SAVED FIG TO ", file)
                    print("Saved FIG TO ", file)
                    plt.savefig(file)
                    plt.close()

                w = 16/2
                w = 16
                plt.figure(); plt.bar(lat_threshold, np.log(np.array(count)), width=w, color=color)
                p(unit=" (log)")
                plt.figure(); plt.bar(lat_threshold, np.array(count), width=w, color=color)
                p(unit="")

            AGG_FUNCTIONS.append(plot_access_count_over_latency)
            if LIMIT_BY_AGG:
                for f in AGG_FUNCTIONS:
                    f()



            def view_error_over_x(x,slowdown, residuals,label, BY_MEAN=True, PROPORTION_ERROR=False, ABS=False):
                sorted_indices = np.argsort(slowdown)
                slowdown_sorted = slowdown[sorted_indices]
                residuals_sorted = residuals[sorted_indices]
                cumsum_residuals = np.cumsum(residuals_sorted)


                n = len(slowdown_sorted)
                # number of bins
                N = 20*100  # points per bin (slowdown interval in terms of count)
                n_bins = int(np.ceil(n / N))
                
                bin_x = []
                bin_y = []


                if not ABS:
                    bin_x = slowdown_sorted
                    bin_y = cumsum_residuals
                else:
                    for i in range(n_bins):
                        start = i * N
                        end = min((i + 1) * N, n)
                        s_chunk = slowdown_sorted[start:end]
                        r_chunk = residuals_sorted[start:end]

                        rm = r_chunk.mean()
                        sm = s_chunk.mean()
                        if PROPORTION_ERROR:
                            v = min(100*(rm/sm), 2000)
                            v = max(-2000, v)
                            bin_y.append(v)
                        else:
                            bin_y.append(rm)
                        bin_x.append(sm)

                
                bin_x = np.array(bin_x)
                bin_y = np.array(bin_y)
                if not BY_MEAN:
                    bin_x = slowdown_sorted
                    bin_y = residuals_sorted


                linewidth=0.5
                if ">=" not in label: 
                    linewidth=1
                else:
                    if " 0 " in label:
                        linewidth=2
                    if "MLP" in label:
                        linewidth=4
                    if "Memory" in label:
                        linewidth=4
                
                if "Core" in label:
                    linewidth=5

                linestyle=("--" if "LLC" in k else "-")
                linestyle=("--" if "Memory" in k else linestyle)
                linestyle=("--" if "Memory" in label else linestyle)

                if "∆" in label:
                    linestyle="--"
                    linewidth=3
                plt.plot(bin_x, bin_y, label=label, linestyle=linestyle, linewidth=linewidth)
            if "%" in x_key and "user" in NORM: 
                #if "Absolute increase in cycles" in x_key and "NONE" in NORM: 
                def normalize_llc(k):
                    return k.replace("(LLC misses)", "").strip()
                def r_errors(k, REGRESS_MODE=SLOWP):
                    global all_errors
                    #x_key = "Absolute increase in cycles"
                    r = all_together[k]
                    #if k.endswith("Instruction Stall Cycles") or k.endswith("Instruction Stall cycles"):
                    if REGRESS_MODE == SLOWP:
                        x_axis = all_together[SLOWP]
                    else:
                        x_axis = all_together[ABS]
                    y_axis = all_together[k]

                    min_x = np.min(x_axis)
                    max_x = np.max(x_axis)
                    bin_sizex = (max_x - min_x)*0.99999

                    min_y = np.min(all_together[k])
                    max_y = np.max(all_together[k])
                    bin_sizey = (max_y - min_y)*0.99999
                    # discretize results to the bins
                    new_x = ( (x_axis // bin_sizex) *bin_sizex) + bin_sizex*0.5
                    new_y = (y_axis // bin_sizey)*bin_sizey + bin_sizey*0.5
                    from scipy.stats.mstats import winsorize
                    new_x = x_axis # winsorize(x_axis, limits=[0.01, 0.01])
                    new_y = winsorize(y_axis, limits=[0.01, 0.01])
                    def obt_limo(a):
                        min_a = np.min(a)
                        max_a = np.max(a)
                        dif = max_a - min_a
                        percent_scale = a/dif
                        return percent_scale
                    #new_x = obt_limo(new_x)
                    #new_y = obt_limo(new_y)
                    #new_x = x_axis
                    #new_y = y_axis
                    # for each percent in percent scale, average 
                        
                        # Counting all instructions stall cycles leads to severe over count. However, when MLP is con
                        # 
                        # Instruction stall cycles is WORST than LLC count. Despite providing mroe informtion, the overlaps are bad.
                        # 





                    

                    SCALE=1
                    try:
                        regress, residuals, rank, singular_values, rcond  = np.polyfit(new_y*SCALE, new_x, 1, full=True)
                        all_errors = residuals
                    except:
                        raise Exception("Blackkk")
                    # calculate results from poly
                    ru = np.array((new_y*SCALE))* regress[0]  + regress[1]
                    #ru = np.clip(ru, -0.30,300)
                    BY_MEAN = len(new_x)
                    BY_MEAN = 1
                    ru = np.abs( (ru - new_x)/BY_MEAN) # **2 <-- not squared.. 
                    out1,out2,out3 = new_y*SCALE,new_x, ru

                    SSE = np.sum( (ru - new_x)**2 )
                    #SSE = residuals[0]
                    SSE = np.sum( np.abs((ru - new_x)) )
                    MSE = SSE / len(x)  # Mean Squared Error
                    RMSE = np.sqrt(MSE) /SCALE

                    # cat regress_errors  | grep REGRESS | awk '{print $NF " " $0 }' | sort  -n | grep "%"
                    print("REGRESS ERROR ", k, x_key, SSE/SCALE, "MSE", MSE/SCALE, "RMSE", RMSE, SSE)
                    return out1,out2,out3
            
            #else:
            #    return
            # calculate regression error
                def should_include(o):
                    if "Middle" in o or "End" in o or "Start" in o or "Average" in o or "Instruction Soar" in o:
                        return False
                    if "Soar" in o:
                        return False
                    if (("Slow" in o or "Instruction" not in o)) and not (o == "LLC count") and not ("Soar" in o or "SOAR" in o): 
                        return False
                    return True

                COLOR_BY_LLC=True
                # LLC miss 


                def plot_llc_diff():


                    plt.figure(figsize=(7,7)) #  figsize=(10,10) ) 
                    plt.rcdefaults()
                    pairs = {}

                    want = [k for k in all_together.keys() if "Memory" in k]
                    for o in all_together:
                        wantt = False
                        wantt = wantt or o in want
                        want = [k for k in all_together.keys() if "Soar" in k]
                        wantt = wantt or o in want
                        want = [k for k in all_together.keys() if 'Core Stall Cycles' in k]
                        wantt = wantt or o in want
                            
                        if "Slow" in o:
                            continue
                        if "Instruction Stall cycles" not in o:
                            if "LLC count" in o:
                                continue
                            if not should_include(o):
                                continue
                        label = normalize_llc(o)
                        try:
                            out = r_errors(o)
                        except Exception as e:
                            print(e) # if it could not converge.. big rip
                            continue
                        if label in pairs:
                            pairs[label].append([*out,o])
                        else:
                            pairs[label] = [[*out,o]]
                    for label in pairs.keys():
                        try:
                            diff_err =  np.abs(pairs[label][0][2] - pairs[label][1][2])
                        except IndexError:
                            #print(len(pairs[label])) print(len(pairs[label][0])) print(len(pairs[label][1])) print(f"Skipping {label}: not enough data points")
                            continue
                        print(pairs[label][0][-1], pairs[label][1][-1])
                        view_error_over_x(
                            pairs[label][0][0],
                            pairs[label][0][1],
                             diff_err, label )
                    plt.legend(loc='upper left')
                    plt.title("Cumulative absolute prediction error over slow down")
                    plt.ylabel("Cumulative error")
                    plt.xlabel("Slow down")
                    plt.savefig("./_finos/fii/__LLC_DIFF_3ALLCLIPED" + "_" + DATASET_S + "__global_slowdown_cdf.png")
                    print("Saved fig",("./_finos/fii/__LLC_DIFF_2ALLCLIPED" + "_" + DATASET_S + "__global_slowdown_cdf.png"))
                    plt.close()
                    #exit(0)

                    plt.figure(figsize=(7,7)) #  figsize=(10,10) ) 
                    plt.rcdefaults()
                    pairs = {}

                    for o in all_together:
                            
                        if "Slow" in o:
                            continue
                        if "Instruction Stall cycles" not in o:
                            if "LLC count" in o:
                                continue
                            if not should_include(o):
                                continue
                        label = normalize_llc(o)
                        try:
                            out = r_errors(o)
                        except Exception as e:
                            print(e) # if it could not converge.. big rip
                            continue
                        if label in pairs:
                            pairs[label].append([*out,o])
                        else:
                            pairs[label] = [[*out,o]]
                    for label in pairs.keys():
                        try:
                            diff_err =  np.abs(pairs[label][0][2] - pairs[label][1][2])
                        except IndexError:
                            #print(len(pairs[label])) print(len(pairs[label][0])) print(len(pairs[label][1])) print(f"Skipping {label}: not enough data points")
                            continue
                        print(pairs[label][0][-1], pairs[label][1][-1])
                        view_error_over_x(
                            pairs[label][0][0],
                            pairs[label][0][1],
                             diff_err, label )
                    plt.legend(loc='upper left')
                    plt.title("Cumulative absolute prediction error over slow down")
                    plt.ylabel("Cumulative error")
                    plt.xlabel("Slow down")
                    plt.savefig("./_finos/fii/__LLC_DIFF_2ALLCLIPED" + "_" + DATASET_S + "__global_slowdown_cdf.png")
                    print("Saved fig",("./_finos/fii/__LLC_DIFF_2ALLCLIPED" + "_" + DATASET_S + "__global_slowdown_cdf.png"))
                    plt.close()
                    #exit(0)
                def setup_fig():
                    plt.figure(figsize=(7,7)) #  figsize=(10,10) ) 
                    plt.rcdefaults()
                def end_fig(s="", PROPORTION_ERROR=False, ABS=True):
                    plt.legend(loc='upper left')
                    plt.ylabel("Cumulative error")
                    plt.xlabel("Slow down")
                    plt.title("Average prediction error over real slow down")
                    if ABS:
                        plt.ylabel("Error")
                    else:
                        plt.title("Cumulative absolute prediction error over slow down")
                        plt.ylabel("Cumulative error")
                        
                    if PROPORTION_ERROR:
                        plt.title("Average prediction error over real slow down")
                        plt.ylabel("Error (%)")
                        plt.ylim(0, 100)
                    e = "Absolute"     if ABS else "Cumulative"

                    #'title': n + " - " + k, 'folder': f"PER_BENCH/{n}"
                    #save_fig(
                    file = (
                        f'./_finos/fii/{folder}/{sf}_{"P" if PROPORTION_ERROR else "A"}_error_over_slow' + e +str(s) + DATASET_S +    ".png"
                    )
                    print("SAVED FIG TO ", file)
                    plt.savefig(file)
                        #"./_finos/fii/" + str(s) +  "__nonsq2ALLCLIPED" + k.replace("/", "D") + "__global_slowdown_cdf.png")



                def error_by_threshold(PROPORTION_ERROR=True,ABS=True):
                    setup_fig()
                    for o in list(all_together.keys()):
                        if o not in  ["∆ Core Stalls Cycles", "∆ Core Memory bound stalls", "Instruction Stall cycles/MLP",  
                                                                  "Δ Instruction Stall cycles/MLP",
                                                                  "Δ Instruction Stall cycles/MLP ", "LLC count"
                                                                  ]:
                            #if not ("Instruction" in o and "MLP" in o):
                            # MARKER
                                if not ("Soar" in o and "prop" in o):
                                    if "mlpCost" not in o: #and ( "mlpCost" not in o and not ( "MLP" in o and "Instruction" in o) ):
                                        continue
                                    if "Start" in o or "End" in o or "Middle" in o:
                                        continue

                        if "mlpCost" in o:
                            i = int(o.split("mlpCost")[1])*16
                            _o = " >= " + str(i) + " cycles"
                            if i != 0 and i not in  [96, 176 ,192, 240]:
                                if i > 192:
                                    continue
                                if i < 47:
                                    continue
                                if i > 81:
                                    continue
                            all_together[str(_o)] = all_together[o]
                            o = _o

                        try:
                            view_error_over_x(*r_errors(o, ),o,PROPORTION_ERROR=PROPORTION_ERROR,ABS=ABS)
                        except Exception as e:
                            print("SADLY I COULD NOT REGERSS", o)

                    end_fig(f"__ZERO_INC_CostBY_interpret_mean", PROPORTION_ERROR=PROPORTION_ERROR,ABS=ABS)

                if BY_MOMENT and not KEY_PLOT:
                    for ABS in [False, True]:
                        error_by_threshold(PROPORTION_ERROR=False, ABS=ABS)
                        error_by_threshold(PROPORTION_ERROR=True, ABS=ABS)
                    #print("DONE")
                    #exit(0)
                    #return
                    
                SKIP_REGRESS = False
                print("Should do it?",not SKIP_REGRESS and not KEY_PLOT and BY_MOMENT)
                if not SKIP_REGRESS and not KEY_PLOT and BY_MOMENT:
                                    

                    plot_llc_diff()
                    plt.figure(figsize=(7,7)) #  figsize=(10,10) ) 
                    plt.rcdefaults()
                    def should_include(o):
                        keys = [
                        'Soar','Core LLC stalls',
                        'Soar slowdown (LLC misses)',
                        'Core Memory bound stalls',
                        'Core LLC stalls',
 #'mlpCost', 'Instruction Soar', "LLC count", "Instruction Stall cycles", "Instruction Stall cycles/MLP", "Δ Instruction Stall cycles/MLP",
                            #"Δ Instruction Stall cycles/MLP (LLC misses)",
                            #"Δ Instruction Stall cycles",
                            #"Instruction Stall cycles/MLP (LLC misses)",
                            #"Instruction Stall cycles (LLC misses)",
                        ]
                        if any(_ in o for _ in keys):
                            return True
                        return False


                    for o in all_together:
                        #if "Core Stalls Cycles" in o: # The best core metric!
                        #r_errors(o)
                        #    continue
                        if not should_include(o):
                            continue

                        #r_errors(pairs[k])

                        try:
                            view_error_over_x(*r_errors(o),o)
                        except:
                            continue
                        

                    plt.legend(loc='upper left')
                    plt.title("Cumulative absolute prediction error over slow down")
                    plt.ylabel("Cumulative error")
                    plt.xlabel("Slow down")
                    i = "./_finos/fii/_1lol__nonsq2ALLCLIPED" + k.replace("/", "D") + DATASET_S + "__global_slowdown_cdf.png"
                    plt.savefig(i)
                    print("Saved fig",i)

                    

                    #plt.figure()
                    plt.close()
                #exit(0)
            else:
                pass
                #return


                

            

            #for x_var in x_keys :
            #    x_axis = all_together[x_var]

            if False and not KEY_PLOT:
                regress = np.polyfit(x_axis, all_together[k], 1)
                #print(regress[0], all_together['global_slowdown'])
                new_k = np.array((x_axis))* regress[0]  + regress[1]
                r = new_k
                
                sorted_slowdown = np.sort(x_axis)
                plt.plot(sorted_slowdown, np.arange(len(sorted_slowdown)) / len(sorted_slowdown), color="black")
                sorted_slowdown = np.sort(r)
                plt.plot(sorted_slowdown, np.arange(len(sorted_slowdown)) / len(sorted_slowdown), color="red")
                #plt.savefig("./_finos/fii/9cdfREG" + k.replace("/", "D") + "__global_slowdown_cdf.png")
                plt.close()
                    #return

            
            def define_size_and_alpha():
                if BY_MOMENT:
                    alfa = 0.1
                    size=0.1
                    size=0.5
                else:
                    size=1
                    alfa = 0.7
                if INTENSITY_metric is not None:
                    alfa = 1
                    size=0.005
                if not BY_MOMENT:
                    size=10
                return [alfa, size]
            def do_legend():
                if 'leg' in EXTRA and not EXTRA['leg']:
                    return
                import matplotlib.patches as mpatches
                if INTENSITY_metric is not None:
                    m = all_together[INTENSITY_metric] # /all_together['Commited loads'] #all_together['Core Stall Cycles']

                    legend_patches = [
            mpatches.Patch(color=plt.cm.hot(intensity), label=f'{benchset} (intensity: {intensity:.2f})' )
                    for benchset, intensity in zip(benchsetsHUMAN, m/np.max(m))
                    ]
                else:
                    legend_patches = [mpatches.Patch(color=color, label=benchset ) 
                                    for benchset, color in zip(benchsetsHUMAN, colors)]
                plt.legend(handles=legend_patches, loc='upper left', **plt_args)

           
            def save_fig(path):
                print('Saved fig to ', path)
                #path = path.replace("∆", "DELTA")
                _ = path.split("/")[-1].replace(" ", "_")
                __ = path.split("/")
                __[-1] = _
                path = "/".join(__)
                ext = ".svg" #".png"
                path += DATASET_S + ext
                plt.savefig(path)
                plt.close()
                print('Saved fig to ', path)

            def do_scatter(x,y, percentage=1, slicee=None, size=1, alfa=1):
                print("Doing the scatter...", x)
                #limit = int(len(x)*percentage)+1
                if slicee:
                    limit=slicee
                #print(np.sum(final_colors[:limit] == "green"))
                # median 
                #print("NUMBER OF DPS", len(x[:limit]) )
                median = 1 # np.sort(y[:limit])[int(limit/2)]

                #plt.xlim(np.min(x), np.max(x))
                yu  = y #[:limit]
                #yu  = np.full( len(y[:limit]), 1) #/median
                c = final_colors #[:limit] 
                if 'sf' in EXTRA:
                    c = 'orange'
                if 'size' in EXTRA:
                    size = EXTRA['size']
                if 'alfa' in EXTRA:
                    alfa = EXTRA['alfa']


                factor = 1 if NORM != "user" else 100
                plt.tick_params(axis='both', which='major', labelsize=14)


                ind = np.array(x) != 0
                from scipy.stats.mstats import winsorize
                AOL_BIG = False
                if AOL_BIG:
                    factor = 1
                    plt.scatter(
                        winsorize(
                            np.array(x)[ind]*factor,
                            limits=[0, 0.01]),

                            
                    winsorize(
                                1/np.array(y)[ind]*factor,
                            limits=[0, 0.1])
                                , s=size, alpha=alfa) # , c=final_colors[ind]) 
                else:

                    
                    def r_errors(k, REGRESS_MODE=SLOWP):
                        global all_errors
                        #x_key = "Absolute increase in cycles"
                        r = all_together[k]
                        #if k.endswith("Instruction Stall Cycles") or k.endswith("Instruction Stall cycles"):
                        if REGRESS_MODE == SLOWP:
                            x_axis = all_together[SLOWP]
                        else:
                            x_axis = all_together[ABS]
                        y_axis = all_together[k]

                        min_x = np.min(x_axis)
                        max_x = np.max(x_axis)
                        bin_sizex = (max_x - min_x)*0.99999

                        min_y = np.min(all_together[k])
                        max_y = np.max(all_together[k])
                        bin_sizey = (max_y - min_y)*0.99999
                        # discretize results to the bins
                        new_x = ( (x_axis // bin_sizex) *bin_sizex) + bin_sizex*0.5
                        new_y = (y_axis // bin_sizey)*bin_sizey + bin_sizey*0.5
                        from scipy.stats.mstats import winsorize
                        new_x = x_axis # winsorize(x_axis, limits=[0.01, 0.01])
                        new_y = winsorize(y_axis, limits=[0.01, 0.01])
                        def obt_limo(a):
                            min_a = np.min(a)
                            max_a = np.max(a)
                            dif = max_a - min_a
                            percent_scale = a/dif
                            return percent_scale

                        SCALE=1
                        try:
                            regress, residuals, rank, singular_values, rcond  = np.polyfit(new_y*SCALE, new_x, 1, full=True)
                            ru = np.array((new_y*SCALE))* regress[0]  + regress[1]
                            all_errors =  (ru - new_x)
                        except:
                            raise Exception("Blackkk")
                        # calculate results from poly
                        #ru = np.clip(ru, -0.30,300)
                        BY_MEAN = len(new_x)
                        BY_MEAN = 1
                        ru = np.abs( (ru - new_x)/BY_MEAN) # **2 <-- not squared.. 
                        out1,out2,out3 = new_y*SCALE,new_x, ru

                        SSE = np.sum( (ru - new_x)**2 )
                        #SSE = residuals[0]
                        SSE = np.sum( np.abs((ru - new_x)) )
                        MSE = SSE / len(x)  # Mean Squared Error
                        RMSE = np.sqrt(MSE) /SCALE

                        # cat regress_errors  | grep REGRESS | awk '{print $NF " " $0 }' | sort  -n | grep "%"
                        print("REGRESS ERROR ", k, x_key, SSE/SCALE, "MSE", MSE/SCALE, "RMSE", RMSE, SSE)
                        return out1,out2,out3
            

                #plt.xlim(0, 250)
                #print(np.max(x))
                #print(np.max(x))
                ##print(np.max(x))
                #print(np.max(x))
                #print(np.max(x))
                #plt.xlim(np.min(x[x != 0]), np.max(x[x != 0]))
                    if ERROR_VIEW:
                        r_errors(k)
                        yu = all_errors
                        yu = np.abs( all_errors)
                        
                        plt.xlabel("Non memory stalls")
                        plt.ylabel("Absolute prediction error")

                    print(len(x), len(yu), "BLA BLA ")

                    """
                    if LLC_ONLY:
                        ind = np.array(all_together['LLC count']) != 0
                    else:
                        ind = (np.array(all_together['LLC count']) != 0) & (np.array(all_together['LLC count']) == 0)

                    x=x[ind]
                    yu=yu[ind]
                    c=c[ind]
                    """



                    if BY_HOT:
                        c=all_together['average_mlp']
                        plt.scatter(x,yu*factor,s=size, alpha=alfa , c=c, cmap="hot")
                    else:
                        plt.scatter(x,yu*factor,s=size, alpha=alfa , c=c)
                    plt.xlim(np.min(x), np.max(x))
                
                #plt.xlim(10, 100)
                #plt.ylim(0, 1000)
                #plt.scatter(x[:limit][final_colors[:limit] == "green"],y[:limit][final_colors[:limit] == "green"],s=size, alpha=alfa , c="green") 
                print("Done with scatter")
                if not BY_MOMENT:
                    for i, label in enumerate(benchname):
                        continue
                        plt.annotate( benchnrrr[i] + label.split("/")[-1].split(".")[0], (x[i], y[i]), xytext=(5, 5), 
                                    textcoords='offset points', fontsize=10)

            if not KEY_PLOT:
                    return
            if not BY_MOMENT:
                plt.figure()
                #plt.figure(figsize=(20,20))
            else:
                plt.figure(figsize=(20,20))
            

            #print(all_together[k])
            alfa, size = define_size_and_alpha()
            from scipy.stats.mstats import winsorize
            print("Winsorizing data...")
            if not NO_WINSOR:
                all_together[k] = winsorize(np.array(all_together[k]), limits=[0, 0.01])
            if "Absolute" in x_key:
                x_axis = winsorize(np.array(x_axis), limits=[0, 0.005])
            
            print("Winsor done!")

            #all_together['global_slowdown']
            #plt.scatter(all_together['global_slowdown'], all_together[k], s=size, alpha=alfa , c=final_colors) 
            if BY_MOMENT or True:
                fontSize = 35
                plt.rcParams.update({'font.size': fontSize, 
                                    'axes.labelsize': fontSize,
                                    'axes.titlesize': fontSize,
                                    'xtick.labelsize': fontSize,
                                    'ytick.labelsize': fontSize,
                                    'legend.fontsize': fontSize,
                                    'figure.titlesize': fontSize})

                plt.tick_params(axis='x', labelsize=30)
                plt.tick_params(axis='y', labelsize=30)
            if '%' in x_key:
                plt.ticklabel_format(axis='x', style='plain')
            plt_args= ( {'fontsize':fontSize} if BY_MOMENT else {})
            do_legend()
            plt.xlabel(x_key, **plt_args)
            plt.ylabel(k, **plt_args)
            kind = ""
            if k.startswith("∆ Core "):
                plt.title("Slowdown relationship between the difference of fast and slow tier only metrics", **plt_args)
            elif k.startswith("Core "):
                plt.title("Relationship between fast tier CPU core metrics and slowdown", **plt_args)
            else:
                plt.title("Relationship between fast tier instruction level metrics and slowdown")
            plt.title("")    


            #plt.title(f"Relationship between CPU Core metrics and {'workload' if BY_MOMENT else 'global'} slow down ")
            print("Going to save plot")
            x_var_descriminator = ""

            if "Slow_down" not in x_key:
                x_var_descriminator = "-" + x_key
            do_scatter(x_axis, all_together[k],size=size, alfa=alfa)

            sf = EXTRA['sf']  if 'sf' in EXTRA else ''
            title = "" if not 'title' in EXTRA else EXTRA['title']
            if 'title' in EXTRA:
                plt.title(EXTRA['title'])
            save_fig(f'./_finos/fii/{folder}{"/LLC_ONLY_" if LLC_ONLY else ""}{sf}A__{"HOT_" if BY_HOT else ""}{"ERVIEW" if ERROR_VIEW else ""}{"BY_MOMENT" if BY_MOMENT else ""} {INTENSITY_metric if INTENSITY_metric else  ""} - {NORM} globos de ouroOO_OO_OO' + k.replace("/", "D") + " " + x_key.replace("/","D") + "_" + DATASET_S + '.png')
            print("Saved!")
            def hexa_plot():
                plt.figure(figsize=(20,20))
                print("Doing hexbin")
                plt.hexbin(all_together['global_slowdown'], all_together[k], gridsize=50, cmap="hot") 
                plt.savefig(f'./_finos/AHEXA---{"BY_MOMENT" if BY_MOMENT else ""} {INTENSITY_metric if INTENSITY_metric else  ""} - {NORM} globos de ouro' + k.replace("/", "D") + '.png'.replace(" ", "_") )
                plt.close()
                """
                plt.figure(figsize=(20,20))
                plt.hexbin(all_together['global_slowdown'], all_together[k], gridsize=50, cmap='hot') 
                plt.savefig(f'./_finos/AHEXA---{"BY_MOMENT" if BY_MOMENT else ""} {INTENSITY_metric if INTENSITY_metric else  ""} - {NORM} globos de ouro' + k.replace("/", "D") + '.png' )
                plt.close()
                """
            return

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
                plt.close()

            print('savefig')
            # ledged with benchstsHUMAN

    """
    if should_load_cached():
        k = "Soar slowdown"
        all_together = {k : np.load("./_finos/npys/" + k + ".npy"), 'global_slowdown' : np.load("./_finos/npys/" + 'global_slowdown' + ".npy")}
    else:
        to_cache = [ "global_slowdown", "Soar slowdown"]
        for k in to_cache:
            print(k , all_together[k])
            print(all_together[k])
            # np.save("./_finos/npys/" + k + ".npy", all_together[k])
    """
        

    #iterate_over_benches(data, valo)
    #all_together = {}

    # plot squash time 
    def save_fig(path):
        print('Saved fig to ', path)
        #path = path.replace("∆", "DELTA")
        _ = path.split("/")[-1].replace(" ", "_")
        __ = path.split("/")
        __[-1] = _
        path = "/".join(__)
        plt.savefig(path)
        print('Saved fig to ', path)
        plt.close()

    if  BY_MOMENT:
        # do a bar plot where, for each bench, 
        # we plot together a value from due_to_squash and from normal_slow 
        # we color bars by weather they came from due_to_squash or normal slow. we label X according to the bench
        # we label Y as % of moments with less squashed instructions in the slow tier
        
        n = len(_EDGE_bench)
        x = np.arange(n)
        width = 0.35  # bar width
        print(_EDGE_normal_slow)
        print(_EDGE_due_to_squash)

        if mode == "LLC_SHOW":
            pass


        def plott():
            # bars: green = normal_slow, red = due_to_squash
            bars_normal = plt.bar(x - width/2, y1,
                                width, label='Slowdown >= 1%', color='green')
            bars_squash = plt.bar(x + width/2, y2,
                                width, label='Slowdown < -1%', color='red')

            plt.xticks(x, _EDGE_bench, rotation=20, ha='right')
            plt.xlabel('Benchmark')
            plt.legend()
            # fig.subplots_adjust(top=0.88)  
            plt.tight_layout()
            plt.grid(axis='y', linestyle='--', alpha=0.3)

        y1 = _EDGE_normal_slow 
        y2 = _EDGE_due_to_squash 
        plt.figure()
        plott()
        plt.title("Slow tier impact on LLC detection")
        plt.ylabel('Increase in detected LLC misses (%)')
        plt.tight_layout()
        #plt.subplots_adjust(top=0.88, left=0.88)  
        save_fig("./_finos/fii/__speedup_llcWEIRD_SLOW.png")
        plt.close()

        y1 = sq__EDGE_normal_slow 
        y2 = sq__EDGE_due_to_squash 
        plt.figure()
        plott()
        plt.title("Slow tier impact on number of squashed instructions")
        plt.ylabel('Moments with less squashed instructions (%)')

        plt.tight_layout()
        #plt.subplots_adjust(top=0.88, left=0.88)  
        save_fig("./_finos/fii/__speedup_squsah_SLOW.png")
        plt.close()
        


    #print(len(all_together['global_slowdown']))

    
    """
    keys = []
    errors = []
    for k in all_together:
        try:
            regress, residuals, rank, singular_values, rcond  = np.polyfit(all_together['non_memory_stalls'], all_together[k], 1, full=True)
            SSE = residuals[0]
            keys.append(k)
            errors.append(SSE)
        except:
            continue
    # sort by the least error and print the top 10 
    results_df = pd.DataFrame({
    'column': keys,
    'SSE': errors,
    #'R_squared': r_squared
    }).sort_values('SSE', ascending=False)

    print("Top 10 predictors of non_memory_stalls:\n")
    print(results_df.tail(10).to_string(index=False))
    
    exit(0)
    """

    #x_keys = [SLOWP]
    #plot_keypair(list(all_together.keys())[0], all_together, BY_MOMENT, x, KEY_PLOT=True)

    def global_plots():
        print("Doing global global plots!")
        do_parallel = 2
        if do_parallel % 2 == 0:
            for x in x_keys:
                for k in all_together:
                    plot_keypair(k, all_together, BY_MOMENT, x)
            return
        from pathos.multiprocessing import Pool
        with Pool(10) as p:
            for x in x_keys:
                def f(k):
                    plot_keypair(k, all_together, BY_MOMENT, x)
                results = p.map(f, [k for k in all_together if not should_skip_key(k)])
        """
        for k in all_together:
            if should_skip_key(k):
                continue

            from pathos.multiprocessing import Pool
            #from multiprocessing import Pool

            for x in x_keys: #[ 'Slow down (%)', 'Absolute increase in cycles', 'Core Stall Cycles']:
                plot_keypair(k, all_together, BY_MOMENT, x)
        """


    corres = {}
    corres_agg = {}
    agg_slowp = []
    benchcor=[]
    benchcor_id=[]
    metric= []
    sane_cor =[]
    benchnrcor =[]
    def per_bench_f():
        for i,b in enumerate(per_bench):
            p = per_bench[i]
            n = benchname[i].split("/")[-1] 
            print("Doing bench ", n)
            #if 'imagi' in n: 
            #continue
                    

            for k in list(p.keys()):
                def correlate_llc_count_slowdown_per_bench(k):
                    #return
                    if BY_MOMENT:
                        if k not in ["LLC count", '∆ Instruction Stall cycles/MLP','Instruction Stall cycles/MLP', 'Instruction Stall cycles'
                                     "∆ Access Time", 'Instruction Soar', 'Soar', 
                                     'Soar slowdown1', 'Soar slowdown2', 'Soar slowdown3'
                                     ]:
                        #if not (  ("Instruction" and ( "Soar" in k or "MLP" in k ))  or "LLC Count" in k or "Access Time" in k):
                            return
                        if k not in corres:
                            corres[k] = []
                            corres_agg[k] = []
                        try:    
                            _ = robust_regress(k,p, p[SLOWP])[1]
                            corres[k].append(_)
                            sane_cor.append(_ )
                        except:    
                            sane_cor.append(0)
                            corres[k].append(0)
                        corres_agg[k].append(np.sum(p[k])) # sum of the metric
                        metric.append(k)
                        agg_slowp.append(np.sum(p["Absolute increase in cycles"])/np.sum(p['Cycles']))
                        benchcor.append(n)
                        benchcor_id.append(i)
                        benchnrcor.append(benchnrrr[i])
                correlate_llc_count_slowdown_per_bench(k)
                #continue
                
                for x in x_keys: #[ 'Slow down (%)', 'Absolute increase in cycles', 'Core Stall Cycles']:
                    #continue
                #if should_skip_key(k):
                #continue
                #for x in x_keys: #[ 'Slow down (%)', 'Absolute increase in cycles', 'Core Stall Cycles']:

                    #/home/ist196723/nas/osdi26/_finos/fii/
                    f = n + "-" + str(benchnrrr[i])
                    os.makedirs(f"/home/ist196723/nas/osdi26/_finos/fii/PER_BENCH/{f}/", exist_ok=True)
                    print("Doing key", k , "and x key",x ) # , len(p[k]), len(p[x]))


                    plot_keypair(k, p, BY_MOMENT, x, 
                                {'title': n + " - " + k, 'folder': f"PER_BENCH/{f}", 'sf' : n , 'size': 10, 'alfa': 1 , 'leg': False}, 
                                KEY_PLOT=BY_MOMENT # there is no scatter to do if we are considering only one bench and only it at the workload level  
                                )
                    break  
                #break

        def plot_correlation_per_bench():
            #print("EXITO")
            #exit(0)
            if not BY_MOMENT:
                return
                
            import pandas as pd
            import seaborn as sns
            import matplotlib.pyplot as plt
            plt.figure(figsize=(10,15))
            corres_agg_cor = {}
            rows = []
            corrLabel =  "Correlation w/Slowdown"
            #for k in corres:
            #    for i in range(len(corres[k])):
            #        rows.append({"Metric": str(k), corrLabel: corres[k][i], 'Bench' :get_color_bin( benchcor[i] ) , 'bid': benchcor_id[i] })
            """
            for k in corres_agg:
                #_ = dr(corres_agg_cor, k, robust_regress(k,corres_agg, agg_slowp)[1])
                print(corres_agg[k], "COOORR")
                for i in range(len(corres_agg[k])):
                    rows.append({"Metric": str(k), "Correlation w/Slowdown": corres_agg[k][i], 'Bench' : i })
            """
            #df = pd.DataFrame({corrLabel: sanerows).fillna(0)
            df = pd.DataFrame({corrLabel: sane_cor, 'Metric' : metric, 'bid' : benchcor_id}).fillna(0)
            df['Metric'] = pd.Categorical(df['Metric'])
            df['bid'] = pd.Categorical(df['bid'])
            print(df['Metric'], "mmmmmmmmm")
            #df = df.groupby('bid')[[  f for  f in df.columns if f != "bid" and f != "Metric" ]]
            xk = 'bid'
            for b in np.unique(df[xk]):
                s = df[xk] == b
                s = np.array(benchcor_id) == b
                #print(b, len(np.array(df[corrLabel][s])),len(np.array(df['Metric'][s])) )
                # convert NANs to -2
                #plt.plot(np.array(df['Metric'][s]), np.array(df[corrLabel][s]), marker='o', markersize=8)
                plt.plot(np.array(metric)[s], np.array(sane_cor)[s], marker='o', markersize=8, color=get_color_bin(benchname[b]))
                for i in range(len(np.array(metric)[s])):
                    print("!!!" if np.array(sane_cor)[s][i] < 0 else "", np.array(metric)[s][i], np.array(sane_cor)[s][i], benchname[b], np.array(benchnrcor)[s])
                #break


            # 45 deg ticks
            plt.xticks(rotation=45, ha='right')
            plt.ylabel('Correlation')
            plt.xlabel('Metric')
            plt.title('Correlation w/Slowdown')
            # beeswarm (swarm plot): k is category, value is numeric point
            """
            df.plot(
                
                   kind='line',
    marker='o',
    markersize=8,
    legend=True
            )
            
            sns.lineplot(data=df,
                             dashes=False,
                             markers=True,
                             markersize=8)
            .swarmplot(
                data=df,
                x="Metric",          # categorical axis (k)
                y="Correlation w/Slowdown",      # point value (_)
                hue=df['Bench'],
                size=4
            )
            """


                
            # X axis is overall correlation
            # Y axis is moment by moment correlation
            
            #plt.xlabel("Slowdown (%)")
            #plt.ylabel("Correlation")
            plt.legend() # Global corr (all together) versus  individual... <-- there is higher correlation when all are considered, given that within each bench everything is the same pretty much
            f = "./__correlation_NEWwithin_outside.png"
            plt.savefig(f)
            print("Saved fig to ",f)
        plot_correlation_per_bench()
    #exit(0)
    # 186233897
    # 290429200
    print("Doing global plots (not by key)(??)")

    def plot_aol():
        global AOL_BIG
        AOL_BIG = True
        for chave in [k for k in all_together.keys() if 'AOL' in k ]:
            xkey = chave 
            for ykey in [k for k in all_together.keys() if '/' in k and 'Slow Cycles' in k  ]: # ['Mem Stall Cycles/Slow Cycles',  "Fast LLC Stall Cycles/Slow Cycles"]: # this is K
                plot_keypair(ykey , all_together, BY_MOMENT, xkey, KEY_PLOT=True)
        exit(0)
    #plot_aol()
    global_plots()
    #exit(0)

    final_soar = [ 'SOAR', 'SOAR Abs']
    plot_keypair(final_soar[0] , all_together, BY_MOMENT, SLOWP, KEY_PLOT=True)
    plot_keypair(final_soar[1] , all_together, BY_MOMENT, ABS, KEY_PLOT=True)

    plot_keypair(list(all_together.keys())[0], all_together, BY_MOMENT, SLOWP, KEY_PLOT=False)

    #per_bench_f()
    #exit(17659693990)



    #return

    
    

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
    AOL = np.where(glob_0['commitedLoads'][:last_idx] == 0, 0, AOL) 
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

print("Current data  ")

import os
import numpy as np


#plot_r()
def cooling_is_bad():
    ratio = 8
    cooldown_period = 2_000_000

    ratios = [1, 2, 3, 4, 5, 6, 7]
    scores1 = {ratio: [] for ratio in ratios}
    scores2 = {ratio: [] for ratio in ratios}
    cooldown_period = 2_000_000


    weight1=1
    weight2=1

    for ratio in ratios:
        scores1[ratio].append(0)
        scores2[ratio].append(0)
        for n in range(0, 25):
            a1 = cooldown_period*ratio/(ratio+1)
            a2 = cooldown_period/(ratio+1)
            scores1[ratio].append(int(scores1[ratio][-1]/2) + a1*weight1)
            scores2[ratio].append(int(scores2[ratio][-1]/2) + a2*weight2)

    plt.figure()
    for ratio in ratios:
        scores1[ratio] = np.array(scores1[ratio])
        scores2[ratio] = np.array(scores2[ratio])
        plt.plot(scores1[ratio]/scores2[ratio], label=f'ratio {ratio}')
    plt.legend()
    plt.savefig(f'{FIGS_FOLDER}/cooling_is_bad.png')
    plt.close()
    
    
cooling_is_bad()
#quinta()
#exit(0)
import sys
if sys.argv[1].startswith("N"):
    sys.argv[1] = sys.argv[1][1:]
    print("evaling", " ".join(sys.argv[1:]))
    eval(" ".join(sys.argv[1:]))
    exit(0)


data = load_bench_data()
print("OLDO")

old_RUN_DATA_FOLDER= RUN_DATA_FOLDER
old_run_meta = run_meta

RUN_DATA_FOLDER="/mnt/nas/inesc/ist196723/osdi26/v4/results_gem5"
RUN_DATA_FOLDER_V4="/mnt/nas/inesc/ist196723/osdi26/v4/results_gem5"
#RUN_DATA_FOLDER="/mnt/nas/inesc/ist196723/osdi26/results_gem5"
run_meta=f"{RUN_DATA_FOLDER}/gem5_pids.txt"
print("V4 bench data!")
data_v4 = load_bench_data()
print("end V4 bench")

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

def dead_last():
    iterate_over_benches(data, aggregate_all_benchmarks)
    plot_global_results()

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

