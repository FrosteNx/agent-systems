from pathlib import Path
import html
import shutil


STATISTIC_GROUPS = {
    "Experiment": [
        "experiment_id",
        "timestamp",
        "scenario_name",
        "output_dir",
        "log_file",
        "population",
        "initial_infected",
    ],
    "Epidemic Outcomes": [
        "total_infections",
        "secondary_infections",
        "peak_active_cases",
        "attack_rate",
        "case_fatality_rate",
        "average_rt",
    ],
    "Transmission": [
        "total_household_infections",
        "total_community_infections",
        "household_infection_share",
        "community_infection_share",
        "household_share_sum",
        "total_home_infections",
        "total_school_infections",
        "total_work_infections",
        "total_other_infections",
        "home_infection_share",
        "school_infection_share",
        "work_infection_share",
        "other_infection_share",
        "location_share_sum",
    ],
    "Interventions": [
        "mask_protected_contacts",
        "total_quarantined_agents",
        "total_quarantined_people",
        "quarantine_rate",
        "total_detected_infections",
        "detection_rate",
        "undetected_infections",
        "undetected_rate",
        "total_asymptomatic_infections",
        "asymptomatic_rate_observed",
    ],
    "Vaccination": [
        "vaccination_campaign_start_step",
        "vaccination_campaign_end_step",
        "vaccination_campaign_duration",
        "initial_vaccinations",
        "total_vaccinations",
        "vaccination_coverage",
        "total_campaign_vaccinations",
        "vaccination_campaign_activation_count",
        "vaccinated_breakthrough_infections",
        "breakthrough_infection_rate",
        "vaccinated_infection_rate",
        "unvaccinated_infection_rate",
        "observed_vaccine_effectiveness",
        "child_campaign_vaccinations",
        "adult_campaign_vaccinations",
        "senior_campaign_vaccinations",
        "child_vaccination_coverage",
        "adult_vaccination_coverage",
        "senior_vaccination_coverage",
    ],
    "Dynamic Policies": [
        "lockdown_start_step",
        "lockdown_end_step",
        "lockdown_duration",
        "lockdown_activation_count",
        "school_closure_start_step",
        "school_closure_end_step",
        "school_closure_duration",
        "school_closure_count",
        "work_closure_start_step",
        "work_closure_end_step",
        "work_closure_duration",
        "work_closure_count",
        "final_mask_compliance",
        "mask_compliance_start_step",
        "mask_compliance_end_step",
        "mask_compliance_duration",
        "mask_compliance_activation_count",
        "final_testing_rate",
        "testing_rate_start_step",
        "testing_rate_end_step",
        "testing_rate_duration",
        "testing_rate_activation_count",
        "final_quarantine_compliance",
        "quarantine_compliance_start_step",
        "quarantine_compliance_end_step",
        "quarantine_compliance_duration",
        "quarantine_compliance_activation_count",
    ],
    "Mobility Policies": [
        "senior_mobility_reduction_start_step",
        "senior_mobility_reduction_end_step",
        "senior_mobility_reduction_duration",
        "senior_mobility_reduction_count",
        "child_mobility_reduction_start_step",
        "child_mobility_reduction_end_step",
        "child_mobility_reduction_duration",
        "child_mobility_reduction_count",
    ],
    "Age Groups": [
        "child_infections",
        "adult_infections",
        "senior_infections",
        "child_attack_rate",
        "adult_attack_rate",
        "senior_attack_rate",
        "child_deaths",
        "adult_deaths",
        "senior_deaths",
        "child_death_rate",
        "adult_death_rate",
        "senior_death_rate",
    ],
}


PLOT_GROUPS = {
    "Epidemic": [
        "epidemic_curve",
        "rt_curve",
        "infections_curve",
        "quarantine_curve",
    ],
    "Policies": [
        "binary_policy_status",
        "continuous_policy_levels",
        "policy_status",
        "lockdown_status",
        "lockdown_thresholds_curve",
        "school_closure_status",
        "work_closure_status",
        "mask_compliance_curve",
        "testing_rate_curve",
        "quarantine_compliance_curve",
    ],
    "Mobility": [
        "mobility_policy_levels",
        "senior_mobility_curve",
    ],
    "Transmission": [
        "location_infections_bar",
        "location_infection_share_bar",
        "location_infection_share_pie",
        "transmission_type_bar",
        "transmission_type_share_pie",
    ],
    "Age Groups": [
        "infections_by_age_bar",
        "attack_rate_by_age_bar",
        "deaths_by_age_bar",
        "death_rate_by_age_bar",
        "vaccination_coverage_by_age_bar",
    ],
    "Vaccination": [
        "vaccination_campaign_curve",
        "campaign_vaccinations_by_age_bar",
    ],
}


def format_metric_value(value):
    if isinstance(value, float):
        return f"{value:.4f}"

    if value is None:
        return "N/A"

    return str(value)


def format_metric_name(name):
    return name.replace("_", " ").title()


def slugify(value):
    return (
        value.lower()
        .replace(" ", "-")
        .replace("_", "-")
        .replace("/", "-")
    )


