import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def analyze_decoupling():
    print("[SFE Decoupling Performance Benchmark]")
    
    # 1. Load Data
    try:
        df = pd.read_csv('decoupling_result.csv')
    except FileNotFoundError:
        print("Error: decoupling_result.csv not found.")
        return

    t = df['Step'].values
    free = df['Free'].values
    echo = df['Echo'].values
    cpmg = df['CPMG'].values
    udd = df['UDD'].values # UDD (SOTA) added
    
    # 2. Calculate Final Coherence
    final_free = free[-1]
    final_echo = echo[-1]
    final_cpmg = cpmg[-1]
    final_udd = udd[-1]
    
    print(f"1. Free Decay : {final_free:.4f}")
    print(f"2. Hahn Echo  : {final_echo:.4f}")
    print(f"3. CPMG (Std) : {final_cpmg:.4f}")
    print(f"4. UDD (SOTA) : {final_udd:.4f}")
    
    # 3. Performance Comparison
    print("\n[Performance Analysis]")
    if final_free < 0.1:
        print("- Free Decay: Collapsed (As expected)")
    else:
        print("- Free Decay: Still alive (Noise might be too weak?)")

    # CPMG vs UDD
    if final_udd > final_cpmg:
        ratio = final_udd / max(final_cpmg, 0.01)
        print(f">> UDD Wins! ({ratio:.2f}x better than CPMG)")
        winner = "UDD"
    else:
        ratio = final_cpmg / max(final_udd, 0.01)
        print(f">> CPMG Wins! ({ratio:.2f}x better than UDD)")
        winner = "CPMG"
        
    # Total Improvement vs Free
    total_gain = max(final_cpmg, final_udd) / max(final_free, 0.01)
    print(f">> Max Gain vs Free: {total_gain:.1f}x")

    # 4. Visualization
    plt.figure(figsize=(12, 7))
    
    plt.plot(t, free, 'k-', alpha=0.3, label='Free Decay')
    plt.plot(t, echo, 'b--', label='Echo (1-pulse)')
    plt.plot(t, cpmg, 'g-', linewidth=2, label='CPMG (Standard)')
    plt.plot(t, udd, 'r-', linewidth=2, label='UDD (SOTA)')
    
    plt.axhline(y=0.368, color='gray', linestyle=':', label='1/e Threshold')
    plt.title(f"SFE Noise Cancellation Benchmark\nWinner: {winner} (Noise Amp=0.12, Pulses=20)")
    plt.xlabel("Time Steps")
    plt.ylabel("Coherence")
    plt.legend(loc='lower left')
    plt.grid(True, linestyle='--', alpha=0.5)
    
    plt.savefig('examples/decoupling_benchmark.png')
    print("Benchmark plot saved to examples/decoupling_benchmark.png")

if __name__ == "__main__":
    analyze_decoupling()
