# config.end.py — gem5 simulation config for memory-tiering experiments
#
# PURPOSE
#   gem5 board/system configuration used as the CONFIG argument when running
#   benchmarks.  Extends the X86 KVM boot flow with:
#     - Configurable DRAM size (--dramsize)
#     - Configurable latency increase for the slow-memory tier (--latency-increase)
#     - A skip-start duration to fast-forward past benchmark initialisation
#     - An execution timeout (--exec_timeout)
#     - flush_all_open_fds() helper to safely fsync all open file descriptors
#       before handing off to gem5 checkpointing
#
# USAGE
#   $GEM5 config.end.py <benchmark_binary> \
#       --latency-increase <ns> --bargs "<args>" --cpu-start KVM \
#       --dramsize=8GiB [--bstdin <file>]
#
# ROLE IN PIPELINE
#   Called by controller.sh (rungem5_with_report) as the CONFIG script.
#   Results are written to results_gem5/output_* and results_gem5/err_*.
#
# NOTE
#   The copyright header below applies to the original gem5 library template
#   this file was derived from (x86-ubuntu-run.py, UC Regents 2021).

# Copyright (c) 2021 The Regents of the University of California
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
This script utilizes the X86DemoBoard to run a simple Ubunutu boot. The script
will boot the the OS to login before exiting the simulation.

A detailed terminal output can be found in `m5out/system.pc.com_1.device`.

**Warning:** The X86DemoBoard uses the Timing CPU. The boot may take
considerable time to complete execution.
`configs/example/gem5_library/x86-ubuntu-run-with-kvm.py` can be referenced as
an example of booting Ubuntu with a KVM CPU.

Usage
-----

```
scons build/X86/gem5.opt
./build/X86/gem5.opt configs/example/gem5_library/x86-ubuntu-run.py
```
"""

#!/usr/bin/env python3
import os
import glob

def flush_all_open_fds():
    """Flush ALL open file descriptors for current process"""
    pid = os.getpid()
    fd_dir = f'/proc/{pid}/fd'
    
    try:
        # Get all numeric FDs (skip symlinks that fail)
        fds = [int(linkname) for linkname in os.listdir(fd_dir) 
               if linkname.isdigit()]
    except OSError:
        print("No /proc access or no fds found")
        return
    
    flushed = 0
    for fd in fds:
        try:
            # Skip stdin/stdout/stderr (0,1,2) if desired
            path = os.readlink(os.path.join(fd_dir, str(fd)))  # map fd → actual object
            #print(f"{fd}: {path}")
            if fd <= 2: 
                continue
            os.fsync(fd)  # Force kernel→disk
            flushed += 1
        except OSError as e:
            # Ignore pipe/socket errors
            #print(e, "BIG ERRROR")
            pass
    
    #print(f"Flushed {flushed} file descriptors")

# Usage in your hybrid app

from gem5.components.boards.simple_board import SimpleBoard
from gem5.resources.resource import obtain_resource
from gem5.simulate.simulator import Simulator

# Here we setup the board. The prebuilt X86DemoBoard allows for Full-System X86
# simulation.
from gem5.components.cachehierarchies.classic.no_cache import NoCache
#SingleChannelSimpleMemory
from gem5.components.memory import SingleChannelDDR4_2400

from gem5.components.memory.simple import SingleChannelSimpleMemory
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.components.processors.simple_switchable_processor import SimpleSwitchableProcessor
from gem5.isas import ISA
from gem5.resources.resource import obtain_resource
from gem5.simulate.simulator import Simulator
from gem5.utils.requires import requires

requires(isa_required=ISA.X86)

from gem5.components.processors.base_cpu_processor import BaseCPUProcessor
from gem5.components.processors.simple_core import SimpleCore
from gem5.components.processors.switchable_processor import SwitchableProcessor
from gem5.isas import ISA
from gem5.utils.override import overrides



import sys
import argparse

parser = argparse.ArgumentParser(description="Increase latency over baseline")

parser.add_argument("bench",type=str, default="/bench/cxl_bandwidth/simple_program.out33")
parser.add_argument("--bargs", type=str, default="", help="Bench args")
parser.add_argument("--latency-increase", type=int, default=0, help="Latency increase over baseline in nanoseconds")
parser.add_argument("--cpu-switch", type=str, default="", help="")
parser.add_argument("--cpu-start", type=str, default="KVM", help="")
parser.add_argument("--bstdin", type=str, default=None , help="")
parser.add_argument("--dramsize", type=str, default="16GB",) 
parser.add_argument("--disable-indirect-prediction", type=bool, default=False)
parser.add_argument("--skip_start_duration", type=int, default=False)
parser.add_argument("--exec_timeout", type=int, default=False)

import os
print("GEM5 WORKDIR", os.getcwd())
args = parser.parse_args()

skip_start = args.skip_start_duration
binary = args.bench

from m5.objects import Process
process = Process()
arr = []
for a in args.bargs.split(" "):
   arr.append(a)
print("ARGUMENTS", arr)
#process.cmd =  arr


from gem5.components.cachehierarchies.ruby.mesi_two_level_cache_hierarchy import (
    MESITwoLevelCacheHierarchy,
)

"""
cache_hierarchy = MESITwoLevelCacheHierarchy(
    l1d_size="32kB",
    l1i_size="32kB",
    l2_size="1MB",  # Adding L2 Cache 39mB / 0  60 cores for 39 -> 
    l1d_assoc=8,
    l1i_assoc=8,
    l2_assoc=16, # vs 16
    num_l2_banks=2
)
cache_hierarchy = MESITwoLevelCacheHierarchy(
    l1d_size="32KiB",
    l1d_assoc=8,
    l1i_size="32KiB",
    l1i_assoc=8,
    l2_size="256KiB",
    l2_assoc=16,
    num_l2_banks=2,
    
)

