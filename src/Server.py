import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"  # hide pycharm import msg

import pickle
import socket
import netifaces
import selectors
import types

import pyperclip

from datetime import datetime

from Game import Game
from Helpers import Colors
from SQL import SQL

sel = selectors.DefaultSelector()

db: SQL
active_player_count: int = 0
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


def service_connection(key, mask):
    global db
    global active_player_count
    global game

    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024).decode()  # Should be ready to read
        if recv_data:
            data.outb = process_requests(recv_data)
        else:
            print(f"Closing connection to {data.addr}")
            sel.unregister(sock)
            sock.close()
            active_player_count -= 1
            db.update_where_from_table('games', {'player_count': active_player_count}, {'game_id': game.game_id})
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]


def process_requests(data: str) -> bytes:
    global db
    global game

    try:
        action, path, queries = process_data(data)

        game.check_if_new_draw_objects_should_be_created()

        if action == 'GET':
            if path[0] == 'game':
                if len(path) == 1:  # 'GET game'
                    return pickle.dumps(game)
                else:
                    if path[1] == 'board':
                        if path[2] == 'grid':  # 'GET game/board/grid'
                            if len(path) == 3:
                                return pickle.dumps(game.grid_draw)
                        elif path[2] == 'offset':  # 'GET game/board/offset'
                            if len(path) == 3:
                                return pickle.dumps(game.board_offset)
                        elif path[2] == 'rect':  # 'GET game/board/rect'
                            if len(path) == 3:
                                return pickle.dumps(game.board.rect)
                        if queries:
                            if queries['position'] == 'center':  # 'GET game/board?&position=center'
                                return pickle.dumps(
                                    {'x': game.board.rect.centerx, 'y': game.board.rect.centery})

                    elif path[1] == 'round':
                        if path[2] == 'active':  # GET game/round/active
                            if len(path) == 3:
                                return pickle.dumps(game.is_round_active)

                    elif path[1] == 'robots':
                        if len(path) == 2:  # 'GET game/robots'
                            return pickle.dumps(game.robots_draw)
                        elif path[2] == 'select':  # 'GET game/robots/select'
                            if len(path) == 3:
                                if game.selected_robot:
                                    return pickle.dumps(game.selected_robot.robot_id)
                                else:
                                    return pickle.dumps(None)

                    elif path[1] == 'targets':
                        if len(path) == 2:  # 'GET game/targets'
                            return pickle.dumps(game.targets_draw)

                    elif path[1] == 'hourglass':
                        if len(path) == 2:  # 'GET game/hourglass'
                            return pickle.dumps(game.hourglass_draw)
                        elif path[2] == 'time_over':  # GET game/hourglass/time_over
                            if len(path) == 3:
                                return pickle.dumps(game.hourglass.get_is_time_over())

                    elif path[1] == 'leaderboard':
                        if len(path) == 2:  # 'GET game/leaderboard'
                            return pickle.dumps(game.leaderboard_draw)

                    elif path[1] == 'best_solution':
                        if len(path) == 2:  # 'GET game/best_solution'
                            return pickle.dumps(game.best_solution_draw)

                    elif path[1] == 'individual_solution':
                        if path[2] == 'position':  # 'GET game/individual_solution/position'
                            if len(path) == 3:
                                return pickle.dumps(game.individual_solution['position'])
                        elif path[2] == 'size':  # 'GET game/individual_solution/size'
                            if len(path) == 3:
                                return pickle.dumps(game.individual_solution['size'])

                    elif path[1] == 'ready_button':
                        if path[2] == 'state':  # 'GET game/ready_button/state'
                            if len(path) == 3:
                                if game.is_round_active:
                                    return 'pressed'.encode()
                                else:
                                    return 'unpressed'.encode()
                        elif path[2] == 'position':  # 'GET game/ready_button/position'
                            if len(path) == 3:
                                return pickle.dumps(game.ready_button['position'])
                        elif path[2] == 'size':  # 'GET game/ready_button/size'
                            if len(path) == 3:
                                return pickle.dumps(game.ready_button['size'])

                    elif path[1] == 'window_dimensions':
                        if len(path) == 2:
                            return pickle.dumps(game.window_dimensions)
            elif path[0] == 'user':
                if path[1] == 'active_player_id':
                    if len(path) == 2:
                        return pickle.dumps(game.active_player_id)
                else:  # player specific request
                    player_id = int(path[1])

                    if path[2] == 'name':  # 'GET user/<n>/name'
                        if len(path) == 3:
                            name = db.select_where_from_table("players", ["name"], {"player_id": player_id},
                                                              single_result=True)
                            return str(name).encode()
                    elif path[2] == 'solution':  # 'GET user/<n>/solution'
                        if len(path) == 3:
                            solution = db.select_where_from_table("players", ["solution"], {"player_id": player_id},
                                                                  single_result=True)
                            return str(solution).encode()

                    elif path[2] == 'ready_button':
                        if path[3] == 'state':  # 'GET user/<n>/ready_button/state'
                            if len(path) == 4:
                                return pickle.dumps(
                                    bool(int(db.select_where_from_table('players', ['ready_for_round'],
                                                                        {'player_id': player_id},
                                                                        single_result=True))))

            elif path[0] == 'colors':
                if len(path) == 1:  # 'GET colors'
                    return pickle.dumps(Colors)
        else:  # action == 'POST'
            if path[0] == 'game':
                if path[1] == 'robots':
                    if path[2] == 'select':  # 'POST game/robots/select?position_x=x&position_y=y
                        if len(path) == 3:
                            if game.selected_robot:
                                db.update_where_from_table('robots', {'in_use': 0},
                                                           {'robot_id': game.selected_robot.robot_id})
                            node_at_position = game.board.get_node(
                                {'x': int(queries['position_x']), 'y': int(queries['position_y'])})
                            grid_position = node_at_position.get_position()
                            try:
                                game.selected_robot = [robot for robot in game.robots if
                                                       robot.get_position()['column'] == grid_position[
                                                           'column'] and
                                                       robot.get_position()['row'] == grid_position['row']][0]
                                db.update_where_from_table('robots', {'in_use': 1},
                                                           {'robot_id': game.selected_robot.robot_id})
                            except IndexError:
                                game.selected_robot = None
                            return str(200).encode()
                    elif path[2] == 'move':  # 'GET game/robots/move'
                        if len(path) == 3:
                            is_moved = game.selected_robot.move(queries['direction'])
                            if is_moved:
                                game.control_move_count += 1
                                if game.control_move_count <= game.active_player_solution:
                                    if game.check_robot_on_target():
                                        game.finish_round()
                                else:
                                    game.pass_active_status_on_to_next_player_in_solution_list()
                            return str(200).encode()

            elif path[0] == 'user':
                if path[1] == 'new':  # 'POST user/new?name=x'
                    if len(path) == 2:
                        db.insert('players', {'game_id': game.game_id,
                                              'name': queries['name']})
                        return str.encode("200")
                else:
                    player_id = int(path[1])

                    if path[2] == 'solution':
                        if len(path) == 3:  # 'POST user/<n>/solution?value=x'
                            solution = queries['value']
                            db.update_where_from_table('players', {'solution': solution}, {'player_id': player_id})
                            if not game.hourglass.get_is_active():
                                game.hourglass.start_timer()
                            return str.encode(str(200))

                    elif path[2] == 'change_status_next_round':  # 'POST user/{id}/change_status_next_round'
                        if len(path) == 3:
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
                            return pickle.dumps(new_status)

            print(f"Request not implemented: {data}")

    except OSError as socket_error:
        print(str(socket_error))
        return None


