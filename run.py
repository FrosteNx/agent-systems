import config
from datetime import datetime
from pathlib import Path
from plots import generate_all_plots
from reports import (
    build_summary_metrics,
    save_full_simulation_summary,
    log_summary_metrics,
)
from io_utils import (
    get_next_experiment_id,
    create_output_dirs,
    save_parameters,
    setup_logging,
    save_all_outputs,
)
from metrics import calculate_all_metrics
from simulation_runner import run_simulation
from model_factory import create_model
from dashboard import generate_dashboard

def main():
    model = create_model()

    steps = config.SIMULATION_STEPS

    print(model.count_age_groups())

    Path("outputs").mkdir(exist_ok=True)

    global_summary_path = "outputs/all_experiments_summary.csv"

    experiment_id = get_next_experiment_id(global_summary_path)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    output_dir, plots_dir, data_dir, logs_dir = create_output_dirs(
        experiment_id,
        timestamp
    )

    log_file = f"{logs_dir}/simulation.log"

    setup_logging(log_file)

    save_parameters(
        data_dir,
        experiment_id,
        timestamp
    )

    actual_steps, execution_time_seconds = run_simulation(
        model,
        steps
    )

    results = model.datacollector.get_model_vars_dataframe()

    print("Peak active cases:", model.peak_active_cases)

    final_counts = model.count_states()

    metrics = calculate_all_metrics(
        model,
        results,
        final_counts,
        actual_steps,
        config.POPULATION,
        config.INITIAL_INFECTED,
    )

    summary_metrics = build_summary_metrics(
        config,
        model,
        metrics,
        experiment_id,
        timestamp,
        output_dir,
        log_file,
    )

    log_summary_metrics(summary_metrics)

    save_all_outputs(
        model,
        results,
        summary_metrics,
        data_dir,
        global_summary_path
    )

    save_full_simulation_summary(
        config,
        model,
        metrics,
        experiment_id,
        timestamp,
        actual_steps,
        final_counts,
        execution_time_seconds,
        log_file,
        data_dir,
    )

    generate_all_plots(
        results,
        plots_dir,
        model,
        metrics,
    )

    generate_dashboard(
        output_dir,
        summary_metrics
    )

if __name__ == "__main__":
    main()
