import os
import pickle
import socket
import netifaces
import sys
from _thread import *
from datetime import datetime

import pyperclip

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"  # hide pycharm import msg

import Game_Objects
from Game import Game
from Helpers import Colors
from SQL import SQL

db: SQL
active_user_count: int = 0
game_id: int


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


def threaded_client(connection, address, game):
    global db
    global active_user_count
    global game_id

    player_id = db.get_next_id('players')
    connection.send(str.encode(str(player_id)))  # send the client the player_id

    while True:
        try:
            data = connection.recv(4096 * 8).decode()

            if not data:
                break
            else:
                action, path, queries = process_data(data)

                if path[0] == 'game':
                    if action == 'GET' and len(path) == 1:  # 'GET game'
                        connection.sendall(pickle.dumps(game))
                    else:
                        if path[1] == 'board':
                            if path[2] == 'grid':
                                if action == 'GET':  # 'GET game/board/grid'
                                    connection.sendall(pickle.dumps(game.board.grid))
                            elif path[2] == 'offset':
                                if action == 'GET':  # 'GET game/board/offset'
                                    connection.sendall(pickle.dumps(game.board_offset))
                            if len(queries) != 0:
                                if queries['position'] == 'center':  # 'GET game/board?&position=center'
                                    connection.sendall(pickle.dumps(
                                        {'x': game.board.rect.centerx, 'y': game.board.rect.centery}))

                        elif path[1] == 'field_size':
                            if action == 'GET':
                                connection.sendall(pickle.dumps(game.FIELD_SIZE))

                        elif path[1] == 'robots':
                            if action == 'GET':  # 'GET game/robots'
                                connection.sendall(pickle.dumps(game.robots))

                        elif path[1] == 'target_chips':
                            if path[2] == 'selected':
                                if action == 'GET':  # 'GET game/target_chips/selected'
                                    connection.sendall(pickle.dumps(db.select_where_from_table('chips', ['chip_id'],
                                                                                               {'game_id': game_id,
                                                                                                'revealed': 1},
                                                                                               single_result=True)))

                        elif path[1] == 'hourglass':
                            if action == 'GET' and len(path) == 2:  # 'GET game/hourglass'
                                connection.sendall(pickle.dumps(game.hourglass))

                        elif path[1] == 'menu':
                            if path[2] == 'button':
                                if action == 'GET' and len(path) == 3:  # 'GET game/menu/button'
                                    connection.sendall(pickle.dumps(game.menu.button))

                        elif path[1] == 'individual_solution':
                            if action == 'GET' and len(path) == 2:  # 'GET game/individual_solution'
                                connection.sendall(pickle.dumps(game.individual_solution))

                            elif path[2] == 'position':  # 'GET game/individual_solution/position'
                                if action == 'GET' and len(path) == 3:
                                    connection.sendall(pickle.dumps(game.individual_solution.position))
                            elif path[2] == 'size':  # 'GET game/individual_solution/size'
                                if action == 'GET':
                                    connection.sendall(pickle.dumps(game.individual_solution.size))

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
                elif path[0] == 'colors':
                    if action == 'GET' and len(path) == 1:  # 'GET colors'
                        connection.sendall(pickle.dumps(Colors))
                elif path[0] == 'others':
                    pass
                else:
                    print(f"Request not implemented: {data}")
        except OSError as socket_error:
            str(socket_error)
            break

    print('Lost connection')
    connection.close()
    active_user_count -= 1


def main():
    global db
    global active_user_count
    global game_id

    db = SQL("localhost", "root", "")
    # db.clear_temporary_tables()

    game_id = db.get_next_id('games')
    db.insert('games', {})
    game = Game(db, game_id)
    print(f'New game created!')

    while True:
        connection, address = s.accept()
        print('Connected to: ', address)

        if active_user_count >= 2:
            if not game.ready:
                print('Ready to play')
            game.ready = True
        else:
            game.ready = False

        start_new_thread(threaded_client, (connection, address, game))

        active_user_count += 1


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
    print(f'Server Started\nIP: {ip_address} | Port: {port}\nWaiting for connections\n')
    pyperclip.copy(port)

    main()
