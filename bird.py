WIN_WIDTH = 1500


class Bird:
    BASE_VEL = 15
    WIDTH = 46
    HEIGHT = 40

    def __init__(self, y):
        self.x = WIN_WIDTH + 200
        self.y = y
        self.vel = self.BASE_VEL

    def move(self):
        self.x -= self.vel

    def bounds(self):
        left = self.x
        bottom = self.y
        right = left + self.WIDTH
        top = bottom - self.HEIGHT
        return left, top, right, bottom

    def accelerate(self, multiplier):
        self.vel = self.BASE_VEL * multiplier
