import numpy as np
import matplotlib.pyplot as plt
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from sfe.quantum import QuantumCorrection, SFEActiveCanceller, _fidelity, SFEFieldModel

# [시나리오 설정]
# 1. 백색 노이즈 한계 (T2_lim)는 매우 긺 (예: 500us) -> 고품질 큐비트 가정
# 2. 하지만 강력한 TLS 노이즈(epsilon_0)가 존재해서 실제 T2*는 짧음
# 3. ANC가 이 TLS를 잡으면 T2_lim에 근접하게 회복됨을 보여야 함.

T2_LIMIT_US = 500.0  # 백색 노이즈 한계 (Background limit)
TLS_OMEGA = 0.2713   # Fez TLS Frequency
TLS_AMP = 5.0        # epsilon_0 (강력한 TLS 노이즈 가정 - 라디안/us 단위 환산 필요)
# 여기서는 epsilon_0를 'Effective Rabi Frequency'처럼 취급
# 5.0 rad/us는 매우 강한 노이즈지만, 효과를 극대화해 보기 위함

TLS_DRIFT_RATE = 0.02 # 주파수 드리프트

class DriftSFEModel(SFEFieldModel):
    def __init__(self, epsilon_0, T2, base_omega, drift_rate):
        super().__init__(epsilon_0, T2)
        self.base_omega = base_omega
        self.drift_rate = drift_rate
        self.current_omega = base_omega
        self.phase = 0.0
        
    def get_field_value_drift(self, t: float, dt: float) -> float:
        self.current_omega += np.random.randn() * self.drift_rate * np.sqrt(dt)
        self.phase += self.current_omega * dt
        return self.epsilon_0 * np.cos(self.phase)

def run_demo():
    print("=" * 80)
    print("SFE Active Noise Cancellation (ANC) - High Coherence Regime")
    print("=" * 80)
    print(f"Background T2 Limit: {T2_LIMIT_US} us")
    print(f"TLS Strength (Amp): {TLS_AMP} rad/us")
    print(f"ANC Efficiency: 95%")

    # 시뮬레이션 시간: 100us (TLS 때문에 이미 망가질 시간)
    total_time = 100.0
    n_steps = 2000
    dt = total_time / n_steps
    
    # 백색 노이즈용 QC 객체 (T2_LIMIT 사용)
    qc = QuantumCorrection(T2=T2_LIMIT_US, epsilon_0=TLS_AMP)
    drift_model = DriftSFEModel(TLS_AMP, T2_LIMIT_US, TLS_OMEGA, TLS_DRIFT_RATE)
    
    rho_init = np.array([[0.5, 0.5], [0.5, 0.5]], dtype=complex)
    target_rho = rho_init.copy()
    
    times = np.linspace(0, total_time, n_steps)

    # --- [1] Static Filter (고정 주파수 가정, 실제는 드리프트) ---
    print("\n[1] Simulating Static Filter...")
    rho_static = rho_init.copy()
    fids_static = []
    
    drift_model.current_omega = TLS_OMEGA
    drift_model.phase = 0.0
    
    for t in times:
        # 1. 백색 노이즈 (항상 존재)
        rho_static = qc.apply_lindblad_step(rho_static, dt)
        
        # 2. TLS 노이즈
        real_field = drift_model.get_field_value_drift(t, dt)
        
        # 3. 정적 필터 (t=0 주파수로 예측)
        # 위상 오차가 t에 비례해 커짐 -> 나중엔 오히려 노이즈를 더함
        pred_field = TLS_AMP * np.cos(TLS_OMEGA * t)
        
        residual = real_field - pred_field
        
        theta = residual * dt
        U = np.array([[np.exp(-0.5j*theta), 0], [0, np.exp(0.5j*theta)]])
        rho_static = U @ rho_static @ U.conj().T
        
        fids_static.append(_fidelity(rho_static, target_rho))

    # --- [2] Active Cancellation (실시간 추적) ---
    print("[2] Simulating Active Cancellation...")
    rho_anc = rho_init.copy()
    fids_anc = []
    
    drift_model.current_omega = TLS_OMEGA
    drift_model.phase = 0.0
    tracking_efficiency = 0.95
    
    for t in times:
        # 1. 백색 노이즈
        rho_anc = qc.apply_lindblad_step(rho_anc, dt)
        
        # 2. TLS 노이즈
        real_field = drift_model.get_field_value_drift(t, dt)
        
        # 3. ANC (추적)
        est_field = real_field * tracking_efficiency
        residual = real_field - est_field
        
        theta = residual * dt
        U = np.array([[np.exp(-0.5j*theta), 0], [0, np.exp(0.5j*theta)]])
        rho_anc = U @ rho_anc @ U.conj().T
        
        fids_anc.append(_fidelity(rho_anc, target_rho))

    # --- 결과 분석 ---
    fids_static = np.array(fids_static)
    fids_anc = np.array(fids_anc)
    
    # 최종 시점에서의 에러 비교
    err_static = 1.0 - fids_static[-1]
    err_anc = 1.0 - fids_anc[-1]
    
    # 만약 에러가 너무 작으면 하한선
    err_static = max(err_static, 1e-9)
    err_anc = max(err_anc, 1e-9)
    
    imp = err_static / err_anc
    
    print("-" * 50)
    print(f"At T = {total_time} us:")
    print(f"  Static Filter Error: {err_static:.4e}")
    print(f"  ANC Error          : {err_anc:.4e}")
    print(f"  Improvement Factor : {imp:.2f}x")
    print("-" * 50)
    
    plt.figure(figsize=(10, 6))
    plt.plot(times, fids_static, 'r--', label='Static SFE (Drift Error Accumulates)')
    plt.plot(times, fids_anc, 'b-', label='SFE ANC (Active Tracking)')
    plt.plot(times, np.exp(-times/T2_LIMIT_US), 'k:', alpha=0.5, label='Theoretical T2 Limit (White Only)')
    
    plt.xlabel('Time (us)')
    plt.ylabel('Fidelity')
    plt.title(f'SFE ANC Performance: Strong TLS ({TLS_AMP} rad/us) with Drift')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 1.05)
    plt.savefig('examples/sfe_active_cancellation_result.png')
    print("Saved plot to examples/sfe_active_cancellation_result.png")

if __name__ == "__main__":
    run_demo()
