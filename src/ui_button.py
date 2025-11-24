import pygame


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
