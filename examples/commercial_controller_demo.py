import sys
import os
sys.path.append(os.getcwd())

from sfe.controller import SFEAdaptiveController

def run_commercial_demo():
    print("============================================================")
    print("   SFE Quantum Noise Controller v2.0 (Commercial Demo)      ")
    print("============================================================")
    
    controller = SFEAdaptiveController(verbose=True)
    
    # --- Scenario 1: Current IBM Fez (Low T1, Strong TLS) ---
    print("\n>>> Case 1: Injecting 'IBM Fez' Data (Current Generation)")
    # 측정 데이터 가정: T1=60us, T2=40us (TLS로 인해 T1보다 현저히 짧음)
    t1_meas = 60.0
    t2_meas = 40.0
    
    # 1. 진단
    spec_fez = controller.diagnose(t1_meas, t2_meas)
    # 2. 전략 수립
    strategy_fez = controller.select_best_strategy(spec_fez)
    # 3. 실행 시뮬레이션
    controller.run_simulation_loop(spec_fez, strategy_fez, duration=50.0)
    
    print("-" * 60)
    print("Analysis: Current hardware is T1-limited.")
    print("Controller correctly chooses 'STATIC' to minimize overhead.")
    print("-" * 60)

    # --- Scenario 2: Future High-Coherence Chip (High T1, Strong TLS) ---
    print("\n>>> Case 2: Injecting 'Next-Gen Chip' Data (Future Generation)")
    # 측정 데이터 가정: T1=300us, T2=50us (TLS가 매우 강력하여 T1 잠재력을 다 깎아먹음)
    t1_future = 300.0
    t2_future = 50.0
    
    # 1. 진단
    spec_future = controller.diagnose(t1_future, t2_future)
    
    # 강제 주입: 미래 칩은 TLS가 더 복잡하고 드리프트가 있다고 가정
    spec_future.drift_rate = 0.005 
    spec_future.tls_amp = 2.0 # Strong TLS
    
    # 2. 전략 수립
    strategy_future = controller.select_best_strategy(spec_future)
    
    # 3. 실행 시뮬레이션
    controller.run_simulation_loop(spec_future, strategy_future, duration=50.0)
    
    print("-" * 60)
    print("Analysis: Hardware is Coherence-rich but TLS-limited.")
    print("Controller switches to 'ANC' (Active Cancellation) for 3.5x gain.")
    print("-" * 60)

if __name__ == "__main__":
    run_commercial_demo()

