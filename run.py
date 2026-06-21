import config
import pandas as pd

from copy import deepcopy
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
from scenarios import SCENARIOS


def get_base_config():
    """
    Store the original config values so each scenario starts from the same baseline.
    """
    base = {}

    for name in dir(config):
        if name.isupper():
            base[name] = deepcopy(getattr(config, name))

    return base


def restore_base_config(base_config):
    """
    Restore config.py values before applying a new scenario.
    This prevents one scenario from leaking settings into the next one.
    """
    for name, value in base_config.items():
        setattr(config, name, deepcopy(value))


def apply_scenario(scenario, seed):
    """
    Apply scenario-specific overrides and set the seed for this run.
    """
    overrides = scenario.get("overrides", {})

    for name, value in overrides.items():
        setattr(config, name, value)

    config.RANDOM_SEED = seed

    if "SCENARIO_NAME" not in overrides:
        config.SCENARIO_NAME = scenario["name"]


def run_single_experiment(
    scenario,
    scenario_index,
    run_index,
    seed,
    batch_id,
    batch_dir,
    global_summary_path,
):
    print("")
    print("=" * 80)
    print(f"Scenario {scenario_index}: {scenario['name']}")
    print(f"Run {run_index}")
    print(f"Seed: {seed}")
    print("=" * 80)

    model = create_model()
    steps = config.SIMULATION_STEPS

    print(model.count_age_groups())

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

    summary_metrics["batch_id"] = batch_id
    summary_metrics["scenario_index"] = scenario_index
    summary_metrics["scenario_run"] = run_index
    summary_metrics["random_seed"] = seed
    summary_metrics["scenario_description"] = scenario.get("description", "")

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

    return summary_metrics


def save_batch_outputs(batch_results, batch_dir):
    if not batch_results:
        print("No batch results to save.")
        return

    batch_df = pd.DataFrame(batch_results)

    batch_summary_path = batch_dir / "batch_summary.csv"
    batch_df.to_csv(batch_summary_path, index=False)

    print(f"Saved batch summary: {batch_summary_path}")

    excluded_numeric_columns = {
        "experiment_id",
        "scenario_index",
        "scenario_run",
        "random_seed",
    }

    numeric_columns = [
        column
        for column in batch_df.select_dtypes(include="number").columns
        if column not in excluded_numeric_columns
    ]

    if numeric_columns:
        aggregate_df = (
            batch_df
            .groupby("scenario_name")[numeric_columns]
            .agg(["mean", "std", "min", "max"])
        )

        aggregate_df.columns = [
            f"{metric}_{stat}"
            for metric, stat in aggregate_df.columns
        ]

        aggregate_df = aggregate_df.reset_index()

        aggregate_path = batch_dir / "batch_aggregate_by_scenario.csv"
        aggregate_df.to_csv(aggregate_path, index=False)

        print(f"Saved batch aggregate: {aggregate_path}")


def main():
    Path("outputs").mkdir(exist_ok=True)

    batch_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    batch_id = f"batch_{batch_timestamp}"
    batch_dir = Path("outputs") / batch_id
    batch_dir.mkdir(parents=True, exist_ok=True)

    global_summary_path = "outputs/all_experiments_summary.csv"

    runs_per_scenario = getattr(config, "RUNS_PER_SCENARIO", 10)
    base_random_seed = getattr(config, "BASE_RANDOM_SEED", 42)

    base_config = get_base_config()

    batch_results = []

    for scenario_index, scenario in enumerate(SCENARIOS, start=1):
        for run_index in range(1, runs_per_scenario + 1):
            seed = base_random_seed + ((scenario_index - 1) * runs_per_scenario) + (run_index - 1)

            restore_base_config(base_config)
            apply_scenario(scenario, seed)

            summary_metrics = run_single_experiment(
                scenario=scenario,
                scenario_index=scenario_index,
                run_index=run_index,
                seed=seed,
                batch_id=batch_id,
                batch_dir=batch_dir,
                global_summary_path=global_summary_path,
            )

            batch_results.append(summary_metrics)

            save_batch_outputs(batch_results, batch_dir)

    print("")
    print("=" * 80)
    print("Batch finished.")
    print(f"Scenarios: {len(SCENARIOS)}")
    print(f"Runs per scenario: {runs_per_scenario}")
    print(f"Total runs: {len(SCENARIOS) * runs_per_scenario}")
    print(f"Batch directory: {batch_dir}")
    print("=" * 80)


if __name__ == "__main__":
    main()