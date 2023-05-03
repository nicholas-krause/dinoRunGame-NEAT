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
# import neat
# import visualize
# import pickle

pygame.font.init()  # init font

WIN_WIDTH = 1500
WIN_HEIGHT = 400
FLOOR = 280  # For Base image
GROUND = 365 # For Dinosaur sprite
BIRD_HEIGHT = 96
FONT_COLOUR = (90, 90, 90)
STAT_FONT = pygame.font.Font(os.path.join("fonts/PublicPixel.ttf"), 18)
END_FONT = pygame.font.SysFont("comicsans", 70)

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Chrome Dino Game")
BACKGROUND_COLOUR = (247, 247, 247)  # Grey


def draw_dino_window(win, dino, base, score, birds, cacti):
    pygame.draw.rect(win, BACKGROUND_COLOUR, [0, 0, WIN_WIDTH, WIN_HEIGHT])
    dino.draw(win)
    base.draw(win)
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
    score_label = STAT_FONT.render("Score: " + extra + str(score), 1, FONT_COLOUR)
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

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


def main():
    score = 0
    count = 0
    velocity = 10
    blocks_travelled = 0
    tick = 31
    level_up = 150
    score_increment = 1
    multiplier = 1

    dino = Dinosaur(200, GROUND)
    base = Base(FLOOR)
    clock = pygame.time.Clock()
    birds = []
    cacti = [Cactus(generate_cactus_variant(), 1.05)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

    run = True

    while run:
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
                pygame.quit()
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    dino.jump()
                if event.key == pygame.K_DOWN:
                    dino.duck()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    dino.stand()

        dino.move()
        base.move()
        for index, bird in enumerate(birds):
            bird.move()
            if bird.x + bird.image.get_width() < -100:
                birds.pop(index)

        for index, cactus in enumerate(cacti):
            cactus.move()
            if cactus.x + cactus.image.get_width() < -100:
                cacti.pop(index)

        count += 1
        if count % 2 == 0:
            score += score_increment  # should accelerate with velocity of ground

        draw_dino_window(win, dino, base, score, birds, cacti)
    pygame.quit()

main()