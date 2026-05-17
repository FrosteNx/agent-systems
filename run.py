from model import FluModel
import matplotlib.pyplot as plt
import config


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
    senior_mortality_rate=config.SENIOR_MORTALITY_RATE
)

steps = config.SIMULATION_STEPS

print(model.count_age_groups())

for i in range(steps):
    model.step()
    counts = model.count_states()

    print(f"Step {i}: {counts}")

results = model.datacollector.get_model_vars_dataframe()

results.to_csv("simulation_results.csv", index_label="Step")
print("Results saved to simulation_results.csv")

plt.plot(results["Susceptible"], label="Susceptible")
plt.plot(results["Exposed"], label="Exposed")
plt.plot(results["Infected"], label="Infected")
plt.plot(results["Recovered"], label="Recovered")
plt.plot(results["Dead"], label="Dead")

plt.xlabel("Step")
plt.ylabel("Number of people")
plt.title("Flu epidemic simulation")
plt.legend()
plt.tight_layout()
plt.show()