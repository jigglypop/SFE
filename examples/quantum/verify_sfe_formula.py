import numpy as np
import matplotlib.pyplot as plt

def filter_func_complex(timings, omega):
    n = len(timings)
    val = 1.0 + ((-1)**(n+1)) * np.exp(1j * omega)
    for j, t in enumerate(timings):
        sign = (-1)**(j+1)
        val += 2 * sign * np.exp(1j * omega * t)
    return val

def calculate_residual_noise(timings, alpha=1.5):
    # Integral of |F(w)|^2 / w^alpha
    omega = np.logspace(-2, 2, 2000)
    f_mag = np.abs(np.array([filter_func_complex(timings, w) for w in omega]))**2
    noise = 1 / (omega ** alpha)
    return np.trapz(f_mag * noise, omega)

def sfe_analytic_sequence(n, beta):
    """
    Pure SFE Formula: Logarithmic distribution for 1/f noise cancellation
    t_j = ln(1 + beta * j / (n + 1)) / ln(1 + beta)
    """
    j = np.arange(1, n + 1)
    # Linear mapping (CPMG)
    linear = j / (n + 1)
    
    # SFE Warp
    if beta == 0:
        return linear
    
    # Logarithmic warping
    # This concentrates pulses at the beginning (t=0) where memory effects are strongest
    val = np.log(1 + beta * linear) / np.log(1 + beta)
    return val

def main():
    print("=== Pure SFE Analytic Formula Verification ===")
    
    n = 16
    alpha_val = 1.5 # 1/f^1.5 noise
    
    # 1. Define Beta Range (SFE Parameter)
    betas = [0.1, 1.0, 5.0, 10.0, 20.0, 50.0]
    
    # Benchmark: CPMG
    cpmg_seq = (np.arange(1, n+1) - 0.5) / n
    res_cpmg = calculate_residual_noise(cpmg_seq, alpha_val)
    print(f"[Benchmark] CPMG Residual Noise: {res_cpmg:.6f}")
    
    # Benchmark: UDD
    udd_seq = np.sin(np.pi * np.arange(1, n+1) / (2*n+2))**2
    res_udd = calculate_residual_noise(udd_seq, alpha_val)
    print(f"[Benchmark] UDD  Residual Noise: {res_udd:.6f}")
    
    print("-" * 60)
    
    best_beta = 0
    min_noise = 1e9
    best_seq = None
    
    # 2. Scan SFE Formula
    for b in betas:
        seq = sfe_analytic_sequence(n, b)
        res = calculate_residual_noise(seq, alpha_val)
        
        ratio = res_cpmg / res
        print(f"SFE (beta={b:4.1f}): Noise={res:.6f} | Gain vs CPMG: {ratio:.2f}x")
        
        if res < min_noise:
            min_noise = res
            best_beta = b
            best_seq = seq
            
    print("-" * 60)
    print(f"WINNER: SFE (beta={best_beta})")
    print(f"  - Noise: {min_noise:.6f}")
    print(f"  - Improvement vs CPMG: {res_cpmg/min_noise:.2f}x")
    print(f"  - Improvement vs UDD : {res_udd/min_noise:.2f}x")
    
    # 3. Plot
    plt.figure(figsize=(10, 6))
    omega = np.logspace(-1, 1.5, 1000)
    
    f_cpmg = np.abs([filter_func_complex(cpmg_seq, w) for w in omega])**2
    f_sfe = np.abs([filter_func_complex(best_seq, w) for w in omega])**2
    
    plt.loglog(omega, f_cpmg, 'k--', label='CPMG', alpha=0.5)
    plt.loglog(omega, f_sfe, 'r-', label=f'Pure SFE (beta={best_beta})', linewidth=2)
    
    plt.xlabel('Frequency')
    plt.ylabel('Filter Power')
    plt.title(f'SFE Analytic Formula vs CPMG (Gain={res_cpmg/min_noise:.2f}x)')
    plt.legend()
    plt.grid(True, which='both', alpha=0.3)
    plt.savefig('examples/results/sfe_formula_verification.png')
    print("Plot saved to examples/results/sfe_formula_verification.png")

    print(f"\nOptimal SFE Sequence (Copy this to Rust/Python):")
    print(f"{np.round(best_seq, 4).tolist()}")

if __name__ == "__main__":
    main()

