import pygame
import os


GROUND = 365 # For Sprite height
SMALL_CACTUS_IMAGES = [pygame.image.load(os.path.join("assets/Sprites", "Cactus_Small_Single.png")), pygame.image.load(os.path.join("assets/Sprites", "Cactus_Small_Double.png")), pygame.image.load(os.path.join("assets/Sprites", "Cactus_Small_Triple.png"))]
LARGE_CACTUS_IMAGES = [pygame.image.load(os.path.join("assets/Sprites", "Cactus_Large_Single.png")), pygame.image.load(os.path.join("assets/Sprites", "Cactus_Large_Double.png")), pygame.image.load(os.path.join("assets/Sprites", "Cactus_Large_Triple.png"))]


class Cactus:
    BASE_VEL = 15
    LARGE_IMAGES = LARGE_CACTUS_IMAGES
    SMALL_IMAGES = SMALL_CACTUS_IMAGES

    def __init__(self, arguments, current_multiplier):
        distance, size, variant = arguments
        self.x = distance  # might need to adjust this should be WIDTH + random_amount * 400
        self.y = GROUND
        self.vel = self.BASE_VEL
        self.size = size
        self.variant = variant
        self.image = SMALL_CACTUS_IMAGES[0]  # default image
        self.multiplier = current_multiplier

    def move(self):
        self.x -= self.vel

    def draw(self, win):
        if self.size == "small":
            images = self.SMALL_IMAGES
            self.image = images[self.variant]
        else:
            images = self.LARGE_IMAGES
            self.image = images[self.variant]

        rect = self.image.get_rect(center=self.image.get_rect(bottomleft=(self.x, self.y)).center)
        win.blit(self.image, rect)

    def collide(self, dino):
        dino_mask = dino.get_mask()
        mask = pygame.mask.from_surface(self.image)
        offset = (self.x - dino.x, self.y - round(dino.y))  # Needs tweaking

        return True if dino_mask.overlap(mask, offset) else False

    def accelerate(self):
        self.vel *= self.multiplier
