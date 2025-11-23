import numpy as np
import os
import time
from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

# --- User Configuration ---
# Try to get API Key from Environment Variable for security
API_KEY = os.getenv("IBM_QUANTUM_API_KEY")
# --------------------------

def get_sfe_optimized_sequence():
    """
    Simulate fetching the optimal pulse sequence from the Rust SFE Engine.
    In a real scenario, this would read from 'sweep_results.csv' or call the Rust binary.
    Values are normalized time (0.0 to 1.0) within the idle window.
    """
    # Example: SFE-Genetic found these optimal dynamical decoupling points
    return np.array([0.12, 0.35, 0.58, 0.82, 0.95])

def main():
    print(f"[*] Connecting to IBM Quantum...")
    
    if not API_KEY:
        print("[!] Warning: IBM_QUANTUM_API_KEY environment variable not found.")
        print("    Trying to use saved account...")
    
    try:
        # 1. Authenticate
        try:
            if API_KEY:
                # If API Key is provided, try to save/overwrite
                QiskitRuntimeService.save_account(channel="ibm_quantum", token=API_KEY, overwrite=True)
            service = QiskitRuntimeService() # Load from saved account
        except Exception as e:
            # If loading failed and we have key, try direct connection
            if API_KEY:
                service = QiskitRuntimeService(channel="ibm_quantum", token=API_KEY)
            else:
                raise e
        
        print(f"[+] Authentication Successful! Account: {service.active_account()}")
        
        # 2. Find the least busy real backend
        print("[*] Searching for the least busy real quantum computer...")
        try:
            backend = service.least_busy(operational=True, simulator=False, min_num_qubits=1)
            print(f"[+] Selected Backend: {backend.name}")
            print(f"    - Status: {backend.status().status_msg}")
            print(f"    - Pending Jobs: {backend.status().pending_jobs}")
        except Exception:
             print("[!] No operational real backend found. Falling back to simulator.")
             backend = service.backend("ibmq_qasm_simulator")

        
        # 3. Construct SFE Circuit
        print("[*] Constructing SFE-Protected Quantum Circuit...")
        qc = QuantumCircuit(1)
        
        # Prepare superposition
        qc.h(0)
        
        # Apply SFE Protection (Dynamical Decoupling Sequence)
        sfe_timings = get_sfe_optimized_sequence()
        total_delay = 1000 # units of dt or abstract time
        
        last_t = 0
        for t_norm in sfe_timings:
            current_t = int(t_norm * total_delay)
            wait_time = current_t - last_t
            if wait_time > 0:
                qc.delay(wait_time, 0)
            qc.x(0) # The decoupling pulse
            last_t = current_t
            
        # Final measurement
        qc.measure_all()
        
        # 4. Transpile & Run
        print("[*] Transpiling for hardware...")
        pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
        isa_circuit = pm.run(qc)
        
        print(f"[*] Submitting job to {backend.name}...")
        # Using Primitives (Sampler) for execution
        sampler = Sampler(mode=backend)
        job = sampler.run([isa_circuit])
        
        print(f"[!] JOB SUBMITTED! Job ID: {job.job_id()}")
        print(f"[*] You can monitor this job at: https://quantum.ibm.com/jobs/{job.job_id()}")
        print("[*] Waiting for results (this may take time depending on the queue)...")
        
    except Exception as e:
        print(f"\n[!] Error occurred: {e}")
        print("Common fixes:")
        print("1. Check if qiskit-ibm-runtime is installed (pip install qiskit-ibm-runtime)")
        print("2. Verify the API key is correct or set IBM_QUANTUM_API_KEY env var.")
        print("3. Ensure you have access to open provider backends.")

if __name__ == "__main__":
    main()

