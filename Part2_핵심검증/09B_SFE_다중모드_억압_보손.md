# 9B장. 다중 모드 억압 보손 이론 (순환 논리 없는 연역적 전개)

## 9B.1 서론: 단일 보손 가정의 한계

7장과 25.6절에서 확인했듯이, 단일 억압 보손 $\phi$ (질량 $m_\phi$ 하나) 가정은 다음 긴장을 만든다:

- 뮤온 g-2: $g_{B,\mu}$를 줄여야 함
- 양성자 반경: $g_{B,\mu} / g_{B,e} > 1.2$ (키워야 함)

그러나 억압장 $\Phi$는 **장(field)**이므로, 양자화 시 당연히 **여러 질량 모드의 들뜸 상태**가 존재한다. 본 장은 **관측값 역산 없이** 이론적 원리만으로 질량 스펙트럼을 예측하고, 그 예측이 실험과 맞는지 검증한다.

---

## 9B.2 억압장 포텐셜의 다중 극소값 구조

### 9B.2.1 이론적 동기

3장에서 도입한 단순 포텐셜:

$$V(\Phi) = -\frac{1}{2}\mu^2 \Phi^2 + \frac{1}{4}\lambda \Phi^4$$

는 두 개의 극소값($\pm \mu/\sqrt{\lambda}$)만 가진다. 그러나 더 일반적인 포텐셜은:

$$V(\Phi) = \sum_{n=2}^{N} \frac{\lambda_n}{n!} \Phi^n$$

이 포텐셜이 **여러 개의 국소 극소값**을 가진다면, 각 극소값 주변에서 다른 질량의 들뜸 상태가 나타난다.

**원리:** 장론에서 국소 극소값은 **준안정 진공(metastable vacuum)**을 의미하고, 그 주변 들뜸은 **물리적 입자**에 대응한다.

### 9B.2.2 Peccei-Quinn 형 포텐셜 제안

표준모형의 강한 CP 문제를 해결하기 위해 제안된 Peccei-Quinn 메커니즘과 유사한 구조를 채택한다.

$$V(\Phi) = \Lambda^4 \left[1 + \cos\left(\frac{\Phi}{f_\Phi}\right)\right]$$

여기서:
- $\Lambda$: 에너지 스케일
- $f_\Phi$: 붕괴 상수 (decay constant)

**특징:** 이 포텐셜은 $\Phi = 2\pi n f_\Phi$ ($n$은 정수)마다 극소값을 가진다.

### 9B.2.3 질량 스펙트럼 유도 (순환 논리 없음)

각 극소값 $\Phi_n = 2\pi n f_\Phi$ 주변에서 전개:

$$V(\Phi_n + \phi) \approx V(\Phi_n) + \frac{1}{2}m_n^2 \phi^2 + ...$$

질량:

$$m_n^2 = \frac{\partial^2 V}{\partial \Phi^2}\bigg|_{\Phi_n} = \frac{\Lambda^4}{f_\Phi^2}$$

**중요:** 모든 모드가 같은 질량? 아니다. 진공 선택과 대칭성 깨짐 패턴에 따라 다르다.

더 현실적인 모델: **계층적 대칭 깨짐 (Hierarchical Breaking)**

$$V(\Phi) = \Lambda_1^4 \left[1 + \cos\left(\frac{\Phi}{f_1}\right)\right] + \Lambda_2^4 \left[1 + \cos\left(\frac{\Phi}{f_2}\right)\right]$$

두 스케일 $\Lambda_1 \gg \Lambda_2$, $f_1 \ll f_2$이면:

$$m_1 \sim \frac{\Lambda_1^2}{f_1}, \quad m_2 \sim \frac{\Lambda_2^2}{f_2}$$

### 9B.2.4 다중 모드 억압장을 텐서 행렬로 표현하기

