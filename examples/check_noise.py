import numpy as np
import matplotlib.pyplot as plt

def check_noise_distribution():
    print("[SFE 1/f Noise Spectrum Check]")
    
    # 1. Generate Noise using the same logic as Rust (simplified)
    steps = 10000
    spectrum = np.zeros(steps, dtype=complex)
    
    # S(f) ~ 1/f (Amplitude ~ 1/sqrt(f))
    # Rust Logic: 
    # for i in 1..steps {
    #    let f = if i <= steps/2 { i as f64 } else { (steps - i) as f64 };
    #    let amplitude = 1.0 / f.sqrt();
    
    for i in range(1, steps):
        f = i if i <= steps//2 else (steps - i)
        amplitude = 1.0 / np.sqrt(f)
        phase = np.exp(2j * np.pi * np.random.rand())
        spectrum[i] = amplitude * phase
        
    # Inverse FFT
    noise = np.fft.ifft(spectrum).real
    
    # Normalize
    noise = (noise - np.mean(noise)) / np.std(noise)
    
    # 2. Analyze Spectrum of Generated Noise
    freqs = np.fft.fftfreq(steps)
    psd = np.abs(np.fft.fft(noise))**2
    
    # Filter positive frequencies
    mask = freqs > 0
    freqs = freqs[mask]
    psd = psd[mask]
    
    # 3. Plot Log-Log Spectrum
    plt.figure(figsize=(10, 6))
    plt.loglog(freqs, psd, 'b-', alpha=0.5, label='Generated Noise PSD')
    
    # Ideal 1/f line
    plt.loglog(freqs, 1/freqs, 'r--', linewidth=2, label='Ideal 1/f')
    
    plt.title("SFE Noise Spectrum Verification")
    plt.xlabel("Frequency")
    plt.ylabel("Power Spectral Density")
    plt.legend()
    plt.grid(True, which="both", linestyle='--')
    
    plt.savefig('examples/noise_spectrum_check.png')
    print("Spectrum plot saved to examples/noise_spectrum_check.png")
    
    # 4. Check Free Decay Logic
    # Phi(t) = integral(noise * A) dt
    # Coherence = cos(Phi(t))
    # If noise is dominated by very low freq (near DC), Phi(t) grows linearly -> cos(Phi) oscillates.
    # It does NOT decay to zero quickly if the ensemble average is not large enough or time is short.
    
    print("\n[Insight]")
    print("If PSD follows 1/f correctly, the noise has huge energy at f->0.")
    print("This looks like a 'Random Constant Field' for each trial.")
    print("Free Decay = Average(cos(C * t)) over trials.")
    print("If C varies normally, this should decay as exp(-t^2).")
    print("WHY FREE DECAY WAS 1.0? -> Maybe noise amplitude (0.05) was TOO SMALL.")
    print("With 0.05, phase drift after 10000 steps is small.")
    
    accumulated_phase_drift = np.sum(np.abs(noise)) * 0.05 * 0.01
    print(f"Estimated Phase Drift (sum|n|*dt*amp): {accumulated_phase_drift:.2f} rad")
    print("If drift << pi, Coherence stays ~1.0.")

if __name__ == "__main__":
    check_noise_distribution()

