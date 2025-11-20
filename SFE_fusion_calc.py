import numpy as np

class SFE_Fusion_Calculator:
    def __init__(self):
        # Constants
        self.c = 3.0e8          # m/s
        self.hbar = 1.055e-34   # J·s
        self.k_B = 1.38e-23     # J/K
        self.e = 1.602e-19      # C
        self.epsilon_0 = 8.854e-12 # F/m
        self.alpha = 1.0/137.036   # Fine structure constant
        
        # Masses (kg)
        self.m_p = 1.673e-27    # Proton
        self.m_B11 = 1.828e-26  # Boron-11 (approx 11 * m_p)
        
    def reduced_mass(self, m1, m2, epsilon=0.0):
        """
        Calculate reduced mass under SFE suppression.
        m_eff = m_0 * (1 - epsilon)
        """
        m1_eff = m1 * (1.0 - epsilon)
        m2_eff = m2 * (1.0 - epsilon)
        return (m1_eff * m2_eff) / (m1_eff + m2_eff)

    def gamow_energy(self, Z1, Z2, mu_eff):
        """
        Calculate Gamow Energy E_G
        E_G = (pi * alpha * Z1 * Z2)^2 * 2 * mu * c^2
        """
        # E_G in Joules
        E_G = (np.pi * self.alpha * Z1 * Z2)**2 * 2 * mu_eff * self.c**2
        # Convert to keV
        return E_G / (1000 * self.e)

    def tunneling_probability_exponent(self, E_G_keV, E_cm_keV):
        """
        Calculate the exponent of the Gamow factor: -sqrt(E_G / E)
        """
        if E_cm_keV <= 0: return -np.inf
        return -np.sqrt(E_G_keV / E_cm_keV)

    def boost_factor(self, Z1, Z2, m1, m2, Temp_keV, epsilon):
        """
        Calculate reaction rate boost factor P_SFE / P_STD
        """
        # Standard Case
        mu_std = self.reduced_mass(m1, m2, epsilon=0.0)
        Eg_std = self.gamow_energy(Z1, Z2, mu_std)
        exp_std = self.tunneling_probability_exponent(Eg_std, Temp_keV)
        
        # SFE Case
        mu_sfe = self.reduced_mass(m1, m2, epsilon=epsilon)
        Eg_sfe = self.gamow_energy(Z1, Z2, mu_sfe)
        exp_sfe = self.tunneling_probability_exponent(Eg_sfe, Temp_keV)
        
        # Boost
        # P ~ exp(-sqrt(Eg/E))
        # Ratio = exp(exp_sfe - exp_std)
        log_boost = exp_sfe - exp_std
        boost = np.exp(log_boost)
        
        return {
            "mu_ratio": mu_sfe / mu_std,
            "Eg_std_keV": Eg_std,
            "Eg_sfe_keV": Eg_sfe,
            "exponent_std": exp_std,
            "exponent_sfe": exp_sfe,
            "boost_factor": boost
        }

    def analyze_nif_scenario(self):
        print("=== SFE NIF(Ignition) Scenario Analysis ===")
        
        # Scenario 1: D-T Fusion (NIF Standard)
        # Deuterium (m_p + m_n), Tritium (m_p + 2m_n)
        m_D = 3.343e-27
        m_T = 5.007e-27
        Z_D = 1
        Z_T = 1
        
        # NIF Approx Temperature: 5 keV to 10 keV (ignition starts)
        # Let's pick 5 keV (sub-optimal) to see if SFE helps.
        T_keV = 5.0 
        
        print(f"\n[Case 1] D-T Fusion at {T_keV} keV")
        
        for eps in [0.0, 0.1, 0.3, 0.5]:
            res = self.boost_factor(Z_D, Z_T, m_D, m_T, T_keV, eps)
            print(f"  epsilon={eps:.1f} | Mass={res['mu_ratio']*100:.0f}% | "
                  f"Gamow Exp: {res['exponent_std']:.2f} -> {res['exponent_sfe']:.2f} | "
                  f"Boost: {res['boost_factor']:.2e} x")

        # Scenario 2: p-B11 Fusion (The Holy Grail)
        print(f"\n[Case 2] p-B11 Fusion (Z=1, Z=5) at {T_keV} keV (Cold for p-B11)")
        
        for eps in [0.0, 0.3, 0.5, 0.7]:
            res = self.boost_factor(1, 5, self.m_p, self.m_B11, T_keV, eps)
            print(f"  epsilon={eps:.1f} | Mass={res['mu_ratio']*100:.0f}% | "
                  f"Gamow Exp: {res['exponent_std']:.2f} -> {res['exponent_sfe']:.2f} | "
                  f"Boost: {res['boost_factor']:.2e} x")

if __name__ == "__main__":
    calc = SFE_Fusion_Calculator()
    calc.analyze_nif_scenario()

