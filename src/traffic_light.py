from __future__ import annotations

import pygame

from abc import ABC, abstractmethod

class LightState(ABC):

    @abstractmethod
    def next_state(self) -> "LightState":
        pass

    @abstractmethod
    def color(self) -> tuple[int, int, int]:
        pass

    @abstractmethod
    def name(self) -> str:
        pass


class RedState(LightState):
    def next_state(self) -> LightState:
        return RedYellowState()

    def color(self):
        return (200, 0, 0)

    def name(self):
        return "RED"

class GreenState(LightState):
    def next_state(self) -> LightState:
        return YellowState()

    def color(self):
        return (0, 200, 0)

    def name(self):
        return "GREEN"


class YellowState(LightState):
    def next_state(self) -> LightState:
        return RedState()

    def color(self):
        return (230, 230, 0)

    def name(self):
        return "YELLOW"

class RedYellowState(LightState):
    def next_state(self) -> LightState:
        return GreenState()

    def color(self):
        return None

    def name(self):
        return "RED_YELLOW"

class TrafficLight:
    HOUSING_COLOR = (20, 20, 20)
    OUTLINE_COLOR = (80, 80, 80)

    def __init__(self, x, y, direction, cycle_time=3.0):
        self.x = x
        self.y = y
        self.direction = direction

        self._state: LightState = RedState()
        self._timer = 0.0
        self.cycle_time = cycle_time

    def update(self, dt: float):
        self._timer += dt
        if self._timer >= self.cycle_time:
            self._timer = 0.0
            self._state = self._state.next_state()

    def switch_manual(self):
        self._timer = 0.0
        self._state = self._state.next_state()

    def current_color(self):
        return self._state.color()

    def current_name(self):
        return self._state.name()

    def set_state(self, state):
        self._state = state
        self._timer = 0.0

    def draw(self, screen):
        if self.direction == "vertical":
            w, h = 26, 70
            lamp_positions = [
                (self.x, self.y - 18),
                (self.x, self.y),
                (self.x, self.y + 18),
            ]
        else:
            w, h = 70, 26
            lamp_positions = [
                (self.x - 18, self.y),
                (self.x, self.y),
                (self.x + 18, self.y),
            ]

        body_rect = (self.x - w // 2, self.y - h // 2, w, h)

        pygame.draw.rect(screen, self.HOUSING_COLOR, body_rect, border_radius=6)
        pygame.draw.rect(screen, self.OUTLINE_COLOR, body_rect, width=2, border_radius=6)

        colors = {
            "RED": (200, 0, 0),
            "YELLOW": (230, 230, 0),
            "GREEN": (0, 200, 0),
        }
        off_color = (50, 50, 50)

        active = self.current_name()

        glow = {
            "RED": [0],
            "RED_YELLOW": [0, 1],
            "YELLOW": [1],
            "GREEN": [2],
        }

        order = ["RED", "YELLOW", "GREEN"]

        for i, name in enumerate(order):
            pos = lamp_positions[i]

            if i in glow[active]:
                color = colors[name]
            else:
                color = off_color

            pygame.draw.circle(screen, color, pos, 9)
            pygame.draw.circle(screen, (10, 10, 10), pos, 9, 2)