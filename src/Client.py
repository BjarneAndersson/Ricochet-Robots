import cProfile
import os
import pstats
import timeit

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

from src.Game_Objects import ReadyButton
from src.Game_Objects import IndividualSolution
from src.Game_Objects import Menu
from Helpers import Colors
from Network import Network

import pygame
import pygame.freetype

window: pygame.display
network: Network
colors: Colors
player_id: int
menu: Menu
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
    window.fill(colors.background)

    for row in network.send("GET game/board/grid"):
        for node in row:
            node.draw(window)

    draw_grid()

    targets = network.send("GET game/targets")
    if type(targets) == list:
        for target in targets:
            target.draw(window)
    else:  # single target
        targets.draw(window)

    for robot in network.send("GET game/robots"):
        robot.draw(window)

    network.send("GET game/hourglass").draw(window)

    menu.draw(window, font)

    individual_solution.draw(window)

    ready_button.set_state(network.send(f"GET user/{player_id}/ready_button/state"))  # update state
    ready_button.draw(window)

    network.send("GET game/best_solution").draw(window, font)

    network.send("GET game/leaderboard").draw(window, font)

    pygame.display.update()


def is_position_on_grid(position: dict) -> bool:
    board_rect = network.send("GET game/board/rect")
    return board_rect.collidepoint((position['x'], position['y']))


def is_position_on_menu_button(position: dict) -> bool:
    return menu.button.rect.collidepoint((position['x'], position['y']))


def is_position_on_menu_entry(position: dict) -> bool:
    return menu.is_position_on_entry(position)


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
    global window, network, server, colors, player_id, menu, individual_solution, ready_button, font

    network = Network(server["ip"], server["port"])
    print("Connected to server!")

    player_id = int(network.send(f"POST user/new?name={player_name}"))
    # print(player_id)

    font = pygame.freetype.SysFont('Comic Sans MS', 0)

    # get the color scheme from the server
    colors = network.send('GET colors')

    # initialize local GUI elements
    menu = Menu(network.send("GET game/menu/position"),
                network.send("GET game/menu/button"),
                font, network, player_id)

    individual_solution = IndividualSolution(network.send("GET game/individual_solution/position"),
                                             network.send("GET game/individual_solution/size"), font, network,
                                             player_id)
    ready_button = ReadyButton(network.send("GET game/ready_button/position"),
                               network.send("GET game/ready_button/size"))
    ready_button.set_state(network.send("GET game/ready_button/state"))

    # initialize window
    window = pygame.display.set_mode(network.send("GET game/window_dimensions"))
    pygame.display.set_caption("Ricochet Robots")

    frame_rate = network.send("GET others/server_tick_rate")

    clock = pygame.time.Clock()
    run: bool = True

    try:
        while run:
            clock.tick(frame_rate)
            print(f"FPS: {clock.get_fps()}")

            t_draw_s = timeit.default_timer()
            draw()
            t_draw_e = timeit.default_timer()
            print(f"Time | draw: {t_draw_e - t_draw_s}")

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if pygame.mouse.get_pressed(num_buttons=5)[0]:  # left click
                    mouse_position_tpl = pygame.mouse.get_pos()
                    mouse_position = {'x': mouse_position_tpl[0], 'y': mouse_position_tpl[1]}

                    # check: mouse click on menu entry
                    if menu.visible:
                        if is_position_on_menu_entry(mouse_position):
                            menu.get_entry_of_position(mouse_position).action()
                        # check: mouse click on menu button
                        elif is_position_on_menu_button(mouse_position):
                            menu.button.change_state()
                            menu.menu_entries['change_name'].input_field.set_active_state(False)

                    # check: mouse click on the grid
                    elif is_position_on_grid(mouse_position):
                        if network.send("GET game/round/phase/move_robots"):
                            if player_id == network.send('GET user/active_player_id'):  # check: select robot
                                network.send(
                                    f"POST game/robots/select?position_x={mouse_position['x']}&position_y={mouse_position['y']}")

                    # check: mouse click on client input field
                    elif is_position_on_input_field(mouse_position):
                        if network.send("GET game/round/phase/collect_solutions"):
                            if individual_solution.input_field.active:
                                individual_solution.input_field.set_active_state(False)
                            else:
                                individual_solution.input_field.set_active_state(True)

                    # check: mouse click on ready button
                    elif is_position_on_ready_button(mouse_position):
                        break
                        is_pressed = network.send(
                            f"POST user/{player_id}/change_status_next_round")  # return state of global ready button
                        ready_button.set_state(is_pressed)

                    # check: mouse click on menu button
                    elif is_position_on_menu_button(mouse_position):
                        menu.button.change_state()

                    else:
                        # deactivate player input field
                        individual_solution.input_field.set_active_state(False)

                if event.type == pygame.KEYDOWN:  # keyboard_input
                    if individual_solution.input_field.active:
                        individual_solution.input_field.handle_event(event)
                    elif menu.menu_entries['change_name'].input_field.active:
                        menu.menu_entries['change_name'].input_field.handle_event(event)
                    elif player_id == network.send('GET user/active_player_id'):
                        if network.send('GET game/robots/select'):
                            if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                                network.send(
                                    f'POST game/robots/move?direction={convert_pygame_key_to_direction_str(event.key)}')
                        if event.key == pygame.K_TAB:
                            network.send(f"POST game/robots/switch")

    except pygame.error as pygame_error:
        print(pygame_error)
        print("Connection closed")
    except Exception as e:
        print(e)
        raise RuntimeError("Game crashed")
    finally:
        pygame.quit()
        print("Connection lost")


if __name__ == '__main__':
    # ip_server = input("IP-address of the server: ")
    port_server = int(input("Port of the server: "))
    server: dict = {"ip": "192.168.1.113", "port": port_server}
    # server: dict = {'ip': ip_server, 'port': port_server}

    # player_name = input('Please enter your name: ')
    player_name = 'PC'

    profile = cProfile.Profile()
    profile.runcall(main)
    ps = pstats.Stats(profile)
    ps.sort_stats('tottime')
    ps.print_stats(20)
    # main()
