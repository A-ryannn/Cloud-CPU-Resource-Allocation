import os
import sys
import copy
from flask import Flask, jsonify, request, render_template

# Ensure project root is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models import CloudHost
from src.simulator import generate_synthetic_workload, StaticSimulator
from src.algorithms import (
    DPKnapsackAllocator,
    FCFSAllocator,
    SJFAllocator,
    RoundRobinAllocator
)

# Resolve template folder absolute path
TEMPLATE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
    'templates'
)

app = Flask(__name__, template_folder=TEMPLATE_DIR)

@app.route('/')
def index():
    """
    Renders the main dashboard webpage.
    """
    return render_template('index.html')

@app.route('/api/simulate', methods=['GET'])
def simulate():
    """
    API endpoint running the batch allocation simulation and returning results as JSON.
    """
    try:
        # Parse query params
        host_cpu = int(request.args.get('cpu', 64))
        host_ram = int(request.args.get('ram', 128))
        num_tasks = int(request.args.get('tasks', 30))
        
        # Initialize host
        host = CloudHost("host_api", host_cpu, host_ram)
        
        # Generate workload with fixed seed for consistent generation
        tasks = generate_synthetic_workload(
            num_tasks=num_tasks,
            value_correlation=True,
            seed=42
        )
        
        allocators = [
            DPKnapsackAllocator(),
            FCFSAllocator(),
            SJFAllocator(),
            RoundRobinAllocator()
        ]
        
        simulation_results = []
        for alloc in allocators:
            sim = StaticSimulator(host, alloc)
            tasks_copy = copy.deepcopy(tasks)
            res = sim.run(tasks_copy)
            simulation_results.append(res)
            
        return jsonify({
            "success": True,
            "host": {
                "cpu": host_cpu,
                "ram": host_ram
            },
            "task_count": num_tasks,
            "results": simulation_results
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

if __name__ == '__main__':
    # Bind to 0.0.0.0 for cross-network connectivity
    app.run(host='0.0.0.0', port=5000, debug=True)
