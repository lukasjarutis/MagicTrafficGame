import random
import pygame
import sys

from road import Road
from traffic_light import TrafficLight
from controller import IntersectionController
from commands import NextPhaseCommand
from vehicles import VehicleFactory
from ui_button import Button
from screens import MenuScreen, OverScreen


class Game:
    WIDTH = 900
    HEIGHT = 700
    FPS = 60
    BG_COLOR = (30, 30, 30)

    WIN_TIME = 10.0
    JAM_THRESHOLD = 6

    def __init__(self, template="cross"):
        pygame.init()

        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Šviesoforų meistras")
        self.clock = pygame.time.Clock()
        self.running = True

        self.font = pygame.font.SysFont("arial", 26)
        self.big_font = pygame.font.SysFont("arial", 64, bold=True)

        btn_w, btn_h = 220, 55
        cx, cy = self.WIDTH // 2, self.HEIGHT // 2
        self.restart_button = Button(
            rect=(cx - btn_w // 2, cy + 40, btn_w, btn_h),
            text="Restart",
            font=self.font
        )
        self.quit_button = Button(
            rect=(cx - btn_w // 2, cy + 110, btn_w, btn_h),
            text="Quit",
            font=self.font
        )

        self.vehicles = []
        self.spawn_timer = 0.0
        self.spawn_interval = 1.0
        self.spawn_prob = 0.7

        self.time_survived = 0.0
        self.game_over = False
        self.win = False

        self.build_intersection(template)

        self.screen_state = MenuScreen()

    def set_screen(self, screen_state):
        self.screen_state = screen_state

    def handle_events(self):
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                self.running = False
        self.screen_state.handle_events(self, events)

    def update(self, dt):
        self.screen_state.update(self, dt)

    def draw(self):
        self.screen_state.draw(self, self.screen)
        pygame.display.flip()

    def update_playing(self, dt):
        if self.game_over:
            return

        self.controller.update(dt)

        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0.0
            if random.random() < self.spawn_prob:
                direction = random.choice(self.road.allowed_directions())
                self.vehicles.append(VehicleFactory.create(direction, self))

        for v in self.vehicles:
            v.update(dt, self)

        self.vehicles = [v for v in self.vehicles if v.alive]

        lane_groups = {}
        for v in self.vehicles:
            lane_groups.setdefault(v.direction, []).append(v)

        MIN_GAP = 45

        for direction, group in lane_groups.items():
            if direction == "N":
                group.sort(key=lambda c: c.y, reverse=True)
            elif direction == "S":
                group.sort(key=lambda c: c.y)
            elif direction == "W":
                group.sort(key=lambda c: c.x, reverse=True)
            elif direction == "E":
                group.sort(key=lambda c: c.x)

            group[0].blocked = False

            for i in range(1, len(group)):
                front = group[i - 1]
                back = group[i]
                gap = abs(front.y - back.y) if direction in ("N", "S") else abs(front.x - back.x)
                back.blocked = gap < MIN_GAP

        inter = self.road.intersection_rect()
        in_intersection = [v for v in self.vehicles if v.rect().colliderect(inter)]

        for i in range(len(in_intersection)):
            for j in range(i + 1, len(in_intersection)):
                a = in_intersection[i]
                b = in_intersection[j]
                if a.rect().colliderect(b.rect()):
                    print("CRASH!")
                    self.game_over = True
                    self.win = False
                    self.set_screen(OverScreen())
                    return

        waiting = sum(1 for v in self.vehicles if v.is_waiting())
        if waiting >= self.JAM_THRESHOLD:
            print("JAM! GAME OVER")
            self.game_over = True
            self.win = False
            self.set_screen(OverScreen())
            return

        self.time_survived += dt
        if self.time_survived >= self.WIN_TIME:
            print("YOU WIN!")
            self.game_over = True
            self.win = True
            self.set_screen(OverScreen())
            return

    def draw_playing(self, screen):
        screen.fill(self.BG_COLOR)
        self.road.draw(screen)

        for light in self.lights:
            light.draw(screen)

        for v in self.vehicles:
            v.draw(screen)

        timer_text = self.font.render(
            f"Time: {self.time_survived:.1f}/{self.WIN_TIME:.0f}s",
            True, (240, 240, 240)
        )
        screen.blit(timer_text, (10, 10))

        waiting = sum(1 for v in self.vehicles if v.is_waiting())
        jam_text = self.font.render(
            f"Waiting cars: {waiting}/{self.JAM_THRESHOLD}",
            True, (240, 240, 240)
        )
        screen.blit(jam_text, (10, 40))

    def build_intersection(self, template):
        self.road = Road(self.WIDTH, self.HEIGHT, template=template)

        cx = self.road.center_x
        cy = self.road.center_y
        off = self.road.stop_offset
        rw_half = self.road.road_width // 2
        side_offset = rw_half + 35

        a = self.road.arms()
        self.lights = []

        if a["N"]:
            self.lights.append(TrafficLight(cx - side_offset, cy - off - 30, direction="vertical"))
        if a["S"]:
            self.lights.append(TrafficLight(cx + side_offset, cy + off + 30, direction="vertical"))
        if a["W"]:
            self.lights.append(TrafficLight(cx - off - 30, cy + side_offset, direction="horizontal"))
        if a["E"]:
            self.lights.append(TrafficLight(cx + off + 30, cy - side_offset, direction="horizontal"))

        vertical = [l for l in self.lights if l.direction == "vertical"]
        horizontal = [l for l in self.lights if l.direction == "horizontal"]

        self.controller = IntersectionController(vertical, horizontal)
        self.next_phase_cmd = NextPhaseCommand(self.controller)

        self.reset()

    def reset(self):
        self.vehicles.clear()
        self.spawn_timer = 0.0
        self.time_survived = 0.0
        self.game_over = False
        self.win = False

        self.controller.phase_index = 0
        self.controller.timer = 0.0
        self.controller._apply_phase()

    def run(self):
        while self.running:
            dt = self.clock.tick(self.FPS) / 1000
            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()