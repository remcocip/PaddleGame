import os
import random

ROUNDS = ('9', '3', '5')  # keep odd and single digit
RUN_IN_CODE_IN_PLACE = True if (os.getcwd() == '/home/pyodide') else False
SPEED = 0 if RUN_IN_CODE_IN_PLACE else 0.01
CONFETTI = 50  # amount of confetti
PADDLE_WIDTH = 80
PADDLE_HEIGHT = 15
CANVAS_WIDTH = 400
CANVAS_HEIGHT = 400
BOX_SIZE = 30
PADDLE_Y1 = CANVAS_HEIGHT - 30
PADDLE_Y2 = 15
BALL_RADIUS = 10
OFFSET = 8


def get_items_dict():
    title_size = 30
    subtitle_size = 20
    no_size = 0
    color = get_color()
    flip_color = 'red'

    """
    Function to get the main dictionary with screen items.
    Contains the names, locations and colors.
    """

    items = {
        ROUNDS[0]:  [CANVAS_WIDTH / 3, 155, subtitle_size, "white", color, CANVAS_WIDTH / 3 + 30, 185, None, 'start', False],
        ROUNDS[1]:  [CANVAS_WIDTH / 2, 155, subtitle_size, "white", color, CANVAS_WIDTH / 2 + 30, 185, None, 'start', False],
        ROUNDS[2]:  [CANVAS_WIDTH * 2 / 3, 155, subtitle_size, "white", color, CANVAS_WIDTH * 2 / 3 + 30, 185, None, 'start', False],
        'Exit':     [30,    280, subtitle_size, 'red', flip_color, 105, 310, None, 'start',None],

        # Paddles
        'paddle_1': [160, PADDLE_Y1, no_size, 'black', 'red', 160 + PADDLE_WIDTH, PADDLE_Y1 + PADDLE_HEIGHT, None, 'play', None],
        'paddle_2': [160, PADDLE_Y2, no_size, 'black', 'red', 160 + PADDLE_WIDTH, PADDLE_Y2 + PADDLE_HEIGHT, None, 'play', None],

        # obstacles
        'pillar_1': [75, 100, no_size, 'red', 'green', 85, 150, None, 'play'],
        'pillar_3': [200, 300, no_size, 'magenta', 'green', 220, 310, None, 'play'],
        'pillar_5': [50, 200, no_size, 'white', 'green', 65, 210, None, 'play'],
        'pillar_7': [180, 100, no_size, 'magenta', 'green', 200, 110, None, 'play'],
        'pillar_8': [320, 260, no_size, 'red', 'green', 330, 310, None, 'play']
        # 'Paddle Game': [70, 50, title_size, color, flip_color, 300, 100, None, 'start',None],
        # 'Rounds':   [50,    150, subtitle_size, color, flip_color, 125, 180, None, None,None],

    }
    return items


def get_items_dict_():
    color = get_color()

    items = [
        # Title:
        {
            "name": "Paddle Game",
            "x1": 70, "y1": 50, "x2": False, "y2": False,
            "text color": color, "flip color": False,
            "ObjectId": None,
            "screen type": "start",
        },
        # Menu items for number_of_rounds
        {
            "name": "Rounds",
            "x1": 50, "y1": 150, "x2": False, "y2": False,
            "text color": color, "flip color": False,
            "ObjectId": None,
            "screen type": "start",
        },
        {
            "name": ROUNDS[0],
            "x1": CANVAS_WIDTH / 3, "y1": 155, "x2": CANVAS_WIDTH / 3 + 30, "y2": 185,
            "text color": 'white', "flip color": color,
            "ObjectId": None,
            "screen type": "start",
        },
        {
            "name": ROUNDS[1],
            "x1": CANVAS_WIDTH / 2, "y1": 155, "x2": CANVAS_WIDTH / 2 + 30, "y2": 185,
            "text color": 'white', "flip color": color,
            "ObjectId": None,
            "screen type": "start",
        },
        {
            "name": ROUNDS[2],
            "x1": CANVAS_WIDTH * 2/ 3, "y1": 155, "x2": CANVAS_WIDTH *2 / 3 + 30, "y2": 185,
            "text color": 'white', "flip color": color,
            "ObjectId": None,
            "screen type": "start",
        },
        {
            "name": "Exit",
            "x1": 30, "y1": 280, "x2": False, "y2": False,
            "text color": 'red', "flip color": False,
            "ObjectId": None,
            "screen type": "start",
        },
    ]
    return items



def get_color():
    """
    Function that returns a random color.
    """
    colors = [
        'orange',
        'green',
        'blue',
        'coral',
        'tomato',
        'red',
        'hot pink',
        'deep pink',
        'maroon',
        'medium purple',
        'purple'
    ]
    return random.choice(colors)
