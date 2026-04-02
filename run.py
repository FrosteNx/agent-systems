from model import FluModel
import matplotlib.pyplot as plt


model = FluModel(
    width=20,
    height=20,
    population=100,
    initial_infected=3,
    infection_probability=0.4,
    recovery_time=5,
)

steps = 50

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