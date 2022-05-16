import os
import pickle
import socket
import netifaces
import sys
from _thread import *
from datetime import datetime

import nodeenv
import pyperclip

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"  # hide pycharm import msg

import Game_Objects
from Game import Game
from Helpers import Colors
from SQL import SQL

db: SQL
active_player_count: int = 0
game_id: int
game: Game


def process_data(data: str):
    """
    process incoming data
    :param data: incoming data stream
    :return:
    """

    action: str
    path: list
    queries: dict = {}

    action, path_plus_queries = data.split(' ')
    path_plus_queries_split = path_plus_queries.split('?')
    unprocessed_path = path_plus_queries_split[0]
    path = unprocessed_path.split('/')

    # queries
    if len(path_plus_queries_split) == 2:
        unprocessed_queries = path_plus_queries_split[1]
        unprocessed_queries_split = unprocessed_queries.split('&')

        # convert queries to dict
        for query in unprocessed_queries_split:
            query_split = query.split('=')
            queries[query_split[0]] = query_split[1]

    return action, path, queries


def threaded_client(connection, address):
    global db
    global active_player_count
    global game_id
    global game

    player_id = db.get_next_id('players')
    connection.send(str.encode(str(player_id)))  # send the client the player_id

    db.update_where_from_table('games', {'player_count': active_player_count}, {'game_id': game_id})

    while True:
        try:
            data = connection.recv(4096 * 8).decode()

            if not data:
                break
            else:
                action, path, queries = process_data(data)

                game.check_if_new_draw_objects_should_be_created()

                if path[0] == 'game':
                    if action == 'GET' and len(path) == 1:  # 'GET game'
                        connection.sendall(pickle.dumps(game))
                    else:
                        if path[1] == 'board':
                            if path[2] == 'grid':
                                if action == 'GET':  # 'GET game/board/grid'
                                    connection.sendall(pickle.dumps(game.grid_draw))
                            elif path[2] == 'offset':
                                if action == 'GET':  # 'GET game/board/offset'
                                    connection.sendall(pickle.dumps(game.board_offset))
                            elif path[2] == 'rect':  # 'GET game/board/rect'
                                if action == 'GET':
                                    connection.sendall(pickle.dumps(game.board.rect))
                            if len(queries) != 0:
                                if queries['position'] == 'center':  # 'GET game/board?&position=center'
                                    connection.sendall(pickle.dumps(
                                        {'x': game.board.rect.centerx, 'y': game.board.rect.centery}))

                        elif path[1] == 'field_size':
                            if action == 'GET':
                                connection.sendall(pickle.dumps(game.FIELD_SIZE))

                        elif path[1] == 'round':
                            if path[2] == 'active':  # GET game/round/active
                                if action == 'GET':
                                    connection.sendall(pickle.dumps(game.is_round_active))

                        elif path[1] == 'robots':
                            if action == 'GET' and len(path) == 2:  # 'GET game/robots'
                                connection.sendall(pickle.dumps(game.robots_draw))

                        elif path[1] == 'targets':
                            if action == 'GET' and len(path) == 2:  # 'GET game/targets'
                                connection.sendall(pickle.dumps(game.targets_draw))

                        elif path[1] == 'hourglass':
                            if action == 'GET' and len(path) == 2:  # 'GET game/hourglass'
                                connection.sendall(pickle.dumps(game.hourglass_draw))
                            elif path[2] == 'time_over':  # GET game/hourglass/time_over
                                connection.sendall(pickle.dumps(game.hourglass.get_is_time_over()))

                        elif path[1] == 'best_solution':
                            if action == 'GET' and len(path) == 2:  # 'GET game/best_solution'
                                connection.sendall(pickle.dumps(game.best_solution_draw))

                        elif path[1] == 'menu':
                            if path[2] == 'button':
                                if action == 'GET' and len(path) == 3:  # 'GET game/menu/button'
                                    connection.sendall(pickle.dumps(game.menu.button))

                        elif path[1] == 'individual_solution':
                            if path[2] == 'position':  # 'GET game/individual_solution/position'
                                if action == 'GET' and len(path) == 3:
                                    connection.sendall(pickle.dumps(game.individual_solution['position']))
                            elif path[2] == 'size':  # 'GET game/individual_solution/size'
                                if action == 'GET':
                                    connection.sendall(pickle.dumps(game.individual_solution['size']))

                        elif path[1] == 'ready_button':
                            if path[2] == 'state':  # 'GET game/ready_button/state'
                                if action == 'GET' and len(path) == 3:
                                    if game.is_round_active:
                                        connection.send('pressed'.encode())
                                    else:
                                        connection.send('unpressed'.encode())
                            elif path[2] == 'position':  # 'GET game/ready_button/position'
                                if action == 'GET' and len(path) == 3:
                                    connection.sendall(pickle.dumps(game.ready_button['position']))
                            elif path[2] == 'size':  # 'GET game/ready_button/size'
                                if action == 'GET':
                                    connection.sendall(pickle.dumps(game.ready_button['size']))

                        elif path[1] == 'window_dimensions':
                            if action == 'GET':
                                connection.sendall(pickle.dumps(game.window_dimensions))

                        elif path[1] == 'reset':
                            game.reset()
                        else:
                            print(f"No action: {path[1]}")
                elif path[0] == 'user':

                    if path[1] == 'new':
                        if action == 'POST':
                            db.insert('players', {'game_id': game_id, 'address': f"{address[0]}:{address[1]}",
                                                  'name': queries['name']})
                            connection.send(str.encode("200"))
                    else:
                        player_id = int(path[1])

                        if path[2] == 'name':
                            if action == 'GET':
                                name = db.select_where_from_table("players", ["name"], {"player_id": player_id},
                                                                  single_result=True)
                                connection.send(str.encode(str(name)))
                            else:  # action == 'POST'
                                # game.setUserName(player_id, name)
                                pass
                        elif path[2] == 'solution':
                            if action == 'GET':
                                solution = db.select_where_from_table("players", ["solution"], {"player_id": player_id},
                                                                      single_result=True)
                                connection.send(str.encode(str(solution)))
                            else:  # action == 'POST'
                                solution = queries['value']
                                db.update_where_from_table('players', {'solution': solution}, {'player_id': player_id})
                                connection.send(str.encode(str(200)))
                                if not game.hourglass.get_is_active():
                                    game.hourglass.start_timer()
                        elif path[2] == 'change_status_next_round':  # "POST user/{id}/change_status_next_round"
                            if action == 'POST':
                                if not game.is_round_active:
                                    old_status = bool(db.select_where_from_table('players', ['ready_for_round'],
                                                                                 {'player_id': player_id},
                                                                                 single_result=True))
                                    new_status = not old_status
                                    if new_status:  # player wasn't ready
                                        db.update_where_from_table('players', {'ready_for_round': 1},
                                                                   {'player_id': player_id})
                                        game.player_count_ready_for_round += 1
                                        if game.get_is_round_ready():
                                            game.start_round()
                                    else:
                                        db.update_where_from_table('players', {'ready_for_round': 0},
                                                                   {'player_id': player_id})
                                        game.player_count_ready_for_round -= 1
                                else:
                                    new_status = True
                                connection.send(pickle.dumps(new_status))

                elif path[0] == 'colors':
                    if action == 'GET' and len(path) == 1:  # 'GET colors'
                        connection.sendall(pickle.dumps(Colors))
                elif path[0] == 'others':
                    if path[1] == 'duration':
                        pass  # calculate and update duration in db
                else:
                    print(f"Request not implemented: {data}")
        except OSError as socket_error:
            str(socket_error)
            break

    print('Lost connection')
    connection.close()
    active_player_count -= 1
    db.update_where_from_table('games', {'player_count': active_player_count}, {'game_id': game_id})


