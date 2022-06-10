def db_position_to_position(db_position: str) -> dict:
    # (6,4)
    column, row = position = db_position.replace("(", "").replace(")", "").split(",")
    return {'column': int(column), 'row': int(row)}
