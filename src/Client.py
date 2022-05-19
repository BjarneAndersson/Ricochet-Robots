import sys
import os

from src.Game_Objects import ReadyButton
from src.Game_Objects import IndividualSolution

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame.freetype

from Helpers import Colors
from Network import Network


# from Game_Objects import IndividualSolution



window: pygame.display
network: Network
colors: Colors
player_id: int
individual_solution: IndividualSolution
ready_button: ReadyButton
font: pygame.freetype

pygame.init()


def draw_grid() -> None:
    board_offset = network.send("GET game/board/offset")
    field_size = network.send("GET game/field_size")

    for i in range(16 + 1):
        pygame.draw.line(window, Colors.wall,
                         (0 + board_offset['left'], i * field_size + board_offset['top']),
                         (16 * field_size + board_offset['left'], i * field_size + board_offset['top']))
        for j in range(16 + 1):
            pygame.draw.line(window, Colors.wall,
                             (i * field_size + board_offset['left'], 0 + board_offset['top']),
                             (i * field_size + board_offset['left'],
                              16 * field_size + board_offset['top']))


def draw() -> None:
    global input_field, ready_button

    window.fill(colors.background)

    for row in network.send("GET game/board/grid"):
        for node in row:
            node.draw(window)

    draw_grid()

    for target in network.send("GET game/targets"):
        target.draw(window)

    for robot in network.send("GET game/robots"):
        robot.draw(window)

    # network.send("GET game/menu/button").draw(window)
    network.send("GET game/hourglass").draw(window)

    individual_solution.draw(window)

    ready_button_state_pressed = network.send(f"GET user/{player_id}/ready_button/state")
    ready_button.set_state(ready_button_state_pressed)
    ready_button.draw(window)

    network.send("GET game/best_solution").draw(window, font)

    network.send("GET game/leaderboard").draw(window, font)

    pygame.display.update()


def is_position_on_grid(position: dict) -> bool:
    board_rect = network.send("GET game/board/rect")
    return board_rect.collidepoint((position['x'], position['y']))


def is_position_on_menu_button(menu_button, position: dict) -> bool:
    return menu_button.rect.collidepoint((position['x'], position['y']))


def is_position_on_input_field(position: dict) -> bool:
    return individual_solution.input_field.rect.collidepoint((position['x'], position['y']))


def is_position_on_ready_button(position: dict) -> bool:
    return ready_button.rect.collidepoint((position['x'], position['y']))


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
    global window, network, server, colors, player_id, individual_solution, ready_button, font

    network = Network(server["ip"], server["port"])
    print("Connected to server!")

    player_id = network.get_player_id()
    network.send(f"POST user/new?name={player_name}")

    font = pygame.freetype.SysFont('Comic Sans MS', 0)

    run: bool = True

    colors = network.send('GET colors')

    individual_solution = IndividualSolution(network.send("GET game/individual_solution/position"),
                                             network.send("GET game/individual_solution/size"), font, network,
                                             player_id)
    ready_button = ReadyButton(network.send("GET game/ready_button/position"),
                               network.send("GET game/ready_button/size"))
    ready_button.set_state(network.send("GET game/ready_button/state"))

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

                if pygame.mouse.get_pressed(num_buttons=5)[0]:  # left
                    mouse_position_tpl = pygame.mouse.get_pos()
                    mouse_position = {'x': mouse_position_tpl[0], 'y': mouse_position_tpl[1]}

                    # check: mouse click on the grid
                    if is_position_on_grid(mouse_position):  # mouse click on the grid
                        if network.send("GET game/hourglass/time_over"):
                            if player_id == network.send('GET user/active_player_id'):
                                network.send(
                                    f"POST game/robots/select?position_x={mouse_position['x']}&position_y={mouse_position['y']}")

                    # check: mouse click on client_input field
                    elif is_position_on_input_field(mouse_position):
                        is_time_over = network.send("GET game/hourglass/time_over")
                        if network.send("GET game/round/active") and not is_time_over:
                            if individual_solution.input_field.active:
                                individual_solution.input_field.set_active_state(False)
                            else:
                                individual_solution.input_field.set_active_state(True)
                    #
                    # elif is_position_on_menu_button(game.menu.button, mouse_position):
                    #     pass
                    # game.menu.button.change_state()

                    elif is_position_on_ready_button(mouse_position):
                        is_pressed = network.send(f"POST user/{player_id}/change_status_next_round")
                        ready_button.set_state(is_pressed)

                    else:
                        individual_solution.input_field.set_active_state(False)

                if event.type == pygame.KEYDOWN:  # keyboard_input
                    if individual_solution.input_field.active:
                        individual_solution.input_field.handle_event(event)
                    elif player_id == network.send('GET user/active_player_id') and network.send(
                            'GET game/robots/select'):
                        if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                            network.send(
                                f'POST game/robots/move?direction={convert_pygame_key_to_direction_str(event.key)}')

    except Exception as e:
        print(e)
        raise RuntimeError("Game crashed")
    finally:
        pygame.quit()
        print("Connection lost")


if __name__ == '__main__':
    ip_server = input("IP-address of the server: ")
    port_server = int(input("Port of the server: "))
    # server: dict = {"ip": "192.168.1.113", "port": port_server}
    server: dict = {'ip': ip_server, 'port': port_server}

    # player_name = input('Please enter your name: ')
    player_name = 'PC'

    main()
