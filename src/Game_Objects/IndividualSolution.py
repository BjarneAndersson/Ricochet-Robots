import pygame

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

    def change_state(self):
        self.set_active_state(not self.active)

    def handle_event(self, event):
        if event.key == pygame.K_RETURN:
            solution = self.text if self.text != '' else -1
            self.network.send(f'POST user/{self.player_id}/solution?value={solution}')
            self.text = ''
            self.active = False
            self.color = Colors.input_field['inactive']
        elif event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
        else:
            if len(self.text) <= 1 and event.key in \
                    (pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                     pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9):
                self.text += event.unicode

    def draw(self, window):
        if self.text and self.active:
            text_rect = self.font.get_rect(str(self.text), size=64)
            text_rect.center = (self.position['x'] + (self.size['width'] // 2),
                                self.position['y'] + (self.size['height'] // 2))
            self.font.render_to(window, text_rect, str(self.text), self.color, size=64)

        pygame.draw.rect(window, self.color, self.rect, width=5)


class IndividualSolution:

    def __init__(self, position: dict, size: dict, font, network, player_id):
        self.position = position
        self.size = size
        self.font = font
        self.network = network
        self.player_id = player_id
        self.input_field = InputField(self.position,
                                      {'width': self.size['width'], 'height': 2 * (self.size['height'] // 3)},
                                      self.font, network, player_id)

    def draw(self, window) -> None:
        pygame.draw.rect(window, Colors.individual_solution['fill'],
                         (self.position['x'],
                          self.position['y'],
                          self.size['width'], self.size['height']))
        pygame.draw.rect(window, Colors.individual_solution['border'],
                         (self.position['x'],
                          self.position['y'],
                          self.size['width'], self.size['height']), width=3)
        pygame.draw.line(window, Colors.individual_solution['border'],
                         (self.position['x'],
                          self.position['y'] + 2 * (self.size['height'] // 3) - 1),
                         (self.position['x'] + self.size['width'] - 1,
                          self.position['y'] + 2 * (self.size['height'] // 3) - 1),
                         width=1)

        self.input_field.draw(window)

        # player solution
        player_solution = int(self.network.send(f"GET user/{self.player_id}/solution"))
        if player_solution == -1 or self.input_field.active:  # show nothing
            pass
            # pygame.draw.rect(window, Colors.individual_solution['fill'],
            #                  (self.position['x'] + 2,
            #                   self.position['y'] + 2,
            #                   self.size['width'] - 4, self.size['height'] - (self.size['width'] // 3)))
        else:  # render player solution
            text_rect = self.font.get_rect(str(player_solution), size=64)
            text_rect.center = (self.position['x'] + (self.size['width'] // 2),
                                self.position['y'] + 0.5 * 2 * (self.size['height'] // 3))
            self.font.render_to(window, text_rect, str(player_solution), (0, 0, 0), size=64)

        # render player name
        font_size_name = 26
        player_name = self.network.send(f"GET user/{self.player_id}/name")
        text_rect_name = self.font.get_rect(player_name, size=font_size_name)
        text_rect_name.center = (self.position['x'] + (self.size['width'] // 2),
                                 self.position['y'] + 2 * (self.size['height'] // 3) + (self.size['height'] // 6))
        self.font.render_to(window, text_rect_name, player_name, (0, 0, 0), size=font_size_name)
