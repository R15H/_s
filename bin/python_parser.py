from ctypes  import *
global_only = False

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

def obtain_weights(data, r):
    print("Obtaining weights for", r)
    l = load_aggregate_fields(data, r)
    l80 = load_aggregate_fields(data, r, 80)

    def split_data_by_instruction(nparray, instructions,l3_idx):
        new_arrays = []
        for i in instructions:
            idx = np.where((nparray !=  i))
            # zero out the array where idx is false
            new_arrays.append(np.intersect1d(l3_idx, idx))
            #new_arrays.append(nparray[idx])
        return new_arrays
    
    try:
        unique_instructions = np.unique(l['address'])
        d = {}
        for i in unique_instructions:
            d[i] = {'cost_inst_stall_time': 0,
            'cost_inst_L3stall_time': 0,
        'cost_inst_L3MLP': 0,
        'cost_inst_MLP': 0,
        'cost_inst_L3stall/total': 0,
        'cost_inst_3MLP/3stall': 0,
        'cost_inst_MLP/stall': 0,
        'cost_inst_MLP*total/stall': 0,
        'cost_inst_MLP/total': 0}

        l['accessBracket'] = l['accessBracket'] * 16
        l3_idx =np.intersect1d(np.where(l['count'] > 0),   np.where(l['accessBracket'] > 32) )# , np.where(l['tlbMiss'] == 0))
        #l3_idx = np.where(l['count'] > 0)
        idxs = split_data_by_instruction(l['address'], unique_instructions, l3_idx)

        i = 0
        for sel in idxs:
            inst = unique_instructions[i]
            length_sel = len(sel)
            if(length_sel == 0):
                continue
            #print("length_sel", length_sel)
            #print(np.sum(l['stallTime'][sel] / l['count'][sel]) / length_sel)
            #print(np.sum(l['stallTime'][sel]/l['count'][sel], dtype=np.float64) / length_sel)
            d[inst]['cost_inst_stall_time'] = np.sum(l['stallTime'][sel]/l['count'][sel], dtype=np.float64) / length_sel
            #print(int(d[inst]['cost_inst_stall_time']))
            d[inst]['cost_inst_L3stall_time'] = np.sum(l['L3stallTime'][sel]/l['count'][sel], dtype=np.float64) / length_sel

            d[inst]['cost_inst_L3MLP'] = np.sum(l['L3stallCyclesMLPLoad'][sel]/l['count'][sel], dtype=np.float64) / length_sel
            d[inst]['cost_inst_MLP'] = np.sum(l['stallCyclesMLPLoad'][sel]/l['count'][sel], dtype=np.float64) / length_sel

            d[inst]['cost_inst_L3stall/total'] = np.sum(l['L3stallTime'][sel]/l['count'][sel]/l['totalTime'][sel], dtype=np.float64) / length_sel
            d[inst]['cost_inst_L3stall'] = np.sum(l['L3stallTime'][sel]/l['count'][sel], dtype=np.float64) / length_sel

            d[inst]['cost_inst_3MLP/3stall'] = 10 #  np.sum(l['L3stallCyclesMLPLoad'][sel]/l['count'][sel]/l['L3stallTime'][sel], dtype=np.float64) / length_sel
            d[inst]['cost_inst_MLP*total/stall'] = np.sum(l['stallCyclesMLPLoad'][sel]*l['totalTime'][sel]/(l['stallTime'][sel]*l['count'][sel]), dtype=np.float64) / length_sel

            d[inst]['cost_inst_MLP/stall'] = np.sum(l['stallCyclesMLPLoad'][sel]/l['stallTime'][sel]/l['count'][sel], dtype=np.float64) / length_sel
            d[inst]['cost_inst_MLP/total'] = np.sum(l['stallCyclesMLPLoad'][sel]/l['totalTime'][sel]/l['count'][sel], dtype=np.float64) / length_sel
            """
            """
            #d[i]['cost_inst_delta'] = np.sum(
            #    (l80['stallTime'][idxs80[a]]/l80['count'][idxs80[a]]) - (l['L3stallTime'][sel]/l['count'][sel]))
            i+=1
        # do the mean across each metric
        total = {} # iterate through insts
        count = {} # iterate through insts
        smallest = {}
        for k in d:
            for k2 in d[k]: # iterate through keys
                if k2 not in total:
                    total[k2] = 0
                    count[k2] = 0
                    smallest[k2] = float('inf')
                total[k2] += d[k][k2]
                count[k2] += 1
                if d[k][k2] < smallest[k2]:
                    smallest[k2] = d[k][k2]
        for k in total:
            total[k] = total[k] / count[k]
        for k in d:
            for k2 in d[k]:
                change = total[k2]
                if smallest[k2]-1 < total[k2]:
                    change = smallest[k2]-1
                d[k][k2] -= change
            
        sorted_insts = sorted(unique_instructions)
        line = ""
        a = -1
        for sel in idxs:
            a += 1
            length_sel = len(sel)
            if(length_sel == 0):
                continue
            instruction  = sorted_insts[a]
            i = d[instruction]
            line += str(instruction) + " "
            line += str(int(i['cost_inst_stall_time'])) + " "
            line += str(int(i['cost_inst_L3stall_time'])) + " "
            line += str(int(i['cost_inst_L3MLP'])) + " "
            line += str(int(i['cost_inst_MLP'])) + " "
            line += str(int(i['cost_inst_L3stall/total'])) + " "
            line += str(int(i['cost_inst_3MLP/3stall'])) + " "
            line += str(int(i['cost_inst_MLP*total/stall'])) + " "
            line += str(int(i['cost_inst_MLP/stall'])) + " "
            line += str(int(i['cost_inst_MLP/total'])) + " "
            #line += str(i['cost_inst_delta']) + "\n"
            line += "\n"
    
        

        # basename of data[r]['0']['bench']
        binary =  os.path.basename(data[r]['0']['bench']) 
        print("Saving", f'{FIGS_FOLDER}/maps/{binary} {r}.txt')
        with open(f'{FIGS_FOLDER}/maps/{binary} {r}.txt', 'w') as f:
            f.write(line)

    except FileNotFoundError:
        print("... f not found..")
        return
    except Exception as e:
        print("Failed to obtain weights for", r)
        print(e)
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

