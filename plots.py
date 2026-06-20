import matplotlib.pyplot as plt
import config

def save_plot(path):
    plt.tight_layout()
    plt.savefig(path, dpi=300)
    print(f"Saved: {path}")
    plt.show()

def plot_epidemic_curve(results, plots_dir):
    plt.figure()

    plt.plot(results["Susceptible"], label="Susceptible")
    plt.plot(results["Exposed"], label="Exposed")
    plt.plot(results["Infected"], label="Infected")
    plt.plot(results["Asymptomatic"], label="Asymptomatic")
    plt.plot(results["Recovered"], label="Recovered")
    plt.plot(results["Dead"], label="Dead")
    plt.plot(results["Vaccinated"], label="Vaccinated")

    plt.xlabel("Step")
    plt.ylabel("Number of people")
    plt.title("Flu epidemic simulation")
    plt.legend()

    save_plot(f"{plots_dir}/epidemic_curve.png")

def plot_rt_curve(results, plots_dir):
    plt.figure()

    plt.plot(results["Rt"], label="Rt")
    plt.axhline(y=1, linestyle="--", label="Rt = 1")

    plt.xlabel("Step")
    plt.ylabel("Rt")
    plt.title("Effective reproduction number")
    plt.legend()

    save_plot(f"{plots_dir}/rt_curve.png")

def plot_infections_curve(results, plots_dir):
    plt.figure()

    plt.plot(results["ActiveCases"], label="Active cases")
    plt.plot(results["NewInfections"], label="New infections")
    plt.plot(results["HouseholdInfections"], label="Household infections")
    plt.plot(results["CommunityInfections"], label="Community infections")
    plt.plot(results["HomeInfections"], label="Home infections")
    plt.plot(results["SchoolInfections"], label="School infections")
    plt.plot(results["WorkInfections"], label="Work infections")
    plt.plot(results["MaskProtectedContacts"], label="Mask protected contacts")

    plt.xlabel("Step")
    plt.ylabel("Number of people")
    plt.title("Active and new infections")
    plt.legend()

    save_plot(f"{plots_dir}/infections_curve.png")

def plot_quarantine_curve(results, plots_dir):
    plt.figure()

    plt.plot(results["QuarantinedAgents"], label="Quarantined agents")
    plt.plot(results["DetectedInfected"], label="Detected infected")
    plt.plot(results["UndetectedInfected"], label="Undetected infected")

    plt.xlabel("Step")
    plt.ylabel("Number of agents")
    plt.title("Quarantine and detection over time")
    plt.legend()

    save_plot(f"{plots_dir}/quarantine_curve.png")

def plot_vaccination_campaign_curve(results, plots_dir):
    plt.figure()

    plt.plot(results["NewVaccinations"], label="New vaccinations")
    plt.plot(
        results["VaccinationCampaignActive"],
        label="Vaccination campaign active"
    )

    plt.xlabel("Step")
    plt.ylabel("Count / status")
    plt.title("Vaccination campaign over time")
    plt.legend()

    save_plot(f"{plots_dir}/vaccination_campaign_curve.png")

def plot_policy_curves(results, plots_dir):
    plt.figure()

    plt.plot(results["LockdownActive"], label="Lockdown active")
    plt.plot(results["SchoolClosedActive"], label="School closed")
    plt.plot(results["WorkClosedActive"], label="Work closed")

    plt.xlabel("Step")
    plt.ylabel("Status")
    plt.title("Binary dynamic policy status")
    plt.yticks([0, 1], ["Off/Open", "On/Closed"])
    plt.legend()

    save_plot(f"{plots_dir}/binary_policy_status.png")

    plt.figure()

    plt.plot(results["MaskComplianceActive"], label="Mask compliance")
    plt.plot(results["TestingRateActive"], label="Testing rate")
    plt.plot(
        results["QuarantineComplianceActive"],
        label="Quarantine compliance"
    )

    plt.xlabel("Step")
    plt.ylabel("Policy level")
    plt.title("Continuous dynamic policy levels")
    plt.ylim(0, 1)
    plt.legend()

    save_plot(f"{plots_dir}/continuous_policy_levels.png")

def plot_mobility_curves(results, plots_dir):
    plt.figure()

    plt.plot(results["SeniorMobilityActive"], label="Senior mobility")
    plt.plot(results["ChildMobilityActive"], label="Child mobility")

    plt.xlabel("Step")
    plt.ylabel("Mobility")
    plt.title("Dynamic mobility levels")
    plt.ylim(0, 1)
    plt.legend()

    save_plot(f"{plots_dir}/mobility_policy_levels.png")

def plot_transmission_bars(
    plots_dir,
    total_home_infections,
    total_school_infections,
    total_work_infections,
    total_other_infections,
    total_household_infections,
    total_community_infections,
):
    plt.figure()

    locations = ["Home", "School", "Work", "Other"]
    location_values = [
        total_home_infections,
        total_school_infections,
        total_work_infections,
        total_other_infections,
    ]

    plt.bar(locations, location_values)
    plt.xlabel("Location")
    plt.ylabel("Number of infections")
    plt.title("Infections by location")

    save_plot(f"{plots_dir}/location_infections_bar.png")

    plt.figure()

    transmission_types = ["Household", "Community"]
    transmission_values = [
        total_household_infections,
        total_community_infections,
    ]

    plt.bar(transmission_types, transmission_values)
    plt.xlabel("Transmission type")
    plt.ylabel("Number of infections")
    plt.title("Household vs community infections")

    save_plot(f"{plots_dir}/transmission_type_bar.png")

