from mesa import Agent




class PersonAgent(Agent):
    def __init__(self, unique_id, model, state="Susceptible"):
        super().__init__(unique_id, model)
        self.state = state
        self.days_in_state = 0
        self.home = None
        self.work = None

    def move(self):
        if self.state == "Infected":
            target = self.home
        else:
            if self.model.step_count % 20 < 10:
                target = self.work
            else:
                target = self.home

        self.model.grid.move_agent(self, target)

    def infect_others(self):
        if self.state != "Infected":
            return

        neighbors = self.model.grid.get_neighbors(
            self.pos,
            moore=True,
            include_center=True
        )

        for agent in neighbors:
            if agent is not self and agent.state == "Susceptible":
                if self.random.random() < self.model.infection_probability:
                    agent.state = "Exposed"
                    agent.days_in_state = 0

    def update_health(self):
        self.days_in_state += 1

        if self.state == "Exposed":
            if self.days_in_state >= self.model.incubation_time:
                self.state = "Infected"
                self.days_in_state = 0

        elif self.state == "Infected":
            if self.days_in_state >= self.model.recovery_time:
                self.state = "Recovered"

    def step(self):
        self.move()
        self.infect_others()
        self.update_health()