import pygame

from .Button import Button
from src.Helpers import Colors


class ReadyButton(Button):
    def __init__(self, position, size):
        super(ReadyButton, self).__init__(position, size)

    def draw(self, window):
        if self.pressed:
            color = Colors.ready_button['pressed']
        else:
            color = Colors.ready_button['unpressed']
        pygame.draw.rect(window, color, self.rect)
