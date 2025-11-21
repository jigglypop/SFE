import sys
sys.path.insert(0, 'E:/SFE')

import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    message=r"Glyph .* missing from font\(s\) DejaVu Sans\."
)

from sfe import QuantumCorrection
import numpy as np

print("=" * 80)
print("양자 회로 SFE 보정 데모")
print("=" * 80)

qc = QuantumCorrection(n_qubits=2, m_qubit=1e-30, T2=1e-7, epsilon_0=0.355)

print("\n시뮬레이션 파라미터:")
info = qc.info()
for key, value in info.items():
    if isinstance(value, float):
        if abs(value) > 1e3 or abs(value) < 1e-3:
            print(f"  {key}: {value:.4e}")
        else:
            print(f"  {key}: {value:.6f}")
    else:
        print(f"  {key}: {value}")

print("\n" + "=" * 80)
print("테스트 1: 게이트 동작에 따른 억압률 누적")
print("=" * 80)

gate_time = 1e-9
max_gates = 100

gate_counts = []
epsilon_values = []

qc.reset_epsilon()
for i in range(max_gates + 1):
    gate_counts.append(i)
    epsilon_values.append(qc.epsilon_total)
    if i < max_gates:
        qc.update_epsilon(gate_time)

print(f"게이트 0개: epsilon = {epsilon_values[0]:.6e}")
print(f"게이트 50개: epsilon = {epsilon_values[50]:.6e}")
print(f"게이트 100개: epsilon = {epsilon_values[100]:.6e}")

plt.figure(figsize=(10, 6))
plt.plot(gate_counts, epsilon_values, 'b-', linewidth=2)
plt.axhline(y=qc.epsilon_0, color='r', linestyle='--', label=f'초기값 ε₀={qc.epsilon_0}')
plt.xlabel('게이트 동작 횟수')
plt.ylabel('총 억압률 ε(t)')
plt.title('SFE 억압률의 누적 진화')
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig('E:/SFE/examples/epsilon_evolution_demo.png', dpi=150)
print("\n그래프 저장: epsilon_evolution_demo.png")

print("\n" + "=" * 80)
print("테스트 2: 충실도 감쇠 비교")
print("=" * 80)

times = np.linspace(0, 1e-6, 100)

fidelity_standard = []
fidelity_sfe = []

for t in times:
    f_std = qc.predict_fidelity(t, mode="standard", F0=1.0)
    f_sfe = qc.predict_fidelity(t, mode="sfe_power", F0=1.0)
    fidelity_standard.append(f_std)
    fidelity_sfe.append(f_sfe)

print(f"시간 0 μs:")
print(f"  표준: {fidelity_standard[0]:.6f}")
print(f"  SFE: {fidelity_sfe[0]:.6f}")

mid_idx = len(times) // 2
print(f"\n시간 {times[mid_idx]*1e6:.2f} μs:")
print(f"  표준: {fidelity_standard[mid_idx]:.6f}")
print(f"  SFE: {fidelity_sfe[mid_idx]:.6f}")

print(f"\n시간 {times[-1]*1e6:.2f} μs:")
print(f"  표준: {fidelity_standard[-1]:.6f}")
print(f"  SFE: {fidelity_sfe[-1]:.6f}")

plt.figure(figsize=(10, 6))
plt.plot(times * 1e6, fidelity_standard, 'r-', linewidth=2, label='표준 감쇠 (지수)')
plt.plot(times * 1e6, fidelity_sfe, 'b-', linewidth=2, label='SFE 보정')
plt.xlabel('시간 (μs)')
plt.ylabel('충실도')
plt.title('양자 상태 충실도 감쇠 비교')
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig('E:/SFE/examples/fidelity_comparison_demo.png', dpi=150)
print("\n그래프 저장: fidelity_comparison_demo.png")

print("\n" + "=" * 80)
print("테스트 3: 단일 큐비트 상태 진화")
print("=" * 80)

qc_single = QuantumCorrection(n_qubits=1, m_qubit=1e-30, T2=1e-7, epsilon_0=0.355)
qc_single.reset_epsilon()

psi_0 = np.array([1, 0], dtype=complex)
rho_0 = np.outer(psi_0, psi_0.conj())

