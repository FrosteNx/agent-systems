def save_simulation_summary(path, content):
    with open(path, "w") as file:
        file.write(content)

    print(f"Saved: {path}")

def build_summary_metrics(**kwargs):
    return kwargs

def build_simulation_summary(summary_lines):
    return "\n".join(summary_lines)