pub mod engine {
    pub mod core;
    pub mod noise;
    pub mod optimizer;
    pub mod benchmark;
    pub mod qec;
}

pub use engine::core::QSFEngine;
pub use engine::noise::generate_pink_noise;
pub use engine::optimizer::run_pulse_optimizer;
pub use engine::benchmark::{run_decoupling_benchmark, run_sweep_benchmark};
pub use engine::qec::simulate_repetition_code;

