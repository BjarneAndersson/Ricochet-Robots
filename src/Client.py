import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

from src.Screen import Screen

from Helpers import Colors
from Network import Network

import pygame
import pygame.freetype

window: pygame.display
network: Network
colors: Colors
player_id: int
screen: Screen

pygame.init()


def is_position_on_grid(position: dict) -> bool:
    board_rect = network.send("GET game/board/rect")
    return board_rect.collidepoint((position['x'], position['y']))


def is_position_on_menu_button(position: dict) -> bool:
    return screen.menu.button.rect.collidepoint((position['x'], position['y']))


def is_position_on_menu_entry(position: dict) -> bool:
    return screen.menu.is_position_on_entry(position)


def is_position_on_input_field(position: dict) -> bool:
    return screen.individual_solution.input_field.rect.collidepoint((position['x'], position['y']))


def is_position_on_ready_button(position: dict) -> bool:
    return screen.ready_button.rect.collidepoint((position['x'], position['y']))


def convert_pygame_key_to_direction_str(key) -> str:
    if key == pygame.K_UP:
        return "up"
    elif key == pygame.K_DOWN:
        return "down"
    elif key == pygame.K_LEFT:
        return "left"
    elif key == pygame.K_RIGHT:
        return "right"


def set_player_name(name: str):
    screen.individual_solution.set_player_name(name)


def set_player_solution(solution: int):
    screen.individual_solution.set_solution(solution)


def main():
    global window, network, colors, player_id, screen

    server: dict = {'ip': input("IP-address of the server: "),
                    'port': int(input("Port of the server: "))}

    player_name = input('Please enter your name: ')

    network = Network(server["ip"], server["port"])
    print("Connected to server!")

    player_id = int(network.send(f"POST user/new?name={player_name}"))

    screen = Screen(network, player_id)

    clock = pygame.time.Clock()
    run: bool = True

    all_fps: list = []

    try:
        while run:
            clock.tick(screen.frame_rate)
            c_fps = clock.get_fps()
            all_fps.append(c_fps)

            draw()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if pygame.mouse.get_pressed(num_buttons=5)[0]:  # left click
                    mouse_position_tpl = pygame.mouse.get_pos()
                    mouse_position = {'x': mouse_position_tpl[0], 'y': mouse_position_tpl[1]}

                    # check: mouse click on menu entry
                    if screen.menu.visible:
                        if is_position_on_menu_entry(mouse_position):
                            screen.menu.get_entry_of_position(mouse_position).action()
                        # check: mouse click on menu button
                        elif is_position_on_menu_button(mouse_position):
                            screen.menu.button.change_state()
                            screen.menu.menu_entries['change_name'].input_field.set_active_state(False)

                    # check: mouse click on the grid
                    elif is_position_on_grid(mouse_position):
                        if network.send("GET game/round/phase/move_robots"):
                            if player_id == network.send('GET user/active_player_id'):  # check: select robot
                                network.send(
                                    f"POST game/robots/select?position=({mouse_position['x']},{mouse_position['y']})")

                    # check: mouse click on client input field
                    elif is_position_on_input_field(mouse_position):
                        if network.send("GET game/round/phase/collect_solutions"):
                            if screen.individual_solution.input_field.active:
                                screen.individual_solution.input_field.set_active_state(False)
                            else:
                                screen.individual_solution.input_field.set_active_state(True)

                    # check: mouse click on ready button
                    elif is_position_on_ready_button(mouse_position):
                        is_pressed = network.send(
                            f"POST user/{player_id}/change_status_next_round")  # return state of global ready button
                        screen.ready_button.set_state(is_pressed)

                    # check: mouse click on menu button
                    elif is_position_on_menu_button(mouse_position):
                        screen.menu.button.change_state()

                    else:
                        # deactivate player input field
                        screen.individual_solution.input_field.set_active_state(False)

                if event.type == pygame.KEYDOWN:  # keyboard_input
                    if screen.individual_solution.input_field.active:
                        screen.individual_solution.input_field.handle_event(event)
                    elif screen.menu.menu_entries['change_name'].input_field.active:
                        screen.menu.menu_entries['change_name'].input_field.handle_event(event)
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
        print(e.with_traceback())
        print("Game crashed")
    finally:
        pygame.quit()
        print("Connection lost")
        print(f"Avg. fps: {sum(all_fps) / len(all_fps)}")


if __name__ == '__main__':
    main()
