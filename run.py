from model import FluModel
import config
import os
from datetime import datetime
import json
from pathlib import Path
import pandas as pd
import logging
import time
from plots import generate_all_plots
from reports import (
    save_simulation_summary,
    build_summary_metrics,
    build_simulation_summary,
)
from io_utils import save_dataframe
from metrics import (
    calculate_age_group_metrics,
    calculate_vaccination_metrics,
    calculate_policy_durations,
    calculate_epidemic_metrics,
    calculate_infection_totals,
    calculate_transmission_metrics,
    calculate_intervention_metrics,
)

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

epidemic_metrics = calculate_epidemic_metrics(
    model,
    results,
    final_counts,
    config.POPULATION,
    config.INITIAL_INFECTED
)

attack_rate = epidemic_metrics["attack_rate"]
case_fatality_rate = epidemic_metrics["case_fatality_rate"]
average_rt = epidemic_metrics["average_rt"]
secondary_infections = epidemic_metrics["secondary_infections"]

infection_totals = calculate_infection_totals(results)

total_household_infections = infection_totals["total_household_infections"]
total_community_infections = infection_totals["total_community_infections"]
total_home_infections = infection_totals["total_home_infections"]
total_school_infections = infection_totals["total_school_infections"]
total_work_infections = infection_totals["total_work_infections"]
total_other_infections = infection_totals["total_other_infections"]
total_quarantined_agents = infection_totals["total_quarantined_agents"]
total_mask_protected_contacts = infection_totals["total_mask_protected_contacts"]

transmission_metrics = calculate_transmission_metrics(
    secondary_infections,
    total_household_infections,
    total_community_infections,
    total_home_infections,
    total_school_infections,
    total_work_infections,
    total_other_infections,
)

household_infection_share = transmission_metrics["household_infection_share"]
community_infection_share = transmission_metrics["community_infection_share"]
home_infection_share = transmission_metrics["home_infection_share"]
school_infection_share = transmission_metrics["school_infection_share"]
work_infection_share = transmission_metrics["work_infection_share"]
other_infection_share = transmission_metrics["other_infection_share"]
household_share_sum = transmission_metrics["household_share_sum"]
location_share_sum = transmission_metrics["location_share_sum"]

intervention_metrics = calculate_intervention_metrics(model)

detection_rate = intervention_metrics["detection_rate"]
quarantine_rate = intervention_metrics["quarantine_rate"]
undetected_infections = intervention_metrics["undetected_infections"]
undetected_rate = intervention_metrics["undetected_rate"]
asymptomatic_rate_observed = intervention_metrics["asymptomatic_rate_observed"]

age_counts = model.count_age_groups()

age_group_metrics = calculate_age_group_metrics(
    model,
    age_counts
)

child_vaccination_coverage = age_group_metrics["child_vaccination_coverage"]
adult_vaccination_coverage = age_group_metrics["adult_vaccination_coverage"]
senior_vaccination_coverage = age_group_metrics["senior_vaccination_coverage"]

child_attack_rate = age_group_metrics["child_attack_rate"]
adult_attack_rate = age_group_metrics["adult_attack_rate"]
senior_attack_rate = age_group_metrics["senior_attack_rate"]

child_death_rate = age_group_metrics["child_death_rate"]
adult_death_rate = age_group_metrics["adult_death_rate"]
senior_death_rate = age_group_metrics["senior_death_rate"]

policy_durations = calculate_policy_durations(model, actual_steps)

lockdown_duration = policy_durations["lockdown_duration"]
school_closure_duration = policy_durations["school_closure_duration"]
mask_compliance_duration = policy_durations["mask_compliance_duration"]
testing_rate_duration = policy_durations["testing_rate_duration"]
quarantine_compliance_duration = policy_durations["quarantine_compliance_duration"]
work_closure_duration = policy_durations["work_closure_duration"]
senior_mobility_reduction_duration = policy_durations["senior_mobility_reduction_duration"]
child_mobility_reduction_duration = policy_durations["child_mobility_reduction_duration"]
vaccination_campaign_duration = policy_durations["vaccination_campaign_duration"]

