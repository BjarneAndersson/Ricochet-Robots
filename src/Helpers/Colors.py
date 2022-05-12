class Colors:
    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)
    yellow = (255, 255, 0)
    white = (255, 255, 255)
    black = (0, 0, 0)
    purple = (128, 0, 128)
    orange = (255, 165, 0)
    grey = (128, 128, 128)
    turquoise = (64, 224, 208)
    dark_grey = (18, 18, 18)
    all = purple

    robot = {
        'yellow': yellow,
        'red': red,
        'green': green,
        'blue': turquoise
    }

    target = {
        'yellow': yellow,
        'red': red,
        'green': green,
        'blue': turquoise,
        'all': all
    }

    wall = grey
    node = {
        'default': dark_grey,
        'barrier': grey
    }

    board = {
        'yellow': yellow,
        'red': red,
        'green': green,
        'blue': blue
    }

    ready_button = {
        'pressed': red,
        'unpressed': green
    }

    background = dark_grey

    individual_solution = {
        'border': white,
        'fill': grey
    }

    input_field = {
        'active': red,
        'inactive': individual_solution['border']
    }
