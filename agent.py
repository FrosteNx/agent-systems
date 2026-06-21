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

        self.initialize_age_parameters()

    def initialize_age_parameters(self):
        if self.age_group == "child":
            self.transmission_multiplier = 1.5
            self.susceptibility_multiplier = 1.2

        elif self.age_group == "senior":
            self.transmission_multiplier = 1.0
            self.susceptibility_multiplier = 1.4

        else:
            self.transmission_multiplier = 1.0
            self.susceptibility_multiplier = 1.0

    def move_home(self):
        self.model.grid.move_agent(self, self.home)
        self.current_location_type = "home"

    def must_stay_home_due_to_policy(self):
        if self.model.lockdown_active:
            if self.random.random() > self.model.lockdown_mobility:
                return True

        if self.age_group == "senior":
            if self.random.random() > self.model.senior_mobility_active:
                return True

        if self.age_group == "child":
            if self.random.random() > self.model.child_mobility_active:
                return True

        if self.age_group == "child" and self.model.school_closed_active:
            return True

        if self.age_group == "adult" and self.model.work_closed_active:
            return True

        return False
    
    def is_quarantined_this_step(self):
        if not self.model.quarantine_enabled:
            return False

        if self.state != "Infected":
            return False

        if not self.is_detected:
            return False

        return self.random.random() < self.model.quarantine_compliance_active
    
    def apply_quarantine(self):
        self.move_home()
        self.model.quarantined_agents += 1

        if not self.was_quarantined:
            self.was_quarantined = True
            self.model.total_quarantined_people += 1

    def get_daily_target(self):
        if self.state == "Infected":
            if self.random.random() < self.model.isolation_rate:
                return self.home

        if self.model.step_count % 20 < 10:
            return self.work

        return self.home
    
    def update_location_type(self, target):
        if target == self.home:
            self.current_location_type = "home"
        elif self.age_group == "child":
            self.current_location_type = "school"
        else:
            self.current_location_type = "work"

    def move(self):
        if self.state == "Dead":
            return

        if self.must_stay_home_due_to_policy():
            self.move_home()
            return

        if self.is_quarantined_this_step():
            self.apply_quarantine()
            return

        target = self.get_daily_target()
        self.model.grid.move_agent(self, target)
        self.update_location_type(target)

    def can_infect(self):
        return self.state in ["Infected", "Asymptomatic"]
    
    def get_infection_candidates(self):
        neighbors = self.model.grid.get_neighbors(
            self.pos,
            moore=True,
            include_center=True
        )

        return [
            agent for agent in neighbors
            if agent is not self
            and agent.state in ["Susceptible", "Vaccinated"]
        ]
    
    def calculate_base_infection_chance(self, target_agent):
        transmission = self.transmission_multiplier

        if self.state == "Asymptomatic":
            transmission *= self.model.asymptomatic_transmission_multiplier

        infection_chance = (
            self.model.infection_probability
            * transmission
            * target_agent.susceptibility_multiplier
        )

        return min(1.0, infection_chance)
    
    def apply_detected_modifier(self, infection_chance):
        if self.is_detected:
            infection_chance *= self.model.detected_transmission_multiplier

        return infection_chance
    
    def apply_mask_modifier(self, infection_chance):
        if (
            self.model.masks_enabled
            and self.current_location_type != "home"
            and self.random.random() < self.model.mask_compliance_active
        ):
            infection_chance *= (1 - self.model.mask_transmission_reduction)
            self.model.mask_protected_contacts += 1

        return infection_chance
    
    def apply_household_modifier(self, target_agent, infection_chance):
        if self.household_id == target_agent.household_id:
            infection_chance *= self.model.household_transmission_multiplier
            infection_chance = min(1.0, infection_chance)

        return infection_chance
    
    def apply_vaccine_modifier(self, target_agent, infection_chance):
        if target_agent.state == "Vaccinated":
            infection_chance *= (1 - self.model.vaccine_effectiveness)

        return infection_chance
    
    def calculate_infection_chance(self, target_agent):
        infection_chance = self.calculate_base_infection_chance(target_agent)

        infection_chance = self.apply_detected_modifier(infection_chance)
        infection_chance = self.apply_mask_modifier(infection_chance)

        infection_chance = self.apply_household_modifier(
            target_agent,
            infection_chance
        )

        infection_chance = self.apply_vaccine_modifier(
            target_agent,
            infection_chance
        )

        return infection_chance
    
    def infect_agent(self, target_agent):
        if target_agent.state == "Vaccinated":
            self.model.vaccinated_breakthrough_infections += 1

        target_agent.state = "Exposed"
        target_agent.days_in_state = 0

        if target_agent.age_group == "child":
            self.model.child_infections += 1
        elif target_agent.age_group == "adult":
            self.model.adult_infections += 1
        elif target_agent.age_group == "senior":
            self.model.senior_infections += 1

        self.model.new_infections += 1
        self.model.total_infections += 1

    def record_location_infection(self):
        if self.current_location_type == "home":
            self.model.home_infections += 1
        elif self.current_location_type == "school":
            self.model.school_infections += 1
        elif self.current_location_type == "work":
            self.model.work_infections += 1
        else:
            self.model.other_infections += 1

    def record_transmission_type(self, target_agent):
        if self.household_id == target_agent.household_id:
            self.model.household_infections += 1
        else:
            self.model.community_infections += 1

    def infect_others(self):
        if not self.can_infect():
            return

        for agent in self.get_infection_candidates():
            infection_chance = self.calculate_infection_chance(agent)

            if self.random.random() < infection_chance:
                self.infect_agent(agent)

                self.record_location_infection()

                self.record_transmission_type(agent)

    def progress_exposed_state(self):
        if self.random.random() < self.model.asymptomatic_rate:
            self.state = "Asymptomatic"
            self.model.total_asymptomatic_infections += 1
        else:
            self.state = "Infected"

            if self.random.random() < self.model.testing_rate_active:
                if not self.is_detected:
                    self.is_detected = True
                    self.model.total_detected_infections += 1

        self.days_in_state = 0

    def get_mortality_rate(self):
        if self.age_group == "child":
            return self.model.child_mortality_rate

        if self.age_group == "senior":
            return self.model.senior_mortality_rate

        return self.model.adult_mortality_rate
    
    def die(self):
        self.state = "Dead"

        if self.age_group == "child":
            self.model.child_deaths += 1
        elif self.age_group == "adult":
            self.model.adult_deaths += 1
        elif self.age_group == "senior":
            self.model.senior_deaths += 1

    def recover(self):
        self.state = "Recovered"
        self.is_detected = False

    def progress_infected_state(self):
        if self.days_in_state < self.model.recovery_time:
            return

        mortality_rate = self.get_mortality_rate()

        if self.random.random() < mortality_rate:
            self.die()
            return

        self.recover()

    def progress_asymptomatic_state(self):
        if self.days_in_state >= self.model.recovery_time:
            self.recover()

    def update_health(self):
        
        self.days_in_state += 1

        if self.state == "Exposed":
            if self.days_in_state >= self.model.incubation_time:
                self.progress_exposed_state()

        elif self.state == "Infected":
            self.progress_infected_state()

        elif self.state == "Asymptomatic":
            self.progress_asymptomatic_state()

    def step(self):
        self.move()
        self.infect_others()
        self.update_health()