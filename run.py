from model import FluModel
import matplotlib.pyplot as plt
import config
import os
from datetime import datetime
import json
from pathlib import Path
import pandas as pd
import logging
import time
from plots import generate_all_plots

def save_dataframe(df, path, index=False, index_label=None):
    df.to_csv(
        path,
        index=index,
        index_label=index_label
    )
    print(f"Saved: {path}")

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
    household_transmission_multiplier=config.HOUSEHOLD_TRANSMISSION_MULTIPLIER,
    senior_mobility=config.SENIOR_MOBILITY,
    child_mobility=config.CHILD_MOBILITY,
    work_closed=config.WORK_CLOSED,
    lockdown=config.LOCKDOWN,
    lockdown_mobility=config.LOCKDOWN_MOBILITY,
    auto_lockdown=config.AUTO_LOCKDOWN,
    lockdown_threshold=config.LOCKDOWN_THRESHOLD,
    auto_lockdown_release=config.AUTO_LOCKDOWN_RELEASE,
    lockdown_release_threshold=config.LOCKDOWN_RELEASE_THRESHOLD,
    masks_enabled=config.MASKS_ENABLED,
    mask_transmission_reduction=config.MASK_TRANSMISSION_REDUCTION,
    mask_compliance=config.MASK_COMPLIANCE,
    quarantine_enabled=config.QUARANTINE_ENABLED,
    quarantine_compliance=config.QUARANTINE_COMPLIANCE,
    testing_rate=config.TESTING_RATE,
    detected_transmission_multiplier=config.DETECTED_TRANSMISSION_MULTIPLIER,
    auto_school_closure=config.AUTO_SCHOOL_CLOSURE,
    school_closure_threshold=config.SCHOOL_CLOSURE_THRESHOLD,
    auto_school_reopen=config.AUTO_SCHOOL_REOPEN,
    school_reopen_threshold=config.SCHOOL_REOPEN_THRESHOLD,
    auto_mask_compliance=config.AUTO_MASK_COMPLIANCE,
    mask_compliance_threshold=config.MASK_COMPLIANCE_THRESHOLD,
    high_mask_compliance=config.HIGH_MASK_COMPLIANCE,
    auto_mask_relaxation=config.AUTO_MASK_RELAXATION,
    mask_relaxation_threshold=config.MASK_RELAXATION_THRESHOLD,
    auto_testing_rate=config.AUTO_TESTING_RATE,
    testing_rate_threshold=config.TESTING_RATE_THRESHOLD,
    high_testing_rate=config.HIGH_TESTING_RATE,
    auto_testing_relaxation=config.AUTO_TESTING_RELAXATION,
    testing_relaxation_threshold=config.TESTING_RELAXATION_THRESHOLD,
    auto_quarantine_compliance=config.AUTO_QUARANTINE_COMPLIANCE,
    quarantine_compliance_threshold=config.QUARANTINE_COMPLIANCE_THRESHOLD,
    high_quarantine_compliance=config.HIGH_QUARANTINE_COMPLIANCE,
    auto_quarantine_relaxation=config.AUTO_QUARANTINE_RELAXATION,
    quarantine_relaxation_threshold=config.QUARANTINE_RELAXATION_THRESHOLD,
    auto_work_closure=config.AUTO_WORK_CLOSURE,
    work_closure_threshold=config.WORK_CLOSURE_THRESHOLD,
    auto_work_reopen=config.AUTO_WORK_REOPEN,
    work_reopen_threshold=config.WORK_REOPEN_THRESHOLD,
    auto_senior_mobility_reduction=config.AUTO_SENIOR_MOBILITY_REDUCTION,
    senior_mobility_threshold=config.SENIOR_MOBILITY_THRESHOLD,
    low_senior_mobility=config.LOW_SENIOR_MOBILITY,
    auto_senior_mobility_restore=config.AUTO_SENIOR_MOBILITY_RESTORE,
    senior_mobility_restore_threshold=config.SENIOR_MOBILITY_RESTORE_THRESHOLD,
    auto_child_mobility_reduction=config.AUTO_CHILD_MOBILITY_REDUCTION,
    child_mobility_threshold=config.CHILD_MOBILITY_THRESHOLD,
    low_child_mobility=config.LOW_CHILD_MOBILITY,
    auto_child_mobility_restore=config.AUTO_CHILD_MOBILITY_RESTORE,
    child_mobility_restore_threshold=config.CHILD_MOBILITY_RESTORE_THRESHOLD,
    auto_vaccination_campaign=config.AUTO_VACCINATION_CAMPAIGN,
    vaccination_campaign_threshold=config.VACCINATION_CAMPAIGN_THRESHOLD,
    daily_vaccination_capacity=config.DAILY_VACCINATION_CAPACITY,
)