def regress(arr, target):
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
    print("Stall regression", reg_stall[0])
    predicted = arr * reg_stall[0]
    # pad to biggest size
    predicted = np.pad(predicted, (0, biggest_size - predicted.shape[0]), 'constant')
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

    print(f"Fitted parameters:")
    print(f" a = {a_opt:.6f} ± {a_err:.6f}")
    print(f" b = {b_opt:.6f} ± {b_err:.6f}")

    # Optional: compute the fitted real_slow_down values
    fitted_real = fit_func(AOL, a_opt, b_opt)

    # Example: compute and print R-squared
    residuals = real - fitted_real
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((real - np.mean(real))**2)
    r_squared = 1 - ss_res / ss_tot
    print(f"R² = {r_squared:.6f}")
    return fitted_real

def calculate_by_sample_cost(data,r):
                def get_all_instructions():
                    #
                    d = load_aggregate_fields(data,r)
                    i = load_inst_fields(data,r)
                    inst = i
                    i80 = load_inst_fields(data,r,'80')
                    d['cost_inst_stall_time'] = np.sum(i['stallTime'])
                    d['cost_inst_L3stall_time'] = np.sum(i['L3stallTime'])
                    d['cost_inst_L3MLP'] = np.sum(i['L3stallCyclesMLPLoad'])
                    d['cost_inst_MLP'] = np.sum(i['stallCyclesMLPLoad'])

                    d['cost_inst_L3stall/total'] = np.sum(i['L3stallTime']/i['totalTime'])

                    d['cost_inst_3MLP/3stall'] = np.sum(i['L3stallCyclesMLPLoad']/i['L3stallTime'])
                    d['cost_inst_MLP/stall'] = np.sum(i['stallCyclesMLPLoad']/i['stallTime'])
                    d['cost_inst_MLP*total/stall'] = np.sum(i['stallCyclesMLPLoad']*i['totalTime']/i['stallTime'])
                    d['cost_inst_MLP/total'] = np.sum(i['stallCyclesMLPLoad']/i['totalTime'])


                    #d['cost_inst_diff_l3stall'] = np.sum(i80['L3stallTime']-i['L3stallTime'])
                    d['cost_inst_diff_stall'] = np.sum(i80['stallTime']-i['stallTime'])
                    d['cost_inst_diff_%L3MLP'] = np.sum((i80['L3stallCyclesMLPLoad']/i80['totalTime'])-(i['L3stallCyclesMLPLoad']/i['totalTime']))



                    d['L3stallTime80'] = get_field(data[r]['80'], AGGREGATE, 'L3stallTime', np.uint64)
                    d['stallTime80'] = get_field(data[r]['80'], AGGREGATE, 'stallTime', np.uint64)
                    d['totalTime80'] = get_field(data[r]['80'], AGGREGATE, 'totalTime', np.uint64)



                    # filter all indexes where accessBracket * 16 > 30
                    print(d['accessBracket'])

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




                    d['cost_inst_l3_mlp'] = np.sum(np.sqrt(inst['L3stallCyclesMLPLoad']*inst['L3stallTime']))
                    d['cost_inst_l3stall'] = np.sum(inst['L3stallTime'])
                    d['cost_inst_stall'] = np.sum(inst['stallTime'])
                    print("NUMBER OF SAMPLES", inst['L3stallTime'].shape)
                        


                    d['cost_avg_l3_stalls'] = calc_cost_simple('L3stallTime')
                    d['cost_avg_l3_mlp'] = calc_cost_simple('L3stallCyclesMLPLoad')
                    d['cost_l3_mlp'] = np.sum(d['L3stallCyclesMLPLoad'][l3_idx]*d['count'][l3_idx])

                    d['cost_delta_l3stall'] =  np.sum((d['L3stallTime80'][l3_idx]-d['L3stallTime'][l3_idx])*d['count'][l3_idx])
                    d['cost_delta_stall'] =  np.sum((d['stallTime80'][l3_idx]-d['stallTime'][l3_idx])*d['count'][l3_idx])
                    d['cost_delta_time'] =  np.sum((d['totalTime80'][l3_idx]-d['totalTime'][l3_idx])*d['count'][l3_idx])

                    d['cost_buffer_pressure'] = calc_cost_buffer_pressure('L3stallCyclesMLPLoad')  
                    
                    # COMPARE COST WITH --> GET THE SOAR WEIGHT FOR THIS INSTANT AND MULTIPLY BY THE SAMPLE
                    # sum(PER timestep nr _of samples *mem_stalls_0/cycles_0)
                    # sum(PER timestep adjusted soar * nr of samples  ) 

                    return d

                print('Cost....')
                d = get_all_instructions()
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
'commitedLoads': []
                  
                  }
    

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
inst_types={'address': np.uint64,'lastStallTime': np.uint64, 'L3stallCyclesMLPLoad': np.uint64, 'stallCyclesMLPBoth': np.uint64, 'MLP_store_at_start': np.uint8, 'MLP_store_at_end': np.uint8, 'MLP_load_at_start': np.uint8, 'MLP_load_at_end': np.uint8, 'L3MLP_store_at_start': np.uint8, 'L3MLP_store_at_end': np.uint8, 'L3MLP_load_at_start': np.uint8, 'L3MLP_load_at_end': np.uint8, 'L3MLP_store_at_middle': np.uint8, 'L3MLP_load_at_middle': np.uint8}
inst_fields = fields + ['lastStallTime']
def load_inst_fields(data, r, tier='0'):
    inst = DictWithGet()
    inst.set_getter(lambda f:get_field(data[r][tier], INST, f, np.uint64 if f not in inst_types else inst_types[f], convolve_skip=True))
    return inst