def create_new_game():
    global db
    global game

    game_id = db.get_next_id('games')
    db.insert('games', {})
    game = Game(db, game_id)
    print(f'New game created!\n')


def clear_unnecessary_data_in_db() -> None:  # delete rows in chips, robots, rounds where there's a winner in the game
    request_result = db.select_where_from_table('games', ['game_id'], {'winner_player_id': 'NULL'},
                                                comparison_symbol='<>')
    request_result = list(range(134, game.game_id))
    if request_result is None:
        return
    else:
        # finished_game_ids = [game_id_tpl[0] for game_id_tpl in request_result]
        finished_game_ids = request_result
        for c_game_id in finished_game_ids:
            db.delete_where_from_table('chips', {'game_id': c_game_id})
            db.delete_where_from_table('robots', {'game_id': c_game_id})
            db.delete_where_from_table('rounds', {'game_id': c_game_id})
        print(f"Cleared tables of game_ids: {finished_game_ids}")


def accept_wrapper(sock):
    connection, address = sock.accept()  # Should be ready to read
    print(f"Accepted connection from {address}")
    connection.setblocking(False)
    data = types.SimpleNamespace(addr=address, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(connection, events, data=data)
    player_id = db.get_next_id('players')
    connection.send(str.encode(str(player_id)))  # send the client the player_id


def main():
    global db
    global active_player_count
    global game

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # get ip-address of local sys
    ip_address = netifaces.ifaddresses(netifaces.interfaces()[0])[netifaces.AF_INET][0]['addr']
    # ip_address = 'localhost'

    try:
        s.bind((ip_address, 0))  # connect to local ip with port 0 -> socket will search for a free port
    except OSError as e:
        str(e)

    port = s.getsockname()[1]

    s.listen()
    s.setblocking(False)
    sel.register(s, selectors.EVENT_READ, data=None)

    db = SQL("localhost", "root", "")

    create_new_game()

    clear_unnecessary_data_in_db()

    print(f'Server Started\nIP: {ip_address} | Port: {port}\n')
    pyperclip.copy(port)

    print("\nWaiting for connections\n")

    while True:
        # check: events for game logics
        datetime_now = datetime.now()
        if game.is_round_active:
            if game.hourglass.active:
                game.hourglass.calc_passed_time(datetime_now)
            if game.hourglass.get_is_time_over() and not game.active_player_id:
                game.solutions_review()

        # check: incoming data from connections
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
                active_player_count += 1
                game.overall_player_count += 1
                db.update_where_from_table('games', {'player_count': active_player_count}, {'game_id': game.game_id})
                game.ready = True if active_player_count >= 2 else False
            else:
                service_connection(key, mask)


if __name__ == '__main__':
    main()