steps = config.SIMULATION_STEPS

print(model.count_age_groups())

Path("outputs").mkdir(exist_ok=True)

global_summary_path = "outputs/all_experiments_summary.csv"

if os.path.exists(global_summary_path):
    previous_summary = pd.read_csv(global_summary_path)

    if len(previous_summary) > 0:
        experiment_id = int(previous_summary["experiment_id"].max()) + 1
    else:
        experiment_id = 1
else:
    experiment_id = 1

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

output_dir = (
    f"outputs/experiment_{experiment_id:03d}_{timestamp}"
)
plots_dir = f"{output_dir}/plots"
data_dir = f"{output_dir}/data"

os.makedirs(plots_dir, exist_ok=True)
os.makedirs(data_dir, exist_ok=True)

logs_dir = f"{output_dir}/logs"
os.makedirs(logs_dir, exist_ok=True)
log_file = f"{logs_dir}/simulation.log"

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logging.info("Simulation started")
logging.info(f"Scenario: {config.SCENARIO_NAME}")
logging.info(f"Population: {config.POPULATION}")

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

save_dataframe(
    initial_population_df,
    f"{data_dir}/initial_population.csv"
)

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

start_time = time.time()

for i in range(steps):
    model.step()
    actual_steps = i + 1
    counts = model.count_states()

    logging.info(
        f"Step {i} | "
        f"S={counts['Susceptible']} "
        f"E={counts['Exposed']} "
        f"I={counts['Infected']} "
        f"A={counts['Asymptomatic']} "
        f"R={counts['Recovered']} "
        f"D={counts['Dead']}"
    )

    print(f"Step {i}: {counts}")

    active_cases = (
        counts["Exposed"]
        + counts["Infected"]
        + counts["Asymptomatic"]
    )

    if active_cases == 0:
        print(f"Epidemic ended at step {i}")
        break

execution_time_seconds = time.time() - start_time

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

