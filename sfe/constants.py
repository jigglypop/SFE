import numpy as np

G = 6.67430e-11
c = 2.99792458e8
hbar = 1.0545718e-34
mp = 1.6726219e-27
me = 9.10938356e-31
alpha_em = 7.297352569e-3

M_P = np.sqrt(hbar * c / G)

# 이전의 Holographic scaling 가설(alpha_dimless = (mp/MP)^(2/3)) 삭제됨
# 이제 SFETheory.derive_alpha() 메소드가 제1원리 유도를 담당함
alpha_si = 2.88e85 # Fallback or approximate value if needed directly

H0_PLANCK = 67.4
OMEGA_M = 0.315
EPSILON_0 = 0.355
OMEGA_LAMBDA = 0.685
EPSILON_MASS = 2 * OMEGA_LAMBDA - 1.0
