import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

"""
SFE Quantum Suppression Field (QSF) Network Simulation
====================================================
이 코드는 억압장(Suppression Field)을 서로 독립적인 입자가 아닌,
상호 연결된 진동자 네트워크(Interconnected Oscillator Network)로 모델링하여
물질원(Source)에 대한 집단적 반응(Collective Response)을 시뮬레이션합니다.

물리적 모델:
- 1차원 격자 (Lattice)
- 각 격자점 i에 억압장 값 Phi[i] 존재
- 인접 격자점 간 탄성 상호작용 (커플링 k)
- 각 지점의 자체 포텐셜 V(Phi) (Double Well Potential)
- 중앙에 물질원(Source) J가 존재할 때의 반응

방정식:
d^2Phi_i/dt^2 = -dV/dPhi_i + k*(Phi_{i+1} + Phi_{i-1} - 2*Phi_i) + J_i
"""

def potential_derivative(phi, mu=1.0, lam=1.0):
    """
    SFE 자체 포텐셜의 도함수 dV/dPhi
    V(phi) = -0.5*mu^2*phi^2 + 0.25*lam*phi^4
    dV/dphi = -mu^2*phi + lam*phi^3
    """
    return -mu**2 * phi + lam * phi**3

def system_equations(y, t, N, k, mu, lam, source_J):
    """
    미분 방정식 시스템 정의
    y: [Phi_0, ..., Phi_{N-1}, dPhi_0/dt, ..., dPhi_{N-1}/dt]
    """
    phi = y[:N]
    dphi_dt = y[N:]
    
    d2phi_dt2 = np.zeros(N)
    
    # 라플라시안 (인접 상호작용)
    laplacian = np.zeros(N)
    for i in range(N):
        left = phi[i-1] if i > 0 else 0 # 경계조건: 0
        right = phi[i+1] if i < N-1 else 0 # 경계조건: 0
        laplacian[i] = left + right - 2*phi[i]
    
    # 운동 방정식: 가속도 = -포텐셜기울기 + 탄성력 + 외부소스 - 감쇠(Damping)
    # 감쇠항 -0.5*dphi_dt는 에너지 발산을 막고 평형 도달을 위해 추가
    d2phi_dt2 = -potential_derivative(phi, mu, lam) + k * laplacian + source_J - 0.5 * dphi_dt
    
    return np.concatenate([dphi_dt, d2phi_dt2])

def run_simulation():
    # 파라미터 설정
    N = 50          # 격자점 수
    k = 5.0         # 상호작용 강도 (클수록 매질이 단단하게 연결됨)
    mu = 1.0
    lam = 1.0
    
    # 시간 설정
    t = np.linspace(0, 20, 200)
    
    # 초기 조건: 진공 상태 (Phi_v = mu/sqrt(lam) = 1.0)
    phi_vac = mu / np.sqrt(lam)
    y0 = np.zeros(2 * N)
    y0[:N] = phi_vac  # 모든 지점이 진공값에 있음
    
    # 물질원(Source) 설정: 중앙에 위치
    source_J = np.zeros(N)
    mid = N // 2
    # 물질은 억압장을 '억압'하는 방향(음의 방향)으로 힘을 가함 (SFE 핵심: g_B * m_0)
    # 여기서는 -5.0 정도의 힘을 중앙 5개 지점에 가함
    source_J[mid-2:mid+3] = -5.0
    
    # 미분 방정식 풀이
    sol = odeint(system_equations, y0, t, args=(N, k, mu, lam, source_J))
    
    # 결과 시각화
    phi_history = sol[:, :N]
    
    plt.figure(figsize=(12, 6))
    
    # 1. 최종 상태 공간 분포
    plt.subplot(1, 2, 1)
    plt.plot(np.arange(N), phi_history[0], 'b--', label='Initial (Vacuum)')
    plt.plot(np.arange(N), phi_history[-1], 'r-', linewidth=2, label='Final (With Matter)')
    plt.axhline(phi_vac, color='g', alpha=0.3, linestyle=':', label='Vacuum Expectation')
    plt.title("Spatial Distribution of Suppression Field")
    plt.xlabel("Lattice Index (Space)")
    plt.ylabel("Phi Value")
    plt.legend()
    plt.grid(True)
    
    # 설명: 중앙의 물질 때문에 억압장 값이 뚝 떨어짐 (억압 효과).
    # 중요한 것은 중앙만 떨어지는 게 아니라, 주변부까지 부드럽게 같이 휘어짐 (상호연결성).
    
    # 2. 중앙 지점의 시간 변화
    plt.subplot(1, 2, 2)
    plt.plot(t, phi_history[:, mid], 'k-', label=f'Center Point ({mid})')
    plt.plot(t, phi_history[:, mid-5], 'b-', label=f'Neighbor Point ({mid-5})')
    plt.plot(t, phi_history[:, 0], 'g-', label='Far Point (0)')
    plt.title("Temporal Evolution at Specific Points")
    plt.xlabel("Time")
    plt.ylabel("Phi Value")
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('examples/qsf_network_result.png')
    print("Simulation complete. Result saved to examples/qsf_network_result.png")
    
    # 결과 분석 텍스트 출력
    print("\n[SFE QSF Simulation Analysis]")
    print(f"Vacuum Expectation Value: {phi_vac}")
    print(f"Center Point Final Value: {phi_history[-1, mid]:.4f}")
    print(f"Suppression Ratio (at center): {1 - phi_history[-1, mid]/phi_vac:.4f}")
    print("Interpretation: The presence of matter locally suppresses the field value.")
    print("Crucially, the 'k' coupling causes this suppression to spread to neighbors,")
    print("demonstrating the 'Collective Medium' behavior of the QSF.")

if __name__ == "__main__":
    run_simulation()

