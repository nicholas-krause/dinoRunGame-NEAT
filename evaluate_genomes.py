"""
The classic game of flappy bird. Make with python
and pygame. Features pixel perfect collision using masks :o

Date Modified:  Apr 30 2023
Author: Nicholas Krause
"""

import pygame
import random
import os
from cactus import Cactus
from dino import Dinosaur
from bird import Bird
from background import Base
import time
import neat
import visualize
import pickle

pygame.font.init()  # init font

WIN_WIDTH = 1500
WIN_HEIGHT = 400
FLOOR = 280  # For Base image
GROUND = 365 # For Dinosaur sprite
BIRD_HEIGHT = 96
FONT_COLOUR = (90, 90, 90)
STAT_FONT = pygame.font.Font(os.path.join("fonts/PublicPixel.ttf"), 18)
END_FONT = pygame.font.SysFont("comicsans", 70)
pygame.display.set_caption("Chrome Dino Game")
BACKGROUND_COLOUR = (247, 247, 247)  # Grey
DRAW_LINES = True

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
gen = 0


def draw_dino_window(win, dinos, base, score, birds, cacti, min_cactus_index, min_bird_index):
    pygame.draw.rect(win, BACKGROUND_COLOUR, [0, 0, WIN_WIDTH, WIN_HEIGHT])

    base.draw(win)
    for dino in dinos:
        if DRAW_LINES:
            try:
                pygame.draw.line(win, (255, 0, 0),
                                 (dino.x + dino.image.get_width()/2, dino.y - dino.image.get_height()/2),
                                 (cacti[min_cactus_index].x,
                                  cacti[min_cactus_index].y - cacti[min_cactus_index].image.get_height()), 5)
                pygame.draw.line(win, (0, 0, 255),
                                 (dino.x + dino.image.get_width() / 2, dino.y - dino.image.get_height() / 2),
                                 (birds[min_bird_index].x,
                                  birds[min_bird_index].y), 5)
            except:
                pass
        dino.draw(win)

    for bird in birds:
        bird.draw(win)
    for cactus in cacti:
        cactus.draw(win)

    score = int(score)
    # score 0000 -> 9999
    if score < 10:
        extra = "0000"
    elif score < 100:
        extra = "000"
    elif score < 1000:
        extra = "00"
    elif score < 10000:
        extra = "0"
    else:
        extra = ""


    # score
    score_label = STAT_FONT.render("Score: " + extra + str(score), True, FONT_COLOUR)
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    # generations
    gen_label = STAT_FONT.render("Gens: " + str(gen-1), True, FONT_COLOUR)
    win.blit(gen_label, (WIN_WIDTH - gen_label.get_width() - 15, 26))

    # dinos
    dino_label = STAT_FONT.render("Alive: " + str(len(dinos)), True, FONT_COLOUR)
    win.blit(dino_label, (WIN_WIDTH - dino_label.get_width() - 15, 42))

    pygame.display.update()


