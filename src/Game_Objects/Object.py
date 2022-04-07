class Object:
    size: tuple
    color: tuple
    position_window: tuple

    def __init__(self, size: tuple, color: tuple, position_window: tuple):
        self.size = size
        self.color = color
        self.position_window = position_window

    def get_position_window(self) -> tuple:
        return self.position_window

    def get_size(self) -> tuple:
        return self.size
