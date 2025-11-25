import numpy as np


class QuantumCorrection:
    def __init__(self, T2: float, epsilon_0: float):
        self.T2 = float(T2)
        self.epsilon_0 = float(epsilon_0)

    def apply_lindblad_step(self, rho: np.ndarray, dt: float, scale: float = 1.0) -> np.ndarray:
        if self.T2 <= 0.0 or dt <= 0.0:
            return rho
        gamma = scale / (2.0 * self.T2)
        sigma_z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
        drho = gamma * (sigma_z @ rho @ sigma_z.conj().T - rho)
        return rho + dt * drho


class SFEFieldModel:
    def __init__(self, epsilon_0: float, T2: float):
        self.epsilon_0 = float(epsilon_0)
        self.T2 = float(T2) if T2 != 0.0 else 1.0
        self.omega = 2.0 * np.pi / self.T2

    def get_field_value(self, t: float) -> float:
        return self.epsilon_0 * float(np.cos(self.omega * t))


class SFEActiveCanceller:
    def __init__(self, qc: QuantumCorrection, efficiency: float):
        self.qc = qc
        self.efficiency = float(efficiency)
        self.sfe_model = SFEFieldModel(qc.epsilon_0, qc.T2)

    def simulate_with_active_cancellation(
        self,
        rho_init: np.ndarray,
        total_time: float,
        n_steps: int,
    ):
        dt = float(total_time) / float(n_steps) if n_steps > 0 else 0.0
        times = np.linspace(0.0, total_time - dt, n_steps) if n_steps > 0 else np.array([])
        rho = np.array(rho_init, dtype=complex)
        target = np.array(rho_init, dtype=complex)
        fids = []
        for t in times:
            rho = self.qc.apply_lindblad_step(rho, dt, scale=1.0)
            field = self.sfe_model.get_field_value(float(t))
            residual = (1.0 - self.efficiency) * field
            theta = residual * dt
            phase = np.exp(-0.5j * theta)
            U = np.array([[phase, 0.0], [0.0, np.conj(phase)]], dtype=complex)
            rho = U @ rho @ U.conj().T
            fids.append(_fidelity(rho, target))
        return times, np.array(fids)


def _fidelity(rho: np.ndarray, target: np.ndarray) -> float:
    return float(np.real(np.trace(target @ rho)))


class SFEErrorModel:
    def __init__(self, e0: float, e_min: float, r: float):
        self.e0 = float(e0)
        self.e_min = float(e_min)
        self.r = float(r)

    def value(self, steps):
        s = np.asarray(steps, dtype=float)
        return self.e_min + (self.e0 - self.e_min) * np.exp(-self.r * s)


def sfe_error_model(e0: float, e_min: float, r: float, steps):
    model = SFEErrorModel(e0, e_min, r)
    return model.value(steps)


def fit_sfe_error_params(pulse_counts, errors) -> SFEErrorModel:
    pc = np.asarray(pulse_counts, dtype=float)
    err = np.asarray(errors, dtype=float)
    min_pulse = float(pc.min())
    steps = pc / min_pulse
    e_min = float(err.min())
    idx0 = int(np.argmin(pc))
    e0 = float(err[idx0])
    denom = e0 - e_min
    if denom <= 0.0:
        return SFEErrorModel(e0, e_min, 0.0)
    num = err - e_min
    mask = num > 0.0
    x = steps[mask]
    y = np.log(num[mask] / denom)
    if x.size == 0:
        r = 0.0
    else:
        r = -float((x * y).sum() / (x * x).sum())
        if not np.isfinite(r):
            r = 0.0
    return SFEErrorModel(e0, e_min, r)