def clear_unnecessary_data_in_db() -> None:  # delete rows in chips, robots, rounds where there's a winner in the game
    request_result = db.select_where_from_table('games', ['game_id'], {'winner_player_id': 'NULL'},
                                                comparison_symbol='<>')
    if request_result is None:
        return
    else:
        finished_game_ids = [game_id_tpl[0] for game_id_tpl in request_result]
        for c_game_id in finished_game_ids:
            db.delete_where_from_table('chips', {'game_id': c_game_id})
            db.delete_where_from_table('robots', {'game_id': c_game_id})
            db.delete_where_from_table('rounds', {'game_id': c_game_id})
        print(f"Cleared tables of game_ids: {finished_game_ids}")


def main():
    global db
    global active_player_count
    global game_id
    global game

    db = SQL("localhost", "root", "")
    # db.clear_temporary_tables()

    game_id = db.get_next_id('games')
    db.insert('games', {})
    game = Game(db, game_id)
    print(f'New game created!\n')

    clear_unnecessary_data_in_db()

    print("\nWaiting for connections\n")

    while True:
        connection, address = s.accept()
        print('Connected to: ', address)

        if active_player_count >= 2:
            if not game.ready:
                print('Ready to play')
            game.ready = True
        else:
            game.ready = False

        start_new_thread(threaded_client, (connection, address))

        active_player_count += 1


if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    ip_address = netifaces.ifaddresses(netifaces.interfaces()[0])[netifaces.AF_INET][0][
        'addr']  # get ip-address of local sys

    try:
        s.bind((ip_address, 0))  # connect to local ip with port 0 -> socket will search for a free port
    except OSError as e:
        str(e)

    port = s.getsockname()[1]  # port

    s.listen()
    print(f'Server Started\nIP: {ip_address} | Port: {port}\n')
    pyperclip.copy(port)

    main()