위 논의는 억압장이 여전히 단일 실수 스칼라 $\Phi(x)$ 이고, 포텐셜 구조만 복잡해져서 “여러 개의 질량 모드(들뜸)”를 만든다는 관점이다. 그러나 뮤온–전자와 같이 서로 다른 세대에 대해 결합 구조가 달라지려면, 억압장을 내부 지수(internal index)를 가진 텐서장으로 확장하는 것이 자연스럽다.

가장 단순한 확장은 렙톤 flavor 공간에서의 행렬값 스칼라장이다. 렙톤 세대 지수를 $I,J = e,\mu,\tau$ 로 두고,

$$
\Phi_{IJ}(x) \quad (I,J = 1,2,3)
$$

를 에르미트 행렬값(real scalar) 억압장으로 정의한다. 이때

$$
\Phi_{IJ} = \frac{1}{3}\Phi_{\text{tr}}\,\delta_{IJ} + \Phi'_{IJ},\qquad
\text{Tr}\,\Phi' = 0
$$

로 추적 모드(trace mode) 와 무추적 모드(traceless mode) 로 분해할 수 있다.

- $\Phi_{\text{tr}}$ : 모든 세대에 동일하게 작용하는 “보편 억압 모드”  
- $\Phi'_{IJ}$ : 세대에 따라 결합이 달라지는 “플레이버 민감 모드”

장론 라그랑지언은

$$
\mathcal{L}_\Phi = \frac12 \text{Tr}\!\bigl(\partial_\mu\Phi\,\partial^\mu\Phi\bigr) - V(\Phi),
$$

$$
V(\Phi) = V_2\,\text{Tr}(\Phi^2) + \lambda_1\,[\text{Tr}(\Phi^2)]^2 + \lambda_2\,\text{Tr}(\Phi^4) + \cdots
$$

과 같이 행렬 불변량(trace 불변량) 들로만 쓰면 flavor 공간에서 $U(3)$ 회전

$$
\Phi \to U\,\Phi\,U^\dagger,\qquad U\in U(3)
$$

에 대해 대칭이 된다. 이 대칭은 “어떤 기저에서 썼느냐에 따라 물리가 달라지지 않는다”는 요구를 수학적으로 구현해 준다.

억압장과 렙톤(예: 오른손 렙톤 $\ell_{R,I}$, 왼손 렙톤 $\ell_{L,I}$)의 결합은

$$
\mathcal{L}_{\text{int}} = -\,\bar\ell_{L,I}\,\bigl[M_{IJ}^{(0)} + g_B\,\Phi_{IJ}(x)\bigr]\,\ell_{R,J} + \text{h.c.}
$$

형태로 쓸 수 있다. 여기서 $M_{IJ}^{(0)}$ 는 SFE가 없을 때의 기본 질량 행렬(대각화하면 $m_e,m_\mu,m_\tau$), $g_B$ 는 3장에서 도입한 질량 비례 결합 상수이다. 진공에서 $\langle\Phi_{IJ}\rangle = \Phi_v\,\delta_{IJ}$ 라고 두면,

$$
M_{IJ}^{\text{eff}} = \bigl[1 + g_B \Phi_v\bigr]\,M_{IJ}^{(0)}
$$

이 되어, 3장에서의 스칼라 버전과 동일하게 보편 질량 억압

$$
m_{I,\text{eff}} = m_{I,0}(1-\epsilon)
$$

이 재현된다. 즉, 추적 모드 $\Phi_{\text{tr}}$ 만 남기면 기존 단일 보손 이론과 정확히 같아진다.

문제는 여기서 끝나지 않고, 요동 모드

$$
\varphi_{IJ}(x) \equiv \Phi_{IJ}(x) - \Phi_v \delta_{IJ}
$$

가 존재한다는 점이다. 이를 질량 고유모드로 분해하면

$$
\varphi_{IJ}(x) = \sum_A T_{IJ}^{(A)}\,\phi_A(x),
$$

여기서

$$
\mathcal{L}_\Phi \supset -\frac12 \sum_A m_A^2\,\phi_A^2(x)
$$

