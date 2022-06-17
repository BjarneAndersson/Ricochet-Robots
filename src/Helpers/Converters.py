def db_position_to_position(db_position: str) -> dict:
    # (6,4)
    column, row = position = db_position.replace("(", "").replace(")", "").split(",")
    return {'column': int(column), 'row': int(row)}


def screen_position_to_position(screen_position: str) -> dict:
    # (60,40) -> {'x': 6, 'y': 4}
    x, y = position = screen_position.replace("(", "").replace(")", "").split(",")
    return {'x': int(x), 'y': int(y)}
