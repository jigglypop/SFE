import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def verify_rust_simulation():
    # 1. Load Data
    try:
        df = pd.read_csv('sfe_output.csv')
    except FileNotFoundError:
        print("Error: sfe_output.csv not found.")
        return

    # 2. Analytical Check
    # Equation: x^3 - x + 5 = 0 (for J = -5.0)
    # Expected Root approx -1.904
    expected_equilibrium = -1.904
    final_value = df['CenterPhi'].iloc[-1]
    
    print(f"[Verification Analysis]")
    print(f"Initial Value: {df['CenterPhi'].iloc[0]} (Expected ~1.0)")
    print(f"Final Value  : {final_value}")
    print(f"Analytical Solution for J=-5.0: {expected_equilibrium}")
    print(f"Error: {abs(final_value - expected_equilibrium):.4f}")
    
    if abs(final_value - expected_equilibrium) < 0.1:
        print(">> PASSED: Simulation converges to the correct physical equilibrium.")
    else:
        print(">> FAILED: Simulation diverged from theory.")

    # 3. Visualization
    plt.figure(figsize=(10, 6))
    plt.plot(df['TimeStep'], df['CenterPhi'], 'b-', linewidth=1.5, label='Rust Simulation')
    plt.axhline(y=1.0, color='g', linestyle='--', alpha=0.5, label='Initial Vacuum (+1.0)')
    plt.axhline(y=expected_equilibrium, color='r', linestyle='--', alpha=0.8, label='Theoretical Equilibrium (-1.9)')
    
    plt.title("SFE Core Engine Verification\n(High-Density Matter Source J=-5.0)")
    plt.xlabel("Time Steps")
    plt.ylabel(r"Field Value ($\Phi$)")
    plt.legend()
    plt.grid(True, which='both', linestyle='--', alpha=0.7)
    
    # Add annotation for phase transition
    plt.annotate('Phase Transition\n(+1.0 -> -1.9)', xy=(50, 0.0), xytext=(1000, 0.5),
                 arrowprops=dict(facecolor='black', shrink=0.05))
    
    plt.savefig('examples/rust_engine_verification.png')
    print("Plot saved to examples/rust_engine_verification.png")

if __name__ == "__main__":
    verify_rust_simulation()

