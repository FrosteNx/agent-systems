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
    vaccination_rate=config.VACCINATION_RATE
)

steps = config.SIMULATION_STEPS

susceptible_counts = []
exposed_counts = []
infected_counts = []
recovered_counts = []

print(model.count_age_groups())

for i in range(steps):
    model.step()
    counts = model.count_states()

    susceptible_counts.append(counts["Susceptible"])
    exposed_counts.append(counts["Exposed"])
    infected_counts.append(counts["Infected"])
    recovered_counts.append(counts["Recovered"])

    print(f"Step {i}: {counts}")

plt.plot(susceptible_counts, label="Susceptible")
plt.plot(exposed_counts, label="Exposed")   # NEW
plt.plot(infected_counts, label="Infected")
plt.plot(recovered_counts, label="Recovered")

plt.xlabel("Step")
plt.ylabel("Number of people")
plt.title("Flu epidemic simulation")
plt.legend()
plt.tight_layout()
plt.show()