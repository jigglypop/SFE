import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import root

def filter_func_complex(timings, omega):
    """
    Calculates the complex filter function value F(omega).
    F(omega) = 1 + (-1)^(n+1) * exp(i*w) + 2 * sum_{j=1}^n (-1)^j * exp(i*w*t_j)
    """
    n = len(timings)
    val = 1.0 + ((-1)**(n+1)) * np.exp(1j * omega)
    for j, t in enumerate(timings):
        sign = (-1)**(j+1)
        val += 2 * sign * np.exp(1j * omega * t)
    return val

def calculate_residual_noise(timings, alpha=1.0):
    """
    Calculates integral of |F(w)|^2 / w^alpha
    """
    omega = np.logspace(-2, 2, 2000) # 0.01 to 100
    f_vals = np.array([filter_func_complex(timings, w) for w in omega])
    f_mag = np.abs(f_vals)**2
    noise_spectrum = 1 / (omega ** alpha)
    
    # Simple Reimann sum
    d_omega = np.diff(omega)
    integrand = f_mag * noise_spectrum
    # Use midpoints for integration
    integral = np.sum(0.5 * (integrand[:-1] + integrand[1:]) * d_omega)
    return integral

def solve_notch_sequence(n_pulses, max_omega):
    def objective_notch(timings):
        n_freqs = len(timings) // 2
        target_omegas = np.linspace(0.1, max_omega, n_freqs)
        residuals = []
        for w in target_omegas:
            val = filter_func_complex(timings, w)
            residuals.append(val.real)
            residuals.append(val.imag)
        return np.array(residuals)

    j = np.arange(1, n_pulses + 1)
    init_guess = np.sin(np.pi * j / (2 * n_pulses + 2)) ** 2
    
    # Solve
    sol = root(objective_notch, init_guess, method='lm')
    if sol.success:
        return np.sort(np.clip(sol.x, 0.0001, 0.9999))
    return init_guess

def main():
    print("=== SFE Verification: Notch vs CPMG (16 Pulses) ===")
    
    n = 16
    alpha_val = 1.5 # Strong low-frequency noise
    
    # 1. CPMG Sequence
    cpmg_seq = (np.arange(1, n+1) - 0.5) / n
    
    # 2. SFE Notch Sequence
    # Optimize up to omega=16 (covering sufficient bandwidth)
    sfe_notch_seq = solve_notch_sequence(n, max_omega=16.0)
    
    # 3. UDD Sequence (Analytic)
    j = np.arange(1, n+1)
    udd_seq = np.sin(np.pi * j / (2 * n + 2)) ** 2
    
    # 4. Compare Residual Noise
    res_cpmg = calculate_residual_noise(cpmg_seq, alpha=alpha_val)
    res_sfe = calculate_residual_noise(sfe_notch_seq, alpha=alpha_val)
    res_udd = calculate_residual_noise(udd_seq, alpha=alpha_val)
    
    print(f"Noise Model: 1/f^{alpha_val}")
    print(f"Residual Noise (Lower is Better):")
    print(f"  - CPMG (Standard): {res_cpmg:.6f}")
    print(f"  - UDD  (Analytic): {res_udd:.6f}")
    print(f"  - SFE  (Notch)   : {res_sfe:.6f}")
    
    ratio = res_cpmg / res_sfe
    print(f"\nPerformance Gain (SFE vs CPMG): {ratio:.2f}x")
    
    if res_sfe < res_cpmg:
        print(">> SFE Notch Filter is theoretically SUPERIOR.")
    else:
        print(">> Warning: CPMG is still better. Notch strategy needs tuning.")

    # Plot
    omega_plot = np.logspace(-1, 1.5, 1000)
    f_cpmg = np.abs([filter_func_complex(cpmg_seq, w) for w in omega_plot])**2
    f_sfe = np.abs([filter_func_complex(sfe_notch_seq, w) for w in omega_plot])**2
    
    plt.figure(figsize=(10, 6))
    plt.loglog(omega_plot, f_cpmg, 'k--', label='CPMG', alpha=0.5)
    plt.loglog(omega_plot, f_sfe, 'r-', label='SFE Notch', linewidth=2)
    plt.xlabel('Frequency')
    plt.ylabel('Filter Power')
    plt.title(f'Filter Shape Comparison (16 Pulses, Gain={ratio:.2f}x)')
    plt.legend()
    plt.grid(True, which='both', alpha=0.3)
    plt.savefig('examples/results/sfe_verification_check.png')
    print("Verification plot saved.")

if __name__ == "__main__":
    main()

