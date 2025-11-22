use rayon::prelude::*;
use super::noise::PinkNoiseGenerator;

/// QEC Simulation Result
pub struct QECResult {
    pub distance: usize,
    pub physical_error_rate: f64,
    pub logical_error_rate: f64,
    pub gain: f64,
}

/// Runs a QEC simulation using a Repetition Code for Phase Flip errors.
/// 
/// # Arguments
/// * `distance` - The code distance (must be odd). Number of physical qubits.
/// * `pulse_seq` - The optimized pulse sequence (timestamps).
/// * `noise_amp` - Amplitude of the pink noise.
/// * `total_time` - Total simulation duration (relative to pulse sequence length).
/// * `measure_interval` - Interval at which QEC correction is applied.
/// * `trials` - Number of Monte Carlo trials.
pub fn simulate_repetition_code(
    distance: usize,
    pulse_seq: &[usize],
    noise_amp: f64,
    total_time: usize,
    measure_interval: usize,
    trials: usize,
) -> QECResult {
    if distance % 2 == 0 {
        panic!("Distance must be odd for majority vote correction.");
    }

    // 1. Generate noise pool for all trials * all qubits
    // We need `distance` independent noise traces per trial.
    // To save memory, we process trials in batches or parallelize the trial loop 
    // and generate noise on the fly per trial.
    
        let logical_errors: usize = (0..trials).into_par_iter().map(|_| {
        // Per trial, we simulate 'distance' qubits
        // We need independent noise for each qubit
        
        // We'll use a simplified noise generation here or instantiate generators.
        // Since `PinkNoiseGenerator` might be heavy, we'll reuse the concept but 
        // maybe we can't share the generator across threads easily if it mutates.
        // Let's instantiate one per thread or use a thread-local one.
        // For simplicity/performance, let's generate 'distance' noise traces.
        
        // Note: Generating FFT based noise is expensive. 
        // If total_time is small, it's okay.
        
        let mut qubit_phases = vec![0.0; distance];
        let mut noise_gen = PinkNoiseGenerator::new(total_time);
        let mut noise_buffer = vec![0.0; total_time];
        
        let mut trial_failed = false;

        // Construct the full noise traces for all qubits
        let mut traces: Vec<Vec<f64>> = Vec::with_capacity(distance);
        for _ in 0..distance {
            noise_gen.generate(&mut noise_buffer);
            traces.push(noise_buffer.clone());
        }

        // Simulate time evolution
        // We check corrections at intervals
        let num_cycles = total_time / measure_interval;
        
        for cycle in 0..num_cycles {
            let start_idx = cycle * measure_interval;

            // Evolve each qubit
            for q in 0..distance {
                let noise = &traces[q];
                
                // Calculate phase accumulation for this interval
                // This needs to account for the pulses that happen in this interval
                // The pulse_seq is defined over the whole [0, total_time] or repeats?
                // Usually DD is repeated. Let's assume pulse_seq maps to [0, measure_interval].
                // If pulse_seq is for the whole duration, we use it directly.
                // The 'evaluate_sequence' logic applies here.
                
                let mut phase = 0.0;
                let mut sign = 1.0;
                
                // Find current pulse index based on absolute time if seq covers whole time
                // Or reset if it repeats. Let's assume repeat for QEC cycles.
                // For this demo, let's assume pulse_seq is designed for 'measure_interval'.
                
                for t_rel in 0..measure_interval {
                    let t_abs = start_idx + t_rel;
                    if t_abs >= noise.len() { break; }
                    
                    // Check for pulse
                    // If pulse_seq contains time 't_rel', flip sign
                    // We assume pulse_seq is sorted
                    if pulse_seq.contains(&t_rel) {
                         sign *= -1.0;
                    }
                    
                    phase += sign * noise[t_abs] * noise_amp * 0.01; // DT approx
                }
                
                // Update accumulated phase? 
                // In QEC, we measure syndrome. 
                // If |phase| > pi/2, it's a logical Z error (after projection).
                // We add this to the 'discrete' error count for this cycle.
                // Then we 'reset' the phase (perfect correction assumption) 
                // or keep residual (imperfect).
                // Let's assume projection measurement:
                // P(error) = sin^2(phase/2) approx for Z-basis?
                // Or simply threshold:
                qubit_phases[q] = phase;
            }

            // Measurement & Correction Step
            let mut error_count = 0;
            for q in 0..distance {
                // A phase flip has occurred if we are closer to |1> than |0> in X-basis?
                // Z-noise causes dephasing. 
                // Coherence is cos(phase). 
                // If cos(phase) < 0, we identify it as an error (flip).
                if qubit_phases[q].cos() < 0.0 {
                    error_count += 1;
                }
            }

            // Majority Vote
            if error_count > distance / 2 {
                trial_failed = true; // Logical error occurred
                break; // Stop this trial, it failed
            }
            
            // Ideal Correction: We assume we fixed the errors for the next cycle
            // (or rather, we tracked them and applied X operations).
            // So phase is effectively reset to 0 relative to the frame.
            // In reality, we don't reset the noise source, but we reset the qubit state.
        }

        if trial_failed { 1 } else { 0 }
    }).sum();

    // Calculate base physical error rate (average over single qubit without QEC)
    // We can estimate this analytically or via a quick sub-simulation.
    // Let's use the 'trials' to also estimate single qubit failure.
    // Actually, let's just run a quick single qubit sim inside the same logic?
    // Or separate. Let's separate for clarity.
    
    let physical_sim_errors: usize = (0..trials/10).into_par_iter().map(|_| {
        let mut noise_gen = PinkNoiseGenerator::new(total_time);
        let mut noise_buffer = vec![0.0; total_time];
        noise_gen.generate(&mut noise_buffer);
        
        let num_cycles = total_time / measure_interval;
        let mut failed = false;
        
        for cycle in 0..num_cycles {
            let start_idx = cycle * measure_interval;
            let mut phase = 0.0;
            let mut sign = 1.0;
             for t_rel in 0..measure_interval {
                let t_abs = start_idx + t_rel;
                if pulse_seq.contains(&t_rel) { sign *= -1.0; }
                phase += sign * noise_buffer[t_abs] * noise_amp * 0.01;
            }
            if phase.cos() < 0.0 {
                failed = true;
                break;
            }
        }
        if failed { 1 } else { 0 }
    }).sum();
    
    let phy_rate = physical_sim_errors as f64 / (trials/10) as f64;
    let log_rate = logical_errors as f64 / trials as f64;

    QECResult {
        distance,
        physical_error_rate: phy_rate,
        logical_error_rate: log_rate,
        gain: if log_rate > 0.0 { phy_rate / log_rate } else { -1.0 }, // -1 indicates infinity/perfect
    }
}