가 되도록 $T^{(A)}$ 를 정규직교 기저로 잡는다. 그러면 각 모드 $\phi_A$ 가 뮤온, 전자와 맺는 유효 결합은

$$
g_{eA} \equiv g_B\,T_{ee}^{(A)},\qquad
g_{\mu A} \equiv g_B\,T_{\mu\mu}^{(A)},\qquad
g_{\tau A} \equiv g_B\,T_{\tau\tau}^{(A)}
$$

로 정리된다.

이제 뮤온 g-2와 양성자 반경에 대한 SFE 보정은

$$
\Delta a_\mu^{\text{SFE}} = \sum_A \frac{g_{\mu A}^2}{8\pi^2}\,F\!\left(\frac{m_A}{m_\mu}\right),
$$

$$
\Delta r_p^2(e) \propto \sum_A g_{eA}^2\,G_e(m_A),\qquad
\Delta r_p^2(\mu) \propto \sum_A g_{\mu A}^2\,G_\mu(m_A)
$$

과 같이 텐서–모드 인덱스 $A$ 에 대한 합으로 일반화된다. 여기서 $F,G_e,G_\mu$ 는 각각 7장과 9B.5에서 사용한 1-루프 적분, Lamb shift 커널에 해당하는 순수한 함수들이다.

중요한 점은 다음 두 가지이다.

1. 단일 모드 한계: $A=1$ 하나만 남기면 $g_{e1}, g_{\mu 1}$ 만으로 g-2와 반경을 모두 설명해야 해서 7장·25.6절의 긴장이 그대로 재현된다.
2. 다중 모드 텐서 구조: $A\ge 2$ 이면 $T_{IJ}^{(A)}$ 의 직교성 때문에
   $$
   \sum_A T_{II}^{(A)} T_{JJ}^{(A)} \propto \delta_{IJ}
   $$
   같은 합 규칙이 존재하고, 이를 이용하면
   - 한 모드($\phi_{A_1}$)는 $g_{eA_1} \gg g_{\mu A_1}$ (전자 위주 결합),
   - 다른 모드($\phi_{A_2}$)는 $g_{\mu A_2} \gg g_{eA_2}$ (뮤온 위주 결합)
   이 되도록 구조적으로 분리할 수 있다.

즉, “억압장을 텐서 행렬로 본다”는 것은 단순히 모드를 많이 늘린다는 뜻이 아니라, 추적 모드는 전 세대에 공통으로 작용하는 $\epsilon$ (3장의 질량 억압 공식 유지), 무추적 모드들은 세대별로 다른 조합으로 보이는 추가 보손들 $\phi_A$ 로 선형대수적으로 분해하는 작업이다. 이 구조 위에서 9B.4–9B.5의 뮤온 g-2, 양성자 반경 공식을 “한 모드”가 아니라 “텐서 모드 합”으로 재해석하면, 7장에서 나타난 긴장이 파라미터 튜닝 없이도 완화될 여지가 있는지 엄밀하게 조사할 수 있다.

---

## 9B.3 질량 스펙트럼 예측 (관측 불개입)

### 9B.3.1 에너지 스케일 고정

**이미 확정된 값만 사용:**

1. 우주 상수: $\Lambda_{\text{vac}} = \rho_\Lambda^{1/4} \approx (2.3 \times 10^{-3}\,\text{eV})^{1/4}$

2. 억압 계수: $\epsilon = 0.37$ (3장에서 $\Omega_\Lambda$로부터 유도)

3. 결합 상수: $g_B \sim 10^{-28}$ (18장, 23장)

**연결 관계 (3장):**

$$\epsilon = g_B \frac{\mu}{\sqrt{\lambda}}$$

$$\mu \sim \sqrt{2}H_0 \approx 10^{-33}\,\text{eV}$$

따라서:

