import pygame
import os


WIN_WIDTH = 1500
WIN_HEIGHT = 400
FLOOR = 280  # For Base image
GROUND = 365  # For Dinosaur sprite
BIRD_IMAGES = [pygame.image.load(os.path.join("assets/Sprites", "Bird_01.png")), pygame.image.load(os.path.join("assets/Sprites", "Bird_02.png"))]
class Bird:
    IMAGES = BIRD_IMAGES
    ANIMATION_TIME = 5
    BASE_VEL = 15

    def __init__(self, y):
        self.x = WIN_WIDTH + 200
        self.y = y
        self.vel = self.BASE_VEL
        self.image_count = 0
        self.image = self.IMAGES[0]

    def move(self):
        self.x -= self.vel

    def draw(self, win):
        self.image_count += 1

        if self.image_count < self.ANIMATION_TIME:
            self.image = self.IMAGES[0]
        elif self.image_count < self.ANIMATION_TIME*2:
            self.image = self.IMAGES[1]
        elif self.image_count < self.ANIMATION_TIME*3:
            self.image = self.IMAGES[0]
            self.image_count = 0

        rect = self.image.get_rect(center=self.image.get_rect(bottomleft=(self.x, self.y)).center)
        win.blit(self.image, rect)

    def collide(self, dino):
        dino_mask = dino.get_mask()
        mask = pygame.mask.from_surface(self.image)
        offset = (self.x - dino.x, self.y - round(dino.y))  # Needs tweaking

        return True if dino_mask.overlap(mask, offset) else False

    def accelerate(self, multiplier):
        self.vel *= multiplier
