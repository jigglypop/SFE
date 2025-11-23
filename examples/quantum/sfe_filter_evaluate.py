import numpy as np

alpha = 0.8


def y_filter(omega, ratios):
    t = [0.0] + list(ratios) + [1.0]
    val = 0.0 + 0.0j
    for k in range(len(t) - 1):
        left = t[k]
        right = t[k + 1]
        sign = 1.0 if k % 2 == 0 else -1.0
        val += sign * (np.exp(1j * omega * right) - np.exp(1j * omega * left)) / (1j * omega)
    return val


def chi_value(ratios):
    omegas = np.logspace(-3, 3, 4000)
    y_vals = np.array([y_filter(w, ratios) for w in omegas])
    s_phi = 1.0 / (omegas ** alpha)
    integrand = s_phi * np.abs(y_vals) ** 2
    chi = np.trapz(integrand, omegas) / (2.0 * np.pi)
    return chi


def sequences_for_n(n):
    j = np.arange(1, n + 1)
    cpmg = (j - 0.5) / n
    udd = np.sin(np.pi * j / (2.0 * n + 2.0)) ** 2
    return cpmg, udd


def main():
    print("SFE 필터 함수 기반 정밀 비교")
    n = 8
    cpmg, udd = sequences_for_n(n)
    sfe_ga = np.array([0.2000, 0.4120, 0.4370, 0.5245, 0.6735, 0.7735, 0.8780, 0.9785])

    labels = ["CPMG", "UDD", "SFE_GA"]
    seqs = [cpmg, udd, sfe_ga]

    for label, seq in zip(labels, seqs):
        c = chi_value(seq)
        s = np.exp(-c)
        print(f"{label}: chi={c:.6e}, S(T)=exp(-chi)={s:.6e}")

    n16 = 16
    cpmg16, udd16 = sequences_for_n(n16)
    sfe_balanced16 = np.array([
        0.0580, 0.1455, 0.2305, 0.3090, 0.3815, 0.4495, 0.5130, 0.5730,
        0.6295, 0.6830, 0.7340, 0.7830, 0.8295, 0.8745, 0.9180, 0.9595
    ])

    print("\n16 펄스 비교")
    labels16 = ["CPMG16", "UDD16", "SFE_BAL16"]
    seqs16 = [cpmg16, udd16, sfe_balanced16]

    for label, seq in zip(labels16, seqs16):
        c = chi_value(seq)
        s = np.exp(-c)
        print(f"{label}: chi={c:.6e}, S(T)=exp(-chi)={s:.6e}")


if __name__ == "__main__":
    main()
