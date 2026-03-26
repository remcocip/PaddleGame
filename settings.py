import os
import random
from typing import Any, Dict

# CONSTANTS NOT TO CHANGE
CANVAS_WIDTH = 400
CANVAS_HEIGHT = 400
PADDLE_Y1 = CANVAS_HEIGHT - 30  # bottom paddle
PADDLE_Y2 = 15  # top paddle
BALL_RADIUS = 10
OFFSET = 8
BOX_SIZE = 30

# CHANGEABLE CONSTANTS
ROUNDS = ('9', '3', '5')  # keep odd and single digit
CONFETTI = 50  # amount of confetti
PADDLE_WIDTH = 80
PADDLE_HEIGHT = 15

def get_color() -> str:
    """
    Function that returns a random color.
    """
    colors = [
        'orange', 'green', 'blue', 'coral', 'tomato', 'red', 
        'hot pink', 'deep pink', 'maroon', 'medium purple', 'purple'
    ]
    return random.choice(colors)

def get_items_dict() -> Dict[str, Dict[str, Any]]:
    """
    Function to get the main dictionary with screen items.
    Contains the names, locations and colors.
    """
    title_size = 30
    subtitle_size = 20
    no_size = 0
    color = get_color()
    flip_color = 'red'

    items = {
        'Paddle Game': {'x1': 70, 'y1': 50, 'font_size': title_size, 'text_color': color, 'box_color': flip_color, 'x2': 300, 'y2': 100, 'object_id': None, 'screen_type': 'start', 'extra': None},
        'Rounds':   {'x1': 50, 'y1': 150, 'font_size': subtitle_size, 'text_color': color, 'box_color': flip_color, 'x2': 125, 'y2': 180, 'object_id': None, 'screen_type': None, 'extra': None},
        ROUNDS[0]:  {'x1': CANVAS_WIDTH/3, 'y1': 155, 'font_size': subtitle_size, 'text_color': "white", 'box_color': color, 'x2': CANVAS_WIDTH/3+30, 'y2': 185, 'object_id': None, 'screen_type': 'start', 'extra': False},
        ROUNDS[1]:  {'x1': CANVAS_WIDTH/2, 'y1': 155, 'font_size': subtitle_size, 'text_color': "white", 'box_color': color, 'x2': CANVAS_WIDTH/2+30, 'y2': 185, 'object_id': None, 'screen_type': 'start', 'extra': False},
        ROUNDS[2]:  {'x1': CANVAS_WIDTH*2/3, 'y1': 155, 'font_size': subtitle_size, 'text_color': "white", 'box_color': color, 'x2': CANVAS_WIDTH*2/3+30, 'y2': 185, 'object_id': None, 'screen_type': 'start', 'extra': False},
        'Exit':     {'x1': 30, 'y1': 280, 'font_size': subtitle_size, 'text_color': 'red', 'box_color': flip_color, 'x2': 105, 'y2': 310, 'object_id': None, 'screen_type': 'start', 'extra': None},

        # Paddles
        'paddle_1': {'x1': 160, 'y1': PADDLE_Y1, 'font_size': no_size, 'text_color': 'black', 'box_color': 'red', 'x2': 160 + PADDLE_WIDTH, 'y2': PADDLE_Y1 + PADDLE_HEIGHT, 'object_id': None, 'screen_type': 'play', 'extra': None},
        'paddle_2': {'x1': 160, 'y1': PADDLE_Y2, 'font_size': no_size, 'text_color': 'black', 'box_color': 'red', 'x2': 160 + PADDLE_WIDTH, 'y2': PADDLE_Y2 + PADDLE_HEIGHT, 'object_id': None, 'screen_type': 'play', 'extra': None},

        # obstacles
        'pillar_1': {'x1': 75, 'y1': 100, 'font_size': no_size, 'text_color': 'red', 'box_color': 'green', 'x2': 85, 'y2': 150, 'object_id': None, 'screen_type': 'play', 'extra': None},
        'pillar_3': {'x1': 200, 'y1': 300, 'font_size': no_size, 'text_color': 'magenta', 'box_color': 'green', 'x2': 220, 'y2': 310, 'object_id': None, 'screen_type': 'play', 'extra': None},
        'pillar_5': {'x1': 50, 'y1': 200, 'font_size': no_size, 'text_color': 'white', 'box_color': 'green', 'x2': 65, 'y2': 210, 'object_id': None, 'screen_type': 'play', 'extra': None},
        'pillar_7': {'x1': 180, 'y1': 100, 'font_size': no_size, 'text_color': 'magenta', 'box_color': 'green', 'x2': 200, 'y2': 110, 'object_id': None, 'screen_type': 'play', 'extra': None},
        'pillar_8': {'x1': 320, 'y1': 260, 'font_size': no_size, 'text_color': 'red', 'box_color': 'green', 'x2': 330, 'y2': 310, 'object_id': None, 'screen_type': 'play', 'extra': None}
    }
    return items
