from ctypes  import *
global_only = False

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
RUN_DATA_FOLDER="/mnt/nas/inesc/ist196723/osdi26/results_gem5"


from sklearn.preprocessing import StandardScaler
from scipy.optimize import differential_evolution, minimize


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

def iterate_over_benches(data, function):
    global bench_nr
    global bench_name
    
    for r in data:
        bench_nr = data[r]['0']['benchnr']
        bench_name = data[r]['0']['bench'].split("/")[-1]
        if '0' not in data[r].keys() or '80' not in data[r].keys():
            print("Skipped run", list(data[r].values())[0]['benchnr'])
            continue
        function(data, r)
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
            key_to_plot = lambda k :  k.startswith('pred_') and k != 'real_slow_down'
            num_keys = len([k for k in res.keys() if key_to_plot(k)])
            # create figure with num_keys subplots
            #fig, axs = plt.subplots(num_keys, 1, figsize=(20, 20))
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
def plot_no_pred(data,loader,r=None, name=""):
    res = obtain_derivate_metrics(data,r, loader)
    key_to_plot = lambda k :  not k.startswith('pred_') and k != 'real_slow_down'
    num_keys = len([k for k in res.keys() if key_to_plot(k)])
    fig, axs = plt.subplots(num_keys, 1, figsize=(20, 40))
    #  current error index 0 is out of bounds for axis 0 with size 0
    if num_keys == 0:
        print("No keys to plot!!"*10)
        return
    i = 0
    for k in res.keys():
        if key_to_plot(k): 
            axs[i].scatter(res['real_slow_down'], res[k], label=k)
            axs[i].set_xlabel('Real Slowdown')
            axs[i].set_ylabel('Predicted ' + k)
            axs[i].set_title("Real vs Predicted Slowdown for " + bench_name + " " + bench_nr)
            i += 1
    f = f'{FIGS_FOLDER}/gen/pmu_pred/scatter_{name}.png'
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
    

