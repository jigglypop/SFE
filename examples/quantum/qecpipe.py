import csv
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path


def apply_calibration_from_json(path: Path):
    if not path.is_file():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    dt = data.get("dt")
    qubits = data.get("qubits", [])
    gates = data.get("gates", [])
    t1_vals = []
    meas_vals = []
    gate_vals = []
    for q in qubits:
        for entry in q:
            name = entry.get("name")
            value = entry.get("value")
            if name == "T1":
                try:
                    t1_vals.append(float(value))
                except (TypeError, ValueError):
                    continue
            elif name in ("readout_error", "prob_meas1_prep0", "prob_meas0_prep1"):
                try:
                    meas_vals.append(float(value))
                except (TypeError, ValueError):
                    continue
    for g in gates:
        for p in g.get("parameters", []):
            if p.get("name") == "gate_error":
                try:
                    gate_vals.append(float(p.get("value")))
                except (TypeError, ValueError):
                    continue
    if dt and t1_vals:
        try:
            dt_val = float(dt)
        except (TypeError, ValueError):
            dt_val = 0.0
        if dt_val > 0.0:
            t1_min = min(t1_vals)
            t1_steps = t1_min / dt_val
            os.environ["SFE_T1_STEPS"] = str(t1_steps)
    if gate_vals:
        os.environ["SFE_GATE_ERROR"] = str(max(gate_vals))
    if meas_vals:
        os.environ["SFE_MEAS_ERROR"] = str(max(meas_vals))


def run_qec(distance, noise, rho):
    env = os.environ.copy()
    env["SFE_NOISE_RHO"] = str(rho)
    root = Path(__file__).resolve().parents[2]
    exe = root / "sfe_core" / "target" / "release" / "sfe_engine.exe"
    cmd = [str(exe), "qec", "--distance", str(distance), "--noise", str(noise)]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env,
        encoding="utf-8",
        errors="replace",
    )
    lines = result.stdout.splitlines()
    sfe_score = None
    p_phy = None
    p_log = None
    gain = None
    time_sec = None
    for line in lines:
        s = line.strip()
        if s.startswith("SFE 결맞음 점수:") or s.startswith("SFE 결맞음 점수"):
            parts = s.split(":")
            if len(parts) > 1:
                sfe_score = float(parts[1].strip())
        elif s.startswith("물리적 오류율 (p_phy):"):
            parts = s.split(":")
            if len(parts) > 1:
                p_phy = float(parts[1].strip())
        elif s.startswith("논리적 오류율 (P_L):"):
            parts = s.split(":")
            if len(parts) > 1:
                p_log = float(parts[1].strip())
        elif s.startswith("이득 (Gain):"):
            parts = s.split(":")
            if len(parts) > 1:
                v = parts[1].strip()
                if v.endswith("x"):
                    v = v[:-1]
                gain = float(v)
        elif s.startswith("총 소요 시간:"):
            parts = s.split(":")
            if len(parts) > 1:
                v = parts[1].strip()
                if v.endswith("s"):
                    v = v[:-1]
                try:
                    time_sec = float(v)
                except ValueError:
                    time_sec = None
    return {
        "distance": distance,
        "noise": noise,
        "rho": rho,
        "sfe_score": sfe_score,
        "p_phy": p_phy,
        "p_log": p_log,
        "gain": gain,
        "time_sec": time_sec,
    }


def main():
    distances = [3, 5, 7]
    noises = [0.10, 0.15, 0.20]
    rhos = [0.0, 0.5, 0.9]
    root = Path(__file__).resolve().parents[2]
    results_dir = root / "examples" / "results"
    calib_path = results_dir / "ibm_fez_calibration.json"
    apply_calibration_from_json(calib_path)
    results_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = results_dir / f"qec_{now}.csv"
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "distance",
                "noise",
                "rho",
                "sfe_score",
                "p_phy",
                "p_log",
                "gain",
                "time_sec",
            ]
        )
        for d in distances:
            for n in noises:
                for r in rhos:
                    print(f"distance={d}, noise={n}, rho={r}")
                    res = run_qec(d, n, r)
                    writer.writerow(
                        [
                            res["distance"],
                            f"{res['noise']:.3f}",
                            f"{res['rho']:.3f}",
                            f"{res['sfe_score']:.6f}" if res["sfe_score"] is not None else "",
                            f"{res['p_phy']:.6f}" if res["p_phy"] is not None else "",
                            f"{res['p_log']:.6f}" if res["p_log"] is not None else "",
                            f"{res['gain']:.3f}" if res["gain"] is not None else "",
                            f"{res['time_sec']:.3f}" if res["time_sec"] is not None else "",
                        ]
                    )
    print(f"결과 CSV: {out_path}")


if __name__ == "__main__":
    main()


