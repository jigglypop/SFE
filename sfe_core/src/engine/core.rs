use ndarray::{Array1, s};
use rayon::prelude::*;

const COUPLING_K: f64 = 50.0;
const DT: f64 = 0.01;

pub struct QSFEngine {
    pub phi: Array1<f64>,
    pub dphi: Array1<f64>,
    pub source_j: Array1<f64>,
    pub forces_buffer: Array1<f64>, // Cached buffer to avoid allocation
    pub mu: f64,
    pub lam: f64,
}

impl QSFEngine {
    pub fn new(size: usize) -> Self {
        let mu: f64 = 1.0;
        let lam: f64 = 1.0;
        let vacuum_vev = mu / lam.sqrt();
        let phi = Array1::from_elem(size, vacuum_vev);
        let dphi = Array1::zeros(size);
        let mut source_j = Array1::zeros(size);
        let forces_buffer = Array1::zeros(size);
        
        // Create a localized source matter
        let mid = size / 2;
        if size > 20 {
            let range = 10;
            let mut slice = source_j.slice_mut(s![mid-range..mid+range]);
            slice.fill(-5.0); 
        }
        QSFEngine { phi, dphi, source_j, forces_buffer, mu, lam }
    }

    #[inline(always)]
    fn potential_force(phi_val: f64, mu: f64, lam: f64) -> f64 {
        // - dV/dphi = -(-mu^2 phi + lambda phi^3) = mu^2 phi - lambda phi^3
        // Optimized: phi * (mu^2 - lambda * phi^2)
        phi_val * (mu.powi(2) - lam * phi_val.powi(2))
    }

    pub fn step(&mut self) {
        let n = self.phi.len();
        
        // We need read-only access to phi for the stencil
        // and write access to forces_buffer.
        // Unsafe is not needed if we slice or iterate correctly, but standard iterators don't give neighbors easily.
        // We'll use a raw slice for the parallel iterator which is safe in Rust.
        
        let phi_slice = self.phi.as_slice().unwrap();
        let dphi_slice = self.dphi.as_slice().unwrap();
        let source_slice = self.source_j.as_slice().unwrap();
        let forces_slice = self.forces_buffer.as_slice_mut().unwrap();
        let mu = self.mu;
        let lam = self.lam;

        // Parallel computation of forces
        forces_slice.par_iter_mut().enumerate().for_each(|(i, force)| {
            // Boundary conditions (Periodic or Dirichlet? Code used 0-index for left of 0, likely clamped or periodic logic intended)
            // Original code: if i==0 { phi[0] } else { phi[i-1] } -> Effectively Neumann/Dirichlet hybrid?
            // Let's stick to the original logic: Clamped at ends.
            let left = if i == 0 { phi_slice[0] } else { phi_slice[i-1] };
            let right = if i == n-1 { phi_slice[n-1] } else { phi_slice[i+1] };
            
            let laplacian = left + right - 2.0 * phi_slice[i];
            let pot_f = Self::potential_force(phi_slice[i], mu, lam);
            let damping = -0.1 * dphi_slice[i];
            
            *force = pot_f + COUPLING_K * laplacian + source_slice[i] + damping;
        });

        // Update state (Symplectic Eulerish)
        // dphi += forces * DT
        // phi += dphi * DT
        // We can parallelize this too, or rely on ndarray's vectorized ops (which are efficient but maybe single-threaded by default unless blas is used).
        // Let's use parallel iterator for consistency and cache locality.
        
        let dphi_slice = self.dphi.as_slice_mut().unwrap();
        let phi_slice = self.phi.as_slice_mut().unwrap();
        let forces_slice = self.forces_buffer.as_slice().unwrap();
        
        dphi_slice.par_iter_mut().zip(forces_slice.par_iter()).for_each(|(v, f)| {
            *v += f * DT;
        });
        
        phi_slice.par_iter_mut().zip(dphi_slice.par_iter()).for_each(|(p, v)| {
            *p += v * DT;
        });
    }

    pub fn get_center_value(&self) -> f64 {
        self.phi[self.phi.len() / 2]
    }
}
