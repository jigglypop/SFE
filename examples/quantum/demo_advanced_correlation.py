import sys
sys.path.insert(0, 'E:/SFE')

import warnings
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# 한글 폰트 경고 무시
warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    message=r"Glyph .* missing from font\(s\) DejaVu Sans\."
)

from sfe import QuantumCorrection
from sfe.utils import density_matrix_from_statevector, fidelity
import numpy as np

print("=" * 80)
print("SFE 고급 회로 시뮬레이션 (상관 노이즈 & 게이트 모델)")
print("=" * 80)

# 1. 시뮬레이션 환경 설정
# 2개의 큐비트가 거리 0.5만큼 떨어져 있고, 상관 길이(xi)가 1.0인 상황 가정
# -> 강한 공간적 상관관계 (exp(-0.5/1.0) ≈ 0.6)
n_qubits = 2
coords = [[0.0, 0.0, 0.0], [0.5, 0.0, 0.0]]
xi = 1.0

print(f"\n[환경 설정]")
print(f"  큐비트 수: {n_qubits}")
print(f"  큐비트 좌표: {coords}")
print(f"  상관 길이(xi): {xi}")

qc = QuantumCorrection(
    n_qubits=n_qubits,
    T2=1e-7,
    epsilon_0=0.355,
    coordinates=coords,
    correlation_length=xi
)

print(f"  상관 행렬 C_01: {qc.correlated_model.correlation_matrix[0, 1]:.4f}")
print(f"  SFE 억압률 epsilon_mass: {qc.epsilon_mass:.4f}")

# 2. 회로 정의: Bell State 생성 (|00> -> |+0> -> (|00>+|11>)/sqrt(2))
# H(0), CNOT(0, 1)
gate_list = [
    ('H', 0),
    ('CNOT', 0, 1)
]
gate_time = 20e-9 # 20ns per gate

print(f"\n[회로 실행]")
print(f"  Gate List: {gate_list}")
print(f"  Gate Time: {gate_time*1e9:.1f} ns")

# 이상적인 Bell State
psi_bell = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
rho_target = density_matrix_from_statevector(psi_bell)

# 초기 상태 |00>
psi_00 = np.array([1, 0, 0, 0], dtype=complex)
rho_init = density_matrix_from_statevector(psi_00)

# 3. 시뮬레이션 실행 (SFE OFF vs ON)
print("\n1) SFE OFF (Standard Noise + Correlation)")
rho_std = qc.simulate_circuit(rho_init, gate_list, dt_gate=gate_time, use_sfe=False)
fid_std = fidelity(rho_std, rho_target)
print(f"  최종 충실도: {fid_std:.6f}")

print("\n2) SFE ON (Suppressed Noise + Correlation)")
rho_sfe = qc.simulate_circuit(rho_init, gate_list, dt_gate=gate_time, use_sfe=True)
fid_sfe = fidelity(rho_sfe, rho_target)
print(f"  최종 충실도: {fid_sfe:.6f}")

print(f"\n[결과 요약]")
print(f"  충실도 개선: {(fid_sfe - fid_std)*100:.2f}%p")
print(f"  오차율 감소: {(1-fid_sfe)/(1-fid_std):.4f} 배 (Error Ratio)")

# 4. 시각화 (상관 노이즈 영향 분석)
# 큐비트 간 거리를 변화시키며 상관 노이즈가 충실도에 미치는 영향 + SFE 보정 효과 비교
distances = np.linspace(0.1, 3.0, 15)
fids_std_dist = []
fids_sfe_dist = []

print(f"\n[거리별 상관 노이즈 분석 시작...]")
for d in distances:
    # 좌표 업데이트 및 모델 재설정
    curr_coords = [[0.0, 0.0, 0.0], [d, 0.0, 0.0]]
    qc_dist = QuantumCorrection(
        n_qubits=2, T2=1e-7, epsilon_0=0.355,
        coordinates=curr_coords, correlation_length=xi
    )
    
    # 회로 실행
    r_std = qc_dist.simulate_circuit(rho_init, gate_list, dt_gate=gate_time, use_sfe=False)
    r_sfe = qc_dist.simulate_circuit(rho_init, gate_list, dt_gate=gate_time, use_sfe=True)
    
    fids_std_dist.append(fidelity(r_std, rho_target))
    fids_sfe_dist.append(fidelity(r_sfe, rho_target))

plt.figure(figsize=(10, 6))
plt.plot(distances, fids_std_dist, 'r-o', label='Standard Noise')
plt.plot(distances, fids_sfe_dist, 'b-s', label='SFE Suppressed')
plt.axhline(y=1.0, color='k', linestyle=':', alpha=0.3)
plt.xlabel('Qubit Distance (arb. units)')
plt.ylabel('Bell State Fidelity')
plt.title(f'Correlated Noise Effect vs Distance (xi={xi})')
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig('E:/SFE/examples/correlated_noise_demo.png', dpi=150)
print("  그래프 저장: correlated_noise_demo.png")

print("\n" + "=" * 80)
print("고급 시뮬레이션 완료")
print("=" * 80)