def get_plot_files(output_dir):
    plots_dir = Path(output_dir) / "plots"

    if not plots_dir.exists():
        return []

    return sorted(
        plot_file
        for plot_file in plots_dir.glob("*.png")
    )


def build_metric_rows(metric_items):
    rows = []

    for i in range(0, len(metric_items), 2):
        left_key, left_value = metric_items[i]

        if i + 1 < len(metric_items):
            right_key, right_value = metric_items[i + 1]
            right_metric = html.escape(format_metric_name(right_key))
            right_value = html.escape(format_metric_value(right_value))
        else:
            right_metric = ""
            right_value = ""

        rows.append(f"""
        <tr>
            <td>{html.escape(format_metric_name(left_key))}</td>
            <td>{html.escape(format_metric_value(left_value))}</td>
            <td>{right_metric}</td>
            <td>{right_value}</td>
        </tr>
        """)

    return "\n".join(rows)


def build_statistics_sections(metrics):
    used_keys = set()
    sections = ""

    for group_name, keys in STATISTIC_GROUPS.items():
        metric_items = []

        for key in keys:
            if key in metrics:
                metric_items.append((key, metrics[key]))
                used_keys.add(key)

        if not metric_items:
            continue

        rows = build_metric_rows(metric_items)
        section_id = f"stats-{slugify(group_name)}"

        sections += f"""
        <div class="card stats-section" id="{section_id}">
            <h3>{html.escape(group_name)}</h3>

            <table>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                {rows}
            </table>
        </div>
        """

    remaining_items = [
        (key, value)
        for key, value in metrics.items()
        if key not in used_keys
    ]

    if remaining_items:
        rows = build_metric_rows(remaining_items)

        sections += f"""
        <div class="card stats-section" id="stats-other">
            <h3>Other</h3>

            <table>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                {rows}
            </table>
        </div>
        """

    return sections


def group_plot_files(plot_files):
    plot_by_stem = {
        plot_file.stem: plot_file
        for plot_file in plot_files
    }

    grouped_plots = {}
    used_stems = set()

    for group_name, stems in PLOT_GROUPS.items():
        group_files = []

        for stem in stems:
            if stem in plot_by_stem:
                group_files.append(plot_by_stem[stem])
                used_stems.add(stem)

        if group_files:
            grouped_plots[group_name] = group_files

    other_files = [
        plot_file
        for plot_file in plot_files
        if plot_file.stem not in used_stems
    ]

    if other_files:
        grouped_plots["Other"] = other_files

    return grouped_plots


def build_plot_card(plot_file):
    plot_title = format_metric_name(plot_file.stem)
    relative_path = f"plots/{plot_file.name}"

    return f"""
    <div class="plot-card" id="plot-{html.escape(slugify(plot_file.stem))}">
        <h3>{html.escape(plot_title)}</h3>
        <img src="{html.escape(relative_path)}" alt="{html.escape(plot_title)}">
    </div>
    """


def build_plot_sections(plot_files):
    grouped_plots = group_plot_files(plot_files)
    sections = ""

    for group_name, files in grouped_plots.items():
        section_id = f"plots-{slugify(group_name)}"
        cards = "\n".join(
            build_plot_card(plot_file)
            for plot_file in files
        )

        sections += f"""
        <section class="plot-section" id="{section_id}">
            <h3>{html.escape(group_name)}</h3>

            <div class="plot-grid">
                {cards}
            </div>
        </section>
        """

    return sections


def build_nav():
    statistic_links = "\n".join(
        f'<a href="#stats-{slugify(group_name)}">{html.escape(group_name)}</a>'
        for group_name in STATISTIC_GROUPS
    )

    plot_links = "\n".join(
        f'<a href="#plots-{slugify(group_name)}">{html.escape(group_name)}</a>'
        for group_name in PLOT_GROUPS
    )

    return f"""
    <div class="nav">
        <strong>Main:</strong>
        <a href="#key-metrics">Key Metrics</a>
        <a href="#all-statistics">Statistics</a>
        <a href="#all-plots">Plots</a>

        <br>

        <strong>Stats:</strong>
        {statistic_links}

        <br>

        <strong>Plots:</strong>
        {plot_links}
    </div>
    """


def write_dashboard_file(path, html_content):
    with open(path, "w", encoding="utf-8") as file:
        file.write(html_content)

    print(f"Dashboard saved: {path}")


def generate_dashboard(output_dir, metrics):
    output_dir = Path(output_dir)
    dashboard_path = output_dir / "dashboard.html"
    index_path = output_dir / "index.html"

    plot_files = get_plot_files(output_dir)
    statistics_sections = build_statistics_sections(metrics)
    plot_sections = build_plot_sections(plot_files)
    navigation = build_nav()

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Flu Simulation Dashboard</title>

<style>
html {{
    scroll-behavior: smooth;
}}

body {{
    font-family: Arial, sans-serif;
    background-color: #f5f5f5;
    margin: 0;
    padding: 30px;
    color: #222;
}}