aggregate_types = {'totalTime': np.uint64, 'count': np.uint64, 'accessBracket': np.uint8, 'address': np.uint64}
global_types = {'totalSquashed': np.uint64,
    'L3stallCyclesMLPLoad': np.uint64,
    'stallCyclesMLPStore': np.uint64,
    'stallCyclesMLPBoth': np.uint64,
    'currentCycle': np.uint64, 'L3stalledCycles': np.uint64, 'stalledCycles': np.uint64, 'stalledCyclesDuringStore': np.uint64, 'stalledCyclesWithMemRequests': np.uint64, 'stalledCyclesWithStores': np.uint64, 'cyclesWithMemrequests': np.uint64, 'commitedStores': np.uint64, 'commitedLoads': np.uint64, 'commitedAtomic': np.uint64, 'commitedInstructions': np.uint64, 'totalSquashed': np.uint64, 'lastStallTime': np.uint64, 'currentCycle': np.uint64,  'tlbMisses': np.uint64}
def load_aggregate_fields(data, r, tier='0'):
    d = DictWithGet()
    d.set_getter(lambda f : get_field(data[r][tier], AGGREGATE, f, np.uint64 if f not in aggregate_types else aggregate_types[f], convolve_skip=True))
    return d 

def load_global_fields_final_pmu(data, r, tier='0'):
    d = DictWithGet()
    d.set_getter(lambda f : get_field(data[r][tier], GLOBAL, f, np.uint64 if f not in global_types else global_types[f], convolve_skip=True)[-1])
    return d 

