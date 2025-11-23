import pygame


class Road:
    ROAD_COLOR = (60, 60, 60)
    LINE_COLOR = (220, 220, 220)
    STOP_LINE_COLOR = (255, 255, 255)

    STOP_LINE_THICKNESS = 7
    STOP_LINE_LENGTH_K = 0.95

    def __init__(self, width, height, template="cross"):
        self.width = width
        self.height = height
        self.template = template

        self.road_width = 220
        self.lane_width = self.road_width // 2
        self.center_x = width // 2
        self.center_y = height // 2

        self.dash_len = 28
        self.dash_gap = 22

        self.stop_offset = self.road_width // 2 + 15
        self.dash_start_offset = 12

    def draw(self, screen):
        self._draw_roads(screen)
        self._draw_center_lines(screen)
        self._draw_stop_lines(screen)

    def _draw_roads(self, screen):
        a = self.arms()
        cx, cy = self.center_x, self.center_y
        rw = self.road_width

        if a["N"] and a["S"]:
            vert_rect = pygame.Rect(cx - rw // 2, 0, rw, self.height)
            pygame.draw.rect(screen, self.ROAD_COLOR, vert_rect)
        else:
            vert_rect = pygame.Rect(
                cx - rw // 2,
                cy - rw // 2,
                rw,
                self.height - (cy - rw // 2)
            )
            pygame.draw.rect(screen, self.ROAD_COLOR, vert_rect)

        if a["W"] or a["E"]:
            hor_rect = pygame.Rect(0, cy - rw // 2, self.width, rw)
            pygame.draw.rect(screen, self.ROAD_COLOR, hor_rect)

    def _draw_center_lines(self, screen):
        a = self.arms()
        cx, cy = self.center_x, self.center_y
        off = self.stop_offset
        start_gap = self.dash_start_offset

        if a["N"]:
            self._draw_dashes_vertical(
                screen, x=cx,
                y_start=cy - off - start_gap,
                y_end=0,
                direction=-1
            )
        if a["S"]:
            self._draw_dashes_vertical(
                screen, x=cx,
                y_start=cy + off + start_gap,
                y_end=self.height,
                direction=1
            )
        if a["W"]:
            self._draw_dashes_horizontal(
                screen, y=cy,
                x_start=cx - off - start_gap,
                x_end=0,
                direction=-1
            )
        if a["E"]:
            self._draw_dashes_horizontal(
                screen, y=cy,
                x_start=cx + off + start_gap,
                x_end=self.width,
                direction=1
            )

    def _draw_dashes_vertical(self, screen, x, y_start, y_end, direction):
        step = self.dash_len + self.dash_gap
        y = y_start

        if direction == -1:
            cond = lambda yy: yy > y_end
        else:
            cond = lambda yy: yy < y_end

        while cond(y):
            y2 = y + direction * self.dash_len
            pygame.draw.line(screen, self.LINE_COLOR, (x, y), (x, y2), 3)
            y += direction * step

    def _draw_dashes_horizontal(self, screen, y, x_start, x_end, direction):
        step = self.dash_len + self.dash_gap
        x = x_start

        if direction == -1:
            cond = lambda xx: xx > x_end
        else:
            cond = lambda xx: xx < x_end

        while cond(x):
            x2 = x + direction * self.dash_len
            pygame.draw.line(screen, self.LINE_COLOR, (x, y), (x2, y), 3)
            x += direction * step

    def _draw_stop_lines(self, screen):
        a = self.arms()
        cx, cy = self.center_x, self.center_y
        rw = self.road_width

        half_len = int((rw * self.STOP_LINE_LENGTH_K) / 2)
        t = self.STOP_LINE_THICKNESS
        off = self.stop_offset

        if a["N"]:
            pygame.draw.line(
                screen, self.STOP_LINE_COLOR,
                (cx - half_len, cy - off),
                (cx + half_len, cy - off),
                t
            )
        if a["S"]:
            pygame.draw.line(
                screen, self.STOP_LINE_COLOR,
                (cx - half_len, cy + off),
                (cx + half_len, cy + off),
                t
            )
        if a["W"]:
            pygame.draw.line(
                screen, self.STOP_LINE_COLOR,
                (cx - off, cy - half_len),
                (cx - off, cy + half_len),
                t
            )
        if a["E"]:
            pygame.draw.line(
                screen, self.STOP_LINE_COLOR,
                (cx + off, cy - half_len),
                (cx + off, cy + half_len),
                t
            )

    def intersection_rect(self):
        size = self.road_width
        return pygame.Rect(
            self.center_x - size // 2,
            self.center_y - size // 2,
            size, size
        )

    def arms(self):
        if self.template == "cross":
            return {"N": True, "S": True, "W": True, "E": True}
        if self.template == "t":
            return {"N": False, "S": True, "W": True, "E": True}
        return {"N": True, "S": True, "W": True, "E": True}

    def allowed_directions(self):
        a = self.arms()
        return [d for d, ok in a.items() if ok]