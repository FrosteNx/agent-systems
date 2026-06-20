def save_simulation_summary(path, content):
    with open(path, "w") as file:
        file.write(content)

    print(f"Saved: {path}")

def build_summary_metrics(
    config,
    model,
    metrics,
    experiment_id,
    timestamp,
    output_dir,
    log_file,
):
    return {
        "experiment_id": experiment_id,
        "timestamp": timestamp,
        "scenario_name": config.SCENARIO_NAME,
        "output_dir": output_dir,
        "log_file": log_file,

        "population": config.POPULATION,
        "initial_infected": config.INITIAL_INFECTED,

        "total_infections": model.total_infections,
        "peak_active_cases": model.peak_active_cases,

        **metrics,
    }

def build_simulation_summary(summary_lines):
    return "\n".join(summary_lines)

def build_summary_lines(
    config,
    model,
    metrics,
    experiment_id,
    timestamp,
    actual_steps,
    final_counts,
    execution_time_seconds,
    log_file,
):
    summary_lines = []

    summary_lines.append("Flu simulation summary")
    summary_lines.append("======================")
    summary_lines.append("")

    summary_lines.append("General information")
    summary_lines.append("-------------------")
    summary_lines.append(f"Experiment ID: {experiment_id}")
    summary_lines.append(f"Timestamp: {timestamp}")
    summary_lines.append(f"Scenario: {config.SCENARIO_NAME}")
    summary_lines.append(f"Population: {config.POPULATION}")
    summary_lines.append(f"Max steps: {config.SIMULATION_STEPS}")
    summary_lines.append(f"Actual steps: {actual_steps}")

    summary_lines.append("")
    summary_lines.append("Epidemic outcomes")
    summary_lines.append("-----------------")
    summary_lines.append(f"Peak active cases: {model.peak_active_cases}")
    summary_lines.append(f"Total infections: {model.total_infections}")
    summary_lines.append(f"Initial infections: {config.INITIAL_INFECTED}")
    summary_lines.append(f"Secondary infections: {metrics['secondary_infections']}")
    summary_lines.append(f"Attack rate: {metrics['attack_rate']:.2%}")
    summary_lines.append(f"Case fatality rate: {metrics['case_fatality_rate']:.2%}")
    summary_lines.append(f"Average Rt: {metrics['average_rt']:.2f}")

    summary_lines.append("")
    summary_lines.append("Transmission analysis")
    summary_lines.append("---------------------")
    summary_lines.append(f"Household infections: {metrics['total_household_infections']}")
    summary_lines.append(f"Household infection share: {metrics['household_infection_share']:.2%}")
    summary_lines.append(f"Community infections: {metrics['total_community_infections']}")
    summary_lines.append(f"Community infection share: {metrics['community_infection_share']:.2%}")
    summary_lines.append(f"Household/community share sum: {metrics['household_share_sum']:.2%}")
    summary_lines.append(f"Home infections: {metrics['total_home_infections']}")
    summary_lines.append(f"Home infection share: {metrics['home_infection_share']:.2%}")
    summary_lines.append(f"School infections: {metrics['total_school_infections']}")
    summary_lines.append(f"School infection share: {metrics['school_infection_share']:.2%}")
    summary_lines.append(f"Work infections: {metrics['total_work_infections']}")
    summary_lines.append(f"Work infection share: {metrics['work_infection_share']:.2%}")
    summary_lines.append(f"Other infections: {metrics['total_other_infections']}")
    summary_lines.append(f"Other infection share: {metrics['other_infection_share']:.2%}")
    summary_lines.append(f"Location share sum: {metrics['location_share_sum']:.2%}")

    summary_lines.append("")
    summary_lines.append("Intervention outcomes")
    summary_lines.append("---------------------")
    summary_lines.append(f"Masks enabled: {config.MASKS_ENABLED}")
    summary_lines.append(f"Mask compliance: {config.MASK_COMPLIANCE:.2%}")
    summary_lines.append(f"Mask transmission reduction: {config.MASK_TRANSMISSION_REDUCTION:.2%}")
    summary_lines.append(f"Mask protected contacts: {metrics['total_mask_protected_contacts']}")
    summary_lines.append(f"Quarantine enabled: {config.QUARANTINE_ENABLED}")
    summary_lines.append(f"Quarantine compliance: {config.QUARANTINE_COMPLIANCE:.2%}")
    summary_lines.append(f"Total quarantined agent-steps: {metrics['total_quarantined_agents']}")
    summary_lines.append(f"Total quarantined people: {model.total_quarantined_people}")
    summary_lines.append(f"Quarantine rate: {metrics['quarantine_rate']:.2%}")
    summary_lines.append(f"Total detected infections: {model.total_detected_infections}")
    summary_lines.append(f"Detection rate: {metrics['detection_rate']:.2%}")
    summary_lines.append(f"Undetected infections: {metrics['undetected_infections']}")
    summary_lines.append(f"Undetected rate: {metrics['undetected_rate']:.2%}")
    summary_lines.append(f"Total asymptomatic infections: {model.total_asymptomatic_infections}")
    summary_lines.append(f"Observed asymptomatic rate: {metrics['asymptomatic_rate_observed']:.2%}")

    summary_lines.append("")
    summary_lines.append("Vaccination campaign")
    summary_lines.append("--------------------")
    summary_lines.append(f"Auto vaccination campaign: {config.AUTO_VACCINATION_CAMPAIGN}")
    summary_lines.append(f"Vaccination campaign threshold: {config.VACCINATION_CAMPAIGN_THRESHOLD}")
    summary_lines.append(f"Daily vaccination capacity: {config.DAILY_VACCINATION_CAPACITY}")
    summary_lines.append(f"Vaccination campaign start step: {model.vaccination_campaign_start_step}")
    summary_lines.append(f"Vaccination campaign end step: {model.vaccination_campaign_end_step}")
    summary_lines.append(f"Vaccination campaign duration: {metrics['vaccination_campaign_duration']}")
    summary_lines.append(f"Initial vaccinations: {model.initial_vaccinations}")
    summary_lines.append(f"Total vaccinations: {metrics['total_vaccinations']}")
    summary_lines.append(f"Vaccination coverage: {metrics['vaccination_coverage']:.2%}")
    summary_lines.append(f"Total campaign vaccinations: {model.total_campaign_vaccinations}")
    summary_lines.append(f"Vaccination campaign activation count: {model.vaccination_campaign_activation_count}")
    summary_lines.append(f"Breakthrough infections: {model.vaccinated_breakthrough_infections}")
    summary_lines.append(f"Breakthrough infection rate: {metrics['breakthrough_infection_rate']:.2%}")
    summary_lines.append(f"Vaccinated infection rate: {metrics['vaccinated_infection_rate']:.2%}")
    summary_lines.append(f"Unvaccinated infection rate: {metrics['unvaccinated_infection_rate']:.2%}")
    summary_lines.append(f"Observed vaccine effectiveness: {metrics['observed_vaccine_effectiveness']:.2%}")
    summary_lines.append(f"Child campaign vaccinations: {model.child_campaign_vaccinations}")
    summary_lines.append(f"Adult campaign vaccinations: {model.adult_campaign_vaccinations}")
    summary_lines.append(f"Senior campaign vaccinations: {model.senior_campaign_vaccinations}")
    summary_lines.append(f"Child vaccination coverage: {metrics['child_vaccination_coverage']:.2%}")
    summary_lines.append(f"Adult vaccination coverage: {metrics['adult_vaccination_coverage']:.2%}")
    summary_lines.append(f"Senior vaccination coverage: {metrics['senior_vaccination_coverage']:.2%}")

    summary_lines.append("")
    summary_lines.append("Dynamic policies")
    summary_lines.append("----------------")
    summary_lines.append(f"Auto lockdown: {config.AUTO_LOCKDOWN}")
    summary_lines.append(f"Lockdown threshold: {config.LOCKDOWN_THRESHOLD}")
    summary_lines.append(f"Lockdown release threshold: {config.LOCKDOWN_RELEASE_THRESHOLD}")
    summary_lines.append(f"Lockdown start step: {model.lockdown_start_step}")
    summary_lines.append(f"Lockdown end step: {model.lockdown_end_step}")
    summary_lines.append(f"Lockdown duration: {metrics['lockdown_duration']}")
    summary_lines.append(f"Lockdown activation count: {model.lockdown_activation_count}")

    summary_lines.append(f"Auto school closure: {config.AUTO_SCHOOL_CLOSURE}")
    summary_lines.append(f"School closure threshold: {config.SCHOOL_CLOSURE_THRESHOLD}")
    summary_lines.append(f"School reopen threshold: {config.SCHOOL_REOPEN_THRESHOLD}")
    summary_lines.append(f"School closure start step: {model.school_closure_start_step}")
    summary_lines.append(f"School closure end step: {model.school_closure_end_step}")
    summary_lines.append(f"School closure duration: {metrics['school_closure_duration']}")
    summary_lines.append(f"School closure count: {model.school_closure_count}")

    summary_lines.append(f"Auto work closure: {config.AUTO_WORK_CLOSURE}")
    summary_lines.append(f"Work closure threshold: {config.WORK_CLOSURE_THRESHOLD}")
    summary_lines.append(f"Work reopen threshold: {config.WORK_REOPEN_THRESHOLD}")
    summary_lines.append(f"Work closure start step: {model.work_closure_start_step}")
    summary_lines.append(f"Work closure end step: {model.work_closure_end_step}")
    summary_lines.append(f"Work closure duration: {metrics['work_closure_duration']}")
    summary_lines.append(f"Work closure count: {model.work_closure_count}")

    summary_lines.append(f"Auto mask compliance: {config.AUTO_MASK_COMPLIANCE}")
    summary_lines.append(f"Mask compliance threshold: {config.MASK_COMPLIANCE_THRESHOLD}")
    summary_lines.append(f"Mask relaxation threshold: {config.MASK_RELAXATION_THRESHOLD}")
    summary_lines.append(f"Final mask compliance: {model.mask_compliance_active:.2%}")
    summary_lines.append(f"Mask compliance start step: {model.mask_compliance_start_step}")
    summary_lines.append(f"Mask compliance end step: {model.mask_compliance_end_step}")
    summary_lines.append(f"Mask compliance duration: {metrics['mask_compliance_duration']}")
    summary_lines.append(f"Mask compliance activation count: {model.mask_compliance_activation_count}")

    summary_lines.append(f"Auto testing rate: {config.AUTO_TESTING_RATE}")
    summary_lines.append(f"Testing rate threshold: {config.TESTING_RATE_THRESHOLD}")
    summary_lines.append(f"Testing relaxation threshold: {config.TESTING_RELAXATION_THRESHOLD}")
    summary_lines.append(f"Final testing rate: {model.testing_rate_active:.2%}")
    summary_lines.append(f"Testing rate start step: {model.testing_rate_start_step}")
    summary_lines.append(f"Testing rate end step: {model.testing_rate_end_step}")
    summary_lines.append(f"Testing rate duration: {metrics['testing_rate_duration']}")
    summary_lines.append(f"Testing rate activation count: {model.testing_rate_activation_count}")

    summary_lines.append(f"Auto quarantine compliance: {config.AUTO_QUARANTINE_COMPLIANCE}")
    summary_lines.append(f"Quarantine compliance threshold: {config.QUARANTINE_COMPLIANCE_THRESHOLD}")
    summary_lines.append(f"Quarantine relaxation threshold: {config.QUARANTINE_RELAXATION_THRESHOLD}")
    summary_lines.append(f"Final quarantine compliance: {model.quarantine_compliance_active:.2%}")
    summary_lines.append(f"Quarantine compliance start step: {model.quarantine_compliance_start_step}")
    summary_lines.append(f"Quarantine compliance end step: {model.quarantine_compliance_end_step}")
    summary_lines.append(f"Quarantine compliance duration: {metrics['quarantine_compliance_duration']}")
    summary_lines.append(f"Quarantine compliance activation count: {model.quarantine_compliance_activation_count}")

    summary_lines.append("")
    summary_lines.append("Mobility policies")
    summary_lines.append("-----------------")
    summary_lines.append(f"Base senior mobility: {config.SENIOR_MOBILITY:.2%}")
    summary_lines.append(f"Low senior mobility: {config.LOW_SENIOR_MOBILITY:.2%}")
    summary_lines.append(f"Senior mobility reduction start step: {model.senior_mobility_reduction_start_step}")
    summary_lines.append(f"Senior mobility reduction end step: {model.senior_mobility_reduction_end_step}")
    summary_lines.append(f"Senior mobility reduction duration: {metrics['senior_mobility_reduction_duration']}")
    summary_lines.append(f"Senior mobility reduction count: {model.senior_mobility_reduction_count}")
    summary_lines.append(f"Base child mobility: {config.CHILD_MOBILITY:.2%}")
    summary_lines.append(f"Low child mobility: {config.LOW_CHILD_MOBILITY:.2%}")
    summary_lines.append(f"Child mobility reduction start step: {model.child_mobility_reduction_start_step}")
    summary_lines.append(f"Child mobility reduction end step: {model.child_mobility_reduction_end_step}")
    summary_lines.append(f"Child mobility reduction duration: {metrics['child_mobility_reduction_duration']}")
    summary_lines.append(f"Child mobility reduction count: {model.child_mobility_reduction_count}")

    summary_lines.append("")
    summary_lines.append("Age-group analysis")
    summary_lines.append("------------------")
    summary_lines.append(f"Child infections: {model.child_infections}")
    summary_lines.append(f"Child attack rate: {metrics['child_attack_rate']:.2%}")
    summary_lines.append(f"Child deaths: {model.child_deaths}")
    summary_lines.append(f"Child death rate: {metrics['child_death_rate']:.2%}")
    summary_lines.append(f"Adult infections: {model.adult_infections}")
    summary_lines.append(f"Adult attack rate: {metrics['adult_attack_rate']:.2%}")
    summary_lines.append(f"Adult deaths: {model.adult_deaths}")
    summary_lines.append(f"Adult death rate: {metrics['adult_death_rate']:.2%}")
    summary_lines.append(f"Senior infections: {model.senior_infections}")
    summary_lines.append(f"Senior attack rate: {metrics['senior_attack_rate']:.2%}")
    summary_lines.append(f"Senior deaths: {model.senior_deaths}")
    summary_lines.append(f"Senior death rate: {metrics['senior_death_rate']:.2%}")

    summary_lines.append("")
    summary_lines.append("Final state counts")
    summary_lines.append("------------------")
    for state, count in final_counts.items():
        summary_lines.append(f"{state}: {count}")

    summary_lines.append("")
    summary_lines.append("Performance")
    summary_lines.append("-----------")
    summary_lines.append(f"Execution time (seconds): {execution_time_seconds:.2f}")
    summary_lines.append(f"Log file: {log_file}")

    return summary_lines

def save_full_simulation_summary(
    config,
    model,
    metrics,
    experiment_id,
    timestamp,
    actual_steps,
    final_counts,
    execution_time_seconds,
    log_file,
    data_dir,
):
    summary_lines = build_summary_lines(
        config,
        model,
        metrics,
        experiment_id,
        timestamp,
        actual_steps,
        final_counts,
        execution_time_seconds,
        log_file,
    )

    summary_text = build_simulation_summary(summary_lines)

    save_simulation_summary(
        f"{data_dir}/simulation_summary.txt",
        summary_text
    )