from .Node import Node
from .TargetSpace import TargetSpace


class TargetChip:
    is_revealed: bool
    is_obtained_by_player_id: int
    target_space: TargetSpace

    def __init__(self, target_space: TargetSpace):
        self.is_revealed = False
        self.is_obtained_by_player_id = None
        self.target_space = target_space

    def draw_to_center(self, window, position_grid_center: dict) -> None:
        self.target_space.draw(window, {'x': position_grid_center['x'] - self.target_space.size['width'] // 2,
                                        'y': position_grid_center['y'] - self.target_space.size['height'] // 2})
