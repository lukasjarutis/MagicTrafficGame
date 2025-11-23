from traffic_light import RedState, RedYellowState, GreenState, YellowState


class IntersectionController:
    def __init__(self, lights_vertical, lights_horizontal):
        self.v_lights = lights_vertical
        self.h_lights = lights_horizontal

        self.phases = [
            (GreenState(), RedState(), 4.0),
            (YellowState(), RedState(), 1.5),
            (RedState(), RedYellowState(), 1.0),
            (RedState(), GreenState(), 4.0),
            (RedState(), YellowState(), 1.5),
            (RedYellowState(), RedState(), 1.0),
        ]

        self.phase_index = 0
        self.timer = 0.0

        self._apply_phase()

    def update(self, dt):
        self.timer += dt
        _, _, dur = self.phases[self.phase_index]
        if self.timer >= dur:
            self.next_phase()

    def next_phase(self):
        self.timer = 0.0
        self.phase_index = (self.phase_index + 1) % len(self.phases)
        self._apply_phase()

    def _apply_phase(self):
        v_state, h_state, _ = self.phases[self.phase_index]

        for l in self.v_lights:
            l.set_state(v_state)

        for l in self.h_lights:
            l.set_state(h_state)

    def get_group_state(self, group_name: str) -> str:
        if group_name == "vertical":
            return self.v_lights[0].current_name()
        else:
            return self.h_lights[0].current_name()