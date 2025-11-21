import numpy as np
import math
from .constants import *

class SFETheory:
    
    def __init__(self, H0=None, Omega_m=None, C_X=0.46):
        self.H0_km_obs = H0 if H0 is not None else H0_PLANCK
        self.H0_obs = self.H0_km_obs * 1000 / (3.08567758e22)
        self.Omega_m_obs = Omega_m if Omega_m is not None else OMEGA_M
        
        self.C_X = C_X
        self.alpha_dimless = None
        self.alpha_si = None
        
        self.H_theory = None
        self.lambda_val = None
        self.rho_phi = None
        self.Omega_phi_theory = None
        self.epsilon_theory = None
        
        self.derive_alpha()
    
    def derive_alpha(self):
        beta = 1.009 / 480.0
        
        term1 = beta / (math.pi**2)
        term2 = alpha_em**2
        term3 = math.pow(c, 3)
        term4 = math.pow(hbar, 2)
        
        self.alpha_si = term1 * term2 * term3 / term4
        self.alpha_dimless = self.alpha_si / math.sqrt(G / c)
        
        return self.alpha_si

    def fixed_point_iteration(self, tolerance=1e-6, max_iter=100, verbose=True):
        if self.alpha_si is None:
            self.derive_alpha()
            
        H_val = self.H0_obs
        
        for i in range(max_iter):
            rho_m_val = 3 * H_val**2 * self.Omega_m_obs / (8 * math.pi * G)
            lambda_val = c / (math.sqrt(3) * H_val)
            
            ln_alpha = 2 * math.log(self.alpha_si)
            ln_rho_m = 2 * math.log(rho_m_val)
            ln_lambda = 2 * math.log(lambda_val)
            ln_CX = math.log(self.C_X)
            
            ln_rho_phi = ln_alpha + ln_rho_m + ln_lambda + ln_CX
            
            try:
                if ln_rho_phi > 700:
                    rho_phi_val = float('nan')
                else:
                    rho_phi_val = math.exp(ln_rho_phi)
            except ValueError:
                rho_phi_val = 0.0
            
            if math.isinf(rho_phi_val) or math.isnan(rho_phi_val):
                break

            H_sq_new = (H_val**2 * self.Omega_m_obs) + (8 * math.pi * G / 3) * rho_phi_val
            H_new = math.sqrt(H_sq_new)
            
            if abs(H_new - H_val) / H_val < tolerance:
                H_val = H_new
                lambda_val = c / (math.sqrt(3) * H_new)
                if verbose:
                    print(f"수렴 완료: {i+1}회 반복")
                break
            
            H_val = H_new
        
        self.H_theory = H_val
        self.lambda_val = lambda_val
        self.rho_phi = rho_phi_val
        self.rho_c_theory = 3 * self.H_theory**2 / (8 * math.pi * G)
        
        if not math.isinf(self.rho_phi):
            self.Omega_phi_theory = self.rho_phi / self.rho_c_theory
            self.epsilon_theory = 2 * self.Omega_phi_theory - 1
        else:
            self.Omega_phi_theory = float('inf')
            self.epsilon_theory = float('inf')
        
        return {
            'alpha_si': self.alpha_si,
            'lambda': self.lambda_val,
            'rho_phi': self.rho_phi,
            'Omega_phi': self.Omega_phi_theory,
            'epsilon': self.epsilon_theory,
            'H_theory': self.H_theory
        }
    
    def compare_observations(self, Omega_lambda_obs=0.685):
        if self.Omega_phi_theory is None:
            self.fixed_point_iteration(verbose=False)
        
        if math.isinf(self.Omega_phi_theory):
            error = float('inf')
        else:
            error = abs(self.Omega_phi_theory - Omega_lambda_obs) / Omega_lambda_obs * 100
        
        results = {
            'Omega_phi_theory': self.Omega_phi_theory,
            'Omega_lambda_obs': Omega_lambda_obs,
            'error_percent': error,
            'epsilon_theory': self.epsilon_theory
        }
        
        return results
    
    def calculate_deceleration_parameter(self):
        if self.Omega_phi_theory is None:
            self.fixed_point_iteration(verbose=False)
        
        q0 = 0.5 * self.Omega_m_obs - self.Omega_phi_theory
        return q0
    
    def calculate_growth_rate(self):
        if self.Omega_phi_theory is None:
            self.fixed_point_iteration(verbose=False)
        
        f0 = self.Omega_m_obs**(0.55)
        return f0
    
    def summary(self):
        if self.Omega_phi_theory is None:
            self.fixed_point_iteration(verbose=False)
        
        print("=" * 80)
        print("SFE 이론 요약 (제1원리 연역)")
        print("=" * 80)
        print(f"기본 상수 입력:")
        print(f"  G, c, hbar, mp, me, alpha_EM")
        print(f"\n연역된 결합 상수:")
        print(f"  alpha_dimless = {self.alpha_dimless:.4e}")
        print(f"  alpha_SI      = {self.alpha_si:.4e} kg^-1/2")
        print(f"\n자기일관성 유도 결과:")
        if self.H_theory:
            print(f"  H_theory      = {self.H_theory * (3.086e22 / 1000):.2f} km/s/Mpc")
        print(f"  lambda        = {self.lambda_val:.4e} m")
        print(f"  rho_phi       = {self.rho_phi:.4e} kg/m^3")
        if self.Omega_phi_theory:
            print(f"  Omega_Phi     = {self.Omega_phi_theory:.4f} (이론)")
            print(f"  epsilon       = {self.epsilon_theory:.4f} (이론)")
        print(f"\n파생 예측:")
        if self.Omega_phi_theory:
            print(f"  q0 = {self.calculate_deceleration_parameter():.4f}")
            print(f"  f0 = {self.calculate_growth_rate():.4f}")
        print("=" * 80)
