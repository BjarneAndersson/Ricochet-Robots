from datetime import datetime

import pygame

try:
    from src.Helpers import Colors
except ModuleNotFoundError:
    from Helpers import Colors


class HourglassDraw:
    def __init__(self, position, size, percentage_of_fill):
        self.position = position
        self.size = size
        self.percentage_of_fill = percentage_of_fill

    def draw(self, window) -> None:
        # background
        pygame.draw.rect(window, Colors.hourglass['background'],
                         (self.position['x'],
                          self.position['y'],
                          self.size['width'], self.size['height']))

        # fill
        pygame.draw.rect(window, Colors.hourglass['fill'],
                         (self.position['x'],
                          self.position['y'] + (1 - self.percentage_of_fill) * self.size['height'],
                          self.size['width'], self.percentage_of_fill * self.size['height']))

        # border
        pygame.draw.rect(window, Colors.hourglass['border'],
                         (self.position['x'],
                          self.position['y'],
                          self.size['width'], self.size['height']),
                         width=1)  # border


class Hourglass:
    def __init__(self, position: dict, size: dict):
        self.position = position
        self.size = size

        self.run = False

        self.start_timestamp = None
        self.active = False
        self.time_passed = 0
        self.max_time = 10

    def start_timer(self):
        self.start_timestamp = datetime.timestamp(datetime.now())
        self.active = True

    def calc_passed_time(self):
        current_timestamp = datetime.timestamp(datetime.now())
        self.time_passed = current_timestamp - self.start_timestamp
        if self.time_passed >= self.max_time:
            self.time_passed = self.max_time
            self.start_timestamp = None
            self.active = False

    def reset(self):
        self.active = False
        self.start_timestamp = None
        self.time_passed = 0

    def get_is_active(self):
        return self.active

    def get_is_time_over(self):
        return self.time_passed == self.max_time

    def create_obj_for_draw(self):
        percentage_of_fill = self.time_passed / self.max_time
        obj_hourglass_draw = HourglassDraw(self.position, self.size, percentage_of_fill)
        return obj_hourglass_draw
