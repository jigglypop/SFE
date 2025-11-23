import numpy as np
from scipy.optimize import curve_fit
import os


def filter_function_val(omega, pulses, T):
    """
    Calculates filter function |Y(omega)|^2 for a specific sequence.
    pulses: relative positions [0, 1]
    y(t): toggle function (+1/-1)
    """
    n_steps = 2000
    dt = T / n_steps
    t = np.linspace(0, T, n_steps, endpoint=False)
    
    y = np.ones(n_steps)
    current_sign = 1.0
    
    valid_pulses = [p for p in pulses if 0 < p < 1]
    pulse_indices = [int(p * n_steps) for p in valid_pulses]
    pulse_indices.sort()
    
    pulse_ptr = 0
    for i in range(n_steps):
        while pulse_ptr < len(pulse_indices) and i >= pulse_indices[pulse_ptr]:
            current_sign *= -1.0
            pulse_ptr += 1
        y[i] = current_sign
        
    if np.isscalar(omega):
        phase = omega * t
        Y = np.sum(y * np.exp(1j * phase)) * dt
        return np.abs(Y)**2
    else:
        Y_vals = []
        for w in omega:
             phase = w * t
             Y = np.sum(y * np.exp(1j * phase)) * dt
             Y_vals.append(np.abs(Y)**2)
        return np.array(Y_vals)


def chi_1overf(T, alpha, A, sequence_type='cpmg'):
    """
    Pure 1/f noise contribution to chi(T).
    chi_1f(T) = A * int (1/w^alpha) * |Y(w, T)|^2 dw / (2pi)
    """
    if T <= 0:
        return 0.0

    if sequence_type == 'cpmg':
        pulses = [(k - 0.5) / 8.0 for k in range(1, 9)]
    elif sequence_type == 'sfe':
        pulses = [0.0300, 0.1170, 0.2500, 0.4030, 0.5870, 0.7500, 0.8830, 0.9700]
    else:
        raise ValueError("Unknown sequence type")
        
    # Fixed frequency range (dimensionless, will be scaled by T internally in filter function)
    # Use normalized frequency z = omega * T
    z_min = 0.1
    z_max = 100.0
    
    nw = 150
    z_vals = np.logspace(np.log10(z_min), np.log10(z_max), nw)
    omegas = z_vals / T
    
    F_vals = filter_function_val(omegas, pulses, T)
    
    S_vals = 1.0 / (omegas**alpha)
    
    integrand = S_vals * F_vals
    
    integral = np.trapezoid(integrand, omegas)
    
    return A * integral / (2 * np.pi)


def chi_suppresson(T, K_sfe, omega_sfe):
    if T <= 0 or K_sfe <= 0.0 or omega_sfe == 0.0:
        return 0.0
    return K_sfe * np.sin(0.5 * omega_sfe * T) ** 2


def chi_extended(T, alpha, A_1f, A_tls, omega_tls, gamma_tls, sequence_type):
    if T <= 0:
        return 0.0
    if sequence_type == 'cpmg':
        pulses = [(k - 0.5) / 8.0 for k in range(1, 9)]
    elif sequence_type == 'sfe':
        pulses = [0.0300, 0.1170, 0.2500, 0.4030, 0.5870, 0.7500, 0.8830, 0.9700]
    else:
        raise ValueError("Unknown sequence type")
    z_min = 0.1
    z_max = 100.0
    nw = 150
    z_vals = np.logspace(np.log10(z_min), np.log10(z_max), nw)
    omegas = z_vals / T
    F_vals = filter_function_val(omegas, pulses, T)
    S_1f = A_1f / (omegas ** alpha)
    S_tls = A_tls * gamma_tls / ((omegas - omega_tls) ** 2 + gamma_tls ** 2)
    S_vals = S_1f + S_tls
    integrand = S_vals * F_vals
    integral = np.trapezoid(integrand, omegas)
    return integral / (2 * np.pi)


def coherence_curve_with_suppresson(T_list, alpha, A, gamma_white, K_sfe, omega_sfe, sequence_type):
    vals = []
    for T in T_list:
        if T == 0:
            vals.append(1.0)
        else:
            chi_1f = chi_1overf(T, alpha, A, sequence_type)
            chi_sup = chi_suppresson(T, K_sfe, omega_sfe)
            chi_total = gamma_white * T + chi_1f + chi_sup
            vals.append(np.exp(-chi_total))
    return np.array(vals)


