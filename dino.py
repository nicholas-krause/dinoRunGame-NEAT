GROUND = 365  # For Dinosaur sprite baseline


class Dinosaur:
    # Approximate hitboxes for headless simulation/canvas rendering.
    STAND_WIDTH = 44
    STAND_HEIGHT = 47
    DUCK_WIDTH = 59
    DUCK_HEIGHT = 30

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel_y = 0
        self.tick_count = 0
        self.height = self.y
        self.is_jumping = False
        self.is_ducking = False

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

    @property
    def width(self):
        return self.DUCK_WIDTH if self.is_ducking and not self.is_jumping else self.STAND_WIDTH

    @property
    def height_px(self):
        return self.DUCK_HEIGHT if self.is_ducking and not self.is_jumping else self.STAND_HEIGHT

    def bounds(self):
        """
        Return AABB bounds as (left, top, right, bottom).
        x/y are treated as sprite bottom-left anchor.
        """
        left = self.x
        bottom = self.y
        right = left + self.width
        top = bottom - self.height_px
        return left, top, right, bottom
