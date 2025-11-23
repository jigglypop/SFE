"""
SFE Rust Controller - Python Launcher
Rust 고속 진단/전략 생성 + Python 안정적 IBM 제출
"""
import subprocess
import sys
import os
import json
import re
from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from ibm_env import load_ibm_api_key

# 기본값 (Rust 연동 실패 시 fallback)
SFE_SEQ_OPT = [0.0125, 0.1170, 0.2500, 0.4130, 0.5870, 0.7300, 0.8830, 0.9900]

# 테스트용 짧은 Durations (크레딧 절약 및 빠른 검증)
DURATIONS_DT = [0, 4444, 8888, 13333, 17777] 

def align_dt(dt, alignment=16):
    """IBM 하드웨어 제약(16dt)에 맞게 정렬"""
    return int(round(dt / alignment)) * alignment

def build_sfe_circuit(seq, duration_dt, name):
    qc = QuantumCircuit(1, 1)
    qc.h(0)
    
    last_t = 0
    # duration 자체도 alignment 맞춤
    duration_dt = align_dt(duration_dt)
    
    for t_ratio in seq:
        curr_t = align_dt(t_ratio * duration_dt)
        delay = curr_t - last_t
        
        if delay > 0:
            qc.delay(delay, 0)
        
        qc.x(0)
        last_t = curr_t
        
    final_delay = duration_dt - last_t
    if final_delay > 0:
        qc.delay(final_delay, 0)
        
    qc.h(0)
    qc.measure(0, 0)
    qc.name = f"{name}_T{duration_dt}"
    return qc

def parse_rust_output(stdout):
    """Rust 출력에서 RAW_SEQ 파싱"""
    try:
        match = re.search(r"RAW_SEQ_START\s+(\[.*?\])\s+RAW_SEQ_END", stdout, re.DOTALL)
        if match:
            seq_str = match.group(1)
            return json.loads(seq_str)
    except Exception as e:
        print(f"[WARN] Rust 출력 파싱 실패: {e}")
    return None

def main():
    print("=" * 80)
    print("   SFE Rust-Python 상용 컨트롤러 (Hybrid Architecture)")
    print("=" * 80)
    
    # Phase 1: Rust 고속 진단 및 전략 수립
    print("\n[Phase 1] Rust 엔진 실행: 하드웨어 진단 + 전략 선택...")
    print("-" * 80)
    
    rust_exe = os.path.join("sfe_core", "target", "release", "sfe_engine.exe")
    
    # Encoding 명시 및 에러 처리
    try:
        result = subprocess.run(
            [rust_exe, "run-controller", "--t1", "60.0", "--t2", "40.0"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=os.path.join(os.path.dirname(__file__), "..", "..")
        )
        print(result.stdout)
        
        if result.returncode != 0:
            print(f"[ERROR] Rust 엔진 실행 실패: {result.stderr}")
            sys.exit(1)
            
        # Rust에서 생성한 시퀀스 파싱
        rust_seq = parse_rust_output(result.stdout)
        
        final_seq = SFE_SEQ_OPT
        if rust_seq:
            print(f"\n[INFO] Rust 엔진이 생성한 최적 시퀀스 감지: {len(rust_seq)} pulses")
            final_seq = rust_seq
        else:
            print(f"\n[WARN] Rust 시퀀스 감지 실패, 기본값 사용")
            
    except Exception as e:
        print(f"[ERROR] Rust 실행 중 예외 발생: {e}")
        sys.exit(1)
    
    # Phase 2: Python으로 IBM Quantum 제출
    print("\n[Phase 2] Python → IBM Quantum 작업 제출...")
    print("-" * 80)
    
    try:
        load_ibm_api_key()
        # 인자 없이 호출하여 저장된 계정 또는 환경변수 사용
        service = QiskitRuntimeService()
        backend = service.backend("ibm_fez")
        
        print(f"[+] Backend: {backend.name}")
        
        # SFE 시퀀스로 회로 생성
        circuits = []
        for d in DURATIONS_DT:
            circuits.append(build_sfe_circuit(final_seq, d, "SFE_RUST"))
        
        print(f"[*] 회로 트랜스파일 중... ({len(circuits)} circuits)")
        pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
        isa_circuits = pm.run(circuits)
        
        print(f"[*] IBM Quantum Runtime에 작업 제출 중...")
        sampler = Sampler(mode=backend)
        job = sampler.run([(c,) for c in isa_circuits], shots=1024)
        
        print("\n" + "=" * 80)
        print(f"[SUCCESS] 작업 제출 완료!")
        print(f"Job ID: {job.job_id()}")
        print(f"Monitor: https://quantum.ibm.com/jobs/{job.job_id()}")
        print("=" * 80)
        
        return job.job_id()
        
    except Exception as e:
        print(f"\n[ERROR] IBM 제출 실패: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    job_id = main()
    print(f"\n다음 명령으로 결과 확인:")
    print(f"  python examples/backend/fetch_ibm_results.py")
    # 자동으로 fetch_ibm_results.py 업데이트하지 않음 (사용자 확인 유도)
