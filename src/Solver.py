import pickle
import sys

from src.Game_Objects import Node

colors: list[str] = ['yellow', 'red', 'green', 'blue']
symbols: list[str] = ['circle', 'triangle', 'square', 'hexagon']
robot_pos_index_and_color: dict[int, str] = {i: color for i, color in enumerate(colors)}


class BoardState:
    def __init__(self):
        self.target: int = 33843
        self.robot_positions: list[int] = [14, 178, 112, 86]


class Board:
    board: list[list[int]]

    def __init__(self, init_board_state: BoardState, grid: list[list[Node]]):

        self.board = []

        for row in range(16):
            c_row_cells = []
            for column in range(16):
                cell = '000'
                cell += '0'
                cell += ''.join(
                    [str(int(direction)) for direction in grid[row][column].convert_neighbors_to_bool_based().values()])
                c_row_cells.append(int(cell))
            self.board.append(c_row_cells)

        for robot_position in convert_robot_positions(init_board_state).values():
            cell: str = format(self.board[robot_position['row']][robot_position['column']], 'b').zfill(8)
            cell = cell[:3] + '1' + cell[4:]
            self.board[robot_position['row']][robot_position['column']] = int(cell, 2)

        self.target = convert_target(init_board_state)

        print(self.board)
        self.pre_compute_map(grid)

    def pre_compute_map(self, grid: list[list[Node]]) -> None:
        target_node = grid[self.target['position']['row']][self.target['position']['column']]

        all_nodes_evaluated_with_move_count: list[tuple[int, Node]] = [(0, target_node)]
        temp_s: list[tuple[int, Node]] = [(0, target_node)]
        evaluated_nodes: list[Node] = [target_node]

        temp_q: list[list] = [[' ' for _ in range(16)] for _ in range(16)]

        # for t_move_count, c_node in temp_s:
        while temp_s:
            t_move_count, c_node = temp_s[0]
            move_count = t_move_count + 1
            if move_count > 5:
                break
            for direction, node in c_node.neighbors.items():
                if node:
                    while True:
                        if node not in evaluated_nodes:
                            all_nodes_evaluated_with_move_count.append((move_count, node))
                            temp_s.append((move_count, node))
                            evaluated_nodes.append(node)
                        else:
                            for m, n in all_nodes_evaluated_with_move_count:
                                if n == node:
                                    if m > move_count:
                                        all_nodes_evaluated_with_move_count.remove((m, node))
                                        all_nodes_evaluated_with_move_count.append((move_count, node))
                                        temp_s.remove((m, node))
                                        temp_s.append((move_count, node))
                                        evaluated_nodes.remove(node)

                        if node.neighbors[direction]:
                            node = node.neighbors[direction]
                        else:
                            break

            for move_count, node in all_nodes_evaluated_with_move_count:
                temp_q[node.position['row']][node.position['column']] = str(move_count)
                print(move_count, format(move_count, 'b').zfill(3),
                      format(self.board[c_node.position['row']][c_node.position['column']], 'b').zfill(8)[3:])
                self.board[c_node.position['row']][c_node.position['column']] = \
                    int(format(move_count, 'b').zfill(3) + format(
                        self.board[c_node.position['row']][c_node.position['column']], 'b').zfill(8)[3:], 2)

            # print(temp_q)
            # print(self.board)

            temp_s.remove((t_move_count, c_node))
            temp_s.sort(key=lambda x: x[0])

        for row in self.board:
            print([format(cell, 'b').zfill(8)[:3] for cell in row])

        with open("pre_computed_grid.pkl", "wb") as outp:
            pickle.dump(temp_q, outp, pickle.HIGHEST_PROTOCOL)


def convert_target(board: BoardState) -> dict:
    def get_binary_of_int(x: int) -> str:
        return format(x, 'b').zfill(16)

    def convert_position(b_position: str) -> dict[str, int]:
        # first four bits -> column | second four bits -> row
        return {'column': int(b_position[:4], 2), 'row': int(b_position[4:], 2)}

    def convert_color(b_color: str) -> str:
        # yellow, red, green, blue | if every color -> all
        if b_color[0] == '1' and b_color == len(b_color) * b_color[0]:
            return 'all'
        else:
            return [colors[int(i)] for i in range(len(b_color)) if bool(int(b_color[i]))][0]

    def convert_symbol(b_symbol: str) -> str:
        # circle, triangle, square, hexagon | if every symbol -> all
        if b_symbol[0] == '1' and b_symbol == len(b_symbol) * b_symbol[0]:
            return 'all'
        else:
            return [symbols[int(i)] for i in range(len(b_symbol)) if bool(int(b_symbol[i]))][0]

    b_specifications = get_binary_of_int(board.target)

    return {
        'color': convert_color(b_specifications[:4]),
        'symbol': convert_symbol(b_specifications[4:8]),
        'position': convert_position(b_specifications[8:])
    }


def convert_robot_positions(board: BoardState) -> dict[str, dict[str, int]]:
    def get_binary_of_int(x: int) -> str:
        return format(x, 'b').zfill(8)

    def convert_position(color: str) -> dict:
        b_pos: str = get_binary_of_int(board.robot_positions[colors.index(color)])
        return {'column': int(b_pos[:4], 2), 'row': int(b_pos[4:], 2)}

    return {color: convert_position(color) for color in robot_pos_index_and_color.values()}


if __name__ == '__main__':
    o = BoardState()
    print(f"Size of object: {sys.getsizeof(o)}")
    print(f"Size of attributes: {sys.getsizeof(o.target) + sys.getsizeof(o.robot_positions)}")

    print(convert_robot_positions(o))
    print(convert_target(o))

    with open('grid.pkl', 'rb') as inp:
        grid = pickle.load(inp)

    b = Board(o, grid)
