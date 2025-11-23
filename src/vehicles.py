import random
import pygame


DIRECTIONS = ("N", "S", "W", "E")


class Vehicle:
    COLOR = (30, 150, 230)
    SIZE = (22, 38)
    SPEED = 120

    def __init__(self, x, y, direction):
        self.x = float(x)
        self.y = float(y)
        self.direction = direction
        self.alive = True
        self.blocked = False
        self.passed_stop = False
        self._should_stop_cached = False
        self.turned = False
        self.priority = False

        self.turn_target_dir = None
        self.turn_triggered = False

    def rect(self):
        w, h = self.SIZE
        if self.direction in ("W", "E"):
            w, h = h, w
        return pygame.Rect(int(self.x - w/2), int(self.y - h/2), w, h)

    def update(self, dt, game):
        if self.blocked:
            return

        self._should_stop_cached = self._should_stop(game)
        if self._should_stop_cached:
            return

        if not self.priority and self._should_yield(game):
            self._should_stop_cached = True
            return

        self.try_turn_if_needed(game)

        v = self.SPEED * dt
        if self.direction == "N":
            self.y += v
        elif self.direction == "S":
            self.y -= v
        elif self.direction == "W":
            self.x += v
        elif self.direction == "E":
            self.x -= v

        if (self.x < -80 or self.x > game.WIDTH + 80 or
            self.y < -80 or self.y > game.HEIGHT + 80):
            self.alive = False

        road = game.road
        cx, cy = road.center_x, road.center_y
        off = road.stop_offset
        margin = 2

        if not self.passed_stop:
            if self.direction == "N":
                if self.y >= (cy - off + margin):
                    self.passed_stop = True
            elif self.direction == "S":
                if self.y <= (cy + off - margin):
                    self.passed_stop = True
            elif self.direction == "W":
                if self.x >= (cx - off + margin):
                    self.passed_stop = True
            elif self.direction == "E":
                if self.x <= (cx + off - margin):
                    self.passed_stop = True

    def try_turn_if_needed(self, game):
        road = game.road
        arms = road.arms()
        cx, cy = road.center_x, road.center_y
        lane = road.lane_width / 2
        inter_half = road.road_width // 2

        if self.turn_triggered:
            return

        if self.turn_target_dir is None:
            forward_arm = {
                "N": "S",
                "S": "N",
                "W": "E",
                "E": "W",
            }[self.direction]

            if arms.get(forward_arm, True):
                return

            options = []

            if self.direction in ("N", "S"):
                if arms.get("W"):
                    options.append("E")
                if arms.get("E"):
                    options.append("W")
            else:
                if arms.get("N"):
                    options.append("S")
                if arms.get("S"):
                    options.append("N")

            if not options:
                return

            self.turn_target_dir = random.choice(options)
            self.turned = True

        if self.direction == "S":
            if self.y > cy:
                return
        elif self.direction == "N":
            if self.y < cy:
                return
        elif self.direction == "W":
            if self.x < cx:
                return
        elif self.direction == "E":
            if self.x > cx:
                return

        new_dir = self.turn_target_dir
        self.direction = new_dir
        self.turn_triggered = True
        self.turn_target_dir = None

        if new_dir in ("W", "E"):
            if new_dir == "W":
                self.y = cy + lane
            else:
                self.y = cy - lane
        else:
            if new_dir == "N":
                self.x = cx - lane
            else:
                self.x = cx + lane

    def _should_stop(self, game):
        if self.priority:
            return False

        if self.passed_stop:
            return False

        road = game.road
        cx, cy = road.center_x, road.center_y
        off = road.stop_offset

        group = "vertical" if self.direction in ("N", "S") else "horizontal"
        light_state = game.controller.get_group_state(group)
        red_like = light_state in ("RED", "RED_YELLOW")

        if not red_like:
            return False

        stop_margin = 6

        if self.direction == "N":
            stop_y = cy - off
            return self.y + self.SIZE[1]/2 >= stop_y - stop_margin

        if self.direction == "S":
            stop_y = cy + off
            return self.y - self.SIZE[1]/2 <= stop_y + stop_margin

        if self.direction == "W":
            stop_x = cx - off
            return self.x + self.SIZE[1]/2 >= stop_x - stop_margin

        if self.direction == "E":
            stop_x = cx + off
            return self.x - self.SIZE[1]/2 <= stop_x + stop_margin

        return False

    def _should_yield(self, game):
        YIELD_DIST = 90

        for other in game.vehicles:
            if not other.priority:
                continue
            if other.direction != self.direction:
                continue

            if self.direction == "N":
                if other.y > self.y and (other.y - self.y) < YIELD_DIST:
                    return True
            elif self.direction == "S":
                if other.y < self.y and (self.y - other.y) < YIELD_DIST:
                    return True
            elif self.direction == "W":
                if other.x > self.x and (other.x - self.x) < YIELD_DIST:
                    return True
            elif self.direction == "E":
                if other.x < self.x and (self.x - other.x) < YIELD_DIST:
                    return True

        return False


    def is_waiting(self):

        return self.blocked or self._should_stop_cached


    def draw(self, screen):
        pygame.draw.rect(screen, self.COLOR, self.rect(), border_radius=4)


class Car(Vehicle):
    COLOR = (40, 170, 240)
    SPEED = 140

class Ambulance(Vehicle):
    COLOR = (255, 255, 255)
    SPEED = 200

    def __init__(self, x, y, direction):
        super().__init__(x, y, direction)
        self.priority = True  # важная


class PoliceCar(Vehicle):
    COLOR = (40, 90, 255)
    SPEED = 190

    def __init__(self, x, y, direction):
        super().__init__(x, y, direction)
        self.priority = True

class VehicleFactory:

    @staticmethod
    def create(direction, game):
        road = game.road
        cx, cy = road.center_x, road.center_y
        lane = road.lane_width / 2

        if direction == "N":
            x = cx - lane
            y = -50
        elif direction == "S":
            x = cx + lane
            y = game.HEIGHT + 50
        elif direction == "W":
            x = -50
            y = cy + lane
        elif direction == "E":
            x = game.WIDTH + 50
            y = cy - lane
        else:
            x, y = cx, cy

        r = random.random()
        if r < 0.08:
            return Ambulance(x, y, direction)
        elif r < 0.14:
            return PoliceCar(x, y, direction)
        else:
            return Car(x, y, direction)