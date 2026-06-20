def calculate_attack_rate(total_infections, population):
    if population > 0:
        return total_infections / population

    return 0

def calculate_case_fatality_rate(dead_count, total_infections):
    if total_infections > 0:
        return dead_count / total_infections

    return 0

def calculate_rate(numerator, denominator):
    if denominator > 0:
        return numerator / denominator

    return 0

def calculate_duration(start_step, end_step, actual_steps):
    if start_step is not None and end_step is not None:
        return end_step - start_step

    if start_step is not None:
        return actual_steps - start_step

    return 0

def calculate_infection_shares(secondary_infections, counts):
    return {
        key: calculate_rate(value, secondary_infections)
        for key, value in counts.items()
    }

def calculate_age_group_metrics(model, age_counts):
    vaccinated_by_age = {
        "child": 0,
        "adult": 0,
        "senior": 0,
    }

    for agent in model.schedule.agents:
        if agent.state == "Vaccinated":
            vaccinated_by_age[agent.age_group] += 1

    return {
        "child_vaccination_coverage": calculate_rate(
            vaccinated_by_age["child"],
            age_counts["child"]
        ),
        "adult_vaccination_coverage": calculate_rate(
            vaccinated_by_age["adult"],
            age_counts["adult"]
        ),
        "senior_vaccination_coverage": calculate_rate(
            vaccinated_by_age["senior"],
            age_counts["senior"]
        ),
        "child_attack_rate": calculate_rate(
            model.child_infections,
            age_counts["child"]
        ),
        "adult_attack_rate": calculate_rate(
            model.adult_infections,
            age_counts["adult"]
        ),
        "senior_attack_rate": calculate_rate(
            model.senior_infections,
            age_counts["senior"]
        ),
        "child_death_rate": calculate_rate(
            model.child_deaths,
            age_counts["child"]
        ),
        "adult_death_rate": calculate_rate(
            model.adult_deaths,
            age_counts["adult"]
        ),
        "senior_death_rate": calculate_rate(
            model.senior_deaths,
            age_counts["senior"]
        ),
    }

def calculate_vaccination_metrics(model, population):
    total_vaccinations = (
        model.initial_vaccinations
        + model.total_campaign_vaccinations
    )

    vaccination_coverage = calculate_rate(
        total_vaccinations,
        population
    )

    breakthrough_infection_rate = calculate_rate(
        model.vaccinated_breakthrough_infections,
        total_vaccinations
    )

    vaccinated_infection_rate = calculate_rate(
        model.vaccinated_breakthrough_infections,
        total_vaccinations
    )

    unvaccinated_population = population - total_vaccinations

    unvaccinated_infections = (
        model.total_infections
        - model.vaccinated_breakthrough_infections
    )

    unvaccinated_infection_rate = calculate_rate(
        unvaccinated_infections,
        unvaccinated_population
    )

    observed_vaccine_effectiveness = (
        1
        - calculate_rate(
            vaccinated_infection_rate,
            unvaccinated_infection_rate
        )
    )

    return {
        "total_vaccinations": total_vaccinations,
        "vaccination_coverage": vaccination_coverage,
        "breakthrough_infection_rate": breakthrough_infection_rate,
        "vaccinated_infection_rate": vaccinated_infection_rate,
        "unvaccinated_infection_rate": unvaccinated_infection_rate,
        "observed_vaccine_effectiveness": observed_vaccine_effectiveness,
    }

def calculate_policy_durations(model, actual_steps):
    return {
        "lockdown_duration": calculate_duration(
            model.lockdown_start_step,
            model.lockdown_end_step,
            actual_steps
        ),
        "school_closure_duration": calculate_duration(
            model.school_closure_start_step,
            model.school_closure_end_step,
            actual_steps
        ),
        "mask_compliance_duration": calculate_duration(
            model.mask_compliance_start_step,
            model.mask_compliance_end_step,
            actual_steps
        ),
        "testing_rate_duration": calculate_duration(
            model.testing_rate_start_step,
            model.testing_rate_end_step,
            actual_steps
        ),
        "quarantine_compliance_duration": calculate_duration(
            model.quarantine_compliance_start_step,
            model.quarantine_compliance_end_step,
            actual_steps
        ),
        "work_closure_duration": calculate_duration(
            model.work_closure_start_step,
            model.work_closure_end_step,
            actual_steps
        ),
        "senior_mobility_reduction_duration": calculate_duration(
            model.senior_mobility_reduction_start_step,
            model.senior_mobility_reduction_end_step,
            actual_steps
        ),
        "child_mobility_reduction_duration": calculate_duration(
            model.child_mobility_reduction_start_step,
            model.child_mobility_reduction_end_step,
            actual_steps
        ),
        "vaccination_campaign_duration": calculate_duration(
            model.vaccination_campaign_start_step,
            model.vaccination_campaign_end_step,
            actual_steps
        ),
    }

def calculate_epidemic_metrics(model, results, final_counts, population, initial_infected):
    total_infections = model.total_infections
    secondary_infections = total_infections - initial_infected
    dead_count = final_counts["Dead"]

    return {
        "attack_rate": calculate_attack_rate(total_infections, population),
        "case_fatality_rate": calculate_case_fatality_rate(
            dead_count,
            total_infections
        ),
        "average_rt": results["Rt"].mean(),
        "secondary_infections": secondary_infections,
    }

def calculate_infection_totals(results):
    return {
        "total_household_infections": results["HouseholdInfections"].sum(),
        "total_community_infections": results["CommunityInfections"].sum(),
        "total_home_infections": results["HomeInfections"].sum(),
        "total_school_infections": results["SchoolInfections"].sum(),
        "total_work_infections": results["WorkInfections"].sum(),
        "total_other_infections": results["OtherInfections"].sum(),
        "total_quarantined_agents": results["QuarantinedAgents"].sum(),
        "total_mask_protected_contacts": results["MaskProtectedContacts"].sum(),
    }

def calculate_transmission_metrics(
    secondary_infections,
    total_household_infections,
    total_community_infections,
    total_home_infections,
    total_school_infections,
    total_work_infections,
    total_other_infections,
):
    transmission_shares = calculate_infection_shares(
        secondary_infections,
        {
            "household": total_household_infections,
            "community": total_community_infections,
        }
    )

    location_shares = calculate_infection_shares(
        secondary_infections,
        {
            "home": total_home_infections,
            "school": total_school_infections,
            "work": total_work_infections,
            "other": total_other_infections,
        }
    )

    return {
        "household_infection_share": transmission_shares["household"],
        "community_infection_share": transmission_shares["community"],
        "home_infection_share": location_shares["home"],
        "school_infection_share": location_shares["school"],
        "work_infection_share": location_shares["work"],
        "other_infection_share": location_shares["other"],
        "household_share_sum": sum(transmission_shares.values()),
        "location_share_sum": sum(location_shares.values()),
    }

def calculate_intervention_metrics(model):
    undetected_infections = (
        model.total_infections
        - model.total_detected_infections
    )

    return {
        "detection_rate": calculate_rate(
            model.total_detected_infections,
            model.total_infections
        ),
        "quarantine_rate": calculate_rate(
            model.total_quarantined_people,
            model.total_infections
        ),
        "undetected_infections": undetected_infections,
        "undetected_rate": calculate_rate(
            undetected_infections,
            model.total_infections
        ),
        "asymptomatic_rate_observed": calculate_rate(
            model.total_asymptomatic_infections,
            model.total_infections
        ),
    }