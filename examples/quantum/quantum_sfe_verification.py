"""
SFE 양자 효과 검증 시뮬레이션

억압장이 양자 시스템(결맞음, 얽힘, 게이트 충실도)에 미치는 영향을 
시뮬레이션하고 예측값을 계산합니다.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from typing import Tuple, List

# 물리 상수
HBAR = 1.054571817e-34  # J·s
KB = 1.380649e-23       # J/K
C = 2.99792458e8        # m/s

class SFEQuantumEnvironment:
    """SFE 억압장 양자 환경 클래스"""
    
    def __init__(self, epsilon: float = 0.37):
        """
        Args:
            epsilon: 질량 억압 계수 (우주론으로부터 고정)
        """
        self.epsilon = epsilon
        self.scaling_decoherence = 1 / (1 - epsilon)  # 1.587
        self.scaling_lifetime = 1 / np.sqrt(1 - epsilon)  # 1.259
        
    def decoherence_time(
        self, 
        m0: float,           # 입자 정지 질량 (kg)
        T: float,            # 온도 (K)
        lambda_eff: float,   # 유효 상호작용 길이 (m)
        standard: bool = False
    ) -> float:
        """
        양자 결맞음 시간 계산
        
        Args:
            m0: 입자 정지 질량
            T: 환경 온도
            lambda_eff: 유효 상호작용 길이
            standard: True이면 표준 이론, False이면 SFE
            
        Returns:
            결맞음 시간 (s)
        """
        # 표준 이론
        tau_std = HBAR**2 / (2 * m0 * KB * T * lambda_eff**2)
        
        if standard:
            return tau_std
        else:
            # SFE 보정
            return tau_std * self.scaling_decoherence
    
    def thermal_noise_psd(
        self,
        m0: float,          # 테스트 질량 (kg)
        T: float,           # 온도 (K)
        omega: float,       # 각진동수 (rad/s)
        standard: bool = False
    ) -> float:
        """
        열잡음 변위 스펙트럼 밀도 (LIGO 등)
        
        Args:
            m0: 테스트 질량
            T: 온도
            omega: 각진동수
            standard: True이면 표준 이론
            
        Returns:
            S_x(ω) (m²/Hz)
        """
        # 표준 이론
        S_x_std = KB * T / (m0 * omega**2)
        
        if standard:
            return S_x_std
        else:
            # SFE 보정
            return S_x_std * self.scaling_decoherence
    
    def relativistic_lifetime(
        self,
        tau_proper_std: float,  # 표준 이론 고유 수명 (s)
        gamma: float,            # 로렌츠 인자
        standard: bool = False
    ) -> float:
        """
        상대론적 입자 관측 수명 (뮤온 등)
        
        Args:
            tau_proper_std: 표준 이론 고유 수명
            gamma: 로렌츠 인자
            standard: True이면 표준 이론
            
        Returns:
            관측 수명 (s)
        """
        # 표준 이론: tau_obs = gamma * tau_proper
        tau_obs_std = gamma * tau_proper_std
        
        if standard:
            return tau_obs_std
        else:
            # SFE 보정
            return tau_obs_std * self.scaling_lifetime


class SFELindblad:
    """SFE 환경에서의 Lindblad 마스터 방정식 솔버"""
    
    def __init__(self, epsilon: float = 0.37, n_levels: int = 2):
        """
        Args:
            epsilon: 억압 계수
            n_levels: 에너지 준위 수 (기본 2-레벨 시스템)
        """
        self.epsilon = epsilon
        self.n = n_levels
        self.gamma_eff = None  # 시스템별로 설정
    
    def set_decay_rate(self, gamma_std: float):
        """
        표준 이론 감쇠율을 SFE 보정
        
        Args:
            gamma_std: 표준 이론 감쇠율 (1/s)
        """
        self.gamma_eff = gamma_std * (1 - self.epsilon)
    
    def lindblad_rhs(self, rho_vec: np.ndarray, t: float, H: np.ndarray, L: np.ndarray) -> np.ndarray:
        """
        Lindblad 마스터 방정식 우변
        
        d(rho)/dt = -i/ℏ[H, rho] + gamma*(L*rho*L† - 1/2{L†L, rho})
        
        Args:
            rho_vec: 밀도 행렬 벡터화
            t: 시간
            H: 해밀토니안
            L: Lindblad 연산자
            
        Returns:
            d(rho_vec)/dt
        """
        # 밀도 행렬 복원
        rho = rho_vec.reshape((self.n, self.n))
        
        # Hamiltonian 진화
        comm = -1j / HBAR * (H @ rho - rho @ H)
        
        # Lindblad 항
        if self.gamma_eff is not None:
            L_dagger = L.conj().T
            lindblad = self.gamma_eff * (
                L @ rho @ L_dagger 
                - 0.5 * (L_dagger @ L @ rho + rho @ L_dagger @ L)
            )
        else:
            lindblad = 0
        
        drho_dt = comm + lindblad
        return drho_dt.flatten()
    
    def solve(
        self, 
        rho0: np.ndarray, 
        t_span: np.ndarray,
        H: np.ndarray,
        L: np.ndarray
    ) -> np.ndarray:
        """
        Lindblad 방정식 시간 전개
        
        Args:
            rho0: 초기 밀도 행렬
            t_span: 시간 배열
            H: 해밀토니안
            L: Lindblad 연산자
            
        Returns:
            시간에 따른 밀도 행렬 (t, n, n)
        """
        rho0_vec = rho0.flatten()
        sol = odeint(self.lindblad_rhs, rho0_vec, t_span, args=(H, L))
        return sol.reshape((len(t_span), self.n, self.n))


def example_c60_decoherence():
    """예제: C60 분자 결맞음 시간 예측"""
    
    env = SFEQuantumEnvironment()
    
    # C60 분자 파라미터
    m_c60 = 60 * 1.66054e-27  # kg (원자질량단위 × 60)
    T = 300  # K
    lambda_eff = 1e-9  # m (나노미터 스케일)
    
    tau_std = env.decoherence_time(m_c60, T, lambda_eff, standard=True)
    tau_sfe = env.decoherence_time(m_c60, T, lambda_eff, standard=False)
    
    print("=== C60 분자 결맞음 시간 예측 ===")
    print(f"표준 이론: {tau_std:.3e} s")
    print(f"SFE 이론: {tau_sfe:.3e} s")
    print(f"배율: {tau_sfe/tau_std:.3f} (예측: 1.587)")
    print()


def example_ligo_noise():
    """예제: LIGO 열잡음 스펙트럼 예측"""
    
    env = SFEQuantumEnvironment()
    
    # LIGO 테스트 질량 파라미터
    m_test = 40  # kg (거울 질량)
    T = 300  # K
    
    # 주파수 스윕
    freq = np.logspace(1, 3, 100)  # 10 Hz ~ 1 kHz
    omega = 2 * np.pi * freq
    
    S_x_std = [env.thermal_noise_psd(m_test, T, w, standard=True) for w in omega]
    S_x_sfe = [env.thermal_noise_psd(m_test, T, w, standard=False) for w in omega]
    
    plt.figure(figsize=(10, 6))
    plt.loglog(freq, S_x_std, 'b-', label='표준 이론', linewidth=2)
    plt.loglog(freq, S_x_sfe, 'r--', label='SFE 이론', linewidth=2)
    plt.xlabel('주파수 (Hz)', fontsize=12)
    plt.ylabel('변위 PSD (m²/Hz)', fontsize=12)
    plt.title('LIGO 열잡음 스펙트럼 예측', fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('ligo_noise_sfe.png', dpi=150)
    print("LIGO 노이즈 스펙트럼 저장: ligo_noise_sfe.png")
    print(f"배율: {S_x_sfe[50]/S_x_std[50]:.3f} (예측: 1.587)")
    print()


def example_muon_lifetime():
    """예제: 우주선 뮤온 생존율 예측"""
    
    env = SFEQuantumEnvironment()
    
    # 뮤온 파라미터
    tau_muon = 2.197e-6  # s (고유 수명)
    
    # 에너지 스윕
    E_array = np.logspace(0, 3, 50)  # GeV
    m_muon_gev = 0.1057  # GeV/c²
    gamma_array = E_array / m_muon_gev
    
    tau_obs_std = [env.relativistic_lifetime(tau_muon, g, standard=True) for g in gamma_array]
    tau_obs_sfe = [env.relativistic_lifetime(tau_muon, g, standard=False) for g in gamma_array]
    
    plt.figure(figsize=(10, 6))
    plt.loglog(E_array, tau_obs_std, 'b-', label='표준 이론', linewidth=2)
    plt.loglog(E_array, tau_obs_sfe, 'r--', label='SFE 이론', linewidth=2)
    plt.xlabel('에너지 (GeV)', fontsize=12)
    plt.ylabel('관측 수명 (s)', fontsize=12)
    plt.title('상대론적 뮤온 수명 예측', fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('muon_lifetime_sfe.png', dpi=150)
    print("뮤온 수명 곡선 저장: muon_lifetime_sfe.png")
    print(f"배율: {tau_obs_sfe[25]/tau_obs_std[25]:.3f} (예측: 1.259)")
    print()


def example_qubit_decoherence():
    """예제: 초전도 큐비트 결맞음 시간"""
    
    # 표준 환경
    solver_std = SFELindblad(epsilon=0)
    solver_sfe = SFELindblad(epsilon=0.37)
    
    # 감쇠율 설정 (전형적인 큐비트 값)
    gamma_std = 1e5  # 1/s (T1 ~ 10 μs)
    solver_std.set_decay_rate(gamma_std)
    solver_sfe.set_decay_rate(gamma_std)
    
    # 2-레벨 시스템
    # 초기 상태: |0⟩ + |1⟩ (중첩 상태)
    rho0 = np.array([[0.5, 0.5], [0.5, 0.5]], dtype=complex)
    
    # 해밀토니안 (간단한 경우: H=0)
    H = np.zeros((2, 2), dtype=complex)
    
    # Lindblad 연산자 (σ⁻, 진폭 감쇠)
    L = np.array([[0, 1], [0, 0]], dtype=complex)
    
    # 시간 전개
    t_span = np.linspace(0, 50e-6, 1000)  # 50 μs
    
    rho_std = solver_std.solve(rho0, t_span, H, L)
    rho_sfe = solver_sfe.solve(rho0, t_span, H, L)
    
    # 비대각 성분 (결맞음 지표)
    coherence_std = np.abs(rho_std[:, 0, 1])
    coherence_sfe = np.abs(rho_sfe[:, 0, 1])
    
    plt.figure(figsize=(10, 6))
    plt.plot(t_span * 1e6, coherence_std, 'b-', label='표준 이론', linewidth=2)
    plt.plot(t_span * 1e6, coherence_sfe, 'r--', label='SFE 이론', linewidth=2)
    plt.xlabel('시간 (μs)', fontsize=12)
    plt.ylabel('결맞음 크기 |ρ₀₁|', fontsize=12)
    plt.title('초전도 큐비트 결맞음 시간', fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('qubit_decoherence_sfe.png', dpi=150)
    print("큐비트 결맞음 곡선 저장: qubit_decoherence_sfe.png")
    
    # T2 시간 추정 (1/e 시간)
    idx_std = np.argmin(np.abs(coherence_std - 1/np.e * 0.5))
    idx_sfe = np.argmin(np.abs(coherence_sfe - 1/np.e * 0.5))
    T2_std = t_span[idx_std]
    T2_sfe = t_span[idx_sfe]
    
    print(f"T2 (표준): {T2_std*1e6:.2f} μs")
    print(f"T2 (SFE): {T2_sfe*1e6:.2f} μs")
    print(f"배율: {T2_sfe/T2_std:.3f} (예측: ~1.587)")
    print()


def parameter_scan():
    """파라미터 스캔: epsilon 값에 따른 스케일링"""
    
    epsilon_array = np.linspace(0, 0.5, 100)
    scaling_dec = 1 / (1 - epsilon_array)
    scaling_life = 1 / np.sqrt(1 - epsilon_array)
    
    plt.figure(figsize=(10, 6))
    plt.plot(epsilon_array, scaling_dec, 'b-', label='결맞음/열잡음 배율', linewidth=2)
    plt.plot(epsilon_array, scaling_life, 'r--', label='뮤온 수명 배율', linewidth=2)
    plt.axvline(0.37, color='g', linestyle=':', label='ε = 0.37 (관측)', linewidth=2)
    plt.axhline(1.587, color='gray', linestyle=':', alpha=0.5)
    plt.axhline(1.259, color='gray', linestyle=':', alpha=0.5)
    plt.xlabel('억압 계수 ε', fontsize=12)
    plt.ylabel('스케일링 배율', fontsize=12)
    plt.title('SFE 효과 파라미터 의존성', fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('sfe_scaling_epsilon.png', dpi=150)
    print("파라미터 스캔 저장: sfe_scaling_epsilon.png")
    print()


if __name__ == "__main__":
    print("\n" + "="*60)
    print(" SFE 양자 효과 검증 시뮬레이션")
    print("="*60 + "\n")
    
    example_c60_decoherence()
    example_ligo_noise()
    example_muon_lifetime()
    example_qubit_decoherence()
    parameter_scan()
    
    print("\n" + "="*60)
    print(" 모든 시뮬레이션 완료")
    print("="*60 + "\n")

