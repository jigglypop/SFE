import numpy as np
import matplotlib.pyplot as plt
from joblib import Parallel, delayed
import time

# --- SFE Pure Analytic Sequence (Symmetrized for DC Cancellation) ---
def generate_symmetric_sfe(n_pulses, beta=50.0):
    """
    Generates a symmetric SFE sequence.
    First half: Logarithmic distribution (SFE)
    Second half: Symmetric reflection of the first half
    This ensures integral(y(t)) = 0, cancelling DC noise perfectly.
    """
    if n_pulses % 2 != 0:
        raise ValueError("Pulse count must be even for symmetry.")
        
    n_half = n_pulses // 2
    # Generate first half (0 to 0.5)
    # Map j=1..n_half to range [0, 0.5]
    
    half_seq = []
    denom = np.log(1 + beta)
    
    for j in range(1, n_half + 1):
        # Linear map to 0.0 ~ 1.0, then scale to 0.5
        # Or simply map to full, then divide by 2?
        # Let's use SFE logic on the half-window.
        linear = j / (n_half + 1) # ends before 1.0
        val = (np.log(1 + beta * linear) / denom) * 0.5
        half_seq.append(val)
        
    half_seq = np.array(half_seq)
    
    # Reflect for second half
    # t' = 1.0 - t
    second_half = 1.0 - half_seq[::-1]
    
    return np.concatenate([half_seq, second_half])

# Re-generate SFE Sequence
SFE_SEQ = generate_symmetric_sfe(16, beta=50.0)
print(f"Symmetrized SFE Sequence: {np.round(SFE_SEQ, 4)}")

def generate_drift_noise(steps, amp_dc=1.0, amp_fluctuation=0.5, rng_seed=None):
    rng = np.random.default_rng(rng_seed)
    dc = rng.standard_normal() * amp_dc
    freq = rng.uniform(0.0001, 0.001)
    phase = rng.uniform(0, 2*np.pi)
    t = np.arange(steps)
    drift = np.sin(2 * np.pi * freq * t + phase) * amp_fluctuation
    return np.full(steps, dc) + drift

def calculate_phase_error(noise_trace, pulse_seq, total_time, coupling):
    if len(pulse_seq) == 0:
        return np.sum(noise_trace) * coupling

    pulse_indices = (pulse_seq * total_time).astype(int)
    pulse_indices = np.unique(pulse_indices)
    
    y = np.ones(total_time)
    current_sign = 1.0
    last_idx = 0
    
    for p_idx in pulse_indices:
        if p_idx >= total_time: break
        y[last_idx:p_idx] = current_sign
        current_sign *= -1.0
        last_idx = p_idx
    y[last_idx:] = current_sign
    
    return np.sum(noise_trace * y) * coupling

def run_trial(distance, total_time, mode='raw'):
    seed_base = int(time.time() * 1000000) % 10000000
    amp_dc = 5.0  
    amp_ac = 2.0  
    coupling = 0.01
    
    noise_traces = []
    for q in range(distance):
        seed = seed_base + q * 100
        trace = generate_drift_noise(total_time, amp_dc, amp_ac, seed)
        noise_traces.append(trace)
    
    if mode == 'sfe': seq = SFE_SEQ
    elif mode == 'cpmg': seq = (np.arange(1, 17) - 0.5) / 16
    else: seq = np.array([])
        
    errors = 0
    for q in range(distance):
        phi = calculate_phase_error(noise_traces[q], seq, total_time, coupling)
        if abs(phi) > np.pi/2:
            errors += 1
            
    if errors > distance // 2: return 1
    else: return 0

def main():
    print("=== SFE + QEC Simulation (Symmetrized Check) ===")
    
    trials = 1000
    distances = [3, 5, 7]
    total_time = 5000
    
    print(f"Time: {total_time}, Noise: Strong DC+Drift")
    print("-" * 70)
    print(f"{'Dist':<5} | {'Raw':<10} | {'CPMG':<10} | {'SFE':<10} | {'Win?'}")
    print("-" * 70)
    
    results_raw = []
    results_cpmg = []
    results_sfe = []
    
    for d in distances:
        fails_raw = Parallel(n_jobs=-1)(delayed(run_trial)(d, total_time, 'raw') for _ in range(trials))
        rate_raw = sum(fails_raw) / trials
        
        fails_cpmg = Parallel(n_jobs=-1)(delayed(run_trial)(d, total_time, 'cpmg') for _ in range(trials))
        rate_cpmg = sum(fails_cpmg) / trials
        
        fails_sfe = Parallel(n_jobs=-1)(delayed(run_trial)(d, total_time, 'sfe') for _ in range(trials))
        rate_sfe = sum(fails_sfe) / trials
        
        win = "Tie"
        if rate_sfe < rate_cpmg: win = "SFE"
        elif rate_cpmg < rate_sfe: win = "CPMG"
        
        print(f"{d:<5} | {rate_raw:.4f}     | {rate_cpmg:.4f}     | {rate_sfe:.4f}     | {win}")
        
        results_raw.append(rate_raw)
        results_cpmg.append(rate_cpmg)
        results_sfe.append(rate_sfe)

    plt.figure(figsize=(10, 6))
    plt.plot(distances, results_raw, 'ko--', label='Raw')
    plt.plot(distances, results_cpmg, 'bs-', label='CPMG')
    plt.plot(distances, results_sfe, 'r*-', label='SFE (Symmetric)')
    plt.xlabel('Distance')
    plt.ylabel('Error Rate')
    plt.title('QEC: Symmetric SFE vs CPMG')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('examples/results/sfe_qec_symmetric.png')
    print("\nPlot saved to examples/results/sfe_qec_symmetric.png")

if __name__ == "__main__":
    main()
