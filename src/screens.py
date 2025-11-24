from abc import ABC, abstractmethod
import pygame
from ui_button import Button


class Screen(ABC):
    @abstractmethod
    def handle_events(self, game, events):
        pass

    @abstractmethod
    def update(self, game, dt):
        pass

    @abstractmethod
    def draw(self, game, screen):
        pass


class MenuScreen(Screen):
    def __init__(self):
        self.cross_button = None
        self.t_button = None
        self._built = False

    def _build(self, game):
        btn_w, btn_h = 300, 70
        mx, my = game.WIDTH // 2, game.HEIGHT // 2

        self.cross_button = Button(
            rect=(mx - btn_w//2, my - 60, btn_w, btn_h),
            text="Cross intersection (+)",
            font=game.font
        )
        self.t_button = Button(
            rect=(mx - btn_w//2, my + 30, btn_w, btn_h),
            text="T intersection (no North)",
            font=game.font
        )
        self._built = True

    def handle_events(self, game, events):
        if not self._built:
            self._build(game)

        mouse_pos = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.cross_button.is_clicked(mouse_pos):
                    game.build_intersection("cross")
                    game.set_screen(PlayScreen())
                elif self.t_button.is_clicked(mouse_pos):
                    game.build_intersection("t")
                    game.set_screen(PlayScreen())

    def update(self, game, dt):
        pass

    def draw(self, game, screen):
        screen.fill(game.BG_COLOR)

        title = game.big_font.render("Šviesoforų meistras", True, (240, 240, 240))
        title_rect = title.get_rect(center=(game.WIDTH//2, game.HEIGHT//2 - 170))
        screen.blit(title, title_rect)

        subtitle = game.font.render("Choose intersection type:", True, (200, 200, 200))
        subtitle_rect = subtitle.get_rect(center=(game.WIDTH//2, game.HEIGHT//2 - 110))
        screen.blit(subtitle, subtitle_rect)

        mp = pygame.mouse.get_pos()
        self.cross_button.draw(screen, mp)
        self.t_button.draw(screen, mp)


class PlayScreen(Screen):
    def handle_events(self, game, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game.next_phase_cmd.execute()

    def update(self, game, dt):
        game.update_playing(dt)

    def draw(self, game, screen):
        game.draw_playing(screen)


class OverScreen(Screen):
    def handle_events(self, game, events):
        mouse_pos = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game.restart_button.is_clicked(mouse_pos):
                    template = game.road.template
                    game.build_intersection(template)
                    game.set_screen(PlayScreen())
                elif game.quit_button.is_clicked(mouse_pos):
                    game.running = False

    def update(self, game, dt):
        pass

    def draw(self, game, screen):
        game.draw_playing(screen)

        overlay = pygame.Surface((game.WIDTH, game.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        screen.blit(overlay, (0, 0))

        panel_w, panel_h = 520, 300
        panel_rect = pygame.Rect(
            (game.WIDTH - panel_w) // 2,
            (game.HEIGHT - panel_h) // 2,
            panel_w, panel_h
        )
        pygame.draw.rect(screen, (25, 25, 25), panel_rect, border_radius=18)
        pygame.draw.rect(screen, (90, 90, 90), panel_rect, width=2, border_radius=18)

        msg = "YOU WIN!" if game.win else "GAME OVER!"
        color = (80, 220, 120) if game.win else (240, 80, 80)
        over_text = game.big_font.render(msg, True, color)
        over_rect = over_text.get_rect(center=(game.WIDTH // 2, game.HEIGHT // 2 - 40))
        screen.blit(over_text, over_rect)

        sub = f"Time: {game.time_survived:.1f}s"
        sub_text = game.font.render(sub, True, (220, 220, 220))
        sub_rect = sub_text.get_rect(center=(game.WIDTH // 2, game.HEIGHT // 2 + 5))
        screen.blit(sub_text, sub_rect)

        game.restart_button.draw(screen, pygame.mouse.get_pos())
        game.quit_button.draw(screen, pygame.mouse.get_pos())