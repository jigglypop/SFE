import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import root

def filter_func_complex(timings, omega):
    """
    Calculates the complex filter function value F(omega).
    F(omega) = 1 + (-1)^(n+1) * exp(i*w) + 2 * sum_{j=1}^n (-1)^j * exp(i*w*t_j)
    """
    n = len(timings)
    # Base term: 1 + (-1)^(n+1) * exp(i*omega)
    val = 1.0 + ((-1)**(n+1)) * np.exp(1j * omega)
    
    # Summation term
    for j, t in enumerate(timings):
        # j is 0-indexed here, but formula uses 1-indexed (-1)^j
        # so (-1)^(j+1)
        sign = (-1)**(j+1)
        val += 2 * sign * np.exp(1j * omega * t)
        
    return val

def objective_notch(timings, target_omegas):
    """
    Objective function for root finding.
    We want F(omega) = 0 for all target_omegas.
    Since F is complex, we need Re(F)=0 and Im(F)=0.
    For N pulses, we have N variables.
    We can enforce N/2 frequency notches (each consumes 2 degrees of freedom).
    """
    residuals = []
    
    # Ensure timings are sorted (add barrier/penalty if not?)
    # Root finding doesn't handle constraints well, so we assume init guess is good.
    
    for w in target_omegas:
        val = filter_func_complex(timings, w)
        residuals.append(val.real)
        residuals.append(val.imag)
        
    return np.array(residuals)

def solve_notch_sequence(n_pulses, max_omega=10.0):
    """
    Solves for a sequence that nulls out frequencies linearly spaced up to max_omega.
    """
    # We need N equations for N variables.
    # Each frequency provides 2 equations (Real=0, Imag=0).
    # So we select N/2 target frequencies.
    
    n_freqs = n_pulses // 2
    # Target frequencies: spread them in the low-frequency dominant region
    # Avoid omega=0 (trivial), start from small value
    target_omegas = np.linspace(0.1, max_omega, n_freqs)
    
    # Initial guess: UDD sequence (usually a good starting point)
    j = np.arange(1, n_pulses + 1)
    init_guess = np.sin(np.pi * j / (2 * n_pulses + 2)) ** 2
    
    # Solve system of equations
    sol = root(objective_notch, init_guess, args=(target_omegas,), method='lm')
    
    if sol.success:
        # Sort and clip to [0,1] just in case
        final_timings = np.sort(np.clip(sol.x, 0.0001, 0.9999))
        return final_timings, target_omegas
    else:
        print(f"Warning: Solver failed for {n_pulses} pulses. Message: {sol.message}")
        return init_guess, target_omegas

def main():
    print("=== SFE Smart Notch Filter Calculator (No Learning) ===")
    
    pulse_counts = [8, 16]
    
    plt.figure(figsize=(12, 6))
    omega_plot = np.logspace(-1, 2, 1000)
    
    for n in pulse_counts:
        print(f"\nCalculating Notch Filter for {n} pulses...")
        
        # 1. Solve for Nulling Sequence
        # Try to null out noise up to omega = n (cover 1/f dominant region)
        seq, targets = solve_notch_sequence(n, max_omega=float(n))
        
        print(f"  Target Frequencies: {targets}")
        print(f"  >> Computed Sequence: {np.round(seq, 4).tolist()}")
        
        # 2. Analyze Filter Performance
        f_vals = np.array([filter_func_complex(seq, w) for w in omega_plot])
        f_mag = np.abs(f_vals)**2
        
        # CPMG for comparison
        cpmg_seq = (np.arange(1, n+1) - 0.5) / n
        f_cpmg_vals = np.array([filter_func_complex(cpmg_seq, w) for w in omega_plot])
        f_cpmg_mag = np.abs(f_cpmg_vals)**2
        
        # Plot
        plt.loglog(omega_plot, f_mag, '-', linewidth=2, label=f'SFE Notch ({n})')
        if n == 8: # Plot CPMG only once for clarity
             plt.loglog(omega_plot, f_cpmg_mag, 'k:', alpha=0.5, label='CPMG (Standard)')
        
        # Mark notch points
        for t_w in targets:
            plt.axvline(x=t_w, color='r', linestyle='--', alpha=0.2)
            
    plt.title("Filter Function: Frequency Nulling Approach")
    plt.xlabel("Frequency ($\omega$)")
    plt.ylabel("Filter Suppression Power $|F(\omega)|^2$")
    plt.legend()
    plt.grid(True, which="both", alpha=0.2)
    plt.savefig('examples/results/sfe_notch_filter.png')
    print("\nPlot saved to examples/results/sfe_notch_filter.png")

if __name__ == "__main__":
    main()
