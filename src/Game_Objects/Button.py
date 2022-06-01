import pygame


class Button:

    def __init__(self, position: dict, size: dict, text=''):
        self.position = position
        self.size = size
        self.rect = pygame.rect.Rect(position['x'], position['y'], size['width'], size['height'])
        self.text = text
        self.pressed = False

    def change_state(self):
        self.pressed = not self.pressed

    def set_state(self, state):
        self.pressed = state

    def update_rect(self, position, size):
        self.rect = pygame.rect.Rect(position['x'], position['y'], size['width'], size['height'])