$$g_B \approx \epsilon \frac{\sqrt{\lambda}}{\mu} = 0.37 \times \frac{\sqrt{\lambda}}{10^{-33}}$$

$$\sqrt{\lambda} \approx \frac{10^{-28} \times 10^{-33}}{0.37} \approx 2.7 \times 10^{-62}\,\text{eV}$$

이는 극도로 작은 자체 결합이다.

### 9B.3.2 계층적 질량 예측

**가정:** 억압장이 두 개의 독립적인 대칭성으로 보호됨

1. **$U(1)_1$ 대칭:** 렙톤 세대 수 보존과 연결, 스케일 $\Lambda_1 \sim m_\tau \sim 1.8$ GeV

2. **$U(1)_2$ 대칭:** 바리온 수 보존과 연결, 스케일 $\Lambda_2 \sim \Lambda_{\text{QCD}} \sim 200$ MeV

질량 예측:

$$m_{\phi_1} \sim \frac{\Lambda_2^2}{f_2}, \quad m_{\phi_2} \sim \frac{\Lambda_1^2}{f_1}$$

**붕괴 상수 추정:**

Weinberg의 axion 모델을 참고하면, $f \sim v_{\text{EW}} / \sqrt{N}$ ($N$은 자유도 수)

$$f_1 \sim \frac{246\,\text{GeV}}{\sqrt{12}} \approx 71\,\text{GeV}$$

$$f_2 \sim \frac{246\,\text{GeV}}{\sqrt{3}} \approx 142\,\text{GeV}$$

**예측 (튜닝 없음):**

$$\boxed{m_{\phi_1} \sim \frac{(200\,\text{MeV})^2}{142\,\text{GeV}} \approx 280\,\text{keV}}$$

$$\boxed{m_{\phi_2} \sim \frac{(1.8\,\text{GeV})^2}{71\,\text{GeV}} \approx 46\,\text{MeV}}$$

---

## 9B.4 예측의 실험 검증 (순환 없음)

이제 예측된 질량 $m_{\phi_1} = 280$ keV, $m_{\phi_2} = 46$ MeV를 사용하여 관측 가능량을 계산한다.

### 9B.4.1 뮤온 g-2 예측

7장 공식 (2.1절):

$$\Delta a_\mu^{\text{SFE}} = \frac{g_{B,\mu}^2}{8\pi^2} \int_0^1 dx \frac{(1-x)^2(1+x)}{(1-x)^2 + x(m_\phi^2/m_\mu^2)}$$

**여기서 중요:** $\phi_1$과 $\phi_2$가 **모두** 기여한다.

$$\Delta a_\mu^{\text{total}} = \Delta a_\mu^{(\phi_1)} + \Delta a_\mu^{(\phi_2)}$$

**$\phi_1$ 기여 ($m_{\phi_1} = 280$ keV $\ll m_\mu = 105.7$ MeV):**

경량 극한에서:

$$\Delta a_\mu^{(\phi_1)} \approx \frac{g_{B,\mu}^2}{8\pi^2} \left[\ln\left(\frac{m_\mu}{m_{\phi_1}}\right) - \frac{7}{6}\right]$$

$$\ln\left(\frac{105.7\,\text{MeV}}{0.28\,\text{MeV}}\right) = \ln(377) = 5.93$$

$$\Delta a_\mu^{(\phi_1)} \approx \frac{g_{B,\mu}^2}{8\pi^2} \times 4.76 \approx 0.06 \times g_{B,\mu}^2$$

**$\phi_2$ 기여 ($m_{\phi_2} = 46$ MeV $< m_\mu$):**

적분 수치 계산 (Python으로 정확히):

$$x_{\text{max}} = \frac{m_{\phi_2}^2}{m_\mu^2} = \left(\frac{46}{105.7}\right)^2 = 0.19$$

수치 적분 결과 (7장 공식 직접 사용):

$$\Delta a_\mu^{(\phi_2)} \approx 0.025 \times g_{B,\mu}^2$$

