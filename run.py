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
    household_size=config.HOUSEHOLD_SIZE,
    household_transmission_multiplier=config.HOUSEHOLD_TRANSMISSION_MULTIPLIER
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
        "current_location_type": agent.current_location_type,
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
        "current_location_type": agent.current_location_type,
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

secondary_infections = model.total_infections - config.INITIAL_INFECTED

total_household_infections = results["HouseholdInfections"].sum()
total_community_infections = results["CommunityInfections"].sum()
total_home_infections = results["HomeInfections"].sum()
total_school_infections = results["SchoolInfections"].sum()
total_work_infections = results["WorkInfections"].sum()
total_other_infections = results["OtherInfections"].sum()

if secondary_infections > 0:
    household_infection_share = total_household_infections / secondary_infections
    community_infection_share = total_community_infections / secondary_infections
    home_infection_share = total_home_infections / secondary_infections
    school_infection_share = total_school_infections / secondary_infections
    work_infection_share = total_work_infections / secondary_infections
    other_infection_share = total_other_infections / secondary_infections
else:
    household_infection_share = 0
    community_infection_share = 0
    home_infection_share = 0
    school_infection_share = 0
    work_infection_share = 0
    other_infection_share = 0

household_share_sum = (
    household_infection_share
    + community_infection_share
)

location_share_sum = (
    home_infection_share
    + school_infection_share
    + work_infection_share
    + other_infection_share
)

summary_metrics = {
    "experiment_id": experiment_id,
    "timestamp": timestamp,
    "output_dir": output_dir,
    "scenario_name": config.SCENARIO_NAME,
    "population": config.POPULATION,
    "initial_infected": config.INITIAL_INFECTED,
    "total_infections": model.total_infections,
    "secondary_infections": secondary_infections,
    "peak_active_cases": model.peak_active_cases,
    "attack_rate": attack_rate,
    "case_fatality_rate": case_fatality_rate,
    "average_rt": average_rt,
    "household_infection_share": household_infection_share,
    "community_infection_share": community_infection_share,
    "home_infection_share": home_infection_share,
    "school_infection_share": school_infection_share,
    "work_infection_share": work_infection_share,
    "other_infection_share": other_infection_share,
}

summary_df = pd.DataFrame([summary_metrics])

summary_df.to_csv(
    f"{data_dir}/summary_metrics.csv",
    index=False
)

print(
    f"Summary metrics saved to "
    f"{data_dir}/summary_metrics.csv"
)

global_summary_path = "outputs/all_experiments_summary.csv"

file_exists = os.path.exists(global_summary_path)

summary_df.to_csv(
    global_summary_path,
    mode="a",
    header=not file_exists,
    index=False
)

print(
    f"Experiment appended to "
    f"{global_summary_path}"
)

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
    file.write(f"Initial infections: {config.INITIAL_INFECTED}\n")
    file.write(f"Secondary infections: {secondary_infections}\n")
    file.write(f"Household/community share sum: {household_share_sum:.2%}\n")
    file.write(f"Location share sum: {location_share_sum:.2%}\n")
    file.write(f"Household infections: {total_household_infections}\n")
    file.write(f"Household infection share: {household_infection_share:.2%}\n")
    file.write(f"Community infections: {total_community_infections}\n")
    file.write(f"Community infection share: {community_infection_share:.2%}\n")
    file.write("\nInfections by location:\n")
    file.write(f"Home infections: {total_home_infections}\n")
    file.write(f"School infections: {total_school_infections}\n")
    file.write(f"Work infections: {total_work_infections}\n")
    file.write(f"Home infection share: {home_infection_share:.2%}\n")
    file.write(f"School infection share: {school_infection_share:.2%}\n")
    file.write(f"Work infection share: {work_infection_share:.2%}\n")
    file.write(f"Other infections: {total_other_infections}\n")
    file.write(f"Other infection share: {other_infection_share:.2%}\n")
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
plt.plot(results["HouseholdInfections"], label="Household infections")
plt.plot(results["CommunityInfections"], label="Community infections")
plt.plot(results["HomeInfections"], label="Home infections")
plt.plot(results["SchoolInfections"], label="School infections")
plt.plot(results["WorkInfections"], label="Work infections")

plt.xlabel("Step")
plt.ylabel("Number of people")
plt.title("Active and new infections")
plt.legend()
plt.tight_layout()

plt.savefig(f"{plots_dir}/infections_curve.png", dpi=300)
print("Infections plot saved to outputs/infections_curve.png")

plt.show()

plt.figure()

locations = ["Home", "School", "Work", "Other"]
location_values = [
    total_home_infections,
    total_school_infections,
    total_work_infections,
    total_other_infections,
]

plt.bar(locations, location_values)

plt.xlabel("Location")
plt.ylabel("Number of infections")
plt.title("Infections by location")
plt.tight_layout()

plt.savefig(f"{plots_dir}/location_infections_bar.png", dpi=300)
print(f"Location infections plot saved to {plots_dir}/location_infections_bar.png")

plt.show()

plt.figure()

transmission_types = ["Household", "Community"]
transmission_values = [
    total_household_infections,
    total_community_infections,
]

plt.bar(transmission_types, transmission_values)

plt.xlabel("Transmission type")
plt.ylabel("Number of infections")
plt.title("Household vs community infections")
plt.tight_layout()

plt.savefig(f"{plots_dir}/transmission_type_bar.png", dpi=300)
print(
    f"Transmission type plot saved to "
    f"{plots_dir}/transmission_type_bar.png"
)

plt.show()

plt.figure()

location_share_labels = ["Home", "School", "Work", "Other"]

location_share_values = [
    home_infection_share * 100,
    school_infection_share * 100,
    work_infection_share * 100,
    other_infection_share * 100,
]

plt.bar(location_share_labels, location_share_values)

plt.xlabel("Location")
plt.ylabel("Share of infections (%)")
plt.title("Infection share by location")
plt.ylim(0, 100)

plt.tight_layout()

plt.savefig(
    f"{plots_dir}/location_infection_share_bar.png",
    dpi=300
)

print(
    f"Location infection share plot saved to "
    f"{plots_dir}/location_infection_share_bar.png"
)

plt.show()

plt.figure()

pie_labels = ["Home", "School", "Work", "Other"]

pie_values = [
    home_infection_share,
    school_infection_share,
    work_infection_share,
    other_infection_share,
]

plt.pie(
    pie_values,
    labels=pie_labels,
    autopct="%1.1f%%"
)

plt.title("Infection share by location")

plt.savefig(
    f"{plots_dir}/location_infection_share_pie.png",
    dpi=300
)

print(
    f"Location infection share pie chart saved to "
    f"{plots_dir}/location_infection_share_pie.png"
)

plt.show()

plt.figure()

transmission_share_labels = ["Household", "Community"]

transmission_share_values = [
    household_infection_share,
    community_infection_share,
]

plt.pie(
    transmission_share_values,
    labels=transmission_share_labels,
    autopct="%1.1f%%"
)

plt.title("Household vs community infection share")

plt.savefig(
    f"{plots_dir}/transmission_type_share_pie.png",
    dpi=300
)

print(
    f"Transmission type share pie chart saved to "
    f"{plots_dir}/transmission_type_share_pie.png"
)

plt.show()