print("초기 상태: |0⟩")
print(f"초기 밀도행렬:")
print(f"  [[{rho_0[0,0].real:.4f}, {rho_0[0,1].real:.4f}],")
print(f"   [{rho_0[1,0].real:.4f}, {rho_0[1,1].real:.4f}]]")

total_time = 1e-7
times_ev, rho_history = qc_single.simulate_evolution(rho_0, total_time, n_steps=100)

rho_final = rho_history[-1]
print(f"\n최종 상태 ({total_time*1e6:.2f} μs 후):")
print(f"최종 밀도행렬:")
print(f"  [[{rho_final[0,0].real:.4f}, {rho_final[0,1].real:.4f}],")
print(f"   [{rho_final[1,0].real:.4f}, {rho_final[1,1].real:.4f}]]")

populations_0 = [rho.real[0, 0] for rho in rho_history]
populations_1 = [rho.real[1, 1] for rho in rho_history]

plt.figure(figsize=(10, 6))
plt.plot(times_ev * 1e6, populations_0, 'b-', linewidth=2, label='|0⟩ 점유')
plt.plot(times_ev * 1e6, populations_1, 'r-', linewidth=2, label='|1⟩ 점유')
plt.xlabel('시간 (μs)')
plt.ylabel('점유 확률')
plt.title('단일 큐비트 상태 진화 (Lindblad)')
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig('E:/SFE/examples/state_evolution_demo.png', dpi=150)
print("\n그래프 저장: state_evolution_demo.png")

print("\n" + "=" * 80)
print("데모 완료")
print("=" * 80)
print("\n생성된 파일:")
print("  - epsilon_evolution_demo.png")
print("  - fidelity_comparison_demo.png")
print("  - state_evolution_demo.png")

print("\n" + "=" * 80)
print("테스트 4: SFE + 동적 디커플링 효과 (CPMG)")
print("=" * 80)

qc_dd = QuantumCorrection(n_qubits=1, m_qubit=1e-30, T2=1e-7, epsilon_0=0.355)
qc_dd.reset_epsilon()

psi_plus = np.array([1.0, 1.0], dtype=complex) / np.sqrt(2.0)
rho_plus = np.outer(psi_plus, psi_plus.conj())

total_time_dd = 2e-7
steps_dd = 200

times_sfe, rho_sfe_base, rho_sfe_dd = qc_dd.simulate_with_decoupling(
    rho_plus,
    total_time_dd,
    n_steps=steps_dd,
    sequence="CPMG",
    n_pulses=4,
    use_sfe=True,
    omega_0=1e9,
    use_phase=False,
    use_amplitude=False,
)

fid_sfe_base = qc_dd.calculate_fidelity_history(rho_sfe_base, rho_plus)
fid_sfe_dd = qc_dd.calculate_fidelity_history(rho_sfe_dd, rho_plus)

print(f"\n총 시간 {total_time_dd*1e6:.2f} μs:")
print(f"  SFE만 적용: 최종 충실도 = {fid_sfe_base[-1]:.6f}")
print(f"  SFE + CPMG: 최종 충실도 = {fid_sfe_dd[-1]:.6f}")
print(f"  개선량: {(fid_sfe_dd[-1] - fid_sfe_base[-1]) * 100:.2f}%p")

print("\n" + "=" * 80)
print("테스트 5: Zero-Noise Extrapolation (ZNE)")
print("=" * 80)

qc_zne = QuantumCorrection(n_qubits=1, m_qubit=1e-30, T2=1e-7, epsilon_0=0.355)
qc_zne.reset_epsilon()

sigma_x = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)

total_time_zne = 1e-7
steps_zne = 200

est0, s_arr, values = qc_zne.zero_noise_extrapolation(
    rho_plus,
    sigma_x,
    total_time_zne,
    n_steps=steps_zne,
    scales=(1.0, 2.0, 3.0),
    order=1,
)

print(f"\n관측 연산자: Pauli-X, 이상적 기대값 = 1.000000")
for s, v in zip(s_arr, values):
    print(f"  노이즈 스케일 s={s:.1f}: 측정 기대값 ≈ {v:.6f}")
print(f"\nZNE 외삽 추정값 (s→0): {est0:.6f}")