def coherence_curve_extended(T_list, alpha, A_1f, A_tls, omega_tls, gamma_tls, gamma_white, sequence_type):
    vals = []
    for T in T_list:
        if T == 0:
            vals.append(1.0)
        else:
            chi_ext = chi_extended(T, alpha, A_1f, A_tls, omega_tls, gamma_tls, sequence_type)
            chi_total = gamma_white * T + chi_ext
            vals.append(np.exp(-chi_total))
    return np.array(vals)


def coherence_curve_full(T_list, alpha, A, gamma_white, sequence_type):
    """
    Full coherence S(T) = exp(-gamma_white * T - chi_1f(T))
    gamma_white: white noise rate (T1, gate errors, etc.)
    """
    vals = []
    for T in T_list:
        if T == 0:
            vals.append(1.0)
        else:
            chi_1f = chi_1overf(T, alpha, A, sequence_type)
            chi_total = gamma_white * T + chi_1f
            vals.append(np.exp(-chi_total))
    return np.array(vals)


def fit_combined_full(x_data, alpha, A, gamma_white):
    """
    Combined fit with white noise.
    x_data: [T_cpmg..., T_sfe...]
    """
    n = len(x_data) // 2
    T_cpmg = x_data[:n]
    T_sfe = x_data[n:]
    
    S_cpmg = coherence_curve_full(T_cpmg, alpha, A, gamma_white, 'cpmg')
    S_sfe = coherence_curve_full(T_sfe, alpha, A, gamma_white, 'sfe')
    
    return np.concatenate([S_cpmg, S_sfe])


def fit_combined_with_suppresson(x_data, alpha, A, gamma_white, K_sfe, omega_sfe):
    n = len(x_data) // 2
    T_cpmg = x_data[:n]
    T_sfe = x_data[n:]
    S_cpmg = coherence_curve_with_suppresson(T_cpmg, alpha, A, gamma_white, K_sfe, omega_sfe, 'cpmg')
    S_sfe = coherence_curve_with_suppresson(T_sfe, alpha, A, gamma_white, K_sfe, omega_sfe, 'sfe')
    return np.concatenate([S_cpmg, S_sfe])


def fit_combined_extended(x_data, alpha, A_1f, A_tls, omega_tls, gamma_tls, gamma_white):
    n = len(x_data) // 2
    T_cpmg = x_data[:n]
    T_sfe = x_data[n:]
    S_cpmg = coherence_curve_extended(T_cpmg, alpha, A_1f, A_tls, omega_tls, gamma_tls, gamma_white, 'cpmg')
    S_sfe = coherence_curve_extended(T_sfe, alpha, A_1f, A_tls, omega_tls, gamma_tls, gamma_white, 'sfe')
    return np.concatenate([S_cpmg, S_sfe])