def obtain_weights(data, r):
    print("Obtaining weights for", r)
    l = load_aggregate_fields(data, r)
    l80 = load_aggregate_fields(data, r, 80)
    #l = l80

    i = load_inst_fields(data, r)
    i80 = load_inst_fields(data, r, 80)

    by_instruction_sampling = True # '/mnt/nas/inesc/ist196723/osdi26/results_gem5/100227/
    if by_instruction_sampling:
        l = i
        l80 = i80

    def split_data_by_instruction(nparray, instructions,l3_idx):
        new_arrays = []
        for i in instructions:
            idx = np.where((nparray !=  i))
            # zero out the array where idx is false
            new_arrays.append(np.intersect1d(l3_idx, idx))
            #new_arrays.append(nparray[idx])
        return new_arrays
    
    try:

        if by_instruction_sampling:
            l3_idx = (np.where(l['totalTime']  > 30) & (l['isStore'] == 0) & (l['isLoad'] == 1)  & (l['tlb_miss'] == 0) ) # ignore TLB misses. we cannot optimize them 
            # np array of the same size as l['totalTime']
            l['count'] = np.ones_like(l['totalTime'])
        else:
            #accessBracket
            l['accessBracket'] = l['accessBracket'] * 16
            l3_idx = (np.where(l['accessBracket']  > 30) & (l['isStore'] == 0) & (l['isLoad'] == 1)  & (l['tlb_miss'] == 0) ) # ignore TLB misses. we cannot optimize them 
            #l3_idx =np.intersect1d(np.where(l['count'] > 0),   np.where(l['accessBracket'] > 32) )# , np.where(l['tlbMiss'] == 0))
        #l3_idx = np.where(l['count'] > 0)
        #idxs = split_data_by_instruction(l['address'], unique_instructions, l3_idx)
        unique_instructions = np.unique(l['address'][l3_idx])
        print("There ARE!", len(unique_instructions), "instructions and ", len(l['address']), "total")
        #print("unique_instructions", unique_instructions)
        d = {}
        for i in unique_instructions:
            d[i] = {}

        i = 0
        metrics = []
        for inst in unique_instructions:
            sel = np.where(l['address'] == inst)
            sel = np.intersect1d(sel, l3_idx)
            length_sel = len(sel)
            #print("length_sel", length_sel)
            #print(np.sum(l['stallTime'][sel] / l['count'][sel]) / length_sel)
            #print(np.sum(l['stallTime'][sel]/l['count'][sel], dtype=np.float64) / length_sel)
            d[inst]['Acost_inst_stall_time'] = np.sum(l['stallTime'][sel]/l['count'][sel], dtype=np.float64) / length_sel
            #print(int(d[inst]['cost_inst_stall_time']))
            d[inst]['Bcost_inst_L3stall_time'] = np.sum(l['L3stallTime'][sel]/l['count'][sel], dtype=np.float64) / length_sel

            d[inst]['Ccost_inst_L3MLP'] = np.sum(l['L3stallCyclesMLPLoad'][sel]/l['count'][sel], dtype=np.float64) / length_sel
            d[inst]['Dcost_inst_MLP'] = np.sum(l['stallCyclesMLPLoad'][sel]/l['count'][sel], dtype=np.float64) / length_sel

            #d[inst]['cost_inst_L3stall/stall'] = np.sum(l['L3stallTime'][sel]/l['count'][sel]/l['stallTime'][sel], dtype=np.float64) / length_sel
            #d[inst]['cost_inst_L3stall'] = np.sum(l['L3stallTime'][sel]/l['count'][sel], dtype=np.float64) / length_sel

            # TODO WHY??
            #d[inst]['cost_inst_3MLP/3stall'] = 10 #  np.sum(l['L3stallCyclesMLPLoad'][sel]/l['count'][sel]/l['L3stallTime'][sel], dtype=np.float64) / length_sel
            #d[inst]['cost_inst_MLP*total/stall'] = np.sum(l['stallCyclesMLPLoad'][sel]*l['totalTime'][sel]/(l['stallTime'][sel]*l['count'][sel]), dtype=np.float64) / length_sel

            d[inst]['Ecost_inst_MLP/stall'] = np.sum(l['stallCyclesMLPLoad'][sel]/l['stallTime'][sel]/l['count'][sel], dtype=np.float64) / length_sel
            d[inst]['Fcost_inst_MLP/total'] = np.sum(l['stallCyclesMLPLoad'][sel]/l['totalTime'][sel]/l['count'][sel], dtype=np.float64) / length_sel
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
    
        
        for quantization_level in range(10, 500, 10): # only cap the top at the last
            bins = np.array([ v for v in range(0, 500, quantization_level)]) #np.linspace(0, 500, quantization_level)
            for m in sorted(list(metricas_numpy.keys()))[0:1]:
                digitized = np.digitize(metricas_numpy[m], bins)
                diff =  np.insert(np.diff(digitized), 0, 1)
                compressed_map = digitized[diff != 0]
                #print("Compressed ",  len(compressed_map) / len(digitized), " times!")
        """
        """

        

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
        for m in ["const_inst_L3MLP"]:#metrics_names:
            metricas_finais[m] = np.copy(metricas_numpiadas[m])
            for mode in WEIGHT_MODES:
                metricas_finais["{}-{}".format(m, mode)] = statistical_weight(metricas_numpiadas[m], mode)
            metricas_finais["{}-{}".format(m, "lossless") ] = lossless_normalize_weight(metricas_numpiadas[m])
            metricas_finais["{}-{}".format(m, "lossy") ] = lossy_normalize_weight(metricas_numpiadas[m])

        """
        def serialize_weights(metricas_finais):
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
            

            #print_numerated_column(mmm)
            
            print("There are ", len(instructions), "instructions")
            for i in range(len(instructions)):
                out += str(int(instructions[i])) + " "
                for m in sorted(metricas_finais.keys()):
                        try:
                            print(str(int(metricas_finais[m][i])), " metric", m, "inst", instructions[i])
                            value = str(int(metricas_finais[m][i]))
                        except:
                            value = "1914"
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
            with open(f'{FIGS_FOLDER}/maps/{binary} {r}.txt', 'w') as f:
                f.write(out)
            return out 
            
        serialize_weights(metricas_numpy)


        
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

        

    except FileNotFoundError:
        print("... f not found..")
        import traceback
        traceback.print_exc()
        return
    except Exception as e:
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
            else:
                all_data[r_number][_['increase']] = _ 
            #_['global'] = load_struct(GlobalStatsss,glob.glob(f"/mnt/nas/inesc/ist196723/osdi26/results_gem5/global_{_['pid']}_{_['host']}*.bin")[0])
            #_['inst'] = load_struct(InstructionData,glob.glob(f"/mnt/nas/inesc/ist196723/osdi26/results_gem5/aggregate_{_['pid']}_{_['host']}*.bin")[0])
            #_['final'] = load_struct(FinalMetrics,glob.glob(f"/mnt/nas/inesc/ist196723/osdi26/results_gem5/inst_{_['pid']}_{_['host']}*.bin")[0])
                #f"/mnt/nas/inesc/ist196723/osdi26/results_gem5/output_{rdata["host"]}.bin")
    exit(0)

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

    

def load_bench_data():
    all_data = {}
    all_lines = []
    with open(run_meta, 'r') as file:
        for line in file:
            all_lines.append(line)


        for line in all_lines:
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
                print("WARNING: Duplicate increase", line)
            all_data[r_number][_['increase']] = _ 
            #_['global'] = load_struct(GlobalStatsss,glob.glob(f"/mnt/nas/inesc/ist196723/osdi26/results_gem5/global_{_['pid']}_{_['host']}*.bin")[0])
            #_['inst'] = load_struct(InstructionData,glob.glob(f"/mnt/nas/inesc/ist196723/osdi26/results_gem5/aggregate_{_['pid']}_{_['host']}*.bin")[0])
            #_['final'] = load_struct(FinalMetrics,glob.glob(f"/mnt/nas/inesc/ist196723/osdi26/results_gem5/inst_{_['pid']}_{_['host']}*.bin")[0])
                #f"/mnt/nas/inesc/ist196723/osdi26/results_gem5/output_{rdata["host"]}.bin")


    return all_data

import numpy as np
import matplotlib.pyplot as plt





def get_field(run, struct,field_name, type_, convolve_skip=False):
    if (run['pid'], struct, field_name) in cached_fields:
        return cached_fields[(run['pid'], struct, field_name)]
    arr =  np.fromfile(f"{RUN_DATA_FOLDER}/{run['pid']}/_{struct}_{field_name}_{run['pid']}.txt", dtype=type_)
    #print("Average window size", average_window_size)
    average_window_size = 250
    if not convolve_skip:
        arr = np.convolve(arr, np.ones(average_window_size)/average_window_size, mode='valid')
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
def obtain_soar_mlp_aware_slowdown(unadjusted, AOL, out):
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
                        d['cost_inst_L3MLP'] = np.sum(i['L3stallCyclesMLPLoad'][indexes]/inside_factor) / (cycles_elapsed*1024)
                        d['cost_inst_MLP'] = np.sum(i['stallCyclesMLPLoad'][indexes]/inside_factor) / (cycles_elapsed*1024)


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
inst_types={'tlb_miss': np.uint8,'isLoad': np.uint8,'isStore': np.uint8,'isMicroop': np.uint8,'address': np.uint64,'lastStallTime': np.uint16,'totalTime': np.uint16, 'stallTime': np.uint16, 'L3stallTime': np.uint16, 
            'L3stallCyclesMLPLoad': np.uint64, 'stallCyclesMLPBoth': np.uint64, 'MLP_store_at_start': np.uint8, 'MLP_store_at_end': np.uint8, 'MLP_load_at_start': np.uint8, 'MLP_load_at_end': np.uint8, 'L3MLP_store_at_start': np.uint8, 'L3MLP_store_at_end': np.uint8, 'L3MLP_load_at_start': np.uint8, 'L3MLP_load_at_end': np.uint8, 'L3MLP_store_at_middle': np.uint8, 'L3MLP_load_at_middle': np.uint8,

'start_cycle': np.uint64,
'L3stallTime': np.uint16,
'stallCyclesMLPLoad': np.uint64,
'stallCyclesMLPStore': np.uint64,
'stallCyclesMLPBoth': np.uint64,
            
            }
inst_fields = fields + ['lastStallTime']
def load_inst_fields(data, r, tier='0', stop=np.inf):
    inst = DictWithGet()
    def gettter(f, stop):
        field =  get_field(data[r][tier], INST, f, inst_types[f], convolve_skip=True)
        if f == 'start_cycle':
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
                   }
global_types = {'totalSquashed': np.uint64,
'totalStalledCyclesSummed': np.uint64,
'totalL3StalledCyclesSummed': np.uint64,
'totalL3MLPStalledCyclesSummed': np.uint64,
'totalMLPStalledCyclesSummed': np.uint64,
    'L3stallCyclesMLPLoad': np.uint64,
    'stallCyclesMLPStore': np.uint64,
    'stallCyclesMLPBoth': np.uint64,
    'currentCycle': np.uint64, 'L3stalledCycles': np.uint64, 'stalledCycles': np.uint64, 'stalledCyclesDuringStore': np.uint64, 'stalledCyclesWithMemRequests': np.uint64, 'stalledCyclesWithStores': np.uint64, 'cyclesWithMemrequests': np.uint64, 'commitedStores': np.uint64, 'commitedLoads': np.uint64, 'commitedAtomic': np.uint64, 'commitedInstructions': np.uint64, 'totalSquashed': np.uint64, 'lastStallTime': np.uint64, 'currentCycle': np.uint64,  'tlbMisses': np.uint64}

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
def load_global_fields(data, r, tier='0'):
    d = DictWithGet()
    d.set_getter(lambda f : fill_if_needed(get_field(data[r][tier], GLOBAL, f, global_types[f], convolve_skip=True)))
    return d 

def all_bench_loader(data,r):
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
            try:
                joined_arrays.append(load_global_fields(data,r)[f])
            except:
                pass
        iterate_over_benches(data, get_f) 
        return np.concatenate(joined_arrays)
    all_bench.set_getter(get_all)
    return all_bench


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


    

def obtain_derivate_metrics(data,r, loader):
    glob_0 = loader(data,r)
    glob_80 = loader(data,r)
    # depending on the load functions, we may be operating with integers or arrays!

    cycles_with_demand_read = glob_0['cyclesWithMemrequests'] 
    cycles_with_demand_read_80 = glob_80['cyclesWithMemrequests'] 
    number_of_demand_reads = glob_0['commitedLoads'] 
    glob_0['commitedLoads'][0] = 1
    print(glob_0['commitedLoads'])
    real_slow_down = glob_0['stalledCycles']/glob_0['currentCycle']
    #_ = glob_0['L3stallCyclesMLPLoad'] 
    #glob_0['L3stallCyclesMLPLoad']  = _/1024



    delta_store_stalls = (glob_80['stalledCyclesDuringStore'] - glob_0['stalledCyclesDuringStore'])/glob_0['currentCycle']
    #res['delta_store_stalls'] = delta_store_stalls
    predicted_store_stalls = regress(glob_0['stalledCyclesDuringStore'], real_slow_down)
    predicted_load_n_store_weighted = regress(glob_0['stallCyclesMLPBoth'] , real_slow_down)
    res = {'real_slow_down': real_slow_down}


    res['stalls_diff/fastCycles'] = (glob_80['stalledCycles'] - glob_0['stalledCycles']) / glob_0['currentCycle']
    res['l3stalls_diff/fastCycles'] = (glob_80['L3stalledCycles'] - glob_0['L3stalledCycles']) / glob_0['currentCycle']
    res['l3stalls(SoarSimple)'] = (glob_80['L3stalledCycles'] - glob_0['L3stalledCycles']) 

    res['mlp_stalls_diff/fastCycles'] = (glob_80['L3stallCyclesMLPLoad'] - glob_0['L3stallCyclesMLPLoad']) / glob_0['currentCycle']
    res['mlp_stalls_diff'] = (glob_80['L3stallCyclesMLPLoad'] - glob_0['L3stallCyclesMLPLoad']) 

    res['l3mlp/fastCycles'] = (glob_0['L3stallCyclesMLPLoad']/glob_0['currentCycle'])

    #res['l3mlp/fastCycles'] = regress(res['l3mlp/fastCycles'], real_slow_down) # SOAR LIKE

    res['weight_stalls_with_mlp'] = ( glob_0['L3stalledCycles'] / (glob_80['L3stallCyclesMLPLoad'] / glob_80['currentCycle']) ) 
    res['weight_stalls_with_mlp'] = np.where(glob_80['L3stallCyclesMLPLoad'] == 0, 0, res['weight_stalls_with_mlp'])
    
    #res['pred_weight_stalls_with_mlp'] = regress(weight_stalls_with_mlp, real_slow_down)
    # all indexes
    for k in list(res.keys()):
        if k == 'real_slow_down':
            continue
        res['pred_'+k] = regress(res[k], real_slow_down)


    AOL = glob_0['cyclesWithMemrequests']/glob_0['commitedLoads'] 
    AOL = np.where(glob_0['commitedLoads'] == 0, 0, AOL) 
    #AOL_80 = cycles_with_demand_read_80/number_of_demand_reads
    # TODO does AOL change in the slow tier? yes -> MLP changes wiht device latency
    unadjusted_slowdown = glob_0['stalledCycles']/glob_0['currentCycle']
    # fit unadjusted_slowdown * 1 / (a + b/AOL) =  real_slow_down to find a and b
    print(AOL)
    res['pred_soar_mlp'] = obtain_soar_mlp_aware_slowdown(unadjusted_slowdown, AOL, real_slow_down)

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
        global_results[k] = np.array(global_results[k])
    global_results['predicted_stall_cycles'] = regress( np.array(global_results['stall_cycles']),np.array(    global_results['mem_stalls']))
    var = np.array(global_results['mem_stalls_weighted'])/np.array(global_results['cycles']) #/ np.array(global_results['commitedLoads'] )

    global_results['predicted_mlp_simple'] = regress(var,np.array(global_results['real_slowdown']) ) / np.array(global_results['mem_stalls'])
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



    global_results['predicte d_load_n_store_weighted'] = multi_regress([  global_results['mem_stalls_weighted']/global_results['cycles'], global_results['store_stalls']/global_results['cycles'], ])
    global_results['predicte d_store_stalls'] = multi_regress([ global_results['store_stalls']/global_results['cycles'], ])

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
def simple_instruction_slowdown(data,r):
    global runs_with_weird_stuff

    i = load_inst_fields(data, r)
    i80 = load_inst_fields(data, r, '80')
    g0 = load_global_fields(data, r)
    g80 = load_global_fields(data, r, '80')
    try:
        last_idx = get_last_idx_of_smallest_vector(g80['currentCycle'],g0['currentCycle'])
        if len(g80['currentCycle']) == 0 or len(g0['currentCycle']) == 0:
            runs_with_weird_stuff += 1
            return
    except Exception as e :
        runs_with_weird_stuff += 1
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
        d['cost_inst_L3MLP'] = np.append(d['cost_inst_L3MLP'], np.sum(i['L3stallCyclesMLPLoad'][indexes]/inside_factor) / (cycles_elapsed*1024))
        d['cost_inst_MLP'] = np.append(d['cost_inst_MLP'], np.sum(i['stallCyclesMLPLoad'][indexes]/inside_factor) / (cycles_elapsed*1024))


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
        slowlyyy = stats.mstats.winsorize(slowlyyy, limits=[0.01, 0.01])
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

iterate_over_benches(data, simple_instruction_slowdown)
print("runs_with_weird_stuff", runs_with_weird_stuff)
exit(0)
#iterate_over_benches(data, simple_slow_sown)
print("runs_with_weird_stuff", runs_with_weird_stuff)
plot_merged()
exit(0)
do_important_plots(data)
exit(0)
print("obtaining weights...")
iterate_over_benches(data, obtain_weights)
    
iterate_over_benches(data, iterate_time_series)

print("runs_with_weird_stuff", runs_with_weird_stuff)
exit(0)
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

exit(0)
print("did derivates")
#plot_global_results()
print("did global")

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
                except Exception as e:
                    print("Error", e,e_count, bench_runs)
                    e_count+=1
                    pass # do not add this bench to the list



iterate_over_benches(data, aggregate_all_benchmarks)
correlate_all()


bench_name="global"; bench_nr=""
#pot_errors(data,all_bench_loader, name="global")


iterate_over_benches(data, lambda d,r: plot_sum_errors(d,lambda x: x, r) )
actually_plot_sum_errors()
#exit(0)

iterate_over_benches(data, lambda d,r:  pot_errors(data, load_global_fields, r, name="global_glob_point"))




bench_name="global"; bench_nr=""
plot_no_pred(data,all_bench_loader, name="global")
bench_name="global"; bench_nr=""
plot_pred(data,all_bench_loader, name="global")

print("did global")
#exit(0)

plot_global_sample_cost()
#learn( np.array(global_learn['inputs']), np.array(global_learn['results']) )

print(len(data.keys()))

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

combine_plots('j')



