import pygame
import os

GROUND = 365  # For Dinosaur sprite
DINO_IMAGES = [pygame.image.load(os.path.join("assets/Sprites", "Dino_Idle.png")),
               pygame.image.load(os.path.join("assets/Sprites", "Dino_Run01.png")),
               pygame.image.load(os.path.join("assets/Sprites", "Dino_Run02.png")),
               pygame.image.load(os.path.join("assets/Sprites", "Dino_Duck01.png")),
               pygame.image.load(os.path.join("assets/Sprites", "Dino_Duck02.png"))]


class Dinosaur:
    IMAGES = DINO_IMAGES
    ANIMATION_TIME = 3  # COULD BE 2 OR 3

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel_y = 0
        self.tick_count = 0
        self.height = self.y
        self.image_count = 0
        self.is_jumping = False
        self.is_ducking = False
        self.image = self.IMAGES[0]

    def jump(self):
        if self.y == GROUND:
            self.vel_y = -5.7
            self.tick_count = 0
            self.height = self.y
            self.is_jumping = True

    def move(self):
        self.tick_count += 1
        elevation_change = self.is_jumping*(self.vel_y*self.tick_count + 0.36*self.tick_count**2)

        if self.is_ducking:
            elevation_change = 30
        elif elevation_change >= 25:
            elevation_change = 25
        new_y = self.y + elevation_change

        if new_y > GROUND:
            self.y = GROUND
            self.vel_y = 0
            self.is_jumping = False
        else:
            self.y = new_y
        # print(self.y)

    def duck(self):
        self.tick_count = 0
        self.vel_y = 10
        self.is_ducking = True

    def stand(self):
        self.tick_count = 0
        self.vel_y = 100
        self.is_ducking = False

    def draw(self, win):
        self.image_count += 1

        if self.is_ducking and not self.is_jumping:
            if self.image_count < self.ANIMATION_TIME:
                self.image = self.IMAGES[3]
            elif self.image_count < self.ANIMATION_TIME * 2:
                self.image = self.IMAGES[4]
            elif self.image_count < self.ANIMATION_TIME * 3:
                self.image = self.IMAGES[3]
                self.image_count = 0
        else:
            if self.y < GROUND:
                self.image = self.IMAGES[0]
                self.image_count = 0
            else:
                if self.image_count < self.ANIMATION_TIME:
                    self.image = self.IMAGES[1]
                elif self.image_count < self.ANIMATION_TIME*2:
                    self.image = self.IMAGES[2]
                elif self.image_count < self.ANIMATION_TIME*3:
                    self.image = self.IMAGES[1]
                    self.image_count = 0

        rect = self.image.get_rect(center=self.image.get_rect(bottomleft=(self.x, self.y)).center)
        win.blit(self.image, rect)


    def get_mask(self):
        return pygame.mask.from_surface(self.image)
