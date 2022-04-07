from datetime import datetime

import pygame

try:
    from src.Helpers import Colors
except ModuleNotFoundError:
    from Helpers import Colors


class Hourglass:
    color_border: tuple
    start_current_timestamp: datetime
    run: bool
    current_time: int
    max_time: int

    def __init__(self, position: dict, size: dict):
        self.position = position
        self.size = size

        self.run = False

        self.start_current_timestamp = None
        self.time_passed = 0
        self.max_time = 10

    def is_time_over(self):
        return self.time_passed == self.max_time

    def draw(self, window) -> None:
        pygame.draw.rect(window, Colors.green,
                         (self.position['x'],
                          self.position['y'],
                          self.size['width'], self.size['height']))  # fill
        pygame.draw.rect(window, Colors.dark_grey,
                         (self.position['x'],
                          self.position['y'],
                          self.size['width'], self.size['height'] - (self.size['height'] // 60) * self.time_passed))  #
        pygame.draw.rect(window, Colors.grey,
                         (self.position['x'],
                          self.position['y'],
                          self.size['width'], self.size['height']),
                         width=1)  # border

    def time_passed(self, time: int) -> None:
        self.time_passed += time
        if self.time_passed >= self.max_time:
            self.time_passed = self.max_time
            self.run = False
