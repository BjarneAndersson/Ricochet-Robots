import sys

import pygame.freetype

from Helpers import Colors
from Network import Network


# from Game_Objects import IndividualSolution


class Input_Field:
    COLOR_ACTIVE = (255, 0, 0)
    COLOR_INACTIVE = (255, 255, 255)

    def __init__(self, position: dict, size: dict, text=''):
        self.position = position
        self.size = size
        self.size['height'] = 2 * (size['height'] // 3)
        self.rect = pygame.Rect(position['x'], position['y'], self.size['width'], self.size['height'])
        self.font = font
        self.active = False
        self.color = self.COLOR_INACTIVE
        self.text = text

    def change_state(self):
        self.active = not self.active
        self.color = self.COLOR_ACTIVE if self.active else self.COLOR_INACTIVE

    def handle_event(self, event):
        if event.key == pygame.K_RETURN:
            network.send(f'POST user/{player_id}/solution?&value={self.text}')
            self.text = ''
            self.active = False
            self.color = self.COLOR_INACTIVE
        elif event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
        else:
            if len(self.text) <= 1 and event.key in \
                    (pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                     pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9):
                self.text += event.unicode

    def draw(self):
        text_rect = self.font.get_rect(str(self.text), size=64)
        text_rect.center = (self.position['x'] + 2 * (self.size['width'] // 4),
                            self.position['y'] + 0.75 * (self.size['height'] // 3))
        self.font.render_to(window, text_rect, str(self.text), self.color, size=64)

        pygame.draw.rect(window, self.color, self.rect, 4)


window: pygame.display
network: Network
colors: Colors
player_id: int
input_field: Input_Field
font: pygame.freetype

pygame.init()


def draw_grid() -> None:
    board_offset = network.send("GET game/board/offset")
    field_size = network.send("GET game/field_size")

    for i in range(17):
        pygame.draw.line(window, Colors.wall,
                         (0 + board_offset['left'], i * field_size + board_offset['top']),
                         (16 * field_size + board_offset['left'], i * field_size + board_offset['top']))
        for j in range(17):
            pygame.draw.line(window, Colors.wall,
                             (i * field_size + board_offset['left'], 0 + board_offset['top']),
                             (i * field_size + board_offset['left'],
                              16 * field_size + board_offset['top']))


def draw() -> None:
    window.fill(colors.background)

    for row in network.send("GET game/board/grid"):
        for node in row:
            node.draw(window)

    draw_grid()

    for robot in network.send("GET game/robots"):
        robot.draw(window)

    if network.send("GET game/target_chips/selected"):
        network.send("GET game/target_chips/selected").target_space.draw_center(window, network.send(
            "GET game/board?&position=center"))

    network.send("GET game/menu/button").draw(window)
    network.send("GET game/hourglass").draw(window)
    network.send("GET game/individual_solution").draw(window, network, player_id, font,
                                                      input_field.active)  # if input_field not active
    # input_field.draw(window)

    pygame.display.update()


def is_position_on_grid(game, position: dict) -> bool:
    return game.board.rect.collidepoint((position['x'], position['y']))


def is_position_on_input_field(input_field, position: dict) -> bool:
    return input_field.rect.collidepoint((position['x'], position['y']))


def is_position_on_menu_button(menu_button, position: dict) -> bool:
    return menu_button.rect.collidepoint((position['x'], position['y']))


def convert_pygame_key_to_direction_str(key) -> str:
    if key == pygame.K_UP:
        return "up"
    elif key == pygame.K_DOWN:
        return "down"
    elif key == pygame.K_LEFT:
        return "left"
    elif key == pygame.K_RIGHT:
        return "right"


def main():
    global window, network, server, colors, player_id, input_field, font

    # player_name = input('Please enter your name: ')
    player_name = 'Bjarne'
    network = Network(server["ip"], server["port"])
    player_id = network.get_player_id()
    network.send(f"POST user/new?name={player_name}")

    font = pygame.freetype.SysFont('Comic Sans MS', 0)

    run: bool = True

    try:
        colors = network.send('GET colors')
    except:
        run = False
        print("Could not get data from the server")

    input_field = Input_Field(network.send("GET game/individual_solution/position"),
                              network.send("GET game/individual_solution/size"))

    window = pygame.display.set_mode(network.send("GET game/window_dimensions"))
    pygame.display.set_caption("Ricochet Robots")

    clock = pygame.time.Clock()

    try:
        while run:
            clock.tick(30)  # 30 fps

            draw()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

    except:
        raise RuntimeError("Game crashed")
    finally:
        pygame.quit()


if __name__ == '__main__':
    # ip_server = input("IP-address of the server: ")
    server: dict = {"ip": "192.168.1.113",
                    "port": 5555}

    main()