from gem5.components.cachehierarchies.classic.classic_cache_hierarchy import ClassicCacheHierarchy
from gem5.components.cachehierarchies.classic.caches import L1ICache, L1DCache, L2Cache, L3Cache
from gem5.components.boards.simple_board import SimpleBoard

class ThreeLevelCache(ClassicCacheHierarchy):
    def __init__(self):
        super().__init__()

        # L1 Caches
        self.l1i = L1ICache(size="32kB", assoc=2, tag_latency=2, data_latency=2, response_latency=2)
        self.l1d = L1DCache(size="32kB", assoc=2, tag_latency=2, data_latency=2, response_latency=2)

        # L2 Cache
        self.l2 = L2Cache(size="256kB", assoc=8, tag_latency=5, data_latency=5, response_latency=5)

        # L3 Cache (Last Level Cache)
        self.l3 = L3Cache(size="2MB", assoc=16, tag_latency=10, data_latency=10, response_latency=10)

        # Wire up the caches
        self.l1i.mem_side = self.l1d.mem_side = self.l2.cpu_side
        self.l2.mem_side = self.l3.cpu_side

    def incorporate_cache(self, board: SimpleBoard) -> None:
        self.connect_caches(board.get_processor(), board.get_memory())
cache_hierarchy = NoCache()
"""




# https://github.com/gem5/gem5/blob/ddd4ae35adb0a3df1f1ba11e9a973a5c2f8c2944/src/python/gem5/components/cachehierarchies/classic/private_l1_private_l2_cache_hierarchy.py
from gem5.components.cachehierarchies.classic.private_l1_private_l2_cache_hierarchy import PrivateL1PrivateL2CacheHierarchy

from m5.objects import StridePrefetcher

class PrefetchingCache(PrivateL1PrivateL2CacheHierarchy):
    def incorporate_cache(self, board):
        super().incorporate_cache(board)
        for b in self.l2buses:
            b.prefetcher = StridePrefetcher(degree=4)

cache_hierarchy = PrefetchingCache(
    l1i_size="32kB",
    l1d_size="32kB",
    l2_size="16384kB"
    )

"""
from gem5.components.cachehierarchies.classic import ClassicCacheHierarchy
#from gem5.components.cachehierarchies.classic import ClassicCacheHierarchy
from m5.objects import StridePrefetcher
cache_hierarchy = ClassicCacheHierarchy(
    l1i_size="32kB",
    l1d_size="32kB",
    l2_size="16GBkB",
    l2_assoc=8,
    l2_prefetcher=StridePrefetcher(degree=4)  # Add StridePrefetcher here
)
"""



memory = SingleChannelDDR4_2400(size=args.dramsize)
#memory = SingleChannelSimpleMemory(latency=str(45+args.latency_increase)+ "ns", latency_var="0ns",bandwidth='12.8GiB/s', size=args.dramsize)
# change bandwidth, check which accesses have the least MLP?

#processor = SimpleSwitchableProcessor( CPUTypes.KVM,  CPUTypes.O3, num_cores=1 )
class P(SwitchableProcessor):
    def switch_to_processor(self, switch_key):
        if switch_key == "KVM":
            self._board.mem_mode = "atomic_noncaching"
        else:
            self._board.mem_mode = "timing"
        super().switch_to_processor(self,core)

if(args.cpu_start == "KVM"):
    startCPU = "KVM" 
else:
    startCPU = "O3" 

processor = SimpleSwitchableProcessor(
    starting_core_type=(CPUTypes.KVM if args.cpu_start == "KVM" else 
                        CPUTypes.O3),
                        #CPUTypes.TIMING), #O3),
    switch_core_type=(CPUTypes.KVM if args.cpu_start != "KVM" else CPUTypes.O3),
    isa=ISA.X86,
    num_cores=1,
)

"""
processor = SwitchableProcessor({
         "O3": [SimpleCore(CPUTypes.O3, 0, ISA.X86)],
         "KVM" : [SimpleCore(CPUTypes.KVM, 0, ISA.X86)],
         "Timing" : [SimpleCore(CPUTypes.TIMING,0,ISA.X86)],
    }, startCPU)

