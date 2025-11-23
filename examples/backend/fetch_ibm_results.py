from qiskit_ibm_runtime import QiskitRuntimeService
from ibm_env import load_ibm_api_key

JOB_ID = "d4hfvsh2bisc73a4enh0"
SHOTS = 1024

print(f"=== Fetching Data for Job {JOB_ID} (CPMG_8 vs SFE_OPT_8, multi-duration) ===", flush=True)

api_key = load_ibm_api_key()
service = QiskitRuntimeService(channel="ibm_quantum_platform", token=api_key)

try:
    job = service.job(JOB_ID)
    status = job.status()
    print(f"Job Status: {status}", flush=True)

    if status == "DONE" or str(status) == "JobStatus.DONE":
        print("Downloading results...", flush=True)
        result = job.result()

        labels = [
            "CPMG_8_T4444",
            "SFE_OPT_8_T4444",
            "CPMG_8_T8888",
            "SFE_OPT_8_T8888",
            "CPMG_8_T13333",
            "SFE_OPT_8_T13333",
        ]
        print("\n--- Survival Probabilities P(|0>) ---", flush=True)

        for i, pub_result in enumerate(result):
            label = labels[i] if i < len(labels) else f"Circuit_{i}"
            meas_data = pub_result.data.c
            counts = meas_data.get_counts()
            p0 = counts.get("0", 0) / SHOTS
            p1 = counts.get("1", 0) / SHOTS
            print(f"{label:14s} | P(0) = {p0:.4f}, P(1) = {p1:.4f}", flush=True)

    elif status in ["QUEUED", "RUNNING", "JobStatus.QUEUED", "JobStatus.RUNNING"]:
        print("Job is still running. Please wait a moment and try again.", flush=True)
        pos = job.queue_position() if hasattr(job, "queue_position") else "Unknown"
        print(f"Queue Position: {pos}", flush=True)
    else:
        print(f"Job ended with status: {status}", flush=True)
        if hasattr(job, "error_message"):
            print(f"Error: {job.error_message()}", flush=True)

except Exception as e:
    print(f"ERROR: {e}", flush=True)