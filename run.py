import config
from datetime import datetime
from pathlib import Path
import pandas as pd
import logging
from plots import generate_all_plots
from reports import (
    save_simulation_summary,
    build_summary_metrics,
    build_simulation_summary,
    build_summary_lines,
)
from io_utils import (
    save_dataframe,
    build_population_dataframe,
    append_global_summary,
    get_next_experiment_id,
    create_output_dirs,
    save_parameters,
    setup_logging,
)
from metrics import calculate_all_metrics
from simulation_runner import run_simulation
from model_factory import create_model

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

logging.info("Simulation started")
logging.info(f"Scenario: {config.SCENARIO_NAME}")
logging.info(f"Population: {config.POPULATION}")

initial_population_df = build_population_dataframe(
    model,
    include_home_and_work=True
)

save_dataframe(
    initial_population_df,
    f"{data_dir}/initial_population.csv"
)

save_parameters(
    data_dir,
    experiment_id,
    timestamp
)

actual_steps, execution_time_seconds = run_simulation(
    model,
    steps
)

logging.info("Simulation finished")
logging.info(
    f"Execution time: "
    f"{execution_time_seconds:.2f} seconds"
)

results = model.datacollector.get_model_vars_dataframe()

save_dataframe(
    results,
    f"{data_dir}/simulation_results.csv",
    index=True,
    index_label="Step"
)

print("Peak active cases:", model.peak_active_cases)

final_counts = model.count_states()

population_df = build_population_dataframe(model)

save_dataframe(
    population_df,
    f"{data_dir}/final_population.csv"
)

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

logging.info("Final summary metrics:")

for key, value in summary_metrics.items():
    logging.info(f"{key}: {value}")

summary_df = pd.DataFrame([summary_metrics])

save_dataframe(
    summary_df,
    f"{data_dir}/summary_metrics.csv"
)

global_summary_path = "outputs/all_experiments_summary.csv"

append_global_summary(
    summary_df,
    global_summary_path
)

summary_lines = build_summary_lines(
    config,
    model,
    metrics,
    experiment_id,
    timestamp,
    actual_steps,
    final_counts,
    execution_time_seconds,
    log_file,
)

summary_text = build_simulation_summary(summary_lines)

save_simulation_summary(
    f"{data_dir}/simulation_summary.txt",
    summary_text
)

generate_all_plots(
    results,
    plots_dir,
    model,
    metrics["total_home_infections"],
    metrics["total_school_infections"],
    metrics["total_work_infections"],
    metrics["total_other_infections"],
    metrics["total_household_infections"],
    metrics["total_community_infections"],
    metrics["home_infection_share"],
    metrics["school_infection_share"],
    metrics["work_infection_share"],
    metrics["other_infection_share"],
    metrics["household_infection_share"],
    metrics["community_infection_share"],
    metrics["child_attack_rate"],
    metrics["adult_attack_rate"],
    metrics["senior_attack_rate"],
    metrics["child_death_rate"],
    metrics["adult_death_rate"],
    metrics["senior_death_rate"],
    metrics["child_vaccination_coverage"],
    metrics["adult_vaccination_coverage"],
    metrics["senior_vaccination_coverage"],
)