"""

board = SimpleBoard(
          clk_freq="3GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
        )


oneCycle = 1/3e9
print("Start latency", board.get_memory().get_memory_controllers()[0].static_backend_latency) # 10ns
print("Increasing latency by ", args.latency_increase)
board.get_memory().get_memory_controllers()[0].static_backend_latency +=  args.latency_increase /1e9
print("End latency", board.get_memory().get_memory_controllers()[0].static_backend_latency)


print(board.m5ops_base," baahh")
#board.m5ops_base = 0xFFFFFFFFFFFF0000  # Move to 64-bit space
#if board.mem_ranges[0].end >= 0xFFFF0000:
#else:
#    board.m5ops_base = 0xFFFF0000  # Original location
"""
if startCPU == "Timing" or startCPU == "O3":
    board.mem_mode = "timing"
elif startCPU == "KVM":
    board.mem_mode = "atomic_noncaching"
"""



from gem5.resources.resource import BinaryResource, FileResource




"""
print("hi")
print("New static backend latency", board.get_memory(), board, dir(board), dir(board.get_memory().get_memory_controllers()[0]))
print("nnnnnnnnnnnnnnnnnnnnii")
print(
        len(board.get_memory().get_memory_controllers()),
        dir(board.get_memory().get_memory_controllers()[0]),
   #     dir(board.get_memory().get_memory_controllers()[0].get_simobj()),
board.get_memory().get_memory_controllers()[0].static_backend_latency,
"jo"
      )
