from mesa import Agent


class PersonAgent(Agent):
    def __init__(self, unique_id, model, state="Susceptible", age_group="adult"):
        super().__init__(model)

        self.unique_id = unique_id
        self.state = state
        self.days_in_state = 0
        self.home = None
        self.work = None
        self.age_group = age_group

        if self.age_group == "child":
            self.transmission_multiplier = 1.5
            self.susceptibility_multiplier = 1.2
        elif self.age_group == "senior":
            self.transmission_multiplier = 1.0
            self.susceptibility_multiplier = 1.4
        else:
            self.transmission_multiplier = 1.0
            self.susceptibility_multiplier = 1.0

    def move(self):
        if self.state == "Dead":
            return
        
        if self.state == "Infected":
            if self.random.random() < self.model.isolation_rate:
                target = self.home
            else:
                if self.model.step_count % 20 < 10:
                    target = self.work
                else:
                    target = self.home

        elif self.state == "Asymptomatic":
            if self.model.step_count % 20 < 10:
                target = self.work
            else:
                target = self.home

        else:
            if self.model.step_count % 20 < 10:
                target = self.work
            else:
                target = self.home

        self.model.grid.move_agent(self, target)

    def infect_others(self):
        if self.state == "Dead":
            return
        if self.state not in ["Infected", "Asymptomatic"]:
            return

        neighbors = self.model.grid.get_neighbors(
            self.pos,
            moore=True,
            include_center=True
        )

        for agent in neighbors:
            if agent is not self and agent.state == "Susceptible":
                transmission = self.transmission_multiplier

                if self.state == "Asymptomatic":
                    transmission *= self.model.asymptomatic_transmission_multiplier

                infection_chance = min(
                    1.0,
                    self.model.infection_probability
                    * transmission
                    * agent.susceptibility_multiplier
                )

                if self.random.random() < infection_chance:
                    agent.state = "Exposed"
                    agent.days_in_state = 0

    def update_health(self):
        if self.state == "Dead":
            return
        
        self.days_in_state += 1

        if self.state == "Exposed":
            if self.days_in_state >= self.model.incubation_time:
                if self.random.random() < self.model.asymptomatic_rate:
                    self.state = "Asymptomatic"
                else:
                    self.state = "Infected"
                self.days_in_state = 0

        elif self.state == "Infected":
            if self.days_in_state >= self.model.recovery_time:
                if self.age_group == "child":
                    mortality_rate = self.model.child_mortality_rate
                elif self.age_group == "senior":
                    mortality_rate = self.model.senior_mortality_rate
                else:
                    mortality_rate = self.model.adult_mortality_rate

                if self.random.random() < mortality_rate:
                    self.state = "Dead"
                else:
                    self.state = "Recovered"

        elif self.state == "Asymptomatic":
            if self.days_in_state >= self.model.recovery_time:
                self.state = "Recovered"

    def step(self):
        self.move()
        self.infect_others()
        self.update_health()