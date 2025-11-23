from qiskit_ibm_runtime import QiskitRuntimeService
from ibm_env import load_ibm_api_key

JOB_ID = "d4hkofelo8as739qqg60"

api_key = load_ibm_api_key()
service = QiskitRuntimeService(channel="ibm_quantum_platform", token=api_key)

job = service.job(JOB_ID)
print(f"현재 상태: {job.status()}")

try:
    job.cancel()
    print(f"[SUCCESS] Job {JOB_ID} 취소 완료!")
except Exception as e:
    print(f"[ERROR] 취소 실패: {e}")

