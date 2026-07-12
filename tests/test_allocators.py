import unittest
from src.models import CloudTask, CloudHost
from src.algorithms import (
    DPKnapsackAllocator,
    FCFSAllocator,
    SJFAllocator,
    RoundRobinAllocator
)

class TestResourceAllocators(unittest.TestCase):
    def setUp(self):
        # Create standard host with 10 CPU and 20 RAM
        self.host = CloudHost("test_host", total_cpu=10, total_ram=20)
        
        # Create standard tasks
        self.tasks = [
            CloudTask("T1", cpu_cores=5, ram_gb=10, value=10.0, duration=10, arrival_time=5),
            CloudTask("T2", cpu_cores=4, ram_gb=8,  value=4.0,  duration=5,  arrival_time=10),
            CloudTask("T3", cpu_cores=3, ram_gb=6,  value=6.0,  duration=15, arrival_time=0),
            CloudTask("T4", cpu_cores=5, ram_gb=10, value=10.0, duration=10, arrival_time=5),
        ]

    def test_dp_knapsack_optimality(self):
        """
        DP Knapsack (CPU-only) should find the optimal value.
        With CPU capacity 10:
        Option A: T1 + T4 (CPU: 10, Value: 20) -> Optimal
        """
        allocator = DPKnapsackAllocator()
        selected = allocator.allocate(self.tasks, self.host)
        
        selected_ids = {t.task_id for t in selected}
        self.assertIn("T1", selected_ids)
        self.assertIn("T4", selected_ids)
        self.assertEqual(len(selected), 2)
        
        total_cpu = sum(t.cpu_cores for t in selected)
        total_value = sum(t.value for t in selected)
        self.assertEqual(total_cpu, 10)
        self.assertEqual(total_value, 20.0)

    def test_fcfs_allocator(self):
        """
        FCFS should allocate in order of arrival time:
        T3 (arrival: 0, CPU: 3, fits) -> allocated (remaining CPU: 7)
        T1 (arrival: 5, CPU: 5, fits) -> allocated (remaining CPU: 2)
        T4 (arrival: 5, CPU: 5, doesn't fit) -> skipped
        T2 (arrival: 10, CPU: 4, doesn't fit) -> skipped
        Selected: T3 and T1
        """
        allocator = FCFSAllocator()
        selected = allocator.allocate(self.tasks, self.host)
        selected_ids = {t.task_id for t in selected}
        self.assertEqual(selected_ids, {"T3", "T1"})

    def test_sjf_allocator(self):
        """
        SJF should allocate in order of duration (job length):
        T2 (dur: 5, CPU: 4, fits) -> allocated (remaining CPU: 6)
        T1 (dur: 10, CPU: 5, fits) -> allocated (remaining CPU: 1)
        T4 (dur: 10, CPU: 5, doesn't fit) -> skipped
        T3 (dur: 15, CPU: 3, doesn't fit) -> skipped
        Selected: T2 and T1
        """
        allocator = SJFAllocator()
        selected = allocator.allocate(self.tasks, self.host)
        selected_ids = {t.task_id for t in selected}
        self.assertEqual(selected_ids, {"T2", "T1"})

    def test_rr_allocator(self):
        """
        Round Robin should alternate selection.
        """
        allocator = RoundRobinAllocator()
        selected = allocator.allocate(self.tasks, self.host)
        self.assertTrue(len(selected) > 0)

    def test_empty_workload(self):
        allocators = [
            DPKnapsackAllocator(),
            FCFSAllocator(),
            SJFAllocator(),
            RoundRobinAllocator()
        ]
        for allocator in allocators:
            selected = allocator.allocate([], self.host)
            self.assertEqual(selected, [])

    def test_oversized_task(self):
        oversized_task = [
            CloudTask("T_BIG", cpu_cores=99, ram_gb=999, value=100.0, duration=5, arrival_time=0)
        ]
        allocators = [
            DPKnapsackAllocator(),
            FCFSAllocator(),
            SJFAllocator(),
            RoundRobinAllocator()
        ]
        for allocator in allocators:
            selected = allocator.allocate(oversized_task, self.host)
            self.assertEqual(selected, [])

if __name__ == "__main__":
    unittest.main()
