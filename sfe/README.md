# SFE 라이브러리

Suppression Field Theory의 핵심 계산 및 양자컴퓨터 보정 알고리즘을 제공하는 Python 라이브러리입니다.

## 설치

```bash
cd E:/SFE
uv venv
uv pip install -e .
```

## 주요 모듈

### sfe.constants
물리 상수 정의
- G, c, hbar, mp, me, alpha_em
- M_P, alpha_dimless, alpha_si

### sfe.core.SFETheory
SFE 이론의 핵심 계산
- fixed_point_iteration(): lambda, Omega_Phi 유도
- compare_observations(): 관측 비교
- calculate_deceleration_parameter(): q0 계산
- calculate_growth_rate(): f0 계산

### sfe.quantum.QuantumCorrection
양자컴퓨터 보정 알고리즘
- update_epsilon(): 억압률 업데이트
- predict_fidelity(): 충실도 예측
- apply_lindblad_step(): Lindblad 진화
- simulate_evolution(): 시간 진화 시뮬레이션

### sfe.quantum.SoftwareNoiseCanceller
소프트웨어 노이즈 캔슬러
- estimate_psd(), estimate_cpsd(): 단측 PSD·CPSD 추정
- design_wiener(): 다중 채널 Wiener 필터와 잔차 PSD 하한 계산
- apply_wiener_frequency(): 주파수영역 적용
- notch_iir(), apply_iir(): 고정선(50/60 Hz) 노치 필터

### sfe.utils
유틸리티 함수
- density_matrix_from_statevector()
- fidelity(), purity(), entropy()
- format_results(), print_results_table()

## 사용 예제

### 기본 사용법

```python
from sfe import SFETheory

theory = SFETheory()
results = theory.fixed_point_iteration()
print(f"Omega_Phi: {results['Omega_phi']:.4f}")
print(f"Epsilon: {results['epsilon']:.4f}")
```

### 양자 보정

```python
from sfe import QuantumCorrection

qc = QuantumCorrection(n_qubits=2, m_qubit=1e-30)
qc.update_epsilon(gate_time=1e-9)
fidelity = qc.predict_fidelity(time=1e-7)
print(f"예측 충실도: {fidelity:.6f}")
```

### 노이즈 캔슬러

```python
import numpy as np
from sfe.quantum import SoftwareNoiseCanceller

fs = 1_000.0
t = np.arange(0, 10.0, 1/fs)
y = np.sin(2*np.pi*7*t) + 0.1*np.random.randn(t.size)
x = np.sin(2*np.pi*7*t + 0.3) + 0.1*np.random.randn(t.size)

snc = SoftwareNoiseCanceller()
summary = snc.design_wiener(refs=np.vstack([x]), primary=y, fs=fs)
y_hat = snc.apply_wiener_frequency(refs=np.vstack([x]), H=summary["H"], fs=fs)
y_clean = y - y_hat
```

### 상세 예제

examples 폴더 참조:
- basic_usage.py: 기본 사용법
- quantum_circuit_demo.py: 양자 회로 시뮬레이션

## 실행

```bash
python examples/basic_usage.py
python examples/quantum_circuit_demo.py
```

## 이론 배경

SFE 이론은 비국소 억압장을 통해 암흑에너지와 양자 결맞음 손실을 통합적으로 설명합니다.
자세한 내용은 Part1~Part6 문서를 참조하세요.

