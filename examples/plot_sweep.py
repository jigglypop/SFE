import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys

def plot_sweep_results(csv_path="sweep_results.csv"):
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: {csv_path} not found. Run 'sfe_engine sweep' first.")
        return

    # 1. Heatmap: SFE Score by Pulse Count vs Noise Amp
    pivot_table = df.pivot(index="NoiseAmp", columns="PulseCount", values="SFE_Score")
    
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    sns.heatmap(pivot_table, annot=True, cmap="viridis", vmin=0.5, vmax=1.0)
    plt.title("SFE Coherence Score (Higher is Better)")
    plt.ylabel("Noise Amplitude")
    plt.xlabel("Pulse Count")

    # 2. Improvement Line Plot
    plt.subplot(1, 2, 2)
    sns.lineplot(data=df, x="PulseCount", y="Improvement_Pct", hue="NoiseAmp", marker="o", palette="flare")
    plt.title("SFE Improvement over UDD (%)")
    plt.ylabel("Improvement (%)")
    plt.xlabel("Pulse Count")
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("sfe_sweep_analysis.png")
    print("Analysis saved to sfe_sweep_analysis.png")

if __name__ == "__main__":
    plot_sweep_results()

