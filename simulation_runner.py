import logging
import time


def run_simulation(model, steps):
    actual_steps = 0
    start_time = time.time()

    for i in range(steps):
        model.step()
        actual_steps = i + 1
        counts = model.count_states()

        logging.info(
            f"Step {i} | "
            f"S={counts['Susceptible']} "
            f"E={counts['Exposed']} "
            f"I={counts['Infected']} "
            f"A={counts['Asymptomatic']} "
            f"R={counts['Recovered']} "
            f"D={counts['Dead']}"
        )

        print(f"Step {i}: {counts}")

        active_cases = (
            counts["Exposed"]
            + counts["Infected"]
            + counts["Asymptomatic"]
        )

        if active_cases == 0:
            print(f"Epidemic ended at step {i}")
            break

    execution_time_seconds = time.time() - start_time

    return actual_steps, execution_time_seconds