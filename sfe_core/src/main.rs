use clap::{Parser, Subcommand};
use std::time::Instant;
use sfe_core::{run_pulse_optimizer, run_sweep_benchmark};
use sfe_core::engine::core::QSFEngine; // Direct access if needed or wrap in lib
use std::fs::File;
use std::io::Write;
use indicatif::{ProgressBar, ProgressStyle};

#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand, Debug)]
enum Commands {
    /// Field Dynamics Simulation
    Dynamics {
        #[arg(short, long, default_value_t = 100_000)]
        size: usize,
        #[arg(short, long, default_value_t = 5_000)]
        steps: usize,
        #[arg(short, long, default_value = "sfe_output.csv")]
        output: String,
    },
    /// Quantum Noise Simulation
    QuantumNoise {
        #[arg(short, long, default_value_t = 10_000)]
        steps: usize,
        #[arg(short, long, default_value_t = 1000)]
        trials: usize,
        #[arg(short, long, default_value = "quantum_noise.csv")]
        output: String,
    },
    /// Decoupling Benchmark (Single Point)
    DecouplingBenchmark {
        #[arg(short, long, default_value_t = 10_000)]
        steps: usize,
        #[arg(short, long, default_value_t = 1000)]
        trials: usize,
        #[arg(short, long, default_value = "decoupling_result.csv")]
        output: String,
    },
    /// SFE-Genetic Pulse Optimizer
    PulseOptimizer {
        #[arg(short, long, default_value_t = 2000)]
        steps: usize,
        #[arg(short, long, default_value_t = 50)]
        pulses: usize,
        #[arg(short, long, default_value_t = 50)]
        generations: usize,
    },
    /// [NEW] Comprehensive Parameter Sweep (Heatmap Data)
    Sweep {
        #[arg(short, long, default_value = "sweep_results.csv")]
        output: String,
    }
}

fn main() {
    let args = Args::parse();
    println!("==========================================");
    println!("   SFE Commercial Engine v1.3 (Library)   ");
    println!("==========================================");

    let start_time = Instant::now();

    match args.command {
        Commands::Dynamics { size, steps, output } => {
             println!("Mode: Field Dynamics Simulation");
             let mut engine = QSFEngine::new(size);
             let pb = ProgressBar::new(steps as u64);
             pb.set_style(ProgressStyle::default_bar().template("{spinner:.green} {bar:40} {pos}/{len}").unwrap());
             let mut history = Vec::with_capacity(steps);
             for t in 0..steps {
                 engine.step();
                 if t % 10 == 0 { history.push((t, engine.get_center_value())); }
                 pb.inc(1);
             }
             pb.finish();
             let mut file = File::create(&output).unwrap();
             writeln!(file, "TimeStep,CenterPhi").unwrap();
             for (t, v) in history { writeln!(file, "{},{}", t, v).unwrap(); }
        },
        Commands::QuantumNoise { .. } => {
            println!("(Deprecated) Use Sweep for comprehensive analysis.");
        },
        Commands::DecouplingBenchmark { .. } => {
            println!("(Deprecated) Use Sweep for comprehensive analysis.");
        },
        Commands::PulseOptimizer { steps, pulses, generations } => {
            // Default noise amp for single run
            let (_, udd, sfe) = run_pulse_optimizer(steps, pulses, generations, 0.15);
            println!("Final Result -> UDD: {:.4}, SFE: {:.4}", udd, sfe);
        },
        Commands::Sweep { output } => {
            run_sweep_benchmark(output);
        }
    }

    println!("Total Time: {:.2}s", start_time.elapsed().as_secs_f64());
}
