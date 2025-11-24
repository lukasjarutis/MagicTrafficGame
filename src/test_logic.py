import os, sys
sys.path.append(os.path.dirname(__file__))

import unittest
from unittest.mock import patch

from traffic_light import RedState, RedYellowState, GreenState, YellowState, TrafficLight
from controller import IntersectionController
from road import Road
from vehicles import Car, VehicleFactory


class DummyGame:
    def __init__(self, template="cross"):
        self.WIDTH = 900
        self.HEIGHT = 700
        self.road = Road(self.WIDTH, self.HEIGHT, template=template)

        cx = self.road.center_x
        cy = self.road.center_y
        off = self.road.stop_offset
        rw_half = self.road.road_width // 2
        side_offset = rw_half + 35

        self.lights = []
        a = self.road.arms()

        if a["N"]:
            self.lights.append(TrafficLight(cx - side_offset, cy - off - 30, "vertical"))
        if a["S"]:
            self.lights.append(TrafficLight(cx + side_offset, cy + off + 30, "vertical"))
        if a["W"]:
            self.lights.append(TrafficLight(cx - off - 30, cy + side_offset, "horizontal"))
        if a["E"]:
            self.lights.append(TrafficLight(cx + off + 30, cy - side_offset, "horizontal"))

        vertical = [l for l in self.lights if l.direction == "vertical"]
        horizontal = [l for l in self.lights if l.direction == "horizontal"]
        self.controller = IntersectionController(vertical, horizontal)

        self.vehicles = []


class TestTrafficLightStates(unittest.TestCase):

    def test_state_cycle_realistic(self):
        s = RedState()
        self.assertIsInstance(s.next_state(), RedYellowState)
        s = s.next_state()
        self.assertIsInstance(s.next_state(), GreenState)
        s = s.next_state()
        self.assertIsInstance(s.next_state(), YellowState)
        s = s.next_state()
        self.assertIsInstance(s.next_state(), RedState)

    def test_state_names(self):
        self.assertEqual(RedState().name(), "RED")
        self.assertEqual(RedYellowState().name(), "RED_YELLOW")
        self.assertEqual(GreenState().name(), "GREEN")
        self.assertEqual(YellowState().name(), "YELLOW")


class TestIntersectionController(unittest.TestCase):

    def test_controller_initial_phase(self):
        game = DummyGame("cross")
        self.assertEqual(game.controller.get_group_state("vertical"), "GREEN")
        self.assertEqual(game.controller.get_group_state("horizontal"), "RED")

    def test_controller_next_phase_changes(self):
        game = DummyGame("cross")
        before_v = game.controller.get_group_state("vertical")
        game.controller.next_phase()
        after_v = game.controller.get_group_state("vertical")
        self.assertNotEqual(before_v, after_v)


class TestRoadTemplates(unittest.TestCase):

    def test_allowed_directions_cross(self):
        road = Road(900, 700, template="cross")
        self.assertCountEqual(road.allowed_directions(), ["N", "S", "W", "E"])

    def test_allowed_directions_t(self):
        road = Road(900, 700, template="t")
        self.assertCountEqual(road.allowed_directions(), ["S", "W", "E"])


class TestVehiclesLogic(unittest.TestCase):

    def test_car_stops_on_red_before_stopline(self):
        game = DummyGame("cross")

        for l in game.controller.v_lights:
            l.set_state(RedState())
        for l in game.controller.h_lights:
            l.set_state(RedState())

        cx, cy, off = game.road.center_x, game.road.center_y, game.road.stop_offset

        car = Car(cx - game.road.lane_width/2, cy - off - 20, "N")
        game.vehicles = [car]

        car.update(0.1, game)
        self.assertLess(car.y, cy - off + 1)

    def test_car_ignores_light_after_stopline(self):
        game = DummyGame("cross")

        for l in game.controller.v_lights:
            l.set_state(RedState())
        for l in game.controller.h_lights:
            l.set_state(RedState())

        cx, cy, off = game.road.center_x, game.road.center_y, game.road.stop_offset

        car = Car(cx - game.road.lane_width/2, cy - off + 10, "N")
        car.passed_stop = True

        y_before = car.y
        car.update(0.2, game)
        self.assertGreater(car.y, y_before)

    @patch("vehicles.random.random", return_value=0.99)
    def test_factory_creates_car_when_random_high(self, _):
        game = DummyGame("cross")
        v = VehicleFactory.create("N", game)
        self.assertIsInstance(v, Car)

    @patch("vehicles.random.choice", return_value="W")
    def test_turn_in_t_intersection(self, _):
        game = DummyGame("t")
        cx, cy = game.road.center_x, game.road.center_y
        lane = game.road.lane_width / 2

        car = Car(cx + lane, cy + 30, "S")
        game.vehicles = [car]

        for l in game.controller.v_lights:
            l.set_state(GreenState())

        for _ in range(10):
            car.update(0.2, game)

        self.assertIn(car.direction, ("W", "E"))


if __name__ == "__main__":
    unittest.main()