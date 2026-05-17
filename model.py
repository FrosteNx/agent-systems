from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector

from agent import PersonAgent

import random


class FluModel(Model):
    def __init__(
        self,
        width=20,
        height=20,
        population=100,
        initial_infected=3,
        infection_probability=0.4,
        recovery_time=5,
        incubation_time=2,   
        vaccination_rate=0.2,
        child_rate=0.25,
        senior_rate=0.15,
        child_mortality_rate=0.001,
        adult_mortality_rate=0.005,
        senior_mortality_rate=0.03,
        asymptomatic_rate=0.3,
        asymptomatic_transmission_multiplier=0.6,
        isolation_rate=0.8,
        vaccine_effectiveness=0.9,
        random_seed=42
    ):
        super().__init__()

        self.num_agents = population
        self.grid = MultiGrid(width, height, torus=True)
        self.schedule = RandomActivation(self)
        self.step_count = 0
        self.schools = [(5, 5), (15, 15)]

        # disease parameters
        self.infection_probability = infection_probability
        self.recovery_time = recovery_time
        self.incubation_time = incubation_time
        self.vaccination_rate = vaccination_rate
        self.child_rate = child_rate
        self.senior_rate = senior_rate
        self.child_mortality_rate = child_mortality_rate
        self.adult_mortality_rate = adult_mortality_rate
        self.senior_mortality_rate = senior_mortality_rate
        self.asymptomatic_rate = asymptomatic_rate
        self.asymptomatic_transmission_multiplier = asymptomatic_transmission_multiplier
        self.isolation_rate = isolation_rate
        self.vaccine_effectiveness = vaccine_effectiveness

        self.peak_active_cases = 0
        self.random_seed = random_seed

        random.seed(self.random_seed)

        for i in range(self.num_agents):
            if i < initial_infected:
                state = "Infected"
            elif random.random() < self.vaccination_rate:
                state = "Vaccinated"
            else:
                state = "Susceptible"

            r = self.random.random()

            if r < self.child_rate:
                age_group = "child"
            elif r < self.child_rate + self.senior_rate:
                age_group = "senior"
            else:
                age_group = "adult"

            agent = PersonAgent(i, self, state, age_group)

            self.schedule.add(agent)

            home_x = self.random.randrange(self.grid.width)
            home_y = self.random.randrange(self.grid.height)
            agent.home = (home_x, home_y)

            if agent.age_group == "child":
                agent.work = self.random.choice(self.schools)
            else:
                work_x = self.random.randrange(self.grid.width)
                work_y = self.random.randrange(self.grid.height)
                agent.work = (work_x, work_y)

            self.grid.place_agent(agent, agent.home)

        self.datacollector = DataCollector(
            model_reporters={
                "Susceptible": lambda m: m.count_states()["Susceptible"],
                "Exposed": lambda m: m.count_states()["Exposed"],
                "Infected": lambda m: m.count_states()["Infected"],
                "Recovered": lambda m: m.count_states()["Recovered"],
                "Dead": lambda m: m.count_states()["Dead"],
                "Asymptomatic": lambda m: m.count_states()["Asymptomatic"],
                "Vaccinated": lambda m: m.count_states()["Vaccinated"],
                "ActiveCases": lambda m: (
                    m.count_states()["Exposed"]
                    + m.count_states()["Infected"]
                    + m.count_states()["Asymptomatic"]
                ),
            }
        )

        self.running = True

    def step(self):
        self.step_count += 1
        self.schedule.step()

        counts = self.count_states()
        active_cases = (
            counts["Exposed"]
            + counts["Infected"]
            + counts["Asymptomatic"]
        )

        self.peak_active_cases = max(self.peak_active_cases, active_cases)

        self.datacollector.collect(self)

    def count_states(self):
        counts = {
            "Susceptible": 0,
            "Exposed": 0,
            "Infected": 0,
            "Recovered": 0,
            "Dead": 0,
            "Asymptomatic": 0,
            "Vaccinated": 0,
        }

        for agent in self.schedule.agents:
            counts[agent.state] += 1

        return counts
    
    def count_age_groups(self):
        counts = {"child": 0, "adult": 0, "senior": 0}
        for agent in self.schedule.agents:
            counts[agent.age_group] += 1
        return counts