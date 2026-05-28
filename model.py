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
        random_seed=42,
        household_size=4,
        household_transmission_multiplier=1.5,
        senior_mobility=0.4,
        child_mobility=1.0,
        school_closed=False,
        work_closed=False,
        lockdown=False,
        lockdown_mobility=0.2,
        masks_enabled=False,
        mask_transmission_reduction=0.4,
        mask_compliance=0.7,
        quarantine_enabled=False,
        quarantine_compliance=0.9,
        testing_rate=0.5,
        detected_transmission_multiplier=0.3
    ):
        super().__init__()

        self.num_agents = population
        self.grid = MultiGrid(width, height, torus=True)
        self.schedule = RandomActivation(self)
        self.step_count = 0
        self.schools = [(5, 5), (15, 15)]
        self.household_size = household_size

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
        self.new_infections = 0
        self.total_infections = initial_infected
        self.household_transmission_multiplier = household_transmission_multiplier
        self.household_infections = 0
        self.community_infections = 0
        self.home_infections = 0
        self.school_infections = 0
        self.work_infections = 0
        self.other_infections = 0
        self.senior_mobility = senior_mobility
        self.child_mobility = child_mobility
        self.school_closed = school_closed
        self.work_closed = work_closed
        self.lockdown = lockdown
        self.lockdown_mobility = lockdown_mobility
        self.masks_enabled = masks_enabled
        self.mask_transmission_reduction = mask_transmission_reduction
        self.mask_compliance = mask_compliance
        self.mask_protected_contacts = 0
        self.quarantine_enabled = quarantine_enabled
        self.quarantine_compliance = quarantine_compliance
        self.quarantined_agents = 0
        self.testing_rate = testing_rate
        self.detected_transmission_multiplier = detected_transmission_multiplier
        self.total_detected_infections = 0
        self.total_quarantined_people = 0
        self.total_asymptomatic_infections = 0
        self.child_deaths = 0
        self.adult_deaths = 0
        self.senior_deaths = 0
        self.child_infections = 0
        self.adult_infections = 0
        self.senior_infections = 0

        self.peak_active_cases = 0
        self.random_seed = random_seed

        random.seed(self.random_seed)

        households = []

        for h in range((self.num_agents // self.household_size) + 1):
            home_x = self.random.randrange(self.grid.width)
            home_y = self.random.randrange(self.grid.height)

            households.append({
                "id": f"H_{h}",
                "home": (home_x, home_y)
            })

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

            household = households[i // self.household_size]

            agent.home = household["home"]
            agent.household_id = household["id"]

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
                "NewInfections": lambda m: m.new_infections,
                "Rt": lambda m: (
                    m.new_infections /
                    max(
                        1,
                        m.count_states()["Infected"]
                        + m.count_states()["Asymptomatic"]
                    )
                ),
                "HouseholdInfections": lambda m: m.household_infections,
                "CommunityInfections": lambda m: m.community_infections,
                "HomeInfections": lambda m: m.home_infections,
                "SchoolInfections": lambda m: m.school_infections,
                "WorkInfections": lambda m: m.work_infections,
                "OtherInfections": lambda m: m.other_infections,
                "MaskProtectedContacts": lambda m: m.mask_protected_contacts,
                "QuarantinedAgents": lambda m: m.quarantined_agents,
                "DetectedInfected": lambda m: sum(
                    1 for agent in m.schedule.agents
                    if agent.state == "Infected" and agent.is_detected
                ),
                "UndetectedInfected": lambda m: sum(
                    1 for agent in m.schedule.agents
                    if agent.state == "Infected" and not agent.is_detected
                ),
            }
        )

        self.running = True

    def step(self):
        self.step_count += 1
        self.new_infections = 0
        self.household_infections = 0
        self.community_infections = 0
        self.home_infections = 0
        self.school_infections = 0
        self.work_infections = 0
        self.other_infections = 0
        self.mask_protected_contacts = 0
        self.quarantined_agents = 0
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