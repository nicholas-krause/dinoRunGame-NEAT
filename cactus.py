GROUND = 365  # For Sprite height


class Cactus:
    BASE_VEL = 15
    SMALL_HITBOXES = {
        0: (17, 35),  # single
        1: (34, 35),  # double
        2: (51, 35),  # triple
    }
    LARGE_HITBOXES = {
        0: (25, 50),  # single
        1: (50, 50),  # double
        2: (75, 50),  # triple
    }

    def __init__(self, arguments):
        distance, size, variant = arguments
        self.x = distance  # might need to adjust this should be WIDTH + random_amount * 400
        self.y = GROUND
        self.vel = self.BASE_VEL
        self.size = size
        self.variant = variant

    def move(self):
        self.x -= self.vel

    @property
    def width(self):
        if self.size == "small":
            return self.SMALL_HITBOXES[self.variant][0]
        return self.LARGE_HITBOXES[self.variant][0]

    @property
    def height_px(self):
        if self.size == "small":
            return self.SMALL_HITBOXES[self.variant][1]
        return self.LARGE_HITBOXES[self.variant][1]

    def bounds(self):
        left = self.x
        bottom = self.y
        right = left + self.width
        top = bottom - self.height_px
        return left, top, right, bottom

    def accelerate(self, multiplier):
        self.vel = self.BASE_VEL * multiplier
