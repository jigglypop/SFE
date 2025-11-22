use rand::prelude::*;
use rand_distr::StandardNormal;
use rustfft::{FftPlanner, num_complex::Complex, Fft};
use rustfft::num_traits::Zero;
use std::sync::Arc;

/// caching the FFT planner to avoid re-initialization overhead.
pub struct PinkNoiseGenerator {
    planner: FftPlanner<f64>,
    fft: Arc<dyn Fft<f64>>,
    steps: usize,
    spectrum_buffer: Vec<Complex<f64>>,
}

impl PinkNoiseGenerator {
    pub fn new(steps: usize) -> Self {
        let mut planner = FftPlanner::new();
        let fft = planner.plan_fft_inverse(steps);
        Self {
            planner, // Keep ownership if we need to plan other sizes later, though we mostly reuse 'fft'
            fft,
            steps,
            spectrum_buffer: vec![Complex::zero(); steps],
        }
    }

    /// Generates 1/f (Pink) Noise using IFFT into a provided buffer or returns a new one
    pub fn generate(&mut self, output: &mut [f64]) {
        if output.len() != self.steps {
            panic!("Output buffer length must match generator steps");
        }

        let mut rng = thread_rng();
        let steps = self.steps;
        
        // Reset buffer
        // DC component (f=0) - Random drift
        let dc_real: f64 = rng.sample(StandardNormal);
        self.spectrum_buffer[0] = Complex::new(dc_real * (steps as f64).sqrt(), 0.0);
        
        // Generate spectrum
        // Optimize: Only compute up to Nyquist and use conjugate symmetry for real output if using real-to-complex,
        // but rustfft's standard FFT is complex-to-complex. We take the real part at the end.
        // A full complex pink noise generation:
        for i in 1..steps {
            // 1/f falloff
            // f = i for i <= N/2, else N-i
            let f = if i <= steps/2 { i as f64 } else { (steps - i) as f64 };
            let amplitude = 1.0 / f.sqrt(); 
            
            let real: f64 = rng.sample(StandardNormal);
            let imag: f64 = rng.sample(StandardNormal);
            
            self.spectrum_buffer[i] = Complex::new(real * amplitude, imag * amplitude);
        }
        
        // In-place IFFT
        self.fft.process(&mut self.spectrum_buffer);
        
        // Extract real part
        for (i, val) in self.spectrum_buffer.iter().enumerate() {
            output[i] = val.re;
        }
    }
    
    pub fn generate_new(&mut self) -> Vec<f64> {
        let mut out = vec![0.0; self.steps];
        self.generate(&mut out);
        out
    }
}

/// Legacy function wrapper for backward compatibility, but simpler
pub fn generate_pink_noise(steps: usize) -> Vec<f64> {
    let mut gen = PinkNoiseGenerator::new(steps);
    gen.generate_new()
}
