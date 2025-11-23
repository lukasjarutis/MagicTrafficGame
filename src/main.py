import random
import pygame
import sys

from road import Road
from traffic_light import TrafficLight
from controller import IntersectionController
from commands import NextPhaseCommand
from vehicles import VehicleFactory

class Button:
    def __init__(self, rect, text, font, bg=(50, 50, 50), hover=(80, 80, 80), fg=(240, 240, 240)):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.bg = bg
        self.hover = hover
        self.fg = fg

    def draw(self, screen, mouse_pos):
        color = self.hover if self.rect.collidepoint(mouse_pos) else self.bg
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, (15, 15, 15), self.rect, width=2, border_radius=10)

        label = self.font.render(self.text, True, self.fg)
        label_rect = label.get_rect(center=self.rect.center)
        screen.blit(label, label_rect)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

class Game:
    WIDTH = 900
    HEIGHT = 700
    FPS = 60
    BG_COLOR = (30, 30, 30)
    WIN_TIME = 60.0
    JAM_THRESHOLD = 4

    def __init__(self, template="cross"):
        pygame.init()

        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Šviesoforų meistras")

        self.clock = pygame.time.Clock()

        self.running = True

        self.road = Road(self.WIDTH, self.HEIGHT, template=template)

        cx = self.road.center_x
        cy = self.road.center_y
        off = self.road.stop_offset
        rw_half = self.road.road_width // 2

        side_offset = rw_half + 35

        a = self.road.arms()

        self.lights = []

        if a["N"]:
            self.lights.append(
                TrafficLight(cx - side_offset, cy - off - 30, direction="vertical")
            )
        if a["S"]:
            self.lights.append(
                TrafficLight(cx + side_offset, cy + off + 30, direction="vertical")
            )

        if a["W"]:
            self.lights.append(
                TrafficLight(cx - off - 30, cy + side_offset, direction="horizontal")
            )
        if a["E"]:
            self.lights.append(
                TrafficLight(cx + off + 30, cy - side_offset, direction="horizontal")
            )

        vertical = [l for l in self.lights if l.direction == "vertical"]
        horizontal = [l for l in self.lights if l.direction == "horizontal"]

        self.controller = IntersectionController(vertical, horizontal)
        self.next_phase_cmd = NextPhaseCommand(self.controller)

        self.vehicles = []
        self.spawn_timer = 0.0
        self.spawn_interval = 1.0
        self.spawn_prob = 0.7

        self.time_survived = 0.0
        self.game_over = False
        self.win = False

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

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.game_over:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.restart_button.is_clicked(mouse_pos):
                        self.reset()
                    elif self.quit_button.is_clicked(mouse_pos):
                        self.running = False
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.next_phase_cmd.execute()

    def update(self, dt):
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
                    return

        waiting = sum(1 for v in self.vehicles if v.is_waiting())
        if waiting >= self.JAM_THRESHOLD:
            self.game_over = True
            self.win = False
            print("JAM! GAME OVER")
            return

        self.time_survived += dt
        if self.time_survived >= self.WIN_TIME:
            self.game_over = True
            self.win = True
            print("YOU WIN!")
            return

    def draw(self):
        self.screen.fill(self.BG_COLOR)
        self.road.draw(self.screen)

        for light in self.lights:
            light.draw(self.screen)

        for v in self.vehicles:
            v.draw(self.screen)

        # HUD: время и состояние
        timer_text = self.font.render(
            f"Time: {self.time_survived:.1f}/{self.WIN_TIME:.0f}s",
            True, (240, 240, 240)
        )
        self.screen.blit(timer_text, (10, 10))

        waiting = sum(1 for v in self.vehicles if v.is_waiting())
        jam_text = self.font.render(
            f"Waiting cars: {waiting}/{self.JAM_THRESHOLD}",
            True, (240, 240, 240)
        )
        self.screen.blit(jam_text, (10, 40))

        if self.game_over:
            overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 170))
            self.screen.blit(overlay, (0, 0))

            panel_w, panel_h = 500, 400
            panel_rect = pygame.Rect(
                (self.WIDTH - panel_w)//2,
                (self.HEIGHT - panel_h)//2,
                panel_w, panel_h
            )
            pygame.draw.rect(self.screen, (25, 25, 25), panel_rect, border_radius=18)
            pygame.draw.rect(self.screen, (90, 90, 90), panel_rect, width=2, border_radius=18)

            msg = "YOU WIN!" if self.win else "GAME OVER!"
            color = (80, 220, 120) if self.win else (240, 80, 80)
            over_text = self.big_font.render(msg, True, color)
            over_rect = over_text.get_rect(center=(self.WIDTH//2, self.HEIGHT//2 - 100))
            self.screen.blit(over_text, over_rect)

            sub = f"Time: {self.time_survived:.1f}s"
            sub_text = self.font.render(sub, True, (220, 220, 220))
            sub_rect = sub_text.get_rect(center=(self.WIDTH//2, self.HEIGHT//2 + 5))
            self.screen.blit(sub_text, sub_rect)

            self.restart_button.draw(self.screen, pygame.mouse.get_pos())
            self.quit_button.draw(self.screen, pygame.mouse.get_pos())

        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(self.FPS) / 1000

            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()

    def reset(self):
        self.vehicles.clear()
        self.spawn_timer = 0.0

        self.time_survived = 0.0
        self.game_over = False
        self.win = False

        self.controller.phase_index = 0
        self.controller.timer = 0.0
        self.controller._apply_phase()

if __name__ == "__main__":
    print("Choose intersection type:")
    print("1 - Cross (+)")
    print("2 - T (no north road)")

    choice = input("Your choice (1/2): ").strip()
    template = "t" if choice == "2" else "cross"

    game = Game(template=template)
    game.run()