def load_global_fields_crescendo(data, r, tier='0'):
    d = DictWithGet()
    d.set_getter(lambda f : get_field(data[r][tier], GLOBAL, f, np.uint64 if f not in global_types else global_types[f], convolve_skip=True))
    return d 
def load_global_fields(data, r, tier='0'):
    d = DictWithGet()
    d.set_getter(lambda f : fill_if_needed(get_field(data[r][tier], GLOBAL, f, np.uint64 if f not in global_types else global_types[f], convolve_skip=True)))
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
                calculate_by_sample_cost(data,r)
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

            
            
            final_cycles = get_field(data[r]['0'], GLOBAL, 'currentCycle', np.uint64)[-1]
            GOT = lambda g: (get_field(data[r]['80'], GLOBAL,g, np.uint64)[-1] - get_field(data[r]['0'], GLOBAL,g, np.uint64)[-1]) / final_cycles
            GOT_o = lambda g: (get_field(data[r]['80'], GLOBAL,g, np.uint64)[-1] - get_field(data[r]['0'], GLOBAL,g, np.uint64)[-1]) / final_cycles
            get_last = lambda g:(get_field(data[r]['0'], GLOBAL,g, np.uint64)[-1])
            
            global_results['real_slowdown'].append(GOT('currentCycle'))
            global_results['cycles'].append(GOT_o('currentCycle'))
            global_results['stall_cycles'].append(GOT_o('stalledCycles'))
            global_results['mem_stalls'].append(GOT_o('stalledCyclesWithMemRequests'))
            global_results['store_stalls'].append(GOT_o('stalledCyclesWithStores'))
            global_results['mem_stalls_weighted'].append(GOT_o('stallCyclesMLPLoad'))
            AOL = get_last('cyclesWithMemrequests')/get_last('commitedLoads')
            AOL = np.where(get_last('commitedLoads') == 0, 0, AOL) 
            global_results['aol'].append(AOL)

            global_results['commitedLoads'].append(get_last('commitedLoads'))
            

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
            print("MLP stall increase", mlp_stalls_0)
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
                print('DOOOOO')
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
            print("Stall regression", reg_stall[0])
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

            print("MLP regression", reg_mlp[0])
            # instead of trying to minimize the error in ALL points, try to minimize the error in 90% points closest to the median
            median = np.median(mlp_stalls_0)
            # find the 90% points closest to the median
            mlp_stalls_0_wout = mlp_stalls_0[np.abs(mlp_stalls_0 - median) < np.percentile(np.abs(mlp_stalls_0 - median), 90)]
            real_slow_down_wout = real_slow_down[np.abs(mlp_stalls_0 - median) < np.percentile(np.abs(mlp_stalls_0 - median), 90)]
            reg_mlp_wout = np.linalg.lstsq(mlp_stalls_0_wout.reshape(-1, 1), real_slow_down_wout, rcond=None)


            #reg_mlp_wout = np.linalg.lstsq(mlp_stalls_0_wout[200:].reshape(-1, 1), real_slow_down[200:], rcond=None)
            predicted_mlp_simple_wout = mlp_stalls_0 * reg_mlp_wout[0]
            print("MLP regression wout", reg_mlp_wout[0])

            

            

            



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
        if(commited_0.shape[0] <  50):
            continue # bad file
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
        continue


        

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

calculate_derivates(data)
print("did derivates")
#plot_global_results()
print("did global")


iterate_over_benches(data, obtain_weights)

bench_name="global"; bench_nr=""
#pot_errors(data,all_bench_loader, name="global")


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



