import os
import subprocess
import sys
from abc import ABC, abstractmethod
from typing import List
from src.models import CloudTask, CloudHost

class BaseAllocator(ABC):
    """
    Abstract base class for all allocation algorithms.
    """
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def allocate(self, tasks: List[CloudTask], host: CloudHost) -> List[CloudTask]:
        pass


class CppAllocator(BaseAllocator):
    """
    Helper allocator that delegates core computation to the compiled C++ binary.
    """
    def __init__(self, name: str, algo_key: str):
        super().__init__(name)
        self.algo_key = algo_key
        # Resolve absolute paths
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.binary_path = os.path.join(self.project_root, "bin", "allocators")
        self.cpp_source_path = os.path.join(self.project_root, "src", "algorithms", "allocators.cpp")

    def _ensure_compiled(self):
        """
        Check if C++ binary exists, compile it if not.
        """
        if not os.path.exists(self.binary_path):
            os.makedirs(os.path.dirname(self.binary_path), exist_ok=True)
            print(f"Compiling C++ binary: {self.cpp_source_path} -> {self.binary_path}", file=sys.stderr)
            try:
                subprocess.run(
                    ["g++", "-O3", "-std=c++17", self.cpp_source_path, "-o", self.binary_path],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            except subprocess.CalledProcessError as e:
                print(f"Error compiling C++ allocators: {e.stderr.decode()}", file=sys.stderr)
                raise RuntimeError("Failed to compile C++ allocation binary.")

    def allocate(self, tasks: List[CloudTask], host: CloudHost) -> List[CloudTask]:
        if not tasks:
            return []

        # Make sure C++ binary is compiled
        self._ensure_compiled()

        # Format input string for C++ stdin
        input_data = f"{self.algo_key} {host.free_cpu} {host.free_ram}\n"
        
        for task in tasks:
            input_data += f"{task.task_id} {task.cpu_cores} {task.ram_gb} {task.value} {task.duration} {task.arrival_time}\n"

        # Execute C++ binary
        try:
            process = subprocess.Popen(
                [self.binary_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout_data, stderr_data = process.communicate(input=input_data)
            
            if process.returncode != 0:
                print(f"C++ binary error: {stderr_data}", file=sys.stderr)
                return []
                
        except Exception as e:
            print(f"Failed to run C++ binary: {e}", file=sys.stderr)
            return []

        # Parse selected task IDs
        selected_ids = set(stdout_data.strip().split())
        
        # Map IDs back to the actual Task objects, maintaining order of selection
        selected_tasks = []
        for task in tasks:
            if task.task_id in selected_ids:
                selected_tasks.append(task)
                
        return selected_tasks


class DPKnapsackAllocator(CppAllocator):
    """
    Delegates dynamic programming 0/1 Knapsack computation to the compiled C++ binary.
    """
    def __init__(self):
        super().__init__("0/1 Knapsack (Dynamic Programming)", "dp")


class FCFSAllocator(CppAllocator):
    """
    Delegates FCFS (First-Come, First-Served) computation to the compiled C++ binary.
    """
    def __init__(self):
        super().__init__("First-Come, First-Served (FCFS)", "fcfs")


class SJFAllocator(CppAllocator):
    """
    Delegates Shortest Job First (SJF) computation to the compiled C++ binary.
    """
    def __init__(self):
        super().__init__("Shortest Job First (SJF)", "sjf")


class RoundRobinAllocator(CppAllocator):
    """
    Delegates Round Robin (RR) computation to the compiled C++ binary.
    """
    def __init__(self):
        super().__init__("Round Robin (RR)", "rr")