"""
# We then set the workload. Here we use the "x86-ubuntu-18.04-boot" workload.
# This boots Ubuntu 18.04 with Linux 5.4.49. If the required resources are not
# found locally, they will be downloaded.
from pathlib import Path
b = BinaryResource(args.bench, #args.bargs.split(" ")
                   )
board.set_se_binary_workload(
        b , stdin_file = FileResource(args.bstdin) if args.bstdin else None,
        arguments= arr ,
        env_list = ["OMP_NUM_THREADS=1"]

        #FileResource("/mnt/nas/inesc/ist196723/benchmarks/cpu2017/benchspec/CPU/603.bwaves_s/run/run_base_refspeed_avxprota-m64.0000/bwaves_1.in"),
        #stdout_file  = Path("./noice"),
        #stderr_file = Path("./not_noice")
        #FileResource("/mnt/nas/inesc/ist196723/benchmarks/cpu2017/benchspec/CPU/603.bwaves_s/run/run_base_refspeed_mytest-m64.0002/bwaves_1.in")
        #obtain_resource("x86-hello64-dynamic")
        #"hello.out", args=[1,2,3,4]
    #obtain_resource("x86-ubuntu-18.04-boot", resource_version="2.0.0")
)
#print( obtain_resource("x86-hello64-dynamic"))

#board.m5ops_base = 0xFFFFFFFFFFFF0000  # Move to 64-bit space
simulator = Simulator(board=board,
                      on_exit_event={
        # using the SimPoints event generator in the standard library to take
        # checkpoints
        #ExitEvent.SIMPOINT_BEGIN: save_checkpoint_generator(dir)
    }
                      )

print(board.m5ops_base," baahh")
#board.m5ops_base = 0xFFFFFFFFFFFF0000  # Move to 64-bit space


print("Starting..")
from time import time
import m5.stats
b=time()
while ( time() - b  < skip_start):
    simulator.run(500000000000) #int(1000000000000))
    #print("Kvm doing..")
print(board.m5ops_base," baahh")
processor.switch()
print("Running O3")
m5.stats.reset()
real_start = time()
i=0
while(time() - real_start < args.exec_timeout):
	print(m5.stats)
	simulator.run(10000000000)
	#flush_all_open_fds()
    #exit(0)
	flush_all_open_fds()
	#if i % 100 == 0:
	i+=1
real_end = time()
#s = m5.stats['sim_seconds']
flush_all_open_fds()
print("ELAPSED_TIME",  real_end-real_start) 
print("EXITING")
exit(0)


while (time()-real_start) < 10:
    simulator.run(
                         1000000000
        #((2+10)*int(1000000000000))
            #//simulator.get_current_tick() +  100000000000*int(3e12)
                )

if(args.cpu_switch == ""):
    print(board.m5ops_base," baahh")
    try:
        simulator.run()
        print("Exitttt:",simulator.get_last_exit_event_cause())
    except:
        print(board.m5ops_base," biaahh")
    exit(0)
print("Running KVM")

print("done")
simulator.run(
        #simulator.get_current_tick() + 10000003*500

)
print(simulator.get_last_exit_event_cause())
print("EXITING")

while True:
    """
    processor.switch_to_processor("KVM")
    board.mem_mode = "atomic_noncaching"
    print("running KVM")
    exit_reason = simulator.run(
        simulator.get_current_tick() + 100000000003
            )
    processor.switch_to_processor("Timing")
    board.mem_mode = "timing"
    print("running Timing")
    simulator.run(
        simulator.get_current_tick() + 10093
            )

    print("running O3")
    processor.switch_to_processor("O3")
    simulator.run(
        simulator.get_current_tick() + 10000019
            )
    """
    print("Running KVM")
    simulator.run(
        simulator.get_current_tick() + 10000003
            )
    print(simulator.get_last_exit_event_cause())
    processor.switch()
    print("Running O3")
    simulator.run(
        simulator.get_current_tick() + 10000019
            )
    print(simulator.get_last_exit_event_cause())
    processor.switch()

