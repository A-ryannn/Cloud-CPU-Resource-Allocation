from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class CloudTask:
    """
    Represents a client container request (e.g., Kubernetes Pod or VM)
    that needs to be scheduled on a physical host.
    """
    task_id: str
    cpu_cores: int
    ram_gb: int
    value: float  # Representing priority weight, billing revenue, or SLA urgency
    duration: int  # Duration in seconds/time-steps the task will run
    arrival_time: int = 0
    time_remaining: int = field(default=0, init=False)
    status: str = "PENDING"  # PENDING, RUNNING, COMPLETED, REJECTED

    def __post_init__(self):
        self.time_remaining = self.duration

    def tick(self, time_step: int = 1) -> bool:
        """
        Decrements the remaining duration of the task.
        Returns True if the task has finished, False otherwise.
        """
        if self.status != "RUNNING":
            return False
        
        self.time_remaining -= time_step
        if self.time_remaining <= 0:
            self.time_remaining = 0
            self.status = "COMPLETED"
            return True
        return False

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "cpu_cores": self.cpu_cores,
            "ram_gb": self.ram_gb,
            "value": self.value,
            "duration": self.duration,
            "arrival_time": self.arrival_time,
            "time_remaining": self.time_remaining,
            "status": self.status,
            "value_density": round(self.value / max(1, self.cpu_cores), 2)
        }

    def __repr__(self) -> str:
        return (f"Task(id={self.task_id}, CPU={self.cpu_cores}, RAM={self.ram_gb}G, "
                f"Value={self.value:.1f}, Dur={self.duration}s, Status={self.status})")


class CloudHost:
    """
    Represents a physical cloud hypervisor host machine with finite CPU and RAM capacity.
    """
    def __init__(self, host_id: str, total_cpu: int, total_ram: int):
        self.host_id = host_id
        self.total_cpu = total_cpu
        self.total_ram = total_ram
        
        self.allocated_cpu = 0
        self.allocated_ram = 0
        self.running_tasks: Dict[str, CloudTask] = {}

    @property
    def free_cpu(self) -> int:
        return self.total_cpu - self.allocated_cpu

    @property
    def free_ram(self) -> int:
        return self.total_ram - self.allocated_ram

    @property
    def cpu_utilization(self) -> float:
        return (self.allocated_cpu / self.total_cpu) * 100 if self.total_cpu > 0 else 0.0

    @property
    def ram_utilization(self) -> float:
        return (self.allocated_ram / self.total_ram) * 100 if self.total_ram > 0 else 0.0

    def can_fit(self, task: CloudTask) -> bool:
        """
        Checks if the host has enough unallocated resources to run the task.
        """
        return (self.free_cpu >= task.cpu_cores) and (self.free_ram >= task.ram_gb)

    def allocate(self, task: CloudTask) -> bool:
        """
        Attempts to allocate a task on the host. Modifies host resources and task status.
        """
        if self.can_fit(task):
            self.allocated_cpu += task.cpu_cores
            self.allocated_ram += task.ram_gb
            task.status = "RUNNING"
            self.running_tasks[task.task_id] = task
            return True
        return False

    def deallocate(self, task_id: str) -> Optional[CloudTask]:
        """
        Removes a task from the host and reclaims resources.
        """
        if task_id in self.running_tasks:
            task = self.running_tasks.pop(task_id)
            self.allocated_cpu -= task.cpu_cores
            self.allocated_ram -= task.ram_gb
            # Ensure resources don't drift below 0 due to float errors or weird states
            self.allocated_cpu = max(0, self.allocated_cpu)
            self.allocated_ram = max(0, self.allocated_ram)
            return task
        return None

    def tick(self, time_step: int = 1) -> List[CloudTask]:
        """
        Updates the state of all running tasks. Releases completed tasks.
        Returns a list of completed tasks in this step.
        """
        completed = []
        # We need a copy of keys to avoid modification issues during iteration
        for task_id in list(self.running_tasks.keys()):
            task = self.running_tasks[task_id]
            finished = task.tick(time_step)
            if finished:
                self.deallocate(task_id)
                completed.append(task)
        return completed

    def reset(self):
        """
        Clears all tasks and resets allocation resources.
        """
        self.allocated_cpu = 0
        self.allocated_ram = 0
        self.running_tasks.clear()

    def __repr__(self) -> str:
        return (f"Host(id={self.host_id}, CPU={self.allocated_cpu}/{self.total_cpu} Cores "
                f"[{self.cpu_utilization:.1f}%], RAM={self.allocated_ram}/{self.total_ram} GB "
                f"[{self.ram_utilization:.1f}%], RunningTasks={len(self.running_tasks)})")