def plot_transmission_shares(
    plots_dir,
    home_infection_share,
    school_infection_share,
    work_infection_share,
    other_infection_share,
    household_infection_share,
    community_infection_share,
):
    plt.figure()

    location_share_labels = ["Home", "School", "Work", "Other"]
    location_share_values = [
        home_infection_share * 100,
        school_infection_share * 100,
        work_infection_share * 100,
        other_infection_share * 100,
    ]

    plt.bar(location_share_labels, location_share_values)
    plt.xlabel("Location")
    plt.ylabel("Share of infections (%)")
    plt.title("Infection share by location")
    plt.ylim(0, 100)

    save_plot(f"{plots_dir}/location_infection_share_bar.png")

    plt.figure()

    pie_labels = ["Home", "School", "Work", "Other"]
    pie_values = [
        home_infection_share,
        school_infection_share,
        work_infection_share,
        other_infection_share,
    ]

    plt.pie(
        pie_values,
        labels=pie_labels,
        autopct="%1.1f%%"
    )
    plt.title("Infection share by location")

    save_plot(f"{plots_dir}/location_infection_share_pie.png")

    plt.figure()

    transmission_share_labels = ["Household", "Community"]
    transmission_share_values = [
        household_infection_share,
        community_infection_share,
    ]

    plt.pie(
        transmission_share_values,
        labels=transmission_share_labels,
        autopct="%1.1f%%"
    )
    plt.title("Household vs community infection share")

    save_plot(f"{plots_dir}/transmission_type_share_pie.png")

def plot_age_group_bars(
    plots_dir,
    model,
    child_attack_rate,
    adult_attack_rate,
    senior_attack_rate,
    child_death_rate,
    adult_death_rate,
    senior_death_rate,
    child_vaccination_coverage,
    adult_vaccination_coverage,
    senior_vaccination_coverage,
):
    age_groups = ["Child", "Adult", "Senior"]

    plt.figure()
    plt.bar(
        age_groups,
        [
            model.child_infections,
            model.adult_infections,
            model.senior_infections,
        ]
    )
    plt.xlabel("Age group")
    plt.ylabel("Infections")
    plt.title("Infections by age group")
    save_plot(f"{plots_dir}/infections_by_age_bar.png")

    plt.figure()
    plt.bar(
        age_groups,
        [
            child_attack_rate * 100,
            adult_attack_rate * 100,
            senior_attack_rate * 100,
        ]
    )
    plt.xlabel("Age group")
    plt.ylabel("Attack rate (%)")
    plt.title("Attack rate by age group")
    plt.ylim(0, 100)
    save_plot(f"{plots_dir}/attack_rate_by_age_bar.png")

    plt.figure()
    plt.bar(
        age_groups,
        [
            model.child_deaths,
            model.adult_deaths,
            model.senior_deaths,
        ]
    )
    plt.xlabel("Age group")
    plt.ylabel("Deaths")
    plt.title("Deaths by age group")
    save_plot(f"{plots_dir}/deaths_by_age_bar.png")

    plt.figure()
    plt.bar(
        age_groups,
        [
            child_death_rate * 100,
            adult_death_rate * 100,
            senior_death_rate * 100,
        ]
    )
    plt.xlabel("Age group")
    plt.ylabel("Death rate (%)")
    plt.title("Death rate by age group")
    plt.ylim(0, 100)
    save_plot(f"{plots_dir}/death_rate_by_age_bar.png")

    plt.figure()
    plt.bar(
        age_groups,
        [
            child_vaccination_coverage * 100,
            adult_vaccination_coverage * 100,
            senior_vaccination_coverage * 100,
        ]
    )
    plt.xlabel("Age group")
    plt.ylabel("Vaccination coverage (%)")
    plt.title("Vaccination coverage by age group")
    plt.ylim(0, 100)
    save_plot(f"{plots_dir}/vaccination_coverage_by_age_bar.png")

def plot_campaign_vaccinations_by_age(plots_dir, model):
    plt.figure()

    age_groups = ["Child", "Adult", "Senior"]
    values = [
        model.child_campaign_vaccinations,
        model.adult_campaign_vaccinations,
        model.senior_campaign_vaccinations,
    ]

    plt.bar(age_groups, values)

    plt.xlabel("Age group")
    plt.ylabel("Vaccinations")
    plt.title("Campaign vaccinations by age group")

    save_plot(f"{plots_dir}/campaign_vaccinations_by_age_bar.png")

