import time
import random
from typing import List, Dict, Any, Optional
from src.models import CloudTask, CloudHost
from src.algorithms.base import BaseAllocator

def generate_synthetic_workload(
    num_tasks: int,
    mean_cpu: float = 4.0,
    mean_ram: float = 8.0,
    value_correlation: bool = True,
    seed: Optional[int] = None
) -> List[CloudTask]:
    """
    Generates a realistic set of container/VM tasks.
    """
    if seed is not None:
        random.seed(seed)

    tasks = []
    for i in range(num_tasks):
        task_id = f"task_{i:03d}"
        
        # CPU cores: usually powers of 2 or simple integers (1, 2, 4, 8, 12, 16)
        cpu = int(random.choice([1, 2, 4, 8, 12, 16]))
        
        # RAM: often 2x to 4x of CPU, with some variation
        ram_multiplier = random.choice([2, 4, 8])
        ram = int(cpu * ram_multiplier)
        
        # Base value
        if value_correlation:
            # Value is proportional to resources with a random multiplier (SLA multiplier)
            sla_multiplier = random.choice([1.0, 1.5, 2.5, 4.0]) # Standard, Silver, Gold, Platinum
            value = (cpu * 10 + ram * 2) * sla_multiplier
        else:
            # Completely random priority/value
            value = random.uniform(10.0, 500.0)
            
        value = round(value, 1)

        duration = random.randint(5, 50)
        arrival_time = random.randint(0, 20)

        tasks.append(
            CloudTask(
                task_id=task_id,
                cpu_cores=cpu,
                ram_gb=ram,
                value=value,
                duration=duration,
                arrival_time=arrival_time
            )
        )
    
    return tasks


class StaticSimulator:
    """
    Runs a static batch allocation simulation.
    All tasks are presented to the allocator at once.
    """
    def __init__(self, host: CloudHost, allocator: BaseAllocator):
        self.host = host
        self.allocator = allocator

    def run(self, tasks: List[CloudTask]) -> Dict[str, Any]:
        # Reset host
        self.host.reset()
        
        # Reset task statuses
        for task in tasks:
            task.status = "PENDING"

        start_time = time.perf_counter()
        selected_tasks = self.allocator.allocate(tasks, self.host)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        # Apply allocation to host
        allocated_count = 0
        total_value = 0.0
        
        for task in selected_tasks:
            success = self.host.allocate(task)
            if success:
                allocated_count += 1
                total_value += task.value
            else:
                task.status = "REJECTED"

        # Mark other tasks as rejected/unallocated
        for task in tasks:
            if task not in selected_tasks:
                task.status = "REJECTED"

        return {
            "algorithm": self.allocator.name,
            "runtime_ms": elapsed_ms,
            "tasks_allocated": allocated_count,
            "tasks_total": len(tasks),
            "allocation_rate_pct": (allocated_count / len(tasks) * 100.0) if tasks else 0.0,
            "value_allocated": round(total_value, 1),
            "value_total": round(sum(t.value for t in tasks), 1),
            "value_efficiency_pct": (total_value / sum(t.value for t in tasks) * 100.0) if tasks else 0.0,
            "cpu_utilization": self.host.cpu_utilization,
            "ram_utilization": self.host.ram_utilization,
            "allocated_cpu": self.host.allocated_cpu,
            "allocated_ram": self.host.allocated_ram
        }
