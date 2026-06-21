import pandas as pd
import os
import json
import config
import logging

def save_dataframe(df, path, index=False, index_label=None):
    df.to_csv(
        path,
        index=index,
        index_label=index_label
    )
    print(f"Saved: {path}")

def build_population_dataframe(model, include_home_and_work=False):
    population_data = []

    for agent in model.schedule.agents:
        row = {
            "agent_id": agent.unique_id,
            "state": agent.state,
            "age_group": agent.age_group,
            "x": agent.pos[0],
            "y": agent.pos[1],
            "household_id": agent.household_id,
            "current_location_type": agent.current_location_type,
        }

        if include_home_and_work:
            row["home_x"] = agent.home[0]
            row["home_y"] = agent.home[1]
            row["work_x"] = agent.work[0]
            row["work_y"] = agent.work[1]

        population_data.append(row)

    return pd.DataFrame(population_data)

def append_global_summary(summary_df, global_summary_path):
    file_exists = os.path.exists(global_summary_path)

    summary_df.to_csv(
        global_summary_path,
        mode="a",
        header=not file_exists,
        index=False
    )

    print(f"Experiment appended to {global_summary_path}")

def get_next_experiment_id(global_summary_path):
    if os.path.exists(global_summary_path):
        previous_summary = pd.read_csv(global_summary_path)

        if len(previous_summary) > 0:
            return int(previous_summary["experiment_id"].max()) + 1

    return 1

def create_output_dirs(experiment_id, timestamp):
    output_dir = f"outputs/experiment_{experiment_id:03d}_{timestamp}"
    plots_dir = f"{output_dir}/plots"
    data_dir = f"{output_dir}/data"
    logs_dir = f"{output_dir}/logs"

    os.makedirs(plots_dir, exist_ok=True)
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)

    return output_dir, plots_dir, data_dir, logs_dir

def save_parameters(data_dir, experiment_id, timestamp):
    with open(f"{data_dir}/parameters.txt", "w") as file:
        file.write("Simulation parameters\n")
        file.write("=====================\n\n")

        for name in dir(config):
            if name.isupper():
                value = getattr(config, name)
                file.write(f"{name}: {value}\n")

    parameters = {
        "EXPERIMENT_ID": experiment_id,
        "TIMESTAMP": timestamp,
    }

    for name in dir(config):
        if name.isupper():
            parameters[name] = getattr(config, name)

    with open(f"{data_dir}/parameters.json", "w") as file:
        json.dump(parameters, file, indent=4)

    print(f"Parameters saved to {data_dir}/parameters.json")

def setup_logging(log_file):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        force=True
    )

def save_summary_metrics(summary_metrics, data_dir, global_summary_path):
    summary_df = pd.DataFrame([summary_metrics])

    save_dataframe(
        summary_df,
        f"{data_dir}/summary_metrics.csv"
    )

    append_global_summary(
        summary_df,
        global_summary_path
    )

    return summary_df

def save_simulation_data(
    model,
    results,
    data_dir,
):
    initial_population_df = build_population_dataframe(
        model,
        include_home_and_work=True
    )

    save_dataframe(
        initial_population_df,
        f"{data_dir}/initial_population.csv"
    )

    save_dataframe(
        results,
        f"{data_dir}/simulation_results.csv",
        index=True,
        index_label="Step"
    )

    final_population_df = build_population_dataframe(model)

    save_dataframe(
        final_population_df,
        f"{data_dir}/final_population.csv"
    )

def save_all_outputs(
    model,
    results,
    summary_metrics,
    data_dir,
    global_summary_path,
):
    save_simulation_data(
        model,
        results,
        data_dir
    )

    save_summary_metrics(
        summary_metrics,
        data_dir,
        global_summary_path
    )