h1 {{
    margin-bottom: 8px;
}}

.subtitle {{
    color: #666;
    margin-bottom: 30px;
}}

.nav {{
    background: white;
    padding: 14px 20px;
    border-radius: 10px;
    margin-bottom: 25px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    line-height: 2;
}}

.nav strong {{
    margin-right: 8px;
}}

.nav a {{
    text-decoration: none;
    color: #1565c0;
    font-weight: 600;
    margin-right: 16px;
}}

.nav a:hover {{
    text-decoration: underline;
}}

.card {{
    background: white;
    padding: 24px;
    margin-bottom: 28px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}}

.metric-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 15px;
}}

.metric-box {{
    background: #fafafa;
    padding: 16px;
    border-radius: 8px;
    border: 1px solid #e0e0e0;
}}

.metric-label {{
    font-size: 14px;
    color: #666;
}}

.metric-value {{
    font-size: 24px;
    font-weight: bold;
    margin-top: 6px;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}}

th {{
    text-align: left;
    background-color: #f0f0f0;
}}

th,
td {{
    padding: 8px 10px;
    border-bottom: 1px solid #dddddd;
    vertical-align: top;
}}

td:nth-child(1),
td:nth-child(3) {{
    font-weight: 600;
    color: #333;
    width: 28%;
}}

td:nth-child(2),
td:nth-child(4) {{
    width: 22%;
    font-family: Consolas, monospace;
}}

tr:hover {{
    background-color: #fafafa;
}}

.section-title {{
    margin-top: 40px;
    margin-bottom: 16px;
}}

.small-note {{
    color: #777;
    font-size: 13px;
}}

.stats-section h3,
.plot-section h3 {{
    margin-top: 0;
}}

.plot-section {{
    margin-bottom: 35px;
}}

.plot-grid {{
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 24px;
}}

.plot-card {{
    background: white;
    padding: 18px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}}

.plot-card h3 {{
    margin-top: 0;
    margin-bottom: 14px;
    font-size: 18px;
}}

.plot-card img {{
    width: 100%;
    max-height: 420px;
    object-fit: contain;
    display: block;
    border: 1px solid #eeeeee;
    border-radius: 8px;
    background: white;
}}

.back-to-top {{
    display: inline-block;
    margin-top: 10px;
    color: #1565c0;
    text-decoration: none;
    font-weight: 600;
}}

.back-to-top:hover {{
    text-decoration: underline;
}}

@media (max-width: 900px) {{
    .plot-grid {{
        grid-template-columns: 1fr;
    }}

    body {{
        padding: 16px;
    }}

    table {{
        font-size: 12px;
    }}

    .nav a {{
        display: inline-block;
        margin-bottom: 4px;
    }}
}}
</style>

</head>

<body id="top">

<h1>Flu Simulation Dashboard</h1>
<div class="subtitle">Automatically generated simulation report</div>

{navigation}

<div class="card" id="key-metrics">
    <h2>Key Metrics</h2>

    <div class="metric-grid">
        <div class="metric-box">
            <div class="metric-label">Scenario</div>
            <div class="metric-value">{html.escape(str(metrics.get("scenario_name", "N/A")))}</div>
        </div>

        <div class="metric-box">
            <div class="metric-label">Population</div>
            <div class="metric-value">{html.escape(str(metrics.get("population", "N/A")))}</div>
        </div>

        <div class="metric-box">
            <div class="metric-label">Total Infections</div>
            <div class="metric-value">{html.escape(str(metrics.get("total_infections", "N/A")))}</div>
        </div>

        <div class="metric-box">
            <div class="metric-label">Peak Active Cases</div>
            <div class="metric-value">{html.escape(str(metrics.get("peak_active_cases", "N/A")))}</div>
        </div>

        <div class="metric-box">
            <div class="metric-label">Attack Rate</div>
            <div class="metric-value">{metrics.get("attack_rate", 0):.2%}</div>
        </div>

        <div class="metric-box">
            <div class="metric-label">Case Fatality Rate</div>
            <div class="metric-value">{metrics.get("case_fatality_rate", 0):.2%}</div>
        </div>

        <div class="metric-box">
            <div class="metric-label">Average Rt</div>
            <div class="metric-value">{metrics.get("average_rt", 0):.2f}</div>
        </div>

        <div class="metric-box">
            <div class="metric-label">Vaccination Coverage</div>
            <div class="metric-value">{metrics.get("vaccination_coverage", 0):.2%}</div>
        </div>
    </div>
</div>

<h2 class="section-title" id="all-statistics">Statistics</h2>
<p class="small-note">Metrics are grouped by topic and displayed two per row.</p>

{statistics_sections}

<h2 class="section-title" id="all-plots">Plots</h2>
<p class="small-note">Plots are grouped by topic. All PNG files from the plots directory are included.</p>

{plot_sections}

<a class="back-to-top" href="#top">Back to top ↑</a>

</body>
</html>
"""

    write_dashboard_file(dashboard_path, html_content)
    write_dashboard_file(index_path, html_content)