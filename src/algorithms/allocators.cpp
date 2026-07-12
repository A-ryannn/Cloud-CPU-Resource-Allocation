#include <iostream>
#include <vector>
#include <string>
#include <algorithm>

using namespace std;

struct Task {
    string id;
    int cpu;
    int ram;
    double value;
    int duration;
    int arrival_time;
};

// 1. 0/1 Knapsack Solver via Dynamic Programming (CPU-only)
vector<Task> solve_dp(const vector<Task>& tasks, int capacity) {
    int n = tasks.size();
    if (n == 0 || capacity <= 0) return {};

    vector<Task> valid_tasks;
    for (const auto& t : tasks) {
        if (t.cpu <= capacity) {
            valid_tasks.push_back(t);
        }
    }
    n = valid_tasks.size();
    if (n == 0) return {};

    vector<vector<double>> dp(n + 1, vector<double>(capacity + 1, 0.0));

    for (int i = 1; i <= n; ++i) {
        int w = valid_tasks[i - 1].cpu;
        double val = valid_tasks[i - 1].value;
        for (int j = 0; j <= capacity; ++j) {
            if (w <= j) {
                dp[i][j] = max(dp[i - 1][j], dp[i - 1][j - w] + val);
            } else {
                dp[i][j] = dp[i - 1][j];
            }
        }
    }

    vector<Task> selected;
    int w = capacity;
    for (int i = n; i > 0; --i) {
        if (dp[i][w] != dp[i - 1][w]) {
            selected.push_back(valid_tasks[i - 1]);
            w -= valid_tasks[i - 1].cpu;
        }
    }
    reverse(selected.begin(), selected.end());
    return selected;
}

// 2. First-Come, First-Served (FCFS)
vector<Task> solve_fcfs(vector<Task> tasks, int capacity) {
    if (capacity <= 0 || tasks.empty()) return {};

    sort(tasks.begin(), tasks.end(), [](const Task& a, const Task& b) {
        if (a.arrival_time != b.arrival_time) {
            return a.arrival_time < b.arrival_time;
        }
        return a.id < b.id;
    });

    vector<Task> selected;
    int current_cpu = 0;
    for (const auto& t : tasks) {
        if (current_cpu + t.cpu <= capacity) {
            selected.push_back(t);
            current_cpu += t.cpu;
        }
    }
    return selected;
}

// 3. Shortest Job First (SJF)
vector<Task> solve_sjf(vector<Task> tasks, int capacity) {
    if (capacity <= 0 || tasks.empty()) return {};

    sort(tasks.begin(), tasks.end(), [](const Task& a, const Task& b) {
        if (a.duration != b.duration) {
            return a.duration < b.duration;
        }
        return a.arrival_time < b.arrival_time;
    });

    vector<Task> selected;
    int current_cpu = 0;
    for (const auto& t : tasks) {
        if (current_cpu + t.cpu <= capacity) {
            selected.push_back(t);
            current_cpu += t.cpu;
        }
    }
    return selected;
}

// 4. Round Robin (RR)
vector<Task> solve_rr(vector<Task> tasks, int capacity) {
    if (capacity <= 0 || tasks.empty()) return {};

    sort(tasks.begin(), tasks.end(), [](const Task& a, const Task& b) {
        return a.arrival_time < b.arrival_time;
    });

    vector<Task> selected;
    int current_cpu = 0;
    vector<bool> visited(tasks.size(), false);
    size_t allocated_count = 0;

    while (allocated_count < tasks.size()) {
        bool progress = false;
        
        for (size_t i = 0; i < tasks.size(); i += 2) {
            if (!visited[i]) {
                visited[i] = true;
                allocated_count++;
                if (current_cpu + tasks[i].cpu <= capacity) {
                    selected.push_back(tasks[i]);
                    current_cpu += tasks[i].cpu;
                    progress = true;
                }
            }
        }
        for (size_t i = 1; i < tasks.size(); i += 2) {
            if (!visited[i]) {
                visited[i] = true;
                allocated_count++;
                if (current_cpu + tasks[i].cpu <= capacity) {
                    selected.push_back(tasks[i]);
                    current_cpu += tasks[i].cpu;
                    progress = true;
                }
            }
        }
        if (!progress) break;
    }
    return selected;
}

int main() {
    string algo;
    int cpu_cap = 0, ram_cap = 0;
    
    if (!(cin >> algo >> cpu_cap >> ram_cap)) {
        cerr << "Error reading configuration parameters from stdin." << endl;
        return 1;
    }

    vector<Task> tasks;
    string id;
    int cpu = 0, ram = 0, duration = 0, arrival_time = 0;
    double value = 0.0;
    
    while (cin >> id >> cpu >> ram >> value >> duration >> arrival_time) {
        tasks.push_back({id, cpu, ram, value, duration, arrival_time});
    }

    vector<Task> selected;
    if (algo == "dp") {
        selected = solve_dp(tasks, cpu_cap);
    } else if (algo == "fcfs") {
        selected = solve_fcfs(tasks, cpu_cap);
    } else if (algo == "sjf") {
        selected = solve_sjf(tasks, cpu_cap);
    } else if (algo == "rr") {
        selected = solve_rr(tasks, cpu_cap);
    } else {
        cerr << "Unknown algorithm: " << algo << endl;
        return 1;
    }

    for (const auto& t : selected) {
        cout << t.id << "\n";
    }

    return 0;
}
