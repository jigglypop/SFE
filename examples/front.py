import argparse
import math
from typing import Callable


def integrate_delta_r(
    n_func: Callable[[float], float],
    eta_start: float,
    eta_end: float,
    steps: int = 10000,
    c0: float = 1.0,
) -> float:
    if eta_end <= eta_start:
        return 0.0
    h = (eta_end - eta_start) / steps
    acc = 0.0
    for i in range(steps + 1):
        eta = eta_start + i * h
        n = max(1.0, float(n_func(eta)))
        f = c0 * (1.0 - 1.0 / n)
        w = 1.0
        if i == 0 or i == steps:
            w = 0.5
        acc += w * f
    return acc * h


def n_constant_window_factory(n_value: float, eta1: float, eta2: float) -> Callable[[float], float]:
    def n_of_eta(eta: float) -> float:
        if eta1 <= eta <= eta2:
            return max(1.0, n_value)
        return 1.0

    return n_of_eta


def n_exponential_relax_factory(eta_trigger: float, a: float, tau: float) -> Callable[[float], float]:
    def n_of_eta(eta: float) -> float:
        if eta < eta_trigger:
            return 1.0
        return 1.0 + max(0.0, a) * math.exp(-(eta - eta_trigger) / max(1e-12, tau))

    return n_of_eta


def constant_window_min_n(
    l_over_c0: float,
    eta_start: float,
    eta_end: float,
    eta1: float,
    eta2: float,
) -> float | None:
    w_start = max(eta_start, eta1)
    w_end = min(eta_end, eta2)
    d_eta = max(0.0, w_end - w_start)
    if d_eta <= 0.0:
        return None
    target = l_over_c0 / d_eta
    if target >= 1.0:
        return math.inf
    if target <= 0.0:
        return 1.0
    return 1.0 / (1.0 - target)


def main() -> None:
    p = argparse.ArgumentParser(prog="front", description="SFE 포섭 프론트 ΔR 판정")
    sub = p.add_subparsers(dest="model", required=True)

    pc = sub.add_parser("const", help="상수 n 구간")
    pc.add_argument("--eta-start", type=float, default=0.0)
    pc.add_argument("--eta-end", type=float, default=1.0)
    pc.add_argument("--eta1", type=float, default=0.0)
    pc.add_argument("--eta2", type=float, default=1.0)
    pc.add_argument("--n", type=float, default=2.0)

    pe = sub.add_parser("exp", help="지수적 복원 n(η)=1+A exp(-(η-η0)/τ)")
    pe.add_argument("--eta-start", type=float, default=0.0)
    pe.add_argument("--eta-end", type=float, default=1.0)
    pe.add_argument("--eta0", type=float, default=0.0)
    pe.add_argument("--A", type=float, default=1.0)
    pe.add_argument("--tau", type=float, default=0.2)

    p.add_argument("--L-over-c0", type=float, default=0.5, help="L*/c0")
    p.add_argument("--c0", type=float, default=1.0)
    p.add_argument("--steps", type=int, default=20000)

    args = p.parse_args()

    if args.model == "const":
        n_func = n_constant_window_factory(args.n, args.eta1, args.eta2)
        d_r = integrate_delta_r(n_func, args.eta_start, args.eta_end, args.steps, args.c0)
        verdict = "충족" if d_r >= args.L_over_c0 else "불충족"
        n_min = constant_window_min_n(args.L_over_c0, args.eta_start, args.eta_end, args.eta1, args.eta2)
        print(f"모델=const, η∈[{args.eta_start},{args.eta_end}], 창=[{args.eta1},{args.eta2}], n={max(1.0,args.n):.6g}")
        print(f"ΔR={d_r:.6g}, 임계={args.L_over_c0:.6g}, 판정={verdict}")
        if n_min is None:
            print("필요 최소 n: 창 지속시간 0 → 정의 불가")
        elif math.isinf(n_min):
            print("필요 최소 n: 창 지속시간이 부족 → 불가능")
        else:
            print(f"필요 최소 n: {n_min:.6g}")
        return

    if args.model == "exp":
        n_func = n_exponential_relax_factory(args.eta0, args.A, args.tau)
        d_r = integrate_delta_r(n_func, args.eta_start, args.eta_end, args.steps, args.c0)
        verdict = "충족" if d_r >= args.L_over_c0 else "불충족"
        print(
            f"모델=exp, η∈[{args.eta_start},{args.eta_end}], η0={args.eta0}, A={max(0.0,args.A):.6g}, τ={max(1e-12,args.tau):.6g}"
        )
        print(f"ΔR={d_r:.6g}, 임계={args.L_over_c0:.6g}, 판정={verdict}")
        return


if __name__ == "__main__":
    main()

