import math
from abc import ABC, abstractmethod

import pygame

from .Button import Button

try:
    from src.Helpers import Colors
except ModuleNotFoundError:
    from Helpers import Colors


class InputField:
    def __init__(self, position: dict, size: dict, font, network, player_id, text=''):
        self.position = position
        self.size = size
        self.rect = pygame.Rect(position['x'], position['y'], self.size['width'], self.size['height'])
        self.font = font
        self.network = network
        self.player_id = player_id
        self.active = False
        self.color = Colors.input_field['inactive']
        self.text = text

    def set_active_state(self, _state):
        self.active = _state
        self.color = Colors.input_field['active'] if self.active else Colors.input_field['inactive']
        self.text = ''

    def handle_event(self, event):
        if event.key == pygame.K_RETURN:
            name = self.text if self.text != '' else self.network.send(f'GET user/{self.player_id}/name')
            self.network.send(f'POST user/{self.player_id}/name?value={name}')
            self.text = ''
            self.active = False
            self.color = Colors.input_field['inactive']
        elif event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
        else:
            if len(self.text) <= 14 and event.key in \
                    (pygame.K_a, pygame.K_b, pygame.K_c, pygame.K_d, pygame.K_e,
                     pygame.K_f, pygame.K_g, pygame.K_h, pygame.K_i, pygame.K_j, pygame.K_k, pygame.K_l, pygame.K_m,
                     pygame.K_n, pygame.K_o, pygame.K_p, pygame.K_q, pygame.K_r, pygame.K_s, pygame.K_t, pygame.K_u,
                     pygame.K_v, pygame.K_w, pygame.K_x, pygame.K_y, pygame.K_z):
                self.text += event.unicode

    def draw(self, window):
        if self.text:
            text_rect = self.font.get_rect(str(self.text), size=26)
            text_rect.center = (self.position['x'] + (self.size['width'] // 2),
                                self.position['y'] + (self.size['height'] // 2))
            self.font.render_to(window, text_rect, str(self.text), self.color, size=26)

        pygame.draw.rect(window, self.color, self.rect, width=5)


class MenuButton(Button):

    def __init__(self, position: dict, size: dict):
        super().__init__(position, size)

    def draw(self, window):
        pygame.draw.rect(window, Colors.grey,
                         (self.position['x'], self.position['y'],
                          self.size['width'], self.size['height']))

        for line in range(3):
            pygame.draw.line(window, Colors.white,
                             (self.position['x'] + self.size['width'] // 5,
                              self.position['y'] + (self.size['height'] // 4) * (line + 1)),
                             (self.position['x'] + self.size['width'] - (self.size['width'] // 5),
                              self.position['y'] + (self.size['height'] // 4) * (line + 1)),
                             width=self.size['height'] // 10)


class MenuEntry(ABC, Button):
    def __init__(self, position: dict, field_size, font, text):
        self.field_size: int = field_size
        self.text: str = text
        self.size: dict = self.calc_size(font)
        self.position: dict = position
        self.input_field: InputField = None
        super().__init__(self.position, self.size, text=self.text)

        self.calc_height()
        self.update_rect(self.position, self.size)

    def calc_size(self, font) -> dict:
        font_size_text = 26
        text_rect = font.get_rect(self.text, size=font_size_text)

        width = math.ceil(text_rect.width / self.field_size) * self.field_size

        size: dict = {'width': width, 'height': text_rect.height}
        return size

    def calc_height(self):
        height_text = 1 + self.text.count("\n")
        height_further_elements = 0
        self.size['height'] = (height_text + height_further_elements) * self.field_size

    def get_size(self) -> dict:
        return self.size

    def set_size(self, n_size: dict):
        self.size = n_size.copy()
        self.update_rect(self.position, self.size)

    def set_position(self, n_position: dict):
        self.position = n_position.copy()
        self.update_rect(self.position, self.size)

    @abstractmethod
    def action(self):
        pass

    @abstractmethod
    def draw(self, window, font):
        pygame.draw.rect(window, Colors.menu['background'], self.rect)
        pygame.draw.rect(window, Colors.menu['border'], self.rect, width=1)

        font_size_text = 26
        text_rect = font.get_rect(self.text, size=font_size_text)
        text_rect.center = self.rect.center
        font.render_to(window, text_rect, self.text, Colors.menu['font_color'], size=font_size_text)


class ChangeNameMenuEntry(MenuEntry):
    def __init__(self, position: dict, field_size, font, network, player_id):
        super().__init__(position, field_size, font, 'change name')
        self.input_field = InputField({'x': self.position['x'] + self.size['width'], 'y': self.position['y']},
                                      {'width': self.size['width'], 'height': self.size['height']},
                                      font, network, player_id)

    def action(self):
        self.change_state()
        self.input_field.set_active_state(self.pressed)

    def draw(self, window, font):
        super().draw(window, font)

        if self.input_field.active:
            self.input_field.draw(window)


class QuitMenuEntry(MenuEntry):
    def __init__(self, position: dict, field_size, font):
        super().__init__(position, field_size, font, 'quit')

    def action(self):
        pygame.quit()

    def draw(self, window, font):
        super().draw(window, font)


class Menu:

    def __init__(self, position: dict, button: dict, font, network, player_id):
        self.position = position
        self.size: dict = {}
        self.button = MenuButton(button['position'], button['size'])
        self.font = font
        self.network = network
        self.field_size = network.send("GET game/field_size")
        self.player_id = player_id

        self.menu_entries: dict[str, MenuEntry] = {}
        self.create_menu_entries()

        self.rect = pygame.Rect(self.position['x'], self.position['y'], self.size['width'], self.size['height'])

        self.visible = self.button.pressed

    def create_menu_entries(self):
        position = self.position.copy()
        overall_height: int = 0
        max_width: int = 4 * self.field_size

        self.menu_entries['change_name'] = ChangeNameMenuEntry(position, self.field_size, self.font, self.network,
                                                               self.player_id)
        self.menu_entries['quit'] = QuitMenuEntry(position, self.field_size, self.font)

        for menu_entry in self.menu_entries.values():
            menu_entry.set_position(position)
            overall_height += menu_entry.get_size()['height']
            max_width = max(max_width, menu_entry.get_size()['width'])
            position['y'] += menu_entry.get_size()['height']

        for menu_entry in self.menu_entries.values():
            menu_entry.set_size({'width': max_width, 'height': menu_entry.get_size()['height']})

        self.size = {'width': max_width, 'height': overall_height}

    def calc_size(self):
        height: int = 0

        for menu_entry in self.menu_entries.values():
            height += menu_entry.get_height()

        return height

    def is_position_on_entry(self, position: dict) -> bool:
        for menu_entry in self.menu_entries.values():
            if menu_entry.rect.collidepoint((position['x'], position['y'])):
                return True

        return False

    def get_entry_of_position(self, position: dict) -> MenuEntry:
        for menu_entry in self.menu_entries.values():
            if menu_entry.rect.collidepoint((position['x'], position['y'])):
                return menu_entry

    def draw(self, window, font) -> None:
        self.visible = self.button.pressed

        self.button.draw(window)

        if self.visible:
            for menu_entry in self.menu_entries.values():
                menu_entry.draw(window, font)
