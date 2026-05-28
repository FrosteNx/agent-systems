import numpy as np
import matplotlib.pyplot as plt
import imageio.v2 as imageio


plt.style.use("dark_background")


def get_agent_color(agent):

    colors = {
        "Susceptible": "#00FF9C",      # neon mint
        "Exposed": "#FFD60A",          # warm amber
        "Infected": "#FF006E",         # neon pink/red
        "Asymptomatic": "#FB8500",    # vivid orange
        "Recovered": "#3A86FF",       # electric blue
        "Vaccinated": "#8338EC",      # vivid violet
        "Dead": "#E0E0E0"             # light gray/white
    }

    return colors.get(agent.state, "#808080")


def save_city_snapshot(model, plots_dir, step):
    fig, ax = plt.subplots(figsize=(8, 8))

    for agent in model.schedule.agents:
        x, y = agent.pos

        x_jitter = x + np.random.uniform(-0.25, 0.25)
        y_jitter = y + np.random.uniform(-0.25, 0.25)

        plt.scatter(
            x_jitter,
            y_jitter,
            color=get_agent_color(agent),
            s=80,
            edgecolors="white",
            linewidths=0.8
        )

    plt.xlim(-0.5, model.grid.width - 0.5)
    plt.ylim(-0.5, model.grid.height - 0.5)

    plt.grid()

    counts = model.count_states()

    active_cases = (
        counts["Exposed"]
        + counts["Infected"]
        + counts["Asymptomatic"]
    )

    if model.step_count % 20 < 10:
        time_of_day = "DAY"
        background_color = "#02294F"
    else:
        time_of_day = "NIGHT"
        background_color = "#000000"
    ax.set_facecolor(background_color)
    plt.title(
        f"{time_of_day} | "
        f"Step {step} | "
        f"Active cases: {active_cases}"
    )
    plt.xlabel("X")
    plt.ylabel("Y")

    plt.scatter([], [], color="#00FF9C", label="Susceptible")
    plt.scatter([], [], color="#FFD60A", label="Exposed")
    plt.scatter([], [], color="#FF006E", label="Infected")
    plt.scatter([], [], color="#FB8500", label="Asymptomatic")
    plt.scatter([], [], color="#3A86FF", label="Recovered")
    plt.scatter([], [], color="#8338EC", label="Vaccinated")
    plt.scatter([], [], color="#E0E0E0", label="Dead")

    plt.legend(
        bbox_to_anchor=(1.05, 1),
        loc="upper left"
    )

    plt.tight_layout()

    snapshot_file = f"{plots_dir}/city_state_step_{step:03d}.png"

    plt.savefig(snapshot_file, dpi=300)
    plt.close()

    print(f"City snapshot saved: city_state_step_{step:03d}.png")

    return snapshot_file


def create_city_animation(snapshot_files, plots_dir, duration):
    if not snapshot_files:
        return

    images = []

    for file in snapshot_files:
        images.append(imageio.imread(file))

    gif_path = f"{plots_dir}/city_animation.gif"

    imageio.mimsave(
        gif_path,
        images,
        duration=duration
    )

    print(f"City animation saved to {gif_path}")