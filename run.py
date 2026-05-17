from model import FluModel
import matplotlib.pyplot as plt
import config
import os


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
    random_seed=config.RANDOM_SEED
)

steps = config.SIMULATION_STEPS

print(model.count_age_groups())

os.makedirs("outputs", exist_ok=True)

with open("outputs/parameters.txt", "w") as file:
    file.write("Simulation parameters\n")
    file.write("=====================\n\n")

    for name in dir(config):
        if name.isupper():
            value = getattr(config, name)
            file.write(f"{name}: {value}\n")

print("Parameters saved to outputs/parameters.txt")

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

results.to_csv("outputs/simulation_results.csv", index_label="Step")
print("Results saved to outputs/simulation_results.csv")

print("Peak active cases:", model.peak_active_cases)

final_counts = model.count_states()

attack_rate = model.total_infections / config.POPULATION

dead_count = final_counts["Dead"]

if model.total_infections > 0:
    case_fatality_rate = dead_count / model.total_infections
else:
    case_fatality_rate = 0

with open("outputs/simulation_summary.txt", "w") as file:
    file.write("Flu simulation summary\n")
    file.write("======================\n\n")
    file.write(f"Population: {config.POPULATION}\n")
    file.write(f"Max steps: {config.SIMULATION_STEPS}\n")
    file.write(f"Actual steps: {actual_steps}\n")
    file.write(f"Peak active cases: {model.peak_active_cases}\n\n")
    file.write(f"Total infections: {model.total_infections}\n")
    file.write(f"Attack rate: {attack_rate:.2%}\n")
    file.write(f"Case fatality rate: {case_fatality_rate:.2%}\n")

    file.write("Final state counts:\n")
    for state, count in final_counts.items():
        file.write(f"{state}: {count}\n")

print("Summary saved to outputs/simulation_summary.txt")

plt.plot(results["Susceptible"], label="Susceptible")
plt.plot(results["Exposed"], label="Exposed")
plt.plot(results["Infected"], label="Infected")
plt.plot(results["Recovered"], label="Recovered")
plt.plot(results["Dead"], label="Dead")
plt.plot(results["Asymptomatic"], label="Asymptomatic")
plt.plot(results["Vaccinated"], label="Vaccinated")
plt.plot(results["ActiveCases"], label="Active cases", linestyle="--")
plt.plot(results["NewInfections"], label="New infections")

plt.xlabel("Step")
plt.ylabel("Number of people")
plt.title("Flu epidemic simulation")
plt.legend()
plt.tight_layout()
plt.show()