save_dataframe(
    population_df,
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
total_quarantined_agents = results["QuarantinedAgents"].sum()

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

total_mask_protected_contacts = results["MaskProtectedContacts"].sum()

if model.total_infections > 0:
    detection_rate = (
        model.total_detected_infections
        / model.total_infections
    )
else:
    detection_rate = 0

if model.total_infections > 0:
    quarantine_rate = (
        model.total_quarantined_people
        / model.total_infections
    )
else:
    quarantine_rate = 0

undetected_infections = (
    model.total_infections
    - model.total_detected_infections
)

if model.total_infections > 0:
    undetected_rate = (
        undetected_infections
        / model.total_infections
    )
else:
    undetected_rate = 0

if model.total_infections > 0:
    asymptomatic_rate_observed = (
        model.total_asymptomatic_infections
        / model.total_infections
    )
else:
    asymptomatic_rate_observed = 0

age_counts = model.count_age_groups()

vaccinated_by_age = {
    "child": 0,
    "adult": 0,
    "senior": 0,
}

for agent in model.schedule.agents:
    if agent.state == "Vaccinated":
        vaccinated_by_age[agent.age_group] += 1

child_vaccination_coverage = (
    vaccinated_by_age["child"] / age_counts["child"]
    if age_counts["child"] > 0 else 0
)

adult_vaccination_coverage = (
    vaccinated_by_age["adult"] / age_counts["adult"]
    if age_counts["adult"] > 0 else 0
)

senior_vaccination_coverage = (
    vaccinated_by_age["senior"] / age_counts["senior"]
    if age_counts["senior"] > 0 else 0
)

child_attack_rate = (
    model.child_infections / age_counts["child"]
    if age_counts["child"] > 0 else 0
)

adult_attack_rate = (
    model.adult_infections / age_counts["adult"]
    if age_counts["adult"] > 0 else 0
)

senior_attack_rate = (
    model.senior_infections / age_counts["senior"]
    if age_counts["senior"] > 0 else 0
)

child_death_rate = (
    model.child_deaths / age_counts["child"]
    if age_counts["child"] > 0 else 0
)

adult_death_rate = (
    model.adult_deaths / age_counts["adult"]
    if age_counts["adult"] > 0 else 0
)

senior_death_rate = (
    model.senior_deaths / age_counts["senior"]
    if age_counts["senior"] > 0 else 0
)

if (
    model.lockdown_start_step is not None
    and model.lockdown_end_step is not None
):
    lockdown_duration = (
        model.lockdown_end_step
        - model.lockdown_start_step
    )
elif model.lockdown_start_step is not None:
    lockdown_duration = actual_steps - model.lockdown_start_step
else:
    lockdown_duration = 0

if (
    model.school_closure_start_step is not None
    and model.school_closure_end_step is not None
):
    school_closure_duration = (
        model.school_closure_end_step
        - model.school_closure_start_step
    )
elif model.school_closure_start_step is not None:
    school_closure_duration = actual_steps - model.school_closure_start_step
else:
    school_closure_duration = 0
if (
    model.mask_compliance_start_step is not None
    and model.mask_compliance_end_step is not None
):
    mask_compliance_duration = (
        model.mask_compliance_end_step
        - model.mask_compliance_start_step
    )
elif model.mask_compliance_start_step is not None:
    mask_compliance_duration = (
        actual_steps
        - model.mask_compliance_start_step
    )
else:
    mask_compliance_duration = 0

if (
    model.testing_rate_start_step is not None
    and model.testing_rate_end_step is not None
):
    testing_rate_duration = (
        model.testing_rate_end_step
        - model.testing_rate_start_step
    )
elif model.testing_rate_start_step is not None:
    testing_rate_duration = actual_steps - model.testing_rate_start_step
else:
    testing_rate_duration = 0


if (
    model.quarantine_compliance_start_step is not None
    and model.quarantine_compliance_end_step is not None
):
    quarantine_compliance_duration = (
        model.quarantine_compliance_end_step
        - model.quarantine_compliance_start_step
    )
elif model.quarantine_compliance_start_step is not None:
    quarantine_compliance_duration = (
        actual_steps
        - model.quarantine_compliance_start_step
    )
else:
    quarantine_compliance_duration = 0


if (
    model.work_closure_start_step is not None
    and model.work_closure_end_step is not None
):
    work_closure_duration = (
        model.work_closure_end_step
        - model.work_closure_start_step
    )
elif model.work_closure_start_step is not None:
    work_closure_duration = actual_steps - model.work_closure_start_step
else:
    work_closure_duration = 0


if (
    model.senior_mobility_reduction_start_step is not None
    and model.senior_mobility_reduction_end_step is not None
):
    senior_mobility_reduction_duration = (
        model.senior_mobility_reduction_end_step
        - model.senior_mobility_reduction_start_step
    )
elif model.senior_mobility_reduction_start_step is not None:
    senior_mobility_reduction_duration = (
        actual_steps
        - model.senior_mobility_reduction_start_step
    )
else:
    senior_mobility_reduction_duration = 0


if (
    model.child_mobility_reduction_start_step is not None
    and model.child_mobility_reduction_end_step is not None
):
    child_mobility_reduction_duration = (
        model.child_mobility_reduction_end_step
        - model.child_mobility_reduction_start_step
    )
elif model.child_mobility_reduction_start_step is not None:
    child_mobility_reduction_duration = (
        actual_steps
        - model.child_mobility_reduction_start_step
    )
else:
    child_mobility_reduction_duration = 0


if (
    model.vaccination_campaign_start_step is not None
    and model.vaccination_campaign_end_step is not None
):
    vaccination_campaign_duration = (
        model.vaccination_campaign_end_step
        - model.vaccination_campaign_start_step
    )
elif model.vaccination_campaign_start_step is not None:
    vaccination_campaign_duration = (
        actual_steps
        - model.vaccination_campaign_start_step
    )
else:
    vaccination_campaign_duration = 0


total_vaccinations = (
    model.initial_vaccinations
    + model.total_campaign_vaccinations
)

vaccination_coverage = (
    total_vaccinations / config.POPULATION
    if config.POPULATION > 0 else 0
)


breakthrough_infection_rate = (
    model.vaccinated_breakthrough_infections / total_vaccinations
    if total_vaccinations > 0 else 0
)


if total_vaccinations > 0:
    vaccinated_infection_rate = (
        model.vaccinated_breakthrough_infections
        / total_vaccinations
    )
else:
    vaccinated_infection_rate = 0

unvaccinated_population = (
    config.POPULATION
    - total_vaccinations
)

unvaccinated_infections = (
    model.total_infections
    - model.vaccinated_breakthrough_infections
)

if unvaccinated_population > 0:
    unvaccinated_infection_rate = (
        unvaccinated_infections
        / unvaccinated_population
    )
else:
    unvaccinated_infection_rate = 0


if unvaccinated_infection_rate > 0:
    observed_vaccine_effectiveness = (
        1
        - vaccinated_infection_rate
        / unvaccinated_infection_rate
    )
else:
    observed_vaccine_effectiveness = 0


summary_metrics = {

    # =====================
    # GENERAL INFORMATION
    # =====================
    "experiment_id": experiment_id,
    "timestamp": timestamp,
    "scenario_name": config.SCENARIO_NAME,
    "output_dir": output_dir,
    "log_file": log_file,

    "population": config.POPULATION,
    "initial_infected": config.INITIAL_INFECTED,

    # =====================
    # EPIDEMIC OUTCOMES
    # =====================
    "total_infections": model.total_infections,
    "secondary_infections": secondary_infections,
    "peak_active_cases": model.peak_active_cases,

    "attack_rate": attack_rate,
    "case_fatality_rate": case_fatality_rate,
    "average_rt": average_rt,

    # =====================
    # TRANSMISSION ANALYSIS
    # =====================
    "household_infection_share": household_infection_share,
    "community_infection_share": community_infection_share,

    "home_infection_share": home_infection_share,
    "school_infection_share": school_infection_share,
    "work_infection_share": work_infection_share,
    "other_infection_share": other_infection_share,

    # =====================
    # INTERVENTION OUTCOMES
    # =====================
    "mask_protected_contacts": total_mask_protected_contacts,

    "total_quarantined_agents": total_quarantined_agents,
    "total_quarantined_people": model.total_quarantined_people,
    "quarantine_rate": quarantine_rate,

    "total_detected_infections": model.total_detected_infections,
    "detection_rate": detection_rate,

    "undetected_infections": undetected_infections,
    "undetected_rate": undetected_rate,

    "total_asymptomatic_infections": model.total_asymptomatic_infections,
    "asymptomatic_rate_observed": asymptomatic_rate_observed,

    # =====================
    # VACCINATION CAMPAIGN
    # =====================
    "vaccination_campaign_start_step": model.vaccination_campaign_start_step,
    "vaccination_campaign_end_step": model.vaccination_campaign_end_step,
    "vaccination_campaign_duration": vaccination_campaign_duration,
    "initial_vaccinations": model.initial_vaccinations,
    "total_vaccinations": total_vaccinations,
    "vaccination_coverage": vaccination_coverage,
    "total_campaign_vaccinations": model.total_campaign_vaccinations,
    "vaccination_campaign_activation_count": model.vaccination_campaign_activation_count,
    "vaccinated_breakthrough_infections": model.vaccinated_breakthrough_infections,
    "breakthrough_infection_rate": breakthrough_infection_rate,
    "vaccinated_infection_rate": vaccinated_infection_rate,
    "unvaccinated_infection_rate": unvaccinated_infection_rate,
    "observed_vaccine_effectiveness": observed_vaccine_effectiveness,

    "child_campaign_vaccinations": model.child_campaign_vaccinations,
    "adult_campaign_vaccinations": model.adult_campaign_vaccinations,
    "senior_campaign_vaccinations": model.senior_campaign_vaccinations,
    "child_vaccination_coverage": child_vaccination_coverage,
    "adult_vaccination_coverage": adult_vaccination_coverage,
    "senior_vaccination_coverage": senior_vaccination_coverage,

    # =====================
    # DYNAMIC POLICIES
    # =====================

    # Lockdown
    "lockdown_start_step": model.lockdown_start_step,
    "lockdown_end_step": model.lockdown_end_step,
    "lockdown_duration": lockdown_duration,
    "lockdown_activation_count": model.lockdown_activation_count,

    # Schools
    "school_closure_start_step": model.school_closure_start_step,
    "school_closure_end_step": model.school_closure_end_step,
    "school_closure_duration": school_closure_duration,
    "school_closure_count": model.school_closure_count,

    # Work
    "work_closure_start_step": model.work_closure_start_step,
    "work_closure_end_step": model.work_closure_end_step,
    "work_closure_duration": work_closure_duration,
    "work_closure_count": model.work_closure_count,

    # Masks
    "final_mask_compliance": model.mask_compliance_active,
    "mask_compliance_start_step": model.mask_compliance_start_step,
    "mask_compliance_end_step": model.mask_compliance_end_step,
    "mask_compliance_duration": mask_compliance_duration,
    "mask_compliance_activation_count": model.mask_compliance_activation_count,

    # Testing
    "final_testing_rate": model.testing_rate_active,
    "testing_rate_start_step": model.testing_rate_start_step,
    "testing_rate_end_step": model.testing_rate_end_step,
    "testing_rate_duration": testing_rate_duration,
    "testing_rate_activation_count": model.testing_rate_activation_count,

    # Quarantine compliance
    "final_quarantine_compliance": model.quarantine_compliance_active,
    "quarantine_compliance_start_step": model.quarantine_compliance_start_step,
    "quarantine_compliance_end_step": model.quarantine_compliance_end_step,
    "quarantine_compliance_duration": quarantine_compliance_duration,
    "quarantine_compliance_activation_count": model.quarantine_compliance_activation_count,

    # =====================
    # MOBILITY POLICIES
    # =====================

    # Seniors
    "senior_mobility_reduction_start_step": model.senior_mobility_reduction_start_step,
    "senior_mobility_reduction_end_step": model.senior_mobility_reduction_end_step,
    "senior_mobility_reduction_duration": senior_mobility_reduction_duration,
    "senior_mobility_reduction_count": model.senior_mobility_reduction_count,

    # Children
    "child_mobility_reduction_start_step": model.child_mobility_reduction_start_step,
    "child_mobility_reduction_end_step": model.child_mobility_reduction_end_step,
    "child_mobility_reduction_duration": child_mobility_reduction_duration,
    "child_mobility_reduction_count": model.child_mobility_reduction_count,

    # =====================
    # AGE GROUP ANALYSIS
    # =====================

    # Infections
    "child_infections": model.child_infections,
    "adult_infections": model.adult_infections,
    "senior_infections": model.senior_infections,

    "child_attack_rate": child_attack_rate,
    "adult_attack_rate": adult_attack_rate,
    "senior_attack_rate": senior_attack_rate,

    # Deaths
    "child_deaths": model.child_deaths,
    "adult_deaths": model.adult_deaths,
    "senior_deaths": model.senior_deaths,

    "child_death_rate": child_death_rate,
    "adult_death_rate": adult_death_rate,
    "senior_death_rate": senior_death_rate,
}

logging.info("Final summary metrics:")

for key, value in summary_metrics.items():
    logging.info(f"{key}: {value}")

summary_df = pd.DataFrame([summary_metrics])

save_dataframe(
    summary_df,
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
    file.write("======================\n\n")

    file.write("General information\n")
    file.write("-------------------\n")
    file.write(f"Experiment ID: {experiment_id}\n")
    file.write(f"Timestamp: {timestamp}\n")
    file.write(f"Scenario: {config.SCENARIO_NAME}\n")
    file.write(f"Population: {config.POPULATION}\n")
    file.write(f"Max steps: {config.SIMULATION_STEPS}\n")
    file.write(f"Actual steps: {actual_steps}\n")

    file.write("\nEpidemic outcomes\n")
    file.write("-----------------\n")
    file.write(f"Peak active cases: {model.peak_active_cases}\n")
    file.write(f"Total infections: {model.total_infections}\n")
    file.write(f"Initial infections: {config.INITIAL_INFECTED}\n")
    file.write(f"Secondary infections: {secondary_infections}\n")
    file.write(f"Attack rate: {attack_rate:.2%}\n")
    file.write(f"Case fatality rate: {case_fatality_rate:.2%}\n")
    file.write(f"Average Rt: {average_rt:.2f}\n")

    file.write("\nTransmission analysis\n")
    file.write("---------------------\n")
    file.write(f"Household infections: {total_household_infections}\n")
    file.write(f"Household infection share: {household_infection_share:.2%}\n")
    file.write(f"Community infections: {total_community_infections}\n")
    file.write(f"Community infection share: {community_infection_share:.2%}\n")
    file.write(f"Household/community share sum: {household_share_sum:.2%}\n")
    file.write(f"Home infections: {total_home_infections}\n")
    file.write(f"Home infection share: {home_infection_share:.2%}\n")
    file.write(f"School infections: {total_school_infections}\n")
    file.write(f"School infection share: {school_infection_share:.2%}\n")
    file.write(f"Work infections: {total_work_infections}\n")
    file.write(f"Work infection share: {work_infection_share:.2%}\n")
    file.write(f"Other infections: {total_other_infections}\n")
    file.write(f"Other infection share: {other_infection_share:.2%}\n")
    file.write(f"Location share sum: {location_share_sum:.2%}\n")

    file.write("\nIntervention outcomes\n")
    file.write("---------------------\n")
    file.write(f"Masks enabled: {config.MASKS_ENABLED}\n")
    file.write(f"Mask compliance: {config.MASK_COMPLIANCE:.2%}\n")
    file.write(f"Mask transmission reduction: {config.MASK_TRANSMISSION_REDUCTION:.2%}\n")
    file.write(f"Mask protected contacts: {total_mask_protected_contacts}\n")
    file.write(f"Quarantine enabled: {config.QUARANTINE_ENABLED}\n")
    file.write(f"Quarantine compliance: {config.QUARANTINE_COMPLIANCE:.2%}\n")
    file.write(f"Total quarantined agent-steps: {total_quarantined_agents}\n")
    file.write(f"Total quarantined people: {model.total_quarantined_people}\n")
    file.write(f"Quarantine rate: {quarantine_rate:.2%}\n")
    file.write(f"Total detected infections: {model.total_detected_infections}\n")
    file.write(f"Detection rate: {detection_rate:.2%}\n")
    file.write(f"Undetected infections: {undetected_infections}\n")
    file.write(f"Undetected rate: {undetected_rate:.2%}\n")
    file.write(f"Total asymptomatic infections: {model.total_asymptomatic_infections}\n")
    file.write(f"Observed asymptomatic rate: {asymptomatic_rate_observed:.2%}\n")

    file.write("\nVaccination campaign\n")
    file.write("--------------------\n")
    file.write(f"Auto vaccination campaign: {config.AUTO_VACCINATION_CAMPAIGN}\n")
    file.write(f"Vaccination campaign threshold: {config.VACCINATION_CAMPAIGN_THRESHOLD}\n")
    file.write(f"Daily vaccination capacity: {config.DAILY_VACCINATION_CAPACITY}\n")
    file.write(f"Vaccination campaign start step: {model.vaccination_campaign_start_step}\n")
    file.write(f"Vaccination campaign end step: {model.vaccination_campaign_end_step}\n")
    file.write(f"Vaccination campaign duration: {vaccination_campaign_duration}\n")
    file.write(f"Initial vaccinations: {model.initial_vaccinations}\n")
    file.write(f"Total vaccinations: {total_vaccinations}\n")
    file.write(f"Vaccination coverage: {vaccination_coverage:.2%}\n")
    file.write(f"Total campaign vaccinations: {model.total_campaign_vaccinations}\n")
    file.write(f"Vaccination campaign activation count: {model.vaccination_campaign_activation_count}\n")
    file.write(f"Breakthrough infections: {model.vaccinated_breakthrough_infections}\n")
    file.write(f"Breakthrough infection rate: {breakthrough_infection_rate:.2%}\n")
    file.write(f"Vaccinated infection rate: "f"{vaccinated_infection_rate:.2%}\n")
    file.write(f"Unvaccinated infection rate: "f"{unvaccinated_infection_rate:.2%}\n")
    file.write(f"Observed vaccine effectiveness: "f"{observed_vaccine_effectiveness:.2%}\n")

    file.write(f"Child campaign vaccinations: {model.child_campaign_vaccinations}\n")
    file.write(f"Adult campaign vaccinations: {model.adult_campaign_vaccinations}\n")
    file.write(f"Senior campaign vaccinations: {model.senior_campaign_vaccinations}\n")
    file.write(f"Child vaccination coverage: {child_vaccination_coverage:.2%}\n")
    file.write(f"Adult vaccination coverage: {adult_vaccination_coverage:.2%}\n")
    file.write(f"Senior vaccination coverage: {senior_vaccination_coverage:.2%}\n")

    file.write("\nDynamic policies\n")
    file.write("----------------\n")
    file.write(f"Auto lockdown: {config.AUTO_LOCKDOWN}\n")
    file.write(f"Lockdown threshold: {config.LOCKDOWN_THRESHOLD}\n")
    file.write(f"Lockdown release threshold: {config.LOCKDOWN_RELEASE_THRESHOLD}\n")
    file.write(f"Lockdown start step: {model.lockdown_start_step}\n")
    file.write(f"Lockdown end step: {model.lockdown_end_step}\n")
    file.write(f"Lockdown duration: {lockdown_duration}\n")
    file.write(f"Lockdown activation count: {model.lockdown_activation_count}\n")

    file.write(f"Auto school closure: {config.AUTO_SCHOOL_CLOSURE}\n")
    file.write(f"School closure threshold: {config.SCHOOL_CLOSURE_THRESHOLD}\n")
    file.write(f"School reopen threshold: {config.SCHOOL_REOPEN_THRESHOLD}\n")
    file.write(f"School closure start step: {model.school_closure_start_step}\n")
    file.write(f"School closure end step: {model.school_closure_end_step}\n")
    file.write(f"School closure duration: {school_closure_duration}\n")
    file.write(f"School closure count: {model.school_closure_count}\n")

    file.write(f"Auto work closure: {config.AUTO_WORK_CLOSURE}\n")
    file.write(f"Work closure threshold: {config.WORK_CLOSURE_THRESHOLD}\n")
    file.write(f"Work reopen threshold: {config.WORK_REOPEN_THRESHOLD}\n")
    file.write(f"Work closure start step: {model.work_closure_start_step}\n")
    file.write(f"Work closure end step: {model.work_closure_end_step}\n")
    file.write(f"Work closure duration: {work_closure_duration}\n")
    file.write(f"Work closure count: {model.work_closure_count}\n")

    file.write(f"Auto mask compliance: {config.AUTO_MASK_COMPLIANCE}\n")
    file.write(f"Mask compliance threshold: {config.MASK_COMPLIANCE_THRESHOLD}\n")
    file.write(f"Mask relaxation threshold: {config.MASK_RELAXATION_THRESHOLD}\n")
    file.write(f"Final mask compliance: {model.mask_compliance_active:.2%}\n")
    file.write(f"Mask compliance start step: {model.mask_compliance_start_step}\n")
    file.write(f"Mask compliance end step: {model.mask_compliance_end_step}\n")
    file.write(f"Mask compliance duration: {mask_compliance_duration}\n")
    file.write(f"Mask compliance activation count: {model.mask_compliance_activation_count}\n")

    file.write(f"Auto testing rate: {config.AUTO_TESTING_RATE}\n")
    file.write(f"Testing rate threshold: {config.TESTING_RATE_THRESHOLD}\n")
    file.write(f"Testing relaxation threshold: {config.TESTING_RELAXATION_THRESHOLD}\n")
    file.write(f"Final testing rate: {model.testing_rate_active:.2%}\n")
    file.write(f"Testing rate start step: {model.testing_rate_start_step}\n")
    file.write(f"Testing rate end step: {model.testing_rate_end_step}\n")
    file.write(f"Testing rate duration: {testing_rate_duration}\n")
    file.write(f"Testing rate activation count: {model.testing_rate_activation_count}\n")

    file.write(f"Auto quarantine compliance: {config.AUTO_QUARANTINE_COMPLIANCE}\n")
    file.write(f"Quarantine compliance threshold: {config.QUARANTINE_COMPLIANCE_THRESHOLD}\n")
    file.write(f"Quarantine relaxation threshold: {config.QUARANTINE_RELAXATION_THRESHOLD}\n")
    file.write(f"Final quarantine compliance: {model.quarantine_compliance_active:.2%}\n")
    file.write(f"Quarantine compliance start step: {model.quarantine_compliance_start_step}\n")
    file.write(f"Quarantine compliance end step: {model.quarantine_compliance_end_step}\n")
    file.write(f"Quarantine compliance duration: {quarantine_compliance_duration}\n")
    file.write(f"Quarantine compliance activation count: {model.quarantine_compliance_activation_count}\n")

    file.write("\nMobility policies\n")
    file.write("-----------------\n")
    file.write(f"Base senior mobility: {config.SENIOR_MOBILITY:.2%}\n")
    file.write(f"Low senior mobility: {config.LOW_SENIOR_MOBILITY:.2%}\n")
    file.write(f"Senior mobility reduction start step: {model.senior_mobility_reduction_start_step}\n")
    file.write(f"Senior mobility reduction end step: {model.senior_mobility_reduction_end_step}\n")
    file.write(f"Senior mobility reduction duration: {senior_mobility_reduction_duration}\n")
    file.write(f"Senior mobility reduction count: {model.senior_mobility_reduction_count}\n")

    file.write(f"Base child mobility: {config.CHILD_MOBILITY:.2%}\n")
    file.write(f"Low child mobility: {config.LOW_CHILD_MOBILITY:.2%}\n")
    file.write(f"Child mobility reduction start step: {model.child_mobility_reduction_start_step}\n")
    file.write(f"Child mobility reduction end step: {model.child_mobility_reduction_end_step}\n")
    file.write(f"Child mobility reduction duration: {child_mobility_reduction_duration}\n")
    file.write(f"Child mobility reduction count: {model.child_mobility_reduction_count}\n")

    file.write("\nAge-group analysis\n")
    file.write("------------------\n")
    file.write(f"Child infections: {model.child_infections}\n")
    file.write(f"Child attack rate: {child_attack_rate:.2%}\n")
    file.write(f"Child deaths: {model.child_deaths}\n")
    file.write(f"Child death rate: {child_death_rate:.2%}\n")
    file.write(f"Adult infections: {model.adult_infections}\n")
    file.write(f"Adult attack rate: {adult_attack_rate:.2%}\n")
    file.write(f"Adult deaths: {model.adult_deaths}\n")
    file.write(f"Adult death rate: {adult_death_rate:.2%}\n")
    file.write(f"Senior infections: {model.senior_infections}\n")
    file.write(f"Senior attack rate: {senior_attack_rate:.2%}\n")
    file.write(f"Senior deaths: {model.senior_deaths}\n")
    file.write(f"Senior death rate: {senior_death_rate:.2%}\n")

    file.write("\nFinal state counts\n")
    file.write("------------------\n")
    for state, count in final_counts.items():
        file.write(f"{state}: {count}\n")

    file.write("\nPerformance\n")
    file.write("-----------\n")
    file.write(f"Execution time (seconds): {execution_time_seconds:.2f}\n")
    file.write(f"Log file: {log_file}\n")

print("Summary saved to outputs/simulation_summary.txt")

generate_all_plots(
    results,
    plots_dir,
    model,
    total_home_infections,
    total_school_infections,
    total_work_infections,
    total_other_infections,
    total_household_infections,
    total_community_infections,
    home_infection_share,
    school_infection_share,
    work_infection_share,
    other_infection_share,
    household_infection_share,
    community_infection_share,
    child_attack_rate,
    adult_attack_rate,
    senior_attack_rate,
    child_death_rate,
    adult_death_rate,
    senior_death_rate,
    child_vaccination_coverage,
    adult_vaccination_coverage,
    senior_vaccination_coverage,
)
