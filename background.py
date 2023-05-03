import pygame
import os

BASE_IMAGE = pygame.image.load(os.path.join("assets/Sprites", "Ground.png"))


class Base:
    BASE_VEL = 15
    WIDTH = BASE_IMAGE.get_width()
    IMAGE = BASE_IMAGE

    def __init__(self, y):
        self.y = y
        self.left = 0  # x-left
        self.right = self.WIDTH  # x-right
        self.vel = self.BASE_VEL

    def move(self):
        self.left -= self.vel
        self.right -= self.vel

        if self.left + self.WIDTH < 0:
            self.left = self.right + self.WIDTH
        if self.right + self.WIDTH < 0:
            self.right = self.left + self.WIDTH

    def draw(self, win):
        win.blit(self.IMAGE, (self.left, self.y))
        win.blit(self.IMAGE, (self.right, self.y))

    def accelerate(self, multiplier):
        self.vel = self.BASE_VEL * multiplier