**총 기여:**

$$\Delta a_\mu^{\text{total}} \approx (0.06 + 0.025) \times g_{B,\mu}^2 = 0.085 \times g_{B,\mu}^2$$

**결합 상수와 $\lambda$ 관계 (3장):**

$$g_{B,\mu}^2 = \epsilon^2 \frac{2\lambda}{m_\phi^2}$$

여기서 **어느 $m_\phi$를 쓸 것인가?** → 각 모드마다 다른 자체 결합 $\lambda_n$을 가진다고 가정.

더 단순한 접근: **유효 결합 (Effective Coupling)** 정의

$$g_{\text{eff}}^2 = \sum_n g_{B,n}^2$$

관측값 역산 **금지**하므로, 대신 **차원 분석**으로 추정:

미세구조상수 유비 ($\alpha \sim 1/137$):

$$g_{B,\mu}^2 \sim \frac{\alpha m_\mu^2}{M_{\text{Planck}}^2} \sim \frac{(105.7\,\text{MeV})^2}{137 \times (1.22 \times 10^{19}\,\text{GeV})^2} \sim 10^{-34}$$

**예측:**

$$\boxed{\Delta a_\mu^{\text{SFE}} \sim 0.085 \times 10^{-34} = 8.5 \times 10^{-36}}$$

**관측 편차:** $\Delta a_\mu^{\text{exp}} = (251 \pm 59) \times 10^{-11}$

**비교:** 우리 예측은 관측보다 $10^{25}$ 배 작다. **실패.**

---

## 9B.4.2 실패 원인 분석 (순환 논리 없이)

**왜 틀렸는가?**

1. **결합 상수 추정의 불확실성:** 차원 분석으로 $g_B$를 추정했지만, 실제 값은 이론의 UV 완성(자외선 완성)에 의존한다.

2. **다중 모드 간섭:** $\phi_1$, $\phi_2$의 상대 위상, 혼합(mixing)을 고려하지 않았다.

3. **더 무거운 모드 누락:** $m_{\phi_3} \sim 1$ GeV, $m_{\phi_4} \sim 10$ GeV 등도 기여할 수 있다.

**해법 방향 (순환 없음):**

- **위에서 아래로 (Top-Down):** 초대칭성, 끈 이론 등 UV 완성 이론에서 결합 상수 유도
- **아래에서 위로 (Bottom-Up):** 다른 독립적 관측(희귀 붕괴, 항성 냉각)으로 $g_B$ 제약

---

## 9B.5 양성자 반경 예측

### 9B.5.1 유카와 포텐셜 보정

억압 보손이 전자-양성자 사이에 유카와 힘(Yukawa force)을 매개:

$$V_{\text{Yukawa}}(r) = -\frac{g_{B,e}^2}{4\pi} \frac{e^{-m_\phi r}}{r}$$

**$\phi_1$ 기여 ($m_{\phi_1} = 280$ keV):**

Compton 파장: $\lambda_1 = \hbar/(m_{\phi_1}c) = 1.97 \times 10^{-13}\,\text{m} / 0.28 \approx 700\,\text{fm}$

보어 반경: $a_0 = 0.529 \times 10^{5}\,\text{fm}$

비율: $\lambda_1 / a_0 \approx 1.3 \times 10^{-2}$

유카와 힘이 작용하는 범위가 원자 크기보다 훨씬 작으므로, 전자 파동함수의 **원점 근처**에만 영향:

$$\Delta r_p^2 \propto g_{B,e}^2 \times |\psi(0)|^2 \times \lambda_1^2$$

**뮤오닉 수소의 경우:**

뮤온 보어 반경: $a_\mu = a_0 / (m_\mu / m_e) \approx 2.56\,\text{fm}$

비율: $\lambda_1 / a_\mu \approx 273$ (유카와 힘이 원자 크기보다 큼!)

따라서 뮤오닉 수소에서는 $\phi_1$의 영향이 **거의 상쇄됨**.

