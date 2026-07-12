#!/usr/bin/env python3
import sys
import argparse
import os

# Ensure current directory is in path so we can run directly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.models import CloudHost
from src.simulator import generate_synthetic_workload, StaticSimulator
from src.algorithms import (
    DPKnapsackAllocator,
    FCFSAllocator,
    SJFAllocator,
    RoundRobinAllocator
)

def run_static_comparison(host: CloudHost, tasks: list, seed: int):
    print("=" * 75)
    print(f" RUNNING STATIC BATCH ALLOCATION SIMULATION (Seed: {seed})")
    print(f" Host Configuration: CPU={host.total_cpu} Cores, RAM={host.total_ram} GB")
    print(f" Total Workload Size: {len(tasks)} Tasks")
    print("=" * 75)
    
    allocators = [
        DPKnapsackAllocator(),
        FCFSAllocator(),
        SJFAllocator(),
        RoundRobinAllocator()
    ]
    
    results = []
    for alloc in allocators:
        sim = StaticSimulator(host, alloc)
        import copy
        tasks_copy = copy.deepcopy(tasks)
        res = sim.run(tasks_copy)
        results.append(res)
        
    # Print formatted table
    header = f"{'Algorithm':<32} | {'Time (ms)':<9} | {'Allocated (%)':<13} | {'Value (%)':<11} | {'CPU / RAM Util':<14}"
    print(header)
    print("-" * len(header))
    
    for r in results:
        alloc_str = f"{r['tasks_allocated']}/{r['tasks_total']} ({r['allocation_rate_pct']:.1f}%)"
        val_str = f"{r['value_allocated']:.1f}/{r['value_total']:.1f} ({r['value_efficiency_pct']:.1f}%)"
        util_str = f"{r['cpu_utilization']:.1f}% / {r['ram_utilization']:.1f}%"
        row = f"{r['algorithm']:<32} | {r['runtime_ms']:<9.2f} | {alloc_str:<13} | {val_str:<11} | {util_str:<14}"
        print(row)
    print("=" * 75)
    print("\nNote: 0/1 Knapsack (DP), FCFS, SJF, and Round Robin (RR) schedulers optimize CPU limits.")


def main():
    parser = argparse.ArgumentParser(description="Cloud CPU Resource Allocation Simulator using Knapsack and OS Scheduling Algorithms")
    parser.add_argument("--tasks", type=int, default=30, help="Number of tasks to generate")
    parser.add_argument("--cpu", type=int, default=64, help="Host CPU capacity (cores)")
    parser.add_argument("--ram", type=int, default=128, help="Host RAM capacity (GB)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    
    args = parser.parse_args()
    
    # Initialize host
    host = CloudHost("host_main", args.cpu, args.ram)
    
    # Generate tasks
    tasks = generate_synthetic_workload(num_tasks=args.tasks, seed=args.seed)
    
    # Run static comparison
    run_static_comparison(host, tasks, args.seed)


if __name__ == "__main__":
    main()
