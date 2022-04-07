class Wall:
    position_node1: dict
    position_node2: dict

    def __init__(self, position_node1: dict, position_node2: dict, directions: dict):
        self.position_node1 = position_node1
        self.position_node2 = position_node2
        self.direction_node1 = directions['node1']
        self.direction_node2 = directions['node2']