def plot_detailed_policy_curves(results, plots_dir):
    plt.figure()
    plt.plot(results["LockdownActive"], label="Lockdown active")
    plt.xlabel("Step")
    plt.ylabel("Active")
    plt.title("Lockdown status over time")
    plt.yticks([0, 1], ["Off", "On"])
    plt.legend()
    save_plot(f"{plots_dir}/lockdown_status.png")

    plt.figure()
    plt.plot(results["ActiveCases"], label="Active cases")
    plt.axhline(
        y=config.LOCKDOWN_THRESHOLD,
        linestyle="--",
        label="Lockdown threshold"
    )
    plt.axhline(
        y=config.LOCKDOWN_RELEASE_THRESHOLD,
        linestyle=":",
        label="Release threshold"
    )
    plt.xlabel("Step")
    plt.ylabel("Active cases")
    plt.title("Active cases and lockdown thresholds")
    plt.legend()
    save_plot(f"{plots_dir}/lockdown_thresholds_curve.png")

    plt.figure()
    plt.plot(results["SchoolClosedActive"], label="School closed")
    plt.xlabel("Step")
    plt.ylabel("Active")
    plt.title("School closure status over time")
    plt.yticks([0, 1], ["Open", "Closed"])
    plt.legend()
    save_plot(f"{plots_dir}/school_closure_status.png")

    plt.figure()
    plt.plot(results["WorkClosedActive"], label="Work closed")
    plt.xlabel("Step")
    plt.ylabel("Active")
    plt.title("Work closure status over time")
    plt.yticks([0, 1], ["Open", "Closed"])
    plt.legend()
    save_plot(f"{plots_dir}/work_closure_status.png")

    plt.figure()
    plt.plot(results["MaskComplianceActive"], label="Mask compliance")
    plt.xlabel("Step")
    plt.ylabel("Compliance")
    plt.title("Mask compliance over time")
    plt.ylim(0, 1)
    plt.legend()
    save_plot(f"{plots_dir}/mask_compliance_curve.png")

    plt.figure()
    plt.plot(results["TestingRateActive"], label="Testing rate")
    plt.xlabel("Step")
    plt.ylabel("Testing rate")
    plt.title("Testing rate over time")
    plt.ylim(0, 1)
    plt.legend()
    save_plot(f"{plots_dir}/testing_rate_curve.png")

    plt.figure()
    plt.plot(
        results["QuarantineComplianceActive"],
        label="Quarantine compliance"
    )
    plt.xlabel("Step")
    plt.ylabel("Compliance")
    plt.title("Quarantine compliance over time")
    plt.ylim(0, 1)
    plt.legend()
    save_plot(f"{plots_dir}/quarantine_compliance_curve.png")

    plt.figure()
    plt.plot(results["LockdownActive"], label="Lockdown active")
    plt.plot(results["SchoolClosedActive"], label="School closed")
    plt.plot(results["WorkClosedActive"], label="Work closed")
    plt.plot(results["MaskComplianceActive"], label="Mask compliance")
    plt.xlabel("Step")
    plt.ylabel("Policy level")
    plt.title("Dynamic policy status over time")
    plt.ylim(0, 1)
    plt.legend()
    save_plot(f"{plots_dir}/policy_status.png")

    plt.figure()
    plt.plot(results["SeniorMobilityActive"], label="Senior mobility")
    plt.xlabel("Step")
    plt.ylabel("Mobility")
    plt.title("Senior mobility over time")
    plt.ylim(0, 1)
    plt.legend()
    save_plot(f"{plots_dir}/senior_mobility_curve.png")

def generate_all_plots(
    results,
    plots_dir,
    model,
    total_home_infections,
    total_school_infections,
    total_work_infections,
    total_other_infections,
    total_household_infections,
    total_community_infections,
    home_infection_share,
    school_infection_share,
    work_infection_share,
    other_infection_share,
    household_infection_share,
    community_infection_share,
    child_attack_rate,
    adult_attack_rate,
    senior_attack_rate,
    child_death_rate,
    adult_death_rate,
    senior_death_rate,
    child_vaccination_coverage,
    adult_vaccination_coverage,
    senior_vaccination_coverage,
):
    plot_epidemic_curve(results, plots_dir)
    plot_rt_curve(results, plots_dir)
    plot_infections_curve(results, plots_dir)
    plot_quarantine_curve(results, plots_dir)
    plot_vaccination_campaign_curve(results, plots_dir)
    plot_policy_curves(results, plots_dir)
    plot_detailed_policy_curves(results, plots_dir)
    plot_mobility_curves(results, plots_dir)

    plot_transmission_bars(
        plots_dir,
        total_home_infections,
        total_school_infections,
        total_work_infections,
        total_other_infections,
        total_household_infections,
        total_community_infections,
    )

    plot_transmission_shares(
        plots_dir,
        home_infection_share,
        school_infection_share,
        work_infection_share,
        other_infection_share,
        household_infection_share,
        community_infection_share,
    )

    plot_age_group_bars(
        plots_dir,
        model,
        child_attack_rate,
        adult_attack_rate,
        senior_attack_rate,
        child_death_rate,
        adult_death_rate,
        senior_death_rate,
        child_vaccination_coverage,
        adult_vaccination_coverage,
        senior_vaccination_coverage,
    )

    plot_campaign_vaccinations_by_age(plots_dir, model)