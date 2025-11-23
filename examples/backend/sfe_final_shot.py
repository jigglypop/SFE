import numpy as np
from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from ibm_env import load_ibm_api_key

SFE_SEQ_OPT_8 = [
    0.0300,
    0.1170,
    0.2500,
    0.4030,
    0.5870,
    0.7500,
    0.8830,
    0.9700,
]

DURATIONS_DT = [4444, 8888, 13333]


def build_cpmg_circuit(duration_dt: int) -> QuantumCircuit:
    qc = QuantumCircuit(1, 1)
    qc.h(0)
    timings = (np.arange(1, 9) - 0.5) / 8.0
    last_t = 0
    for t_ratio in timings:
        curr_t = int(t_ratio * duration_dt)
        delay = curr_t - last_t
        if delay > 0:
            qc.delay(delay, 0)
        qc.x(0)
        last_t = curr_t
    if duration_dt - last_t > 0:
        qc.delay(duration_dt - last_t, 0)
    qc.h(0)
    qc.measure(0, 0)
    qc.name = f"CPMG_8_T{duration_dt}"
    return qc


def build_sfe_circuit(duration_dt: int) -> QuantumCircuit:
    qc = QuantumCircuit(1, 1)
    qc.h(0)
    last_t = 0
    for t_ratio in SFE_SEQ_OPT_8:
        curr_t = int(t_ratio * duration_dt)
        delay = curr_t - last_t
        if delay > 0:
            qc.delay(delay, 0)
        qc.x(0)
        last_t = curr_t
    if duration_dt - last_t > 0:
        qc.delay(duration_dt - last_t, 0)
    qc.h(0)
    qc.measure(0, 0)
    qc.name = f"SFE_OPT_8_T{duration_dt}"
    return qc


def main():
    print("=== SFE Final Shot: 8-pulse Optimized SFE vs CPMG (Multi-duration) ===")

    try:
        api_key = load_ibm_api_key()
        service = QiskitRuntimeService(channel="ibm_quantum_platform", token=api_key)
        backend = service.backend("ibm_fez")
        print(f"[+] Targeted Backend: {backend.name}")

        circuits = []
        for duration_dt in DURATIONS_DT:
            circuits.append(build_cpmg_circuit(duration_dt))
            circuits.append(build_sfe_circuit(duration_dt))

        print(f"[*] Submitting batch: {len(circuits)} circuits")
        pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
        isa_circuits = pm.run(circuits)

        sampler = Sampler(mode=backend)
        job = sampler.run([(c,) for c in isa_circuits], shots=1024)

        print(f"[!] JOB LAUNCHED: {job.job_id()}")
        print(f"[*] Monitor: https://quantum.ibm.com/jobs/{job.job_id()}")

    except Exception as e:
        print(f"[!] Error: {e}")


if __name__ == "__main__":
    main()
