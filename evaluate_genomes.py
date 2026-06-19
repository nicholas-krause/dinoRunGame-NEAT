import os

import neat

from simulation import Simulation, SimulationParams


def run(configuration_file, max_generations=50, seed=None):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        configuration_file,
    )
    sim = Simulation(config, SimulationParams(max_generations=max_generations, seed=seed))
    while not sim.finished:
        sim.step()
    return sim


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "configuration_FF.txt")
    result = run(config_path)
    if result.generation_history:
        best = max(result.generation_history, key=lambda g: g["best_fitness"])
        print(f"Best generation: {best['generation']} fitness={best['best_fitness']:.2f}")
