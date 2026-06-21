from pathlib import Path
import html


def format_metric_value(value):
    if isinstance(value, float):
        return f"{value:.4f}"

    if value is None:
        return "N/A"

    return str(value)


def format_metric_name(name):
    return name.replace("_", " ").title()


def get_plot_files(output_dir):
    plots_dir = Path(output_dir) / "plots"

    if not plots_dir.exists():
        return []

    return sorted(
        plot_file
        for plot_file in plots_dir.glob("*.png")
    )


def build_metric_rows(metrics):
    items = list(metrics.items())
    rows = []

    for i in range(0, len(items), 2):
        left_key, left_value = items[i]

        if i + 1 < len(items):
            right_key, right_value = items[i + 1]
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


def generate_dashboard(output_dir, metrics):
    output_dir = Path(output_dir)
    dashboard_path = output_dir / "dashboard.html"

    plot_files = get_plot_files(output_dir)
    metric_rows = build_metric_rows(metrics)

    plot_cards = ""

    for plot_file in plot_files:
        plot_title = format_metric_name(plot_file.stem)
        relative_path = f"plots/{plot_file.name}"

        plot_cards += f"""
        <div class="plot-card">
            <h3>{html.escape(plot_title)}</h3>
            <img src="{html.escape(relative_path)}" alt="{html.escape(plot_title)}">
        </div>
        """

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Flu Simulation Dashboard</title>

<style>
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
}}
</style>

</head>

<body>

<h1>Flu Simulation Dashboard</h1>
<div class="subtitle">Automatically generated simulation report</div>

<div class="card">
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

<div class="card">
    <h2>All Statistics</h2>
    <p class="small-note">Two metrics are shown per row to make the table more compact.</p>

    <table>
        <tr>
            <th>Metric</th>
            <th>Value</th>
            <th>Metric</th>
            <th>Value</th>
        </tr>
        {metric_rows}
    </table>
</div>

<h2 class="section-title">All Plots</h2>

<div class="plot-grid">
    {plot_cards}
</div>

</body>
</html>
"""

    with open(dashboard_path, "w", encoding="utf-8") as file:
        file.write(html_content)

    print(f"Dashboard saved: {dashboard_path}")