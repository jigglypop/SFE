import numpy as np


def pulses_from_ratios(steps, ratios):
    return sorted(set(int(round(r * (steps - 1))) for r in ratios))


def pulses_udd(steps, n_pulses):
    idx = []
    for j in range(1, n_pulses + 1):
        t = np.sin(j * np.pi / (2.0 * n_pulses + 2.0)) ** 2
        t_idx = int(round(t * (steps - 1)))
        idx.append(t_idx)
    return sorted(set(idx))


def pulses_cpmg(steps, n_pulses):
    idx = []
    for k in range(n_pulses):
        t = (k + 0.5) / float(n_pulses)
        t_idx = int(round(t * (steps - 1)))
        idx.append(t_idx)
    return sorted(set(idx))


def make_y(steps, pulses):
    y = np.ones(steps, dtype=float)
    sign = 1.0
    pset = set(pulses)
    for t in range(steps):
        if t in pset:
            sign = -sign
        y[t] = sign
    return y


def chi_1overf(y, alpha=0.8, w_max=10.0, n_omega=2000):
    steps = len(y)
    dt = 1.0
    t = np.arange(steps, dtype=float) * dt
    omega = np.linspace(0.001, w_max, n_omega)
    yft = np.empty_like(omega)
    for i, w in enumerate(omega):
        v = np.abs(np.sum(y * np.exp(1j * w * t)) * dt) ** 2
        yft[i] = v
    s = 1.0 / (omega ** alpha)
    integrand = s * yft
    return np.trapz(integrand, omega) / (2.0 * np.pi)


def moments(y, order=3):
    steps = len(y)
    steps_f = float(steps - 1)
    if steps_f <= 0.0:
        return [0.0] * order
    dt_norm = 1.0 / steps_f
    m0 = 0.0
    m1 = 0.0
    m2 = 0.0
    for t_idx, y_val in enumerate(y):
        t_norm = float(t_idx) / steps_f
        m0 += y_val * dt_norm
        if order >= 2:
            m1 += t_norm * y_val * dt_norm
        if order >= 3:
            m2 += t_norm * t_norm * y_val * dt_norm
    if order == 1:
        return [m0]
    if order == 2:
        return [m0, m1]
    return [m0, m1, m2]


def main():
    steps = 2000
    n_pulses = 8
    ratios_sfe = [0.2000, 0.4120, 0.4370, 0.5245, 0.6735, 0.7735, 0.8780, 0.9785]
    p_free = []
    p_cpmg = pulses_cpmg(steps, n_pulses)
    p_udd = pulses_udd(steps, n_pulses)
    p_sfe = pulses_from_ratios(steps, ratios_sfe)
    seqs = [("free", p_free), ("cpmg", p_cpmg), ("udd", p_udd), ("sfe", p_sfe)]
    for name, p in seqs:
        y = make_y(steps, p)
        m = moments(y, order=3)
        chi = chi_1overf(y, alpha=0.8)
        print(name, m, chi)


if __name__ == "__main__":
    main()