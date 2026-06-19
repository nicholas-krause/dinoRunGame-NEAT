import os

import neat

from simulation import Simulation, SimulationParams


def load_config():
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "configuration_FF.txt")
    return neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path,
    )


def main():
    config = load_config()
    params = SimulationParams(max_generations=5, seed=42)
    sim = Simulation(config, params=params)

    frame = 0
    while not sim.finished and frame < 200_000:
        state = sim.step()
        frame += 1
        if frame % 500 == 0:
            print(
                f"frame={frame} gen={state['generation']} alive={state['alive']} "
                f"score={state['score']}"
            )

    if sim.generation_history:
        print("\nGeneration summary:")
        for item in sim.generation_history:
            print(
                f"gen={item['generation']} best={item['best_fitness']:.2f} "
                f"avg={item['avg_fitness']:.2f} species={item['species_count']} "
                f"score={item['score']}"
            )

    print("\nDone")


if __name__ == "__main__":
    main()
