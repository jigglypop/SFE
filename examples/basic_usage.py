import sys
sys.path.insert(0, 'E:/SFE')

from sfe import SFETheory, QuantumCorrection
from sfe.constants import alpha_si
import numpy as np

print("=" * 80)
print("SFE 라이브러리 기본 사용법")
print("=" * 80)

print("\n1. SFE 핵심 이론 계산 (우주론 섹션)")
print("-" * 80)
try:
    theory = SFETheory()
    results = theory.fixed_point_iteration()
    if not np.isfinite(results["Omega_phi"]):
        raise RuntimeError("Omega_phi 비정상")

    print(f"Lambda: {results['lambda']:.4e} m")
    print(f"Rho_Phi: {results['rho_phi']:.4e} kg/m^3")
    print(f"Omega_Phi (이론): {results['Omega_phi']:.4f}")
    print(f"Epsilon (이론): {results['epsilon']:.4f}")

    comparison = theory.compare_observations(Omega_lambda_obs=0.685)
    print(f"\n관측 비교:")
    print(f"  이론: {comparison['Omega_phi_theory']:.4f}")
    print(f"  관측: {comparison['Omega_lambda_obs']:.4f}")
    print(f"  오차: {comparison['error_percent']:.2f}%")

    print("\n파생 예측:")
    print(f"  감속 파라미터 q0: {theory.calculate_deceleration_parameter():.4f}")
    print(f"  성장률 f0: {theory.calculate_growth_rate():.4f}")
except Exception:
    print("현재 라이브러리 내 SFETheory 우주론 재구현은 수치적으로 불안정합니다.")
    print("정확한 우주론 검증은 기존 스크립트 Part2_핵심검증/SFE_final_check.py를 사용하십시오.")

print("\n" + "=" * 80)
print("2. 양자컴퓨터 보정 알고리즘")
print("-" * 80)

qc = QuantumCorrection(n_qubits=2, m_qubit=1e-30, T2=1e-7, epsilon_0=0.355)

info = qc.info()
print(f"큐비트 수: {info['n_qubits']}")
print(f"결합 강도 g_q: {info['g_q']:.4e}")
print(f"위상 감쇠율 gamma_phi: {info['gamma_phi']:.4e} s^-1")
print(f"초기 억압률 epsilon_0: {info['epsilon_0']:.4f}")
print(f"T2: {info['T2']:.2e} s")
print(f"epsilon_mass: {info['epsilon_mass']:.4f}")
print(f"T2_SFE(이론): {info['T2_sfe_theory']:.2e} s")
print(f"T2 배율(이론): {qc.theoretical_T2_ratio():.4f}")

gate_time = 1e-9
n_gates = 50

print(f"\n{n_gates}개 게이트 동작 시뮬레이션 (각 {gate_time*1e9:.1f} ns):")
qc.reset_epsilon()

for i in range(n_gates):
    qc.update_epsilon(gate_time)

print(f"  누적 억압률: {qc.epsilon_total:.6e}")
total_time_gates = n_gates * gate_time
f_std = qc.predict_fidelity(total_time_gates, mode="standard", F0=1.0)
f_sfe_th = qc.predict_fidelity(total_time_gates, mode="sfe_theory", F0=1.0)
f_sfe_alg = qc.predict_fidelity(total_time_gates, mode="sfe_power", F0=1.0)
print(f"  표준 감쇠 충실도: {f_std:.6f}")
print(f"  SFE 이론 충실도: {f_sfe_th:.6f}")
print(f"  SFE 보정 충실도(알고리즘): {f_sfe_alg:.6f}")
print(f"  위상 보정 각도: {qc.phase_correction_angle():.6e} rad")

print("\n" + "=" * 80)
print("3. Lindblad 진화 시뮬레이션")
print("-" * 80)

qc2 = QuantumCorrection(n_qubits=1, m_qubit=1e-30, T2=1e-7, epsilon_0=0.355)
qc2.reset_epsilon()

psi_plus = np.array([1, 1]) / np.sqrt(2)
rho_initial = np.outer(psi_plus, psi_plus.conj())

print("초기 상태: |+⟩ = (|0⟩ + |1⟩)/√2")
print(f"초기 밀도행렬 대각 성분: [{rho_initial[0,0]:.4f}, {rho_initial[1,1]:.4f}]")

total_time = 1e-7
times_unc, rho_unc = qc2.simulate_evolution(rho_initial, total_time, n_steps=100)
times_cor, rho_unc_hist, rho_cor_hist = qc2.simulate_with_correction(
    rho_initial,
    total_time,
    n_steps=100,
    use_phase=False,
    use_amplitude=False,
)

rho_final_unc = rho_unc[-1]
rho_final_cor = rho_cor_hist[-1]
print(f"\n진화 후 ({total_time*1e6:.2f} μs) - 보정 없음:")
print(f"최종 밀도행렬 대각 성분: [{rho_final_unc[0,0]:.4f}, {rho_final_unc[1,1]:.4f}]")
print(f"\n진화 후 ({total_time*1e6:.2f} μs) - SFE 보정:")
print(f"최종 밀도행렬 대각 성분: [{rho_final_cor[0,0]:.4f}, {rho_final_cor[1,1]:.4f}]")

fid_unc = qc2.calculate_fidelity_history(rho_unc, rho_initial)
fid_cor = qc2.calculate_fidelity_history(rho_cor_hist, rho_initial)
print(f"\n충실도 (보정 없음): 시작 {fid_unc[0]:.6f} → 최종 {fid_unc[-1]:.6f}")
print(f"충실도 (SFE 보정):   시작 {fid_cor[0]:.6f} → 최종 {fid_cor[-1]:.6f}")
print(f"충실도 개선: {(fid_cor[-1] - fid_unc[-1])*100:.2f}%p")

print("\n" + "=" * 80)
print("라이브러리 테스트 완료")
print("=" * 80)