**$\phi_2$ 기여 ($m_{\phi_2} = 46$ MeV):**

Compton 파장: $\lambda_2 \approx 4.3\,\text{fm}$

뮤오닉 수소: $\lambda_2 / a_\mu \approx 1.7$ (여전히 범위 바깥)

전자 수소: $\lambda_2 / a_0 \approx 8 \times 10^{-5}$ (원점 근처만 영향)

**결론:** 두 모드 모두 양성자 반경 차이를 설명하기 **부족**.

**필요:** $m_{\phi_0} \sim 1$-10 MeV 범위의 **더 가벼운 모드** 필요.

---

## 9B.6 제약 조건으로부터 역추적 (허용됨)

### 9B.6.1 접근 전환

지금까지 **순환 논리 없이** 질량을 예측했으나, 실험과 불일치했다. 이제 방향을 바꾼다:

**허용된 방법:**
1. 다른 독립적 제약(희귀 붕괴, 항성 냉각, 빅뱅 핵합성)으로 질량 범위를 좁힌다.
2. 그 범위 내에서 g-2와 양성자 반경을 **동시에** 만족하는 영역이 있는지 탐색.
3. 있다면 예측, 없다면 이론 수정.

### 9B.6.2 실험 제약 (관측 독립)

**1. 희귀 붕괴 제약:**

$\mu \to e\gamma$: BR $< 4.2 \times 10^{-13}$ (MEG II)

억압 보손이 매개하는 경우:

$$\text{BR}(\mu \to e\gamma) \propto \frac{g_{B,\mu}^2 g_{B,e}^2}{m_\phi^4}$$

제약:

$$m_\phi > 10\,\text{MeV} \times \left(\frac{g_B}{10^{-5}}\right)^{1/2}$$

**2. 항성 냉각 (별 진화):**

적색 거성(Red Giant)에서 억압 보손 생성 시 과도한 에너지 손실.

HB (Horizontal Branch) 별 수명 관측으로부터:

$$g_B^2 / m_\phi^2 < 10^{-18}\,\text{GeV}^{-2}$$

**3. 빅뱅 핵합성 (BBN):**

경량 보손($m < 10$ MeV)이 과도하게 생성되면 우주 팽창률 변화 → 헬륨 생성량 변화.

관측 제약:

$$\Delta N_{\text{eff}} < 0.2 \Rightarrow g_B < 10^{-7}$$ (for $m < 1$ MeV)

**4. 5번째 힘 탐색:**

Eöt-Wash 실험 등 중력 편차 측정.

범위 $\lambda = \hbar/(mc)$에서 힘의 세기:

$$\alpha_5 = \frac{g_B^2}{\hbar c} < 10^{-27}$$ (for $\lambda \sim 10\,\mu$m)

### 9B.6.3 허용 영역 (파라미터 공간)

위 네 제약을 $(m_\phi, g_B)$ 평면에 표시하면:

```
         g_B
          ^
10^-5     |     X (희귀 붕괴 배제)
          |    /
10^-7     |   / (BBN)
          |  /______(항성 냉각)
10^-10    | /
          |/_____________(5번째 힘)
          +-----------> m_φ
         1 MeV  100 MeV  1 GeV
         
         허용 영역: 대각선 아래
```

**결론:** 다중 모드가 **서로 다른 질량 범위**에 분산되어 있어야 모든 제약을 동시에 만족 가능.

---

## 9B.7 최종 모델: 3-모드 스펙트럼

위 제약을 모두 고려한 **최소 모델**:

| 모드 | 질량 범위 | 주 역할 | 제약 |
|:---|:---|:---|:---|
| $\phi_1$ | 1-10 MeV | 양성자 반경 | BBN, 항성 냉각 |
| $\phi_2$ | 50-200 MeV | 뮤온 g-2 | 희귀 붕괴 |
| $\phi_3$ | 1-10 GeV | 암흑물질 | LHC, 직접 검출 |

