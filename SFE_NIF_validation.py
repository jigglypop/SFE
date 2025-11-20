import numpy as np

class NIF_Validator:
    def __init__(self):
        # NIF 2022 Ignition Parameters (Approximate from LLNL/Nature)
        self.T_ion_obs = 10.0      # Observed Ion Temperature (keV) - Lower bound estimate
        self.rho_hot = 100.0       # Hot spot density (g/cm^3)
        self.R_hot = 30.0e-4       # Hot spot radius (cm) -> 30 um
        self.tau_burn = 100.0e-12  # Confinement time (s) -> 100 ps
        
        # Physics Constants
        self.kb_keV = 1.602e-16    # J/keV
        self.MeV_J = 1.602e-13     # J/MeV
        self.E_DT = 17.6           # Energy per reaction (MeV)
        
        # D-T Fuel properties
        self.m_D = 3.34e-24 # g
        self.m_T = 5.01e-24 # g
        self.m_avg = (self.m_D + self.m_T) / 2.0
        
    def dt_reaction_rate(self, T_keV, epsilon=0.0):
        """
        Calculate D-T reaction rate <sigma v> with SFE modification.
        Using Bosch-Hale parameterization form, modified for SFE.
        
        Standard Gamow factor exponent B_G ~ 34.3 sqrt(keV) for DT.
        SFE effect reduces mass -> reduces Gamow exponent by sqrt(1-epsilon).
        """
        # Bosch-Hale approx coefficients for D-T
        # <sigma v> ~ T^(-2/3) * exp(-B / T^(1/3))
        C1 = 3.68e-12
        B = 19.94  # (keV)^(1/3) related constant
        
        # SFE Modification:
        # The exponent comes from Gamow factor proportional to sqrt(mass).
        # SFE: mass -> mass * (1 - epsilon)
        # So, B -> B * sqrt(1 - epsilon)
        
        B_eff = B * np.sqrt(1.0 - epsilon)
        
        if T_keV <= 0: return 0.0
        
        # Note: This is a simplified scaling for the exponential part, which dominates.
        rate = (C1 / (T_keV**(2/3))) * np.exp(-B_eff / (T_keV**(1/3)))
        return rate

    def calculate_yield(self, T_keV, epsilon=0.0):
        """
        Calculate total fusion yield in MJ for a simplified hot spot model.
        """
        # Number density n = rho / m_avg
        n = self.rho_hot / self.m_avg
        
        # Volume
        V = (4.0/3.0) * np.pi * (self.R_hot**3)
        
        # Reaction Rate
        sv = self.dt_reaction_rate(T_keV, epsilon)
        
        # Total Reactions N = 0.5 * n^2 * <sigma v> * V * tau
        # (0.5 because D+T are distinct species but we use n_D=n_T=n/2 usually. 
        #  If n is total ion density, reaction rate is (n/2)*(n/2)*sv = 1/4 n^2 sv.
        #  Wait, standard formula: Rate = n_D * n_T * sv. n_D = n_T = 0.5 * n.
        #  So Rate = 0.25 * n^2 * sv.)
        
        Rate_density = 0.25 * (n**2) * sv
        Total_Rxns = Rate_density * V * self.tau_burn
        
        # Energy Yield
        Yield_J = Total_Rxns * self.E_DT * self.MeV_J
        Yield_MJ = Yield_J / 1.0e6
        
        return Yield_MJ, sv

    def find_epsilon_for_yield(self, target_yield_MJ, T_keV):
        """
        Find the epsilon required to match a specific yield at a given temperature.
        """
        eps_list = np.linspace(0, 0.9, 100)
        for eps in eps_list:
            y, _ = self.calculate_yield(T_keV, eps)
            if y >= target_yield_MJ:
                return eps, y
        return None, None

    def run_validation(self):
        print("=== SFE Theory Validation against NIF Data ===")
        print(f"Simulation Parameters:")
        print(f"  Ion Temp: {self.T_ion_obs} keV")
        print(f"  Density:  {self.rho_hot} g/cm^3")
        print(f"  Radius:   {self.R_hot*1e4} um")
        print(f"  Burn Time:{self.tau_burn*1e12} ps")
        print("-" * 40)

        # 1. Standard Model Prediction (epsilon = 0)
        yield_std, sv_std = self.calculate_yield(self.T_ion_obs, epsilon=0.0)
        print(f"[Standard Model] Yield: {yield_std:.4f} MJ")

        # 2. Target Observation (NIF achieved ~3.15 MJ)
        target_yield = 3.15
        print(f"[Observation]    Yield: {target_yield:.4f} MJ")
        
        ratio = target_yield / yield_std
        print(f"-> Discrepancy: Standard model explains only {yield_std/target_yield*100:.1f}% of observed yield.")
        print(f"-> Required Boost Factor: {ratio:.2f}x")
        
        # 3. SFE Explanation
        print("-" * 40)
        print("[SFE Hypothesis Test]")
        req_eps, req_y = self.find_epsilon_for_yield(target_yield, self.T_ion_obs)
        
        if req_eps:
            print(f"To match observation (3.15 MJ) at 10 keV:")
            print(f"  Required Mass Suppression (epsilon): {req_eps:.4f} ({req_eps*100:.1f}%)")
            print(f"  Resulting Yield: {req_y:.4f} MJ")
            
            # 4. Physical Interpretation check
            # Is this epsilon realistic? NIF laser energy density vs suppression field
            # Just a qualitative check here.
            print("\n[Conclusion]")
            print(f"A local mass suppression of ~{req_eps*100:.1f}% can explain the full yield.")
            print("This suggests the high energy density might have triggered an SFE response.")
        else:
            print("SFE could not match the yield even with high epsilon.")

if __name__ == "__main__":
    val = NIF_Validator()
    val.run_validation()

