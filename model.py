from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation

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
        vaccination_rate=0.2
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

        for i in range(self.num_agents):
            if i < initial_infected:
                state = "Infected"
            elif random.random() < self.vaccination_rate:
                state = "Recovered"  
            else:
                state = "Susceptible"

            if self.random.random() < 0.25:
                age_group = "child"
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

        self.running = True

    def step(self):
        self.step_count += 1
        self.schedule.step()

    def count_states(self):
        counts = {
            "Susceptible": 0,
            "Exposed": 0,
            "Infected": 0,
            "Recovered": 0
        }

        for agent in self.schedule.agents:
            counts[agent.state] += 1

        return counts
    
    def count_age_groups(self):
        counts = {"child": 0, "adult": 0}
        for agent in self.schedule.agents:
            counts[agent.age_group] += 1
        return counts