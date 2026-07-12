# Cloud Resource Allocation using Knapsack Algorithms

This project is a simulation environment that models and solves the problem of cloud resource allocation. It assigns incoming tasks (requesting CPU and RAM) to host machines while trying to maximize the overall scheduling value.

The core optimization algorithms are written in **C++** for performance, while the simulation framework and dashboard backend are implemented in **Python** (Flask).

---

## Features

- **C++ Optimization Solvers**:
  - **0/1 Knapsack (Dynamic Programming)**: Guarantees optimal CPU allocation under 0/1 Knapsack constraints.
  - **First-Come, First-Served (FCFS)**: Baseline scheduler allocating tasks in arrival sequence.
  - **Shortest Job First (SJF)**: Minimizes task queue latency by prioritizing tasks with shorter durations.
  - **Round Robin (RR)**: Enforces allocation fairness by cycling through tasks sequentially.
- **Python simulation harness** to generate synthetic container workloads.
- **Flask Web Dashboard**: Responsive dark-mode interface utilizing Vanilla CSS glassmorphism, Javascript fetch API, and Chart.js animations.

---

## How to Run

### 1. Compile C++ Code
Build the C++ allocation executable:
```bash
mkdir -p bin
g++ -O3 -std=c++17 src/algorithms/allocators.cpp -o bin/allocators
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Command-Line Interface (CLI)
Compare allocators in the terminal:
```bash
python main.py --tasks 30 --cpu 64 --ram 128
```

### 4. Launch Flask Web UI Dashboard
Open the visual dashboard webpage:
```bash
python src/app.py
```
Then navigate to `http://localhost:5000` in your web browser.

---

## Run Tests
To execute the automated unit test suite:
```bash
python -m unittest discover tests/
```
