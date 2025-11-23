import json
from pathlib import Path

from qiskit_ibm_runtime import QiskitRuntimeService
from ibm_env import load_ibm_api_key


BACKEND_NAME = "ibm_fez"


def main():
    api_key = load_ibm_api_key()
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=api_key)
    backend = service.backend(BACKEND_NAME)
    props = backend.properties()
    conf = backend.configuration()
    props_dict = props.to_dict()
    for gate in props_dict.get("gates", []):
        params = gate.get("parameters", [])
        for p in params:
            if "date" in p:
                if not isinstance(p["date"], (str, type(None))):
                    p["date"] = str(p["date"])
    data = {
        "backend_name": backend.name,
        "dt": getattr(conf, "dt", None),
        "qubits": props_dict.get("qubits", []),
        "gates": props_dict.get("gates", []),
    }
    root = Path(__file__).resolve().parents[2]
    out_dir = root / "examples" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{BACKEND_NAME}_calibration.json"
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(str(path), flush=True)


if __name__ == "__main__":
    main()