def main():
    print("=== SFE Noise Parameter Fitter (with White Noise) ===")
    print("Estimating (alpha, A, gamma_white) from IBM Fez 10-duration sweep...")
    
    dt_ns = 4.5
    durations_dt = np.array([0, 2222, 4444, 6666, 8888, 11111, 13333, 15555, 17777, 20000])
    T_us = durations_dt * dt_ns * 1e-3
    
    # Real experimental data (Job d4hith0lslhc73d1n5n0)
    P0_exp_cpmg = np.array([0.9951, 0.8896, 0.7646, 0.7725, 0.6240, 0.6641, 0.6504, 0.6240, 0.6172, 0.5664])
    P0_exp_sfe = np.array([1.0000, 0.7959, 0.8047, 0.7441, 0.6709, 0.6602, 0.6250, 0.5928, 0.5898, 0.5488])
    
    S_exp_cpmg = 2 * P0_exp_cpmg - 1
    S_exp_sfe = 2 * P0_exp_sfe - 1
    
    x_combined = np.concatenate([T_us, T_us])
    y_combined = np.concatenate([S_exp_cpmg, S_exp_sfe])
    
    # Fitting with 3 params: alpha, A, gamma_white
    # alpha: 0.7 ~ 1.3 (pink noise)
    # A: > 0
    # gamma_white: > 0 (includes T1, gate errors)
    
    p0 = [0.8, 0.5, 0.02]
    bounds = ([0.6, 0.0, 0.0], [1.5, np.inf, 0.1])
    
    try:
        popt, pcov = curve_fit(fit_combined_full, x_combined, y_combined, p0=p0, bounds=bounds, maxfev=5000)
        alpha_fit, A_fit, gamma_fit = popt
        
        perr = np.sqrt(np.diag(pcov))
        
        print(f"\n[Fit Result]")
        print(f"Alpha (1/f exponent)  : {alpha_fit:.4f} ± {perr[0]:.4f}")
        print(f"A (1/f Strength)      : {A_fit:.4e} ± {perr[1]:.2e}")
        print(f"Gamma_white (T1+gate) : {gamma_fit:.4f} ± {perr[2]:.4f} /us")
        print("-" * 50)
        
        S_fit_cpmg = coherence_curve_full(T_us, alpha_fit, A_fit, gamma_fit, 'cpmg')
        S_fit_sfe = coherence_curve_full(T_us, alpha_fit, A_fit, gamma_fit, 'sfe')
        
        print(f"{'Time(us)':<10} | {'CPMG Exp':<10} {'CPMG Fit':<10} | {'SFE Exp':<10} {'SFE Fit':<10}")
        for i in range(len(T_us)):
            print(f"{T_us[i]:<10.2f} | {S_exp_cpmg[i]:<10.4f} {S_fit_cpmg[i]:<10.4f} | {S_exp_sfe[i]:<10.4f} {S_fit_sfe[i]:<10.4f}")
            
        print("-" * 50)
        
        if len(T_us) > 1:
            T_test = T_us[1]
            chi_1f_cpmg = chi_1overf(T_test, alpha_fit, A_fit, 'cpmg')
            chi_1f_sfe = chi_1overf(T_test, alpha_fit, A_fit, 'sfe')
            chi_white = gamma_fit * T_test
            
            print(f"[Contribution at T={T_test:.1f}us]")
            print(f"  White noise (T1+gate): chi_white = {chi_white:.4f}")
            print(f"  1/f (CPMG): chi_1f = {chi_1f_cpmg:.4f}")
            print(f"  1/f (SFE):  chi_1f = {chi_1f_sfe:.4f}")
            print(f"  1/f reduction: CPMG/SFE = {chi_1f_cpmg/chi_1f_sfe:.2f}x")
        
        if 0.7 <= alpha_fit <= 1.3:
             print("\n[Physics Check] Alpha is in typical 1/f range (0.7–1.3). PASS")
        else:
             print(f"\n[Physics Check] Alpha={alpha_fit:.2f} outside 1/f range. Review model.")
             
        # Rust Engine Params
        print("\n[Rust Engine Params]")
        print(f"SFE_NOISE_ALPHA = {alpha_fit:.4f}")
        print(f"SFE_NOISE_SCALE = {A_fit:.4e}")
        print(f"(Note: gamma_white absorbed into effective p_phy in QEC sim)")

        K_sfe = float(os.environ.get("SFE_SUPPRESSON_K", "0.0"))
        omega_sfe = float(os.environ.get("SFE_SUPPRESSON_OMEGA", "0.0"))
        if K_sfe > 0.0 and omega_sfe != 0.0:
            S_fit_cpmg_sup = coherence_curve_with_suppresson(T_us, alpha_fit, A_fit, gamma_fit, K_sfe, omega_sfe, 'cpmg')
            S_fit_sfe_sup = coherence_curve_with_suppresson(T_us, alpha_fit, A_fit, gamma_fit, K_sfe, omega_sfe, 'sfe')
            print("-" * 50)
            print("[With Suppresson Contribution]")
            print(f"{'Time(us)':<10} | {'CPMG Sup':<10} {'SFE Sup':<10}")
            for i in range(len(T_us)):
                print(f"{T_us[i]:<10.2f} | {S_fit_cpmg_sup[i]:<10.4f} {S_fit_sfe_sup[i]:<10.4f}")

        try:
            p0_sup = [alpha_fit, A_fit, gamma_fit, 0.01, 0.1]
            bounds_sup = ([0.6, 0.0, 0.0, 0.0, 0.01], [1.5, np.inf, 0.1, 0.5, 10.0])
            popt_sup, pcov_sup = curve_fit(
                fit_combined_with_suppresson,
                x_combined,
                y_combined,
                p0=p0_sup,
                bounds=bounds_sup,
                maxfev=10000,
            )
            alpha_sup, A_sup, gamma_sup, K_sup, omega_sup = popt_sup
            print("-" * 50)
            print("[Suppresson Fit Result]")
            print(f"Alpha_sup        : {alpha_sup:.4f}")
            print(f"A_sup            : {A_sup:.4e}")
            print(f"Gamma_white_sup  : {gamma_sup:.4f} /us")
            print(f"K_sfe_fit        : {K_sup:.4e}")
            print(f"Omega_sfe_fit    : {omega_sup:.4f} rad/us")
            S_cpmg_cur = coherence_curve_with_suppresson(T_us, alpha_sup, A_sup, gamma_sup, K_sup, omega_sup, 'cpmg')
            S_sfe_cur = coherence_curve_with_suppresson(T_us, alpha_sup, A_sup, gamma_sup, K_sup, omega_sup, 'sfe')
            S_cpmg_removed = coherence_curve_full(T_us, alpha_sup, A_sup, gamma_sup, 'cpmg')
            S_sfe_removed = coherence_curve_full(T_us, alpha_sup, A_sup, gamma_sup, 'sfe')
            idx_mid = len(T_us) // 2
            Tc = T_us[idx_mid]
            Sc_cur = S_cpmg_cur[idx_mid]
            Sc_rm = S_cpmg_removed[idx_mid]
            Ss_cur = S_sfe_cur[idx_mid]
            Ss_rm = S_sfe_removed[idx_mid]
            err_c_cur = max(1.0 - Sc_cur, 1e-12)
            err_c_rm = max(1.0 - Sc_rm, 1e-12)
            err_s_cur = max(1.0 - Ss_cur, 1e-12)
            err_s_rm = max(1.0 - Ss_rm, 1e-12)
            imp_c = err_c_cur / err_c_rm
            imp_s = err_s_cur / err_s_rm
            print("-" * 50)
            print(f"[Ideal Suppresson Removal at T={Tc:.1f}us]")
            print(f"  CPMG: error_now={err_c_cur:.4e}, error_removed={err_c_rm:.4e}, factor={imp_c:.2f}x")
            print(f"  SFE : error_now={err_s_cur:.4e}, error_removed={err_s_rm:.4e}, factor={imp_s:.2f}x")
        except Exception as e_sup:
            print(f"Suppresson fit failed: {e_sup}")

        try:
            p0_ext = [max(alpha_fit, 0.7), max(A_fit, 1e-6), 0.01, 0.05, 0.05, gamma_fit]
            bounds_ext = ([0.5, 0.0, 0.0, 0.01, 0.001, 0.0], [1.5, np.inf, np.inf, 1.0, 1.0, 0.1])
            popt_ext, pcov_ext = curve_fit(
                fit_combined_extended,
                x_combined,
                y_combined,
                p0=p0_ext,
                bounds=bounds_ext,
                maxfev=10000,
            )
            alpha_ext, A_1f_ext, A_tls_ext, omega_tls_ext, gamma_tls_ext, gamma_white_ext = popt_ext
            print("-" * 50)
            print("[Extended Spectrum Fit Result]")
            print(f"Alpha_ext        : {alpha_ext:.4f}")
            print(f"A_1f_ext         : {A_1f_ext:.4e}")
            print(f"A_tls_ext        : {A_tls_ext:.4e}")
            print(f"Omega_tls_ext    : {omega_tls_ext:.4f} rad/us")
            print(f"Gamma_tls_ext    : {gamma_tls_ext:.4f} rad/us")
            print(f"Gamma_white_ext  : {gamma_white_ext:.4f} /us")
            S_cpmg_ext = coherence_curve_extended(T_us, alpha_ext, A_1f_ext, A_tls_ext, omega_tls_ext, gamma_tls_ext, gamma_white_ext, 'cpmg')
            S_sfe_ext = coherence_curve_extended(T_us, alpha_ext, A_1f_ext, A_tls_ext, omega_tls_ext, gamma_tls_ext, gamma_white_ext, 'sfe')
            print(f"{'Time(us)':<10} | {'CPMG Ext':<10} {'SFE Ext':<10}")
            for i in range(len(T_us)):
                print(f"{T_us[i]:<10.2f} | {S_cpmg_ext[i]:<10.4f} {S_sfe_ext[i]:<10.4f}")
        except Exception as e_ext:
            print(f"Extended spectrum fit failed: {e_ext}")
        
    except Exception as e:
        print(f"Fitting failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

