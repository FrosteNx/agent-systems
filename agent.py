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
        self.current_location_type = "home"
        self.is_detected = False
        self.was_quarantined = False

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
        
        if self.model.lockdown_active:
            if self.random.random() > self.model.lockdown_mobility:
                target = self.home
                self.model.grid.move_agent(self, target)
                self.current_location_type = "home"
                return
        
        if self.age_group == "senior":
            if self.random.random() > self.model.senior_mobility:
                target = self.home
                self.model.grid.move_agent(self, target)
                self.current_location_type = "home"
                return
            
        if self.age_group == "child":
            if self.random.random() > self.model.child_mobility:
                target = self.home
                self.model.grid.move_agent(self, target)
                self.current_location_type = "home"
                return
            
        if self.age_group == "child" and self.model.school_closed:
            target = self.home
            self.model.grid.move_agent(self, target)
            self.current_location_type = "home"
            return
        
        if self.age_group == "adult" and self.model.work_closed:
            target = self.home
            self.model.grid.move_agent(self, target)
            self.current_location_type = "home"
            return
        
        if self.state == "Infected" and self.model.quarantine_enabled and self.is_detected:
            if self.random.random() < self.model.quarantine_compliance:
                target = self.home
                self.model.grid.move_agent(self, target)
                self.current_location_type = "home"
                self.model.quarantined_agents += 1

                if not self.was_quarantined:
                    self.was_quarantined = True
                    self.model.total_quarantined_people += 1
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

        if target == self.home:
            self.current_location_type = "home"
        elif self.age_group == "child":
            self.current_location_type = "school"
        else:
            self.current_location_type = "work"

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
            if agent is not self and agent.state in ["Susceptible", "Vaccinated"]:
                transmission = self.transmission_multiplier

                if self.state == "Asymptomatic":
                    transmission *= self.model.asymptomatic_transmission_multiplier

                infection_chance = min(
                    1.0,
                    self.model.infection_probability
                    * transmission
                    * agent.susceptibility_multiplier
                )
                if self.is_detected:
                    infection_chance *= (
                        self.model.detected_transmission_multiplier
                    )

                if (
                    self.model.masks_enabled
                    and self.current_location_type != "home"
                    and self.random.random() < self.model.mask_compliance
                ):
                    infection_chance *= (1 - self.model.mask_transmission_reduction)
                    self.model.mask_protected_contacts += 1

                if self.household_id == agent.household_id:
                    infection_chance *= self.model.household_transmission_multiplier
                    infection_chance = min(1.0, infection_chance)

                if agent.state == "Vaccinated":
                    infection_chance *= (1 - self.model.vaccine_effectiveness)

                if self.random.random() < infection_chance:
                    agent.state = "Exposed"
                    agent.days_in_state = 0

                    if agent.age_group == "child":
                        self.model.child_infections += 1
                    elif agent.age_group == "adult":
                        self.model.adult_infections += 1
                    elif agent.age_group == "senior":
                        self.model.senior_infections += 1

                    self.model.new_infections += 1
                    self.model.total_infections += 1

                    if self.current_location_type == "home":
                        self.model.home_infections += 1
                    elif self.current_location_type == "school":
                        self.model.school_infections += 1
                    elif self.current_location_type == "work":
                        self.model.work_infections += 1
                    else:
                        self.model.other_infections += 1

                    if self.household_id == agent.household_id:
                        self.model.household_infections += 1
                    else:
                        self.model.community_infections += 1

    def update_health(self):
        
        self.days_in_state += 1

        if self.state == "Exposed":
            if self.days_in_state >= self.model.incubation_time:
                if self.random.random() < self.model.asymptomatic_rate:
                    self.state = "Asymptomatic"
                    self.model.total_asymptomatic_infections += 1
                else:
                    self.state = "Infected"
                    if self.random.random() < self.model.testing_rate:
                        if not self.is_detected:
                            self.is_detected = True
                            self.model.total_detected_infections += 1
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
                    if self.age_group == "child":
                        self.model.child_deaths += 1
                    elif self.age_group == "adult":
                        self.model.adult_deaths += 1
                    elif self.age_group == "senior":
                        self.model.senior_deaths += 1
                    return
                else:
                    self.state = "Recovered"
                    self.is_detected = False

        elif self.state == "Asymptomatic":
            if self.days_in_state >= self.model.recovery_time:
                self.state = "Recovered"

    def step(self):
        self.move()
        self.infect_others()
        self.update_health()