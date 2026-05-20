from model import FluModel
import matplotlib.pyplot as plt
import config
import os
from datetime import datetime
import json
from pathlib import Path
import pandas as pd


model = FluModel(
    width=config.WIDTH,
    height=config.HEIGHT,
    population=config.POPULATION,
    initial_infected=config.INITIAL_INFECTED,
    infection_probability=config.INFECTION_PROBABILITY,
    recovery_time=config.RECOVERY_TIME,
    incubation_time=config.INCUBATION_TIME,
    vaccination_rate=config.VACCINATION_RATE,
    child_rate=config.CHILD_RATE,
    senior_rate=config.SENIOR_RATE,
    child_mortality_rate=config.CHILD_MORTALITY_RATE,
    adult_mortality_rate=config.ADULT_MORTALITY_RATE,
    senior_mortality_rate=config.SENIOR_MORTALITY_RATE,
    asymptomatic_rate=config.ASYMPTOMATIC_RATE,
    asymptomatic_transmission_multiplier=config.ASYMPTOMATIC_TRANSMISSION_MULTIPLIER,
    isolation_rate=config.ISOLATION_RATE,
    vaccine_effectiveness=config.VACCINE_EFFECTIVENESS,
    random_seed=config.RANDOM_SEED,
    household_size=config.HOUSEHOLD_SIZE
)

steps = config.SIMULATION_STEPS

print(model.count_age_groups())

Path("outputs").mkdir(exist_ok=True)

existing_runs = sorted(Path("outputs").glob("experiment_*"))
experiment_id = len(existing_runs) + 1

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

output_dir = (
    f"outputs/experiment_{experiment_id:03d}_{timestamp}"
)
plots_dir = f"{output_dir}/plots"
data_dir = f"{output_dir}/data"

os.makedirs(plots_dir, exist_ok=True)
os.makedirs(data_dir, exist_ok=True)

initial_population_data = []

for agent in model.schedule.agents:
    initial_population_data.append({
        "agent_id": agent.unique_id,
        "state": agent.state,
        "age_group": agent.age_group,
        "x": agent.pos[0],
        "y": agent.pos[1],
        "household_id": agent.household_id,
        "home_x": agent.home[0],
        "home_y": agent.home[1],
        "work_x": agent.work[0],
        "work_y": agent.work[1],
    })

initial_population_df = pd.DataFrame(initial_population_data)

initial_population_df.to_csv(
    f"{data_dir}/initial_population.csv",
    index=False
)

print(f"Initial population saved to {data_dir}/initial_population.csv")

with open(f"{data_dir}/parameters.txt", "w") as file:
    file.write("Simulation parameters\n")
    file.write("=====================\n\n")

    for name in dir(config):
        if name.isupper():
            value = getattr(config, name)
            file.write(f"{name}: {value}\n")

print("Parameters saved to outputs/parameters.txt")

parameters = {}

parameters["EXPERIMENT_ID"] = experiment_id
parameters["TIMESTAMP"] = timestamp

for name in dir(config):
    if name.isupper():
        parameters[name] = getattr(config, name)

with open(f"{data_dir}/parameters.json", "w") as file:
    json.dump(parameters, file, indent=4)

print(f"Parameters saved to {data_dir}/parameters.json")

actual_steps = 0

for i in range(steps):
    model.step()
    actual_steps = i + 1
    counts = model.count_states()

    print(f"Step {i}: {counts}")

    active_cases = (
        counts["Exposed"]
        + counts["Infected"]
        + counts["Asymptomatic"]
    )

    if active_cases == 0:
        print(f"Epidemic ended at step {i}")
        break

results = model.datacollector.get_model_vars_dataframe()

results.to_csv(f"{data_dir}/simulation_results.csv", index_label="Step")
print("Results saved to outputs/simulation_results.csv")

print("Peak active cases:", model.peak_active_cases)

final_counts = model.count_states()

population_data = []

for agent in model.schedule.agents:
    population_data.append({
        "agent_id": agent.unique_id,
        "state": agent.state,
        "age_group": agent.age_group,
        "x": agent.pos[0],
        "y": agent.pos[1],
        "household_id": agent.household_id,
    })

population_df = pd.DataFrame(population_data)

population_df.to_csv(
    f"{data_dir}/final_population.csv",
    index=False
)

print(
    f"Final population saved to "
    f"{data_dir}/final_population.csv"
)

attack_rate = model.total_infections / config.POPULATION

dead_count = final_counts["Dead"]

if model.total_infections > 0:
    case_fatality_rate = dead_count / model.total_infections
else:
    case_fatality_rate = 0

average_rt = results["Rt"].mean()

with open(f"{data_dir}/simulation_summary.txt", "w") as file:
    file.write("Flu simulation summary\n")
    file.write(f"Experiment ID: {experiment_id}\n")
    file.write(f"Timestamp: {timestamp}\n\n")
    file.write(f"Scenario: {config.SCENARIO_NAME}\n\n")
    file.write("======================\n\n")
    file.write(f"Population: {config.POPULATION}\n")
    file.write(f"Max steps: {config.SIMULATION_STEPS}\n")
    file.write(f"Actual steps: {actual_steps}\n")
    file.write(f"Peak active cases: {model.peak_active_cases}\n\n")
    file.write(f"Total infections: {model.total_infections}\n")
    file.write(f"Attack rate: {attack_rate:.2%}\n")
    file.write(f"Case fatality rate: {case_fatality_rate:.2%}\n")
    file.write(f"Average Rt: {average_rt:.2f}\n")

    file.write("Final state counts:\n")
    for state, count in final_counts.items():
        file.write(f"{state}: {count}\n")

print("Summary saved to outputs/simulation_summary.txt")

plt.plot(results["Susceptible"], label="Susceptible")
plt.plot(results["Exposed"], label="Exposed")
plt.plot(results["Infected"], label="Infected")
plt.plot(results["Asymptomatic"], label="Asymptomatic")
plt.plot(results["Recovered"], label="Recovered")
plt.plot(results["Dead"], label="Dead")
plt.plot(results["Vaccinated"], label="Vaccinated")

plt.xlabel("Step")
plt.ylabel("Number of people")
plt.title("Flu epidemic simulation")
plt.legend()
plt.tight_layout()

plt.savefig(f"{plots_dir}/epidemic_curve.png", dpi=300)

plt.show()


plt.figure()

plt.plot(results["Rt"], label="Rt")
plt.axhline(y=1, linestyle="--", label="Rt = 1")

plt.xlabel("Step")
plt.ylabel("Rt")
plt.title("Effective reproduction number")
plt.legend()
plt.tight_layout()

plt.savefig(f"{plots_dir}/rt_curve.png", dpi=300)
print("Rt plot saved to outputs/rt_curve.png")

plt.show()


plt.figure()

plt.plot(results["ActiveCases"], label="Active cases")
plt.plot(results["NewInfections"], label="New infections")

plt.xlabel("Step")
plt.ylabel("Number of people")
plt.title("Active and new infections")
plt.legend()
plt.tight_layout()

plt.savefig(f"{plots_dir}/infections_curve.png", dpi=300)
print("Infections plot saved to outputs/infections_curve.png")

plt.show()