def generate_cactus_variant():
    distance = WIN_WIDTH + random.randint(WIN_WIDTH // 4, WIN_WIDTH // 2)
    variant = random.randint(0, 2)
    size = "small" if random.randint(0, 1) else "large"
    return distance, size, variant


def generate_bird_height(minimum, maximum):
    return random.randint(minimum, maximum)


# def accelerate_all(base, birds, cacti):
#     base.accelerate()
#     for bird in birds:
#         bird.accelerate()
#     for cactus in cacti:
#         cactus.accelerate()


def evaluate_genomes(genomes, configuration):
    global WIN, gen
    win = WIN
    gen += 1

    nets = []
    dinos = []
    genome_list = []

    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, configuration)
        nets.append(net)
        dinos.append(Dinosaur(200, GROUND))
        genome_list.append(genome)

    score = 0
    count = 0
    velocity = 10
    blocks_travelled = 0
    tick = 31
    level_up = 150
    score_increment = 1
    multiplier = 1

    base = Base(FLOOR)
    clock = pygame.time.Clock()
    birds = []
    cacti = [Cactus(generate_cactus_variant(), 1.05)]
    cacti_distances = []
    bird_distances = []
    min_cactus_index = 0
    min_bird_index = 0

    run = True

    while run and len(dinos) > 0:
        clock.tick(tick)  # function of time -> increase every 20 seconds? 100 score?
        # variable for game velocity, use this to convert time to how much distance has been travelled?
        blocks_travelled += velocity

        if blocks_travelled > WIN_WIDTH/2:
            blocks_travelled = 0
            cacti.append(Cactus(generate_cactus_variant(), multiplier))

        # might need to scale this down with acceleration
        if int(score) % level_up == 0:
            score += 1
            velocity *= 1
            score_increment *= 1
            multiplier *= 1
            # add a bird
            birds.append(Bird(generate_bird_height(BIRD_HEIGHT, FLOOR - BIRD_HEIGHT), multiplier))
            # accelerate_all(base, birds, cacti)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break

        if len(cacti) > 0:
            for cactus in cacti:
                cacti_distances.append(abs(cactus.x - 200))
            min_cactus_index = cacti_distances.index(min(cacti_distances))

        closest_bird = WIN_WIDTH
        if len(birds) > 0:
            for bird in birds:
                bird_distances.append(abs(bird.x - 200))
            min_bird_index = bird_distances.index(min(bird_distances))
            closest_bird = birds[min_bird_index].x

        for x, dino in enumerate(dinos):  # give each bird a fitness of 0.1 for each frame it stays alive
            genome_list[x].fitness += 0.1
            dino.move()

            # Just works out whether to jump or not based on cactus proximity, need to add in birds
            output = nets[dinos.index(dino)].activate((dino.x,
                                                       abs(dino.x - cacti[min_cactus_index].x),
                                                       abs(dino.x - closest_bird)))
            # abs(dino.x - birds[min_bird_index].x)) ? birds dont always exist, need a try catch?


            # outputs could be jump, duck or stand
            # between 1.0 and 0.5 -> jump
            # between 0.5 and 0 -> stand
            # between 0 and - 0.25 -> duck
            if output[0] > 0.5:  # we use a tanh activation function so result will be between -1 and 1. if over 0.5 jump
                dino.jump()
            elif 0.5 > output[0] < 0.25:
                dino.stand()
            elif 0.25 > output[0] < -1:
                dino.duck()

        base.move()
        for index, bird in enumerate(birds):
            bird.move()

            for dino in dinos:
                if bird.collide(dino):
                    genome_list[dinos.index(dino)].fitness -= 1
                    nets.pop(dinos.index(dino))
                    genome_list.pop(dinos.index(dino))
                    dinos.pop(dinos.index(dino))

            if bird.x + bird.image.get_width() < -100:
                birds.pop(index)

        for index, cactus in enumerate(cacti):
            cactus.move()

            for dino in dinos:
                if cactus.collide(dino):
                    genome_list[dinos.index(dino)].fitness -= 1
                    nets.pop(dinos.index(dino))
                    genome_list.pop(dinos.index(dino))
                    dinos.pop(dinos.index(dino))

            if cactus.x + cactus.image.get_width() < -100:
                cacti.pop(index)

        count += 1
        if count % 2 == 0:
            score += score_increment  # should accelerate with velocity of ground

        draw_dino_window(win, dinos, base, score, birds, cacti, min_cactus_index, min_cactus_index)
        cacti_distances = []
        bird_distances = []


def run(configuration_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                configuration_file)

    # Create the population, which is the top-level object for a NEAT run.
    pop = neat.Population(config)
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)

    # Run for up to 50 generations.
    max_generations = 50
    winner = pop.run(evaluate_genomes, max_generations)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))

if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'configuration_FF.txt')
    run(config_path)
