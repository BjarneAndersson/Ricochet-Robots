import pygame


class Button:

    def __init__(self, position: dict, size: dict):
        self.position = position
        self.size = size
        self.rect = pygame.rect.Rect(position['x'], position['y'], size['width'], size['height'])
        self.pressed = False

    def change_state(self):
        self.pressed = not self.pressed
