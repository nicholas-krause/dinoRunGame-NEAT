import random
from dataclasses import dataclass

import neat

from background import Base
from bird import Bird
from cactus import Cactus
from dino import Dinosaur

WIN_WIDTH = 1500
FLOOR = 280
GROUND = 365
BIRD_HEIGHT = 96


def _aabb_overlap(a, b):
    a_left, a_top, a_right, a_bottom = a
    b_left, b_top, b_right, b_bottom = b
    return a_left < b_right and a_right > b_left and a_top < b_bottom and a_bottom > b_top


@dataclass
class SimulationParams:
    max_generations: int = 50
    tick_rate: int = 31
    start_velocity: float = 10.0
    level_up_interval: int = 150
    score_increment: float = 1.0
    speed_scale: float = 1.04
    birds_enabled: bool = True
    draw_lines: bool = True
    seed: int | None = None


class Simulation:
    def __init__(self, config, params=None):
        self.config = config
        self.params = params or SimulationParams()
        if self.params.seed is not None:
            random.seed(self.params.seed)

        self.population = neat.Population(config)
        self.population.add_reporter(neat.StdOutReporter(True))
        self.stats = neat.StatisticsReporter()
        self.population.add_reporter(self.stats)

        self.generation = 0
        self.finished = False
        self.generation_history = []
        self._last_level_bucket = 0
        self._start_generation()

    def _generate_cactus_variant(self):
        distance = WIN_WIDTH + random.randint(WIN_WIDTH // 4, WIN_WIDTH // 2)
        variant = random.randint(0, 2)
        size = "small" if random.randint(0, 1) else "large"
        return distance, size, variant

    def _generate_bird_height(self):
        return random.randint(BIRD_HEIGHT, FLOOR)

    def _accelerate_all(self):
        self.base.accelerate(self.multiplier)
        for bird in self.birds:
            bird.accelerate(self.multiplier)
        for cactus in self.cacti:
            cactus.accelerate(self.multiplier)

    def _start_generation(self):
        self.population.reporters.start_generation(self.population.generation)
        self.generation += 1

        self.nets = []
        self.dinos = []
        self.genomes = []
        for _, genome in self.population.population.items():
            genome.fitness = 0.0
            self.nets.append(neat.nn.FeedForwardNetwork.create(genome, self.config))
            self.dinos.append(Dinosaur(200, GROUND))
            self.genomes.append(genome)

        self.score = 0.0
        self.frame_count = 0
        self.velocity = self.params.start_velocity
        self.blocks_travelled = 0.0
        self.score_increment = self.params.score_increment
        self.multiplier = 1.0
        self._last_level_bucket = 0

        self.base = Base(FLOOR)
        self.birds = []
        self.cacti = [Cactus(self._generate_cactus_variant())]

    def _end_generation(self):
        best = max(self.genomes, key=lambda g: g.fitness) if self.genomes else None
        avg = sum(g.fitness for g in self.genomes) / len(self.genomes) if self.genomes else 0.0
        best_fit = best.fitness if best else 0.0
        species_count = len(self.population.species.species)
        self.generation_history.append(
            {
                "generation": self.generation,
                "best_fitness": best_fit,
                "avg_fitness": avg,
                "species_count": species_count,
                "score": int(self.score),
            }
        )

        self.population.reporters.post_evaluate(
            self.config, self.population.population, self.population.species, best
        )
        if self.population.best_genome is None or (best and best.fitness > self.population.best_genome.fitness):
            self.population.best_genome = best

        fitness_values = (g.fitness for g in self.population.population.values())
        if self.population.fitness_criterion(fitness_values) >= self.config.fitness_threshold:
            self.finished = True
            self.population.reporters.found_solution(
                self.config, self.population.generation, best
            )
            return

        self.population.population = self.population.reproduction.reproduce(
            self.config,
            self.population.species,
            self.config.pop_size,
            self.population.generation,
        )

        if not self.population.species.species:
            self.population.reporters.complete_extinction()
            if self.config.reset_on_extinction:
                self.population.population = self.population.reproduction.create_new(
                    self.config.genome_type, self.config.genome_config, self.config.pop_size
                )
            else:
                raise neat.CompleteExtinctionException()

        self.population.species.speciate(
            self.config, self.population.population, self.population.generation
        )
        self.population.reporters.end_generation(
            self.config, self.population.population, self.population.species
        )
        self.population.generation += 1

        if self.generation >= self.params.max_generations:
            self.finished = True
            return
        self._start_generation()

    def _get_nearest_indices(self):
        min_cactus_index = 0
        if self.cacti:
            min_cactus_index = min(
                range(len(self.cacti)), key=lambda i: abs(self.cacti[i].x - 200)
            )

        min_bird_index = None
        if self.birds:
            min_bird_index = min(
                range(len(self.birds)), key=lambda i: abs(self.birds[i].x - 200)
            )
        return min_cactus_index, min_bird_index

    def _update_agents(self):
        min_cactus_index, min_bird_index = self._get_nearest_indices()
        closest_bird_x = WIN_WIDTH
        closest_bird_y = 0
        if min_bird_index is not None:
            closest_bird_x = self.birds[min_bird_index].x
            closest_bird_y = self.birds[min_bird_index].y

        cactus_ref = self.cacti[min_cactus_index]
        for idx, dino in enumerate(self.dinos):
            self.genomes[idx].fitness += 0.1
            dino.move()
            output = self.nets[idx].activate(
                (
                    dino.x,
                    dino.y,
                    abs(dino.x - cactus_ref.x),
                    abs(dino.x - closest_bird_x),
                    abs(dino.y - closest_bird_y),
                )
            )
            if output[0] > 0.5:
                dino.jump()
            elif 0.5 > output[0] < 0.25:
                dino.stand()
            elif 0.25 > output[0] < -1:
                self.genomes[idx].fitness += 0.05
                dino.duck()

    def _handle_collisions(self):
        alive = list(range(len(self.dinos)))
        for bird in self.birds:
            bird_box = bird.bounds()
            for idx in list(alive):
                if _aabb_overlap(self.dinos[idx].bounds(), bird_box):
                    self.genomes[idx].fitness -= 1
                    alive.remove(idx)
        for cactus in self.cacti:
            cactus_box = cactus.bounds()
            for idx in list(alive):
                if _aabb_overlap(self.dinos[idx].bounds(), cactus_box):
                    self.genomes[idx].fitness -= 1
                    alive.remove(idx)

        if len(alive) != len(self.dinos):
            self.dinos = [self.dinos[i] for i in alive]
            self.nets = [self.nets[i] for i in alive]
            self.genomes = [self.genomes[i] for i in alive]

    def _step_world(self):
        self.blocks_travelled += self.velocity
        if self.blocks_travelled > WIN_WIDTH / 2:
            self.blocks_travelled = 0
            new_cactus = Cactus(self._generate_cactus_variant())
            new_cactus.accelerate(self.multiplier)
            self.cacti.append(new_cactus)

        level_bucket = int(self.score) // self.params.level_up_interval
        if level_bucket > self._last_level_bucket:
            self._last_level_bucket = level_bucket
            self.score += 1
            self.velocity *= self.params.speed_scale
            self.score_increment *= self.params.speed_scale
            self.multiplier *= self.params.speed_scale
            if self.params.birds_enabled:
                self.birds.append(Bird(self._generate_bird_height()))
            self._accelerate_all()

        self.base.move()
        for bird in self.birds:
            bird.move()
        for cactus in self.cacti:
            cactus.move()

        self.birds = [b for b in self.birds if b.x + b.WIDTH >= -100]
        self.cacti = [c for c in self.cacti if c.x + c.width >= -100]

        self.frame_count += 1
        if self.frame_count % 2 == 0:
            self.score += self.score_increment

    def _frame_state(self):
        min_cactus_index, min_bird_index = self._get_nearest_indices()
        return {
            "generation": self.generation,
            "alive": len(self.dinos),
            "score": int(self.score),
            "base": {"left": self.base.left, "right": self.base.right, "y": self.base.y},
            "dinos": [
                {
                    "x": d.x,
                    "y": d.y,
                    "jumping": d.is_jumping,
                    "ducking": d.is_ducking,
                    "width": d.width,
                    "height": d.height_px,
                }
                for d in self.dinos
            ],
            "cacti": [
                {"x": c.x, "y": c.y, "size": c.size, "variant": c.variant, "width": c.width, "height": c.height_px}
                for c in self.cacti
            ],
            "birds": [{"x": b.x, "y": b.y, "width": b.WIDTH, "height": b.HEIGHT} for b in self.birds],
            "nearest_cactus_index": min_cactus_index,
            "nearest_bird_index": min_bird_index,
            "history": self.generation_history[-1] if self.generation_history else None,
            "done": self.finished,
        }

    def step(self):
        if self.finished:
            return self._frame_state()

        self._step_world()
        self._update_agents()
        self._handle_collisions()

        if len(self.dinos) == 0:
            self._end_generation()

        return self._frame_state()
