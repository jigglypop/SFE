다이렉트 계산만 정리.

- 기본식(300 K, 1 atm, 이상기체, 충돌시간 $\tau_0\!=\!10^{-12}\,\text{s}$):
  - $\log_{10} T_{\text{yr}} \;=\; -19.5 \;+\; 10.70\,N$  ($N$=분자 수)
  - 연간 확률: $p_{\text{yr}}\approx 1/T_{\text{yr}}$

- 목표 대기시간 역산
  - $T_{\text{yr}}=10^{4}$년 → $N^\ast=(4+19.5)/10.70\approx 2.19$
    - $N=2$: $T\approx 10^{1.91}=8.13\times 10^{1}$년,  $p_{\text{yr}}\approx 1.23\times 10^{-2}$
    - $N=3$: $T\approx 10^{12.61}=4.07\times 10^{12}$년,  $p_{\text{yr}}\approx 2.46\times 10^{-13}$
  - $T_{\text{yr}}=10^{16}$년(1 경년) → $N^\ast=(16+19.5)/10.70\approx 3.30$
    - $N=3$: $T\approx 4.07\times 10^{12}$년
    - $N=4$: $T\approx 10^{23.31}=2.04\times 10^{23}$년,  $p_{\text{yr}}\approx 4.90\times 10^{-24}$

- 표준 체적(300 K, 1 atm)에서 분자수와 결과
  - 1 cm³: $N\approx 2.45\times 10^{19}$ → $\log_{10}T\approx 2.62\times 10^{20}$ → $T\approx 10^{2.62\times 10^{20}}$년,  $p_{\text{yr}}\approx 10^{-2.62\times 10^{20}}$
  - 1 L: $N\approx 2.45\times 10^{22}$ → $T\approx 10^{2.62\times 10^{23}}$년
  - 1 m³: $N\approx 2.45\times 10^{25}$ → $T\approx 10^{2.62\times 10^{26}}$년

- SFE 보정(예: $\epsilon\approx 0.37$로 질량 억압 시 분자당 $\Delta\log_{10}T\approx -0.30$)
  - 보정식: $\log_{10}T_{\text{yr}}\approx -19.5 + (10.70-0.30)N = -19.5 + 10.40N$
  - $N=2$: $T\approx 10^{1.30}=2.00\times 10^{1}$년
  - $N=3$: $T\approx 10^{11.70}=5.01\times 10^{11}$년
  - $N=4$: $T\approx 10^{22.10}=1.26\times 10^{22}$년

원하시면 특정 온도·압력·부피 조건으로 바로 수치 넣어 계산해 드리겠습니다.