vaccination_metrics = calculate_vaccination_metrics(
    model,
    config.POPULATION
)

total_vaccinations = vaccination_metrics["total_vaccinations"]
vaccination_coverage = vaccination_metrics["vaccination_coverage"]
breakthrough_infection_rate = vaccination_metrics["breakthrough_infection_rate"]
vaccinated_infection_rate = vaccination_metrics["vaccinated_infection_rate"]
unvaccinated_infection_rate = vaccination_metrics["unvaccinated_infection_rate"]
observed_vaccine_effectiveness = vaccination_metrics["observed_vaccine_effectiveness"]


summary_metrics = build_summary_metrics(
    experiment_id=experiment_id,
    timestamp=timestamp,
    scenario_name=config.SCENARIO_NAME,
    output_dir=output_dir,
    log_file=log_file,

    population=config.POPULATION,
    initial_infected=config.INITIAL_INFECTED,

    total_infections=model.total_infections,
    secondary_infections=secondary_infections,
    peak_active_cases=model.peak_active_cases,
    attack_rate=attack_rate,
    case_fatality_rate=case_fatality_rate,
    average_rt=average_rt,

    household_infection_share=household_infection_share,
    community_infection_share=community_infection_share,
    home_infection_share=home_infection_share,
    school_infection_share=school_infection_share,
    work_infection_share=work_infection_share,
    other_infection_share=other_infection_share,

    mask_protected_contacts=total_mask_protected_contacts,
    total_quarantined_agents=total_quarantined_agents,
    total_quarantined_people=model.total_quarantined_people,
    quarantine_rate=quarantine_rate,
    total_detected_infections=model.total_detected_infections,
    detection_rate=detection_rate,
    undetected_infections=undetected_infections,
    undetected_rate=undetected_rate,
    total_asymptomatic_infections=model.total_asymptomatic_infections,
    asymptomatic_rate_observed=asymptomatic_rate_observed,

    vaccination_campaign_start_step=model.vaccination_campaign_start_step,
    vaccination_campaign_end_step=model.vaccination_campaign_end_step,
    vaccination_campaign_duration=vaccination_campaign_duration,
    initial_vaccinations=model.initial_vaccinations,
    total_vaccinations=total_vaccinations,
    vaccination_coverage=vaccination_coverage,
    total_campaign_vaccinations=model.total_campaign_vaccinations,
    vaccination_campaign_activation_count=model.vaccination_campaign_activation_count,
    vaccinated_breakthrough_infections=model.vaccinated_breakthrough_infections,
    breakthrough_infection_rate=breakthrough_infection_rate,
    vaccinated_infection_rate=vaccinated_infection_rate,
    unvaccinated_infection_rate=unvaccinated_infection_rate,
    observed_vaccine_effectiveness=observed_vaccine_effectiveness,

    child_campaign_vaccinations=model.child_campaign_vaccinations,
    adult_campaign_vaccinations=model.adult_campaign_vaccinations,
    senior_campaign_vaccinations=model.senior_campaign_vaccinations,
    child_vaccination_coverage=child_vaccination_coverage,
    adult_vaccination_coverage=adult_vaccination_coverage,
    senior_vaccination_coverage=senior_vaccination_coverage,

    lockdown_start_step=model.lockdown_start_step,
    lockdown_end_step=model.lockdown_end_step,
    lockdown_duration=lockdown_duration,
    lockdown_activation_count=model.lockdown_activation_count,

    school_closure_start_step=model.school_closure_start_step,
    school_closure_end_step=model.school_closure_end_step,
    school_closure_duration=school_closure_duration,
    school_closure_count=model.school_closure_count,

    work_closure_start_step=model.work_closure_start_step,
    work_closure_end_step=model.work_closure_end_step,
    work_closure_duration=work_closure_duration,
    work_closure_count=model.work_closure_count,

    final_mask_compliance=model.mask_compliance_active,
    mask_compliance_start_step=model.mask_compliance_start_step,
    mask_compliance_end_step=model.mask_compliance_end_step,
    mask_compliance_duration=mask_compliance_duration,
    mask_compliance_activation_count=model.mask_compliance_activation_count,

    final_testing_rate=model.testing_rate_active,
    testing_rate_start_step=model.testing_rate_start_step,
    testing_rate_end_step=model.testing_rate_end_step,
    testing_rate_duration=testing_rate_duration,
    testing_rate_activation_count=model.testing_rate_activation_count,

    final_quarantine_compliance=model.quarantine_compliance_active,
    quarantine_compliance_start_step=model.quarantine_compliance_start_step,
    quarantine_compliance_end_step=model.quarantine_compliance_end_step,
    quarantine_compliance_duration=quarantine_compliance_duration,
    quarantine_compliance_activation_count=model.quarantine_compliance_activation_count,

    senior_mobility_reduction_start_step=model.senior_mobility_reduction_start_step,
    senior_mobility_reduction_end_step=model.senior_mobility_reduction_end_step,
    senior_mobility_reduction_duration=senior_mobility_reduction_duration,
    senior_mobility_reduction_count=model.senior_mobility_reduction_count,

    child_mobility_reduction_start_step=model.child_mobility_reduction_start_step,
    child_mobility_reduction_end_step=model.child_mobility_reduction_end_step,
    child_mobility_reduction_duration=child_mobility_reduction_duration,
    child_mobility_reduction_count=model.child_mobility_reduction_count,

    child_infections=model.child_infections,
    adult_infections=model.adult_infections,
    senior_infections=model.senior_infections,
    child_attack_rate=child_attack_rate,
    adult_attack_rate=adult_attack_rate,
    senior_attack_rate=senior_attack_rate,

    child_deaths=model.child_deaths,
    adult_deaths=model.adult_deaths,
    senior_deaths=model.senior_deaths,
    child_death_rate=child_death_rate,
    adult_death_rate=adult_death_rate,
    senior_death_rate=senior_death_rate,
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

summary_lines = []

summary_lines.append("Flu simulation summary")
summary_lines.append("======================")
summary_lines.append("")

summary_lines.append("General information")
summary_lines.append("-------------------")
summary_lines.append(f"Experiment ID: {experiment_id}")
summary_lines.append(f"Timestamp: {timestamp}")
summary_lines.append(f"Scenario: {config.SCENARIO_NAME}")
summary_lines.append(f"Population: {config.POPULATION}")
summary_lines.append(f"Max steps: {config.SIMULATION_STEPS}")
summary_lines.append(f"Actual steps: {actual_steps}")

summary_lines.append("")
summary_lines.append("Epidemic outcomes")
summary_lines.append("-----------------")
summary_lines.append(f"Peak active cases: {model.peak_active_cases}")
summary_lines.append(f"Total infections: {model.total_infections}")
summary_lines.append(f"Initial infections: {config.INITIAL_INFECTED}")
summary_lines.append(f"Secondary infections: {secondary_infections}")
summary_lines.append(f"Attack rate: {attack_rate:.2%}")
summary_lines.append(f"Case fatality rate: {case_fatality_rate:.2%}")
summary_lines.append(f"Average Rt: {average_rt:.2f}")

summary_lines.append("")
summary_lines.append("Transmission analysis")
summary_lines.append("---------------------")
summary_lines.append(f"Household infections: {total_household_infections}")
summary_lines.append(f"Household infection share: {household_infection_share:.2%}")
summary_lines.append(f"Community infections: {total_community_infections}")
summary_lines.append(f"Community infection share: {community_infection_share:.2%}")
summary_lines.append(f"Household/community share sum: {household_share_sum:.2%}")
summary_lines.append(f"Home infections: {total_home_infections}")
summary_lines.append(f"Home infection share: {home_infection_share:.2%}")
summary_lines.append(f"School infections: {total_school_infections}")
summary_lines.append(f"School infection share: {school_infection_share:.2%}")
summary_lines.append(f"Work infections: {total_work_infections}")
summary_lines.append(f"Work infection share: {work_infection_share:.2%}")
summary_lines.append(f"Other infections: {total_other_infections}")
summary_lines.append(f"Other infection share: {other_infection_share:.2%}")
summary_lines.append(f"Location share sum: {location_share_sum:.2%}")

summary_lines.append("")
summary_lines.append("Intervention outcomes")
summary_lines.append("---------------------")
summary_lines.append(f"Masks enabled: {config.MASKS_ENABLED}")
summary_lines.append(f"Mask compliance: {config.MASK_COMPLIANCE:.2%}")
summary_lines.append(f"Mask transmission reduction: {config.MASK_TRANSMISSION_REDUCTION:.2%}")
summary_lines.append(f"Mask protected contacts: {total_mask_protected_contacts}")
summary_lines.append(f"Quarantine enabled: {config.QUARANTINE_ENABLED}")
summary_lines.append(f"Quarantine compliance: {config.QUARANTINE_COMPLIANCE:.2%}")
summary_lines.append(f"Total quarantined agent-steps: {total_quarantined_agents}")
summary_lines.append(f"Total quarantined people: {model.total_quarantined_people}")
summary_lines.append(f"Quarantine rate: {quarantine_rate:.2%}")
summary_lines.append(f"Total detected infections: {model.total_detected_infections}")
summary_lines.append(f"Detection rate: {detection_rate:.2%}")
summary_lines.append(f"Undetected infections: {undetected_infections}")
summary_lines.append(f"Undetected rate: {undetected_rate:.2%}")
summary_lines.append(f"Total asymptomatic infections: {model.total_asymptomatic_infections}")
summary_lines.append(f"Observed asymptomatic rate: {asymptomatic_rate_observed:.2%}")

summary_lines.append("")
summary_lines.append("Vaccination campaign")
summary_lines.append("--------------------")
summary_lines.append(f"Auto vaccination campaign: {config.AUTO_VACCINATION_CAMPAIGN}")
summary_lines.append(f"Vaccination campaign threshold: {config.VACCINATION_CAMPAIGN_THRESHOLD}")
summary_lines.append(f"Daily vaccination capacity: {config.DAILY_VACCINATION_CAPACITY}")
summary_lines.append(f"Vaccination campaign start step: {model.vaccination_campaign_start_step}")
summary_lines.append(f"Vaccination campaign end step: {model.vaccination_campaign_end_step}")
summary_lines.append(f"Vaccination campaign duration: {vaccination_campaign_duration}")
summary_lines.append(f"Initial vaccinations: {model.initial_vaccinations}")
summary_lines.append(f"Total vaccinations: {total_vaccinations}")
summary_lines.append(f"Vaccination coverage: {vaccination_coverage:.2%}")
summary_lines.append(f"Total campaign vaccinations: {model.total_campaign_vaccinations}")
summary_lines.append(f"Vaccination campaign activation count: {model.vaccination_campaign_activation_count}")
summary_lines.append(f"Breakthrough infections: {model.vaccinated_breakthrough_infections}")
summary_lines.append(f"Breakthrough infection rate: {breakthrough_infection_rate:.2%}")
summary_lines.append(f"Vaccinated infection rate: {vaccinated_infection_rate:.2%}")
summary_lines.append(f"Unvaccinated infection rate: {unvaccinated_infection_rate:.2%}")
summary_lines.append(f"Observed vaccine effectiveness: {observed_vaccine_effectiveness:.2%}")
summary_lines.append(f"Child campaign vaccinations: {model.child_campaign_vaccinations}")
summary_lines.append(f"Adult campaign vaccinations: {model.adult_campaign_vaccinations}")
summary_lines.append(f"Senior campaign vaccinations: {model.senior_campaign_vaccinations}")
summary_lines.append(f"Child vaccination coverage: {child_vaccination_coverage:.2%}")
summary_lines.append(f"Adult vaccination coverage: {adult_vaccination_coverage:.2%}")
summary_lines.append(f"Senior vaccination coverage: {senior_vaccination_coverage:.2%}")

summary_lines.append("")
summary_lines.append("Dynamic policies")
summary_lines.append("----------------")
summary_lines.append(f"Auto lockdown: {config.AUTO_LOCKDOWN}")
summary_lines.append(f"Lockdown threshold: {config.LOCKDOWN_THRESHOLD}")
summary_lines.append(f"Lockdown release threshold: {config.LOCKDOWN_RELEASE_THRESHOLD}")
summary_lines.append(f"Lockdown start step: {model.lockdown_start_step}")
summary_lines.append(f"Lockdown end step: {model.lockdown_end_step}")
summary_lines.append(f"Lockdown duration: {lockdown_duration}")
summary_lines.append(f"Lockdown activation count: {model.lockdown_activation_count}")
summary_lines.append(f"Auto school closure: {config.AUTO_SCHOOL_CLOSURE}")
summary_lines.append(f"School closure threshold: {config.SCHOOL_CLOSURE_THRESHOLD}")
summary_lines.append(f"School reopen threshold: {config.SCHOOL_REOPEN_THRESHOLD}")
summary_lines.append(f"School closure start step: {model.school_closure_start_step}")
summary_lines.append(f"School closure end step: {model.school_closure_end_step}")
summary_lines.append(f"School closure duration: {school_closure_duration}")
summary_lines.append(f"School closure count: {model.school_closure_count}")
summary_lines.append(f"Auto work closure: {config.AUTO_WORK_CLOSURE}")
summary_lines.append(f"Work closure threshold: {config.WORK_CLOSURE_THRESHOLD}")
summary_lines.append(f"Work reopen threshold: {config.WORK_REOPEN_THRESHOLD}")
summary_lines.append(f"Work closure start step: {model.work_closure_start_step}")
summary_lines.append(f"Work closure end step: {model.work_closure_end_step}")
summary_lines.append(f"Work closure duration: {work_closure_duration}")
summary_lines.append(f"Work closure count: {model.work_closure_count}")
summary_lines.append(f"Auto mask compliance: {config.AUTO_MASK_COMPLIANCE}")
summary_lines.append(f"Mask compliance threshold: {config.MASK_COMPLIANCE_THRESHOLD}")
summary_lines.append(f"Mask relaxation threshold: {config.MASK_RELAXATION_THRESHOLD}")
summary_lines.append(f"Final mask compliance: {model.mask_compliance_active:.2%}")
summary_lines.append(f"Mask compliance start step: {model.mask_compliance_start_step}")
summary_lines.append(f"Mask compliance end step: {model.mask_compliance_end_step}")
summary_lines.append(f"Mask compliance duration: {mask_compliance_duration}")
summary_lines.append(f"Mask compliance activation count: {model.mask_compliance_activation_count}")
summary_lines.append(f"Auto testing rate: {config.AUTO_TESTING_RATE}")
summary_lines.append(f"Testing rate threshold: {config.TESTING_RATE_THRESHOLD}")
summary_lines.append(f"Testing relaxation threshold: {config.TESTING_RELAXATION_THRESHOLD}")
summary_lines.append(f"Final testing rate: {model.testing_rate_active:.2%}")
summary_lines.append(f"Testing rate start step: {model.testing_rate_start_step}")
summary_lines.append(f"Testing rate end step: {model.testing_rate_end_step}")
summary_lines.append(f"Testing rate duration: {testing_rate_duration}")
summary_lines.append(f"Testing rate activation count: {model.testing_rate_activation_count}")
summary_lines.append(f"Auto quarantine compliance: {config.AUTO_QUARANTINE_COMPLIANCE}")
summary_lines.append(f"Quarantine compliance threshold: {config.QUARANTINE_COMPLIANCE_THRESHOLD}")
summary_lines.append(f"Quarantine relaxation threshold: {config.QUARANTINE_RELAXATION_THRESHOLD}")
summary_lines.append(f"Final quarantine compliance: {model.quarantine_compliance_active:.2%}")
summary_lines.append(f"Quarantine compliance start step: {model.quarantine_compliance_start_step}")
summary_lines.append(f"Quarantine compliance end step: {model.quarantine_compliance_end_step}")
summary_lines.append(f"Quarantine compliance duration: {quarantine_compliance_duration}")
summary_lines.append(f"Quarantine compliance activation count: {model.quarantine_compliance_activation_count}")

summary_lines.append("")
summary_lines.append("Mobility policies")
summary_lines.append("-----------------")
summary_lines.append(f"Base senior mobility: {config.SENIOR_MOBILITY:.2%}")
summary_lines.append(f"Low senior mobility: {config.LOW_SENIOR_MOBILITY:.2%}")
summary_lines.append(f"Senior mobility reduction start step: {model.senior_mobility_reduction_start_step}")
summary_lines.append(f"Senior mobility reduction end step: {model.senior_mobility_reduction_end_step}")
summary_lines.append(f"Senior mobility reduction duration: {senior_mobility_reduction_duration}")
summary_lines.append(f"Senior mobility reduction count: {model.senior_mobility_reduction_count}")
summary_lines.append(f"Base child mobility: {config.CHILD_MOBILITY:.2%}")
summary_lines.append(f"Low child mobility: {config.LOW_CHILD_MOBILITY:.2%}")
summary_lines.append(f"Child mobility reduction start step: {model.child_mobility_reduction_start_step}")
summary_lines.append(f"Child mobility reduction end step: {model.child_mobility_reduction_end_step}")
summary_lines.append(f"Child mobility reduction duration: {child_mobility_reduction_duration}")
summary_lines.append(f"Child mobility reduction count: {model.child_mobility_reduction_count}")

summary_lines.append("")
summary_lines.append("Age-group analysis")
summary_lines.append("------------------")
summary_lines.append(f"Child infections: {model.child_infections}")
summary_lines.append(f"Child attack rate: {child_attack_rate:.2%}")
summary_lines.append(f"Child deaths: {model.child_deaths}")
summary_lines.append(f"Child death rate: {child_death_rate:.2%}")
summary_lines.append(f"Adult infections: {model.adult_infections}")
summary_lines.append(f"Adult attack rate: {adult_attack_rate:.2%}")
summary_lines.append(f"Adult deaths: {model.adult_deaths}")
summary_lines.append(f"Adult death rate: {adult_death_rate:.2%}")
summary_lines.append(f"Senior infections: {model.senior_infections}")
summary_lines.append(f"Senior attack rate: {senior_attack_rate:.2%}")
summary_lines.append(f"Senior deaths: {model.senior_deaths}")
summary_lines.append(f"Senior death rate: {senior_death_rate:.2%}")

summary_lines.append("")
summary_lines.append("Final state counts")
summary_lines.append("------------------")
for state, count in final_counts.items():
    summary_lines.append(f"{state}: {count}")

summary_lines.append("")
summary_lines.append("Performance")
summary_lines.append("-----------")
summary_lines.append(f"Execution time (seconds): {execution_time_seconds:.2f}")
summary_lines.append(f"Log file: {log_file}")

summary_text = build_simulation_summary(summary_lines)

save_simulation_summary(
    f"{data_dir}/simulation_summary.txt",
    summary_text
)

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