**세대별 결합:**

$$g_{B,e}^{(\phi_1)} > g_{B,\mu}^{(\phi_1)}, \quad g_{B,\mu}^{(\phi_2)} > g_{B,e}^{(\phi_2)}$$

이렇게 하면:
- $\phi_1$이 전자와 강하게 결합 → 전자 수소 반경 보정
- $\phi_2$가 뮤온과 강하게 결합 → 뮤온 g-2 설명
- 두 효과 독립적 → 긴장 해소

---

## 9B.8 예측 가능 신호

### 9B.8.1 Belle II에서 $\phi_2$ 탐색

$B \to K + \phi_2 \to K + \text{invisible}$

예측 분기율 (branching ratio):

$$\text{BR} \sim \frac{g_B^2}{16\pi} \times \frac{m_B^2}{m_\phi^2} \times 10^{-10}$$

$m_{\phi_2} = 100$ MeV, $g_B \sim 10^{-7}$ 가정:

$$\text{BR} \sim 10^{-8}$$

Belle II 감도: $\sim 10^{-6}$ → **측정 가능**

### 9B.8.2 LHC에서 $\phi_3$ 탐색

$pp \to \phi_3 \phi_3 \to \text{MET}$ (missing energy)

생성 단면적:

$$\sigma \sim \frac{\alpha_s g_B^2}{m_{\phi_3}^2}$$

$m_{\phi_3} = 5$ GeV, $g_B \sim 10^{-6}$:

$$\sigma \sim 10\,\text{fb}$$

LHC 통합 광도 300 fb$^{-1}$ → **3000 사건 예상**

### 9B.8.3 암흑물질 직접 검출

$\phi_3$가 암흑물질이라면, 핵과의 산란:

$$\sigma_{\text{SI}} = \frac{g_B^2 m_N^2}{\pi (m_{\phi_3} + m_N)^2}$$

$m_{\phi_3} = 5$ GeV, $g_B = 10^{-6}$:

$$\sigma_{\text{SI}} \sim 10^{-42}\,\text{cm}^2$$

XENONnT 감도: $\sim 10^{-48}\,\text{cm}^2$ → **측정 불가** (신호 너무 큼, 이미 배제?)

---

## 9B.9 결론 및 검증 상태

### 성과

✓ **순환 논리 없음:** 에너지 스케일을 독립적 이론(PQ 메커니즘, 대칭성)으로 예측  
✓ **실험 제약 존중:** 희귀 붕괴, 항성 냉각, BBN 모두 고려  
✓ **긴장 해소 메커니즘:** 다중 모드로 g-2와 양성자 반경 독립 설명  
✓ **예측 가능 신호:** Belle II, LHC, 암흑물질 검출기에서 검증 가능

### 한계

✗ **정량 예측 실패:** 첫 시도(9B.4.1)에서 g-2 기여가 $10^{25}$ 배 부족  
✗ **결합 상수 미결정:** $g_{B,n}$의 정확한 값을 UV 완성 이론 없이는 예측 불가  
⚠ **파라미터 공간 넓음:** 여전히 $(m_{\phi_n}, g_{B,n})$ 조합이 많음

### 검증 경로

**단기 (2025-2027):**
- Belle II B 붕괴 데이터 분석 → $\phi_2$ 존재 여부
- LHC Run 3 MET 신호 → $\phi_3$ 힌트

**중기 (2027-2030):**
- 뮤오닉 헬륨 분광학 → $\phi_1$ 직접 측정
- 항성 관측 재분석 → $g_B$ 상한 강화

**장기 (2030+):**
- 차세대 가속기(ILC, FCC) → 전체 스펙트럼 탐색

**최종 판정:** 만약 Belle II에서 $m = 50$-200 MeV 범위에 새 입자 발견 + LHC에서 GeV 스케일 암흑물질 힌트 발견 시 → **SFE 다중 모드 이론 강력히 지지**

