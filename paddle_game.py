"""
File: paddle_game.py
Author: Remco (remco.cip@gmail.com)
Repository: https://github.com/remcocip/PaddleGame
Version date: Friday, June 13th 2025

This is my 'final project' for Code in Place 2025.

In this game two players will pass the ball to each other,
if a player misses the ball, a point goes to the other.

The bottom player needs to use the Left and Right arrow key.
The top player needs to use the mouse.
"""
from graphics import Canvas
import time
import random
import sys
import os

RUN_IN_CODE_IN_PLACE = True if (os.getcwd() == '/home/pyodide') else False
if RUN_IN_CODE_IN_PLACE:
    from ai import call_gpt
    print("Running in Code in Place!")

# CONSTANTS NOT TO CHANGE
CANVAS_WIDTH = 400
CANVAS_HEIGHT = 400
PADDLE_Y1 = CANVAS_HEIGHT - 30  # bottom paddle
PADDLE_Y2 = 15  # top paddle
BALL_RADIUS = 10
OFFSET = 8
BOX_SIZE = 30

# CHANGEABLE CONSTANTS
SPEED = 0 if RUN_IN_CODE_IN_PLACE else 0.01
ROUNDS = ('9', '3', '5')  # keep odd and single digit
CONFETTI = 50  # amount of confetti
PADDLE_WIDTH = 80
PADDLE_HEIGHT = 15

global ball, change_x, change_y, paddle_1, paddle_2, pillar_1, pillar_2, pillar_3, pillar_5, pillar_7, pillar_8

def get_items_dict():
    """
    Function to get the main dictionary with screen items.
    Contains the names, locations and colors.

    The items dict contains all the menu items:
    key : the text shown on screen
    value[0] : the x-coordinate
    value[1] : the y-coordinate
    value[2] : the font size
    value[3] : the text color
    value[4] : the box color
    value[5] : box x2-coordinate
    value[6] : box y2-coordinate
    value[7] : objectId
    value[8] : screen type
    value[9] : menu option selected (None if not selectable)

    """
    title_size = 30
    subtitle_size = 20
    no_size = 0
    color = get_color()
    flip_color = 'red'

    items = {
        # Title:
        'Paddle Game': [70, 50, title_size, color, flip_color, 300, 100, None, 'start',None],
        # Menu items for number_of_rounds
        'Rounds':   [50,    150, subtitle_size, color, flip_color, 125, 180, None, None,None],
        ROUNDS[0]:  [CANVAS_WIDTH/3,   155, subtitle_size, "white", color, CANVAS_WIDTH/3+30, 185, None, 'start',False],
        ROUNDS[1]:  [CANVAS_WIDTH/2,   155, subtitle_size, "white", color, CANVAS_WIDTH/2+30, 185, None, 'start',False],
        ROUNDS[2]:  [CANVAS_WIDTH*2/3,   155, subtitle_size, "white", color, CANVAS_WIDTH*2/3+30, 185, None, 'start',False],
        'Exit':     [30,    280, subtitle_size, 'red', flip_color, 105, 310, None, 'start',None],

        # Paddles
        'paddle_1': [160, PADDLE_Y1, no_size, 'black', 'red', 160 + PADDLE_WIDTH, PADDLE_Y1 + PADDLE_HEIGHT, None, 'play',None],
        'paddle_2': [160, PADDLE_Y2, no_size, 'black', 'red', 160 + PADDLE_WIDTH, PADDLE_Y2 + PADDLE_HEIGHT, None, 'play',None],

        # obstacles
        'pillar_1': [75, 100, no_size, 'red', 'green', 85, 150, None, 'play'],
        'pillar_3': [200, 300, no_size, 'magenta', 'green', 220, 310, None, 'play'],
        'pillar_5': [50, 200, no_size, 'white', 'green', 65, 210, None, 'play'],
        'pillar_7': [180, 100, no_size, 'magenta', 'green', 200, 110, None, 'play'],
        'pillar_8': [320, 260, no_size, 'red', 'green', 330, 310, None, 'play']
    }
    return items


def main():
    """
    Function to handle the main loop.
    """
    canvas = Canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    items = get_items_dict()
    while True:
        key = start(canvas, items)
        if key in ROUNDS:
            rounds_to_play = int(key)
            score = play(canvas, rounds_to_play, items)
            end(canvas, score)
        elif key == 'Exit':
            canvas.clear()
            if not RUN_IN_CODE_IN_PLACE:
                sys.exit()
            else:
                exit_screen(canvas)


def play(canvas, rounds_to_play, items):
    """
    Function to handle the game loop.

    change_x: the direction of the x-coordinates.
    change_y: the direction of the y-coordinates.
    """
    global ball, change_x, change_y

    create_play_screen(canvas, items)
    score = [0,0]

    for i in range(rounds_to_play):
        ball = create_ball(canvas)
        canvas.wait_for_click()
        # initial movement of ball in random direction
        change_x = get_random_direction()
        change_y = get_random_direction()
        while True:
            canvas.move(ball, change_x, change_y)
            move_paddle_mouse(canvas)
            move_paddle_keys(canvas)
            point_scored = colliders(canvas, items, score)
            if point_scored:
                break
            time.sleep(SPEED)
            if not RUN_IN_CODE_IN_PLACE:
                canvas.update()
        if i == rounds_to_play:
            break
    canvas.clear()
    if not RUN_IN_CODE_IN_PLACE:
        canvas.update()
    return score


def colliders(canvas, items, score):
    """
    Function to handle the collision with paddles and pillars.

    Updates the score if a point is made.
    Returns a new change_x and change_y.
    """
    global ball, change_x, change_y

    # To not have the ball gluing to objects, 1 pixel before touching the ball returns
    glue_fixer = 0
    # retrieve the x and y coordinates of the ball:
    x1_ball = canvas.get_left_x(ball) - glue_fixer
    y1_ball = canvas.get_top_y(ball) - glue_fixer
    x2_ball = x1_ball + 2 * BALL_RADIUS + glue_fixer
    y2_ball = y1_ball + 2 * BALL_RADIUS + glue_fixer
    # retrieve the items that the ball collides with:
    colliding_with = canvas.find_overlapping(x1_ball, y1_ball, x2_ball, y2_ball)

    '''check x position of ball'''
    if x1_ball <= 0 or x2_ball > CANVAS_WIDTH:
        # ball bounces at the walls
        change_x = -change_x
        return False

    '''check y position of ball'''
    # if ball not caught:
    # if (y2_ball > PADDLE_Y1 + 2) and (y1_ball > CANVAS_HEIGHT / 2):
    if (y2_ball > CANVAS_HEIGHT) and (y1_ball > CANVAS_HEIGHT / 2):
        # player 1
        canvas.delete(ball)
        score[1] += 1
        return True
    elif (y1_ball < 0) and (y1_ball < CANVAS_HEIGHT / 2):
        # player 2
        canvas.delete(ball)
        score[0] += 1
        return True

    for key, value in items.items():
        if value[7] in colliding_with:
            if key in ['paddle_1', 'paddle_2']:
                # ball caught with paddle
                change_y = -change_y
            elif key in ['pillar_1', 'pillar_2', 'pillar_3', 'pillar_4', 'pillar_5', 'pillar_6', 'pillar_7', 'pillar_8']:
                change_x = get_random_direction()
                change_y = get_random_direction()
    return False


def start(canvas, items):
    """
    Function to handle the start menu loop.
    """
    info = create_start_screen(canvas, items)
    while True:
        if RUN_IN_CODE_IN_PLACE:
            canvas.wait_for_click()
            click = canvas.get_last_click()
        else:
            # graphics.py (def wait_for_click(self)): 'return [self.get_mouse_x(), self.get_mouse_y()];
            click = canvas.wait_for_click()
        if click:
            x = click[0]
            y = click[1]
            key = get_start_screen_key(items, x, y)
            if key in ROUNDS:
                start_screen_updater(canvas, items, key, info)
            return key
        if not RUN_IN_CODE_IN_PLACE:
            canvas.update()


def start_screen_updater(canvas, items, key, info):
    """
    Function to update the start screen elements.
    """
    canvas.delete(key)
    value = items[key]
    canvas.create_rectangle(
        value[0], # x1-coord
        value[1], # y1-coord
        value[5], # x2-coord
        value[6], # y2-coord
        color='red'
    )
    canvas.create_text(
        value[0] + OFFSET, # x-coord
        value[1] + OFFSET, # y-coord
        text=key,
        font='Arial',
        font_size=value[2],
        color='white'
    )
    start_screen_wait_for_user(canvas, info)
    if not RUN_IN_CODE_IN_PLACE:
        canvas.update()


def start_screen_wait_for_user(canvas, info):
    """
    Function to update the info box
    and wait for the user to click.
    """
    if RUN_IN_CODE_IN_PLACE:
        canvas.change_text(info, "Click to continue...")
        canvas.wait_for_click()
    else:
        canvas.delete(info)
        click_to_continue(canvas)


def click_to_continue(canvas):
    canvas.create_text(
        CANVAS_WIDTH / 2,
        CANVAS_HEIGHT - 50,
        "Click to continue...",
        color='lime green',
        anchor='center',
        )
    canvas.wait_for_click()
    canvas.clear()
    if not RUN_IN_CODE_IN_PLACE:
        canvas.update()


def end(canvas, score):
    """
    Function to create the end_screen.
    """
    # determine the winner:
    winner = 'player 1' if score[0] > score[1] else 'player 2'
    topic = 'winner'

    # Get the haiku from ChatGPT
    if RUN_IN_CODE_IN_PLACE:
        haiku = call_gpt(f"Create a haiku with the words {winner} {topic}")
        haiku = [line.strip() for line in haiku.split(',')]
    else:
        haiku = ["In a pixel world", f"{winner.title()} claims the crown", "Victory's sweet sound."]

    create_end_screen_confetti_frame(canvas, score)
    create_background_image(canvas, 'soft')
    for i in range(len(haiku)):
        canvas.create_text(
            50,
            85 + i*60,
            text=haiku[i],
            font='Arial',
            font_size=20,
            color="lime green"
        )
        time.sleep(1.5)
    click_to_continue(canvas)


def exit_screen(canvas):
    """
    Function to create the exit_screen,
    only used when RUN_IN_CODE_IN_PLACE = True.
    """
    create_background_image(canvas, 'soft')
    canvas.create_text(
        20,
        CANVAS_HEIGHT / 2 - 30,
        text="You can check out any time you like,",
        font='Arial',
        font_size=15,
        color='lime green'
    )
    canvas.create_text(
        20,
        CANVAS_HEIGHT / 2,
        text="but you can never leave.",
        font='Arial',
        font_size=15,
        color='lime green'
    )
    click_to_continue(canvas)


def move_paddle_keys(canvas):
    """
    Function to move the paddle with the keys.
    """
    # global paddle_1, pressed_key

    # get the x position of the paddle
    paddle_x = canvas.get_left_x(paddle_1)
    # determine the movement
    if RUN_IN_CODE_IN_PLACE:
        pressed_key = canvas.get_last_key_press()
    else:
        pressed_key = canvas.get_new_key_presses()
        if pressed_key:
            if pressed_key[0].keysym == 'Left':
                pressed_key = 'ArrowLeft'
            elif pressed_key[0].keysym == 'Right':
                pressed_key = 'ArrowRight'
    if pressed_key == 'ArrowLeft' and paddle_x > 0:
        paddle_x -= 10
    elif pressed_key == 'ArrowRight' and paddle_x < CANVAS_WIDTH - PADDLE_WIDTH:
        paddle_x += 10
    # and move the paddle to the new location
    canvas.moveto(paddle_1, paddle_x, PADDLE_Y1)


def move_paddle_mouse(canvas):
    """
    Function to move the paddle with the mouse
    relative to the middle of the paddle.
    """
    global paddle_2

    # get the x position of the paddle
    paddle_x = canvas.get_left_x(paddle_2)

    # determine the movement
    mouse_x = canvas.get_mouse_x()
    if mouse_x < (paddle_x + PADDLE_WIDTH / 2):
        if paddle_x > 0:
            paddle_x -= 3
    elif mouse_x > paddle_x:
        paddle_x += 3
        if paddle_x + PADDLE_WIDTH > CANVAS_WIDTH:
            paddle_x = CANVAS_WIDTH - PADDLE_WIDTH
    canvas.moveto(paddle_2, paddle_x, PADDLE_Y2)


def create_start_screen(canvas, items):
    """
    Function to create the start screen elements.
    """
    create_background_image(canvas)

    for key, value in items.items():
        if key in ROUNDS:
            canvas.create_rectangle(
                value[0],  # x1-coord
                value[1],  # y1-coord
                value[5],  # x2-coord
                value[6],  # y2-coord
                value[4]  # color
            )
        if value[2] != 0 and value[8] == 'start':
            canvas.create_text(
                value[0] + OFFSET,
                value[1] + OFFSET,
                text=key,
                font='Arial',
                font_size=value[2],
                color=value[3]
            )

    info = canvas.create_text(
        CANVAS_WIDTH/2,
        CANVAS_HEIGHT - 50,
        "Player 1: arrow keys        Player 2: mouse.",
        color='lime green',
        anchor='center'
    )
    return info


def create_play_screen(canvas, items):
    """
    Function to create the play screen elements.
    """
    global paddle_1, paddle_2, pillar_1, pillar_3, pillar_5, pillar_7, pillar_8

    create_background_image(canvas, 'soft')

    paddle_1 = create_play_screen_elements(canvas, 'paddle_1', items)
    paddle_2 = create_play_screen_elements(canvas, 'paddle_2', items)
    pillar_1 = create_play_screen_elements(canvas, 'pillar_1', items)
    pillar_3 = create_play_screen_elements(canvas, 'pillar_3', items)
    pillar_5 = create_play_screen_elements(canvas, 'pillar_5', items)
    pillar_7 = create_play_screen_elements(canvas, 'pillar_7', items)
    pillar_8 = create_play_screen_elements(canvas, 'pillar_8', items)


def create_ball(canvas):
    """
    Function to create the ball.
    """

    ball_x1 = CANVAS_WIDTH / 2 - BALL_RADIUS
    ball_y1 = CANVAS_HEIGHT / 2 - BALL_RADIUS
    ball_x2 = ball_x1 + BALL_RADIUS * 2
    ball_y2 = ball_y1 + BALL_RADIUS * 2
    color = get_color()

    new_ball = canvas.create_oval(ball_x1, ball_y1, ball_x2, ball_y2, color)
    return new_ball


def create_end_screen_confetti_frame(canvas, score):
    """
    Function to create the score screen with confetti.
    """
    create_background_image(canvas, 'soft')
    for i in range(CONFETTI):
        create_score_text(canvas, score)
        color = get_color()
        # define random size
        size = random.randint(1, 20)
        # define random location on canvas
        x_coordinate = random.randint(0, CANVAS_WIDTH - size)
        y_coordinate = random.randint(0, CANVAS_HEIGHT - size)
        function = random.choice(["circle", "rectangle", "line"])
        if function == "circle":
            create_confetti_circle(canvas, x_coordinate, y_coordinate, size, color)
        elif function == "rectangle":
            create_confetti_square(canvas, x_coordinate, y_coordinate, size, color)
        elif function == "line":
            length = random.randint(50, 250)
            create_confetti_line(canvas, x_coordinate, y_coordinate, color, length, size)
        if not RUN_IN_CODE_IN_PLACE:
            canvas.update()
        time.sleep(0.1)
    click_to_continue(canvas)


def create_confetti_line(canvas, x1, y1, color, length=100, width=1):
    """
    Function to draw a line.
    """
    x2 = x1 + width
    y2 = y1 + length
    canvas.create_line(x1, y1, x2, y2, color)


def create_confetti_square(canvas, x1, y1, size, color):
    """
    Function to draw a square.
    """
    x2 = x1 + size
    y2 = y1 + size
    canvas.create_rectangle(x1, y1, x2, y2, color)


def create_confetti_circle(canvas, x1, y1, size, color):
    """
    Function to draw a circle.
    """
    x2 = x1 + size
    y2 = y1 + size
    canvas.create_oval(x1, y1, x2, y2, color)


def create_score_text(canvas, score):
    """
    Function to create the score text.
    """
    score_dict = {
        'player1': [str(score[0]), 80],
        '-': [' - ', CANVAS_WIDTH / 2 - 35],
        'player2': [str(score[1]), 280]
    }
    for key in score_dict:
        canvas.create_text(
            score_dict[key][1],
            CANVAS_HEIGHT / 2 - 40,
            text=score_dict[key][0],
            font='Arial',
            font_size=60,
            color='white'
        )


def create_background_image(canvas, pic_type='hard'):
    """
    Function to show the background image
    """
    if pic_type == 'soft':
        canvas.create_image(0, 0, 'paddle_soft.jpg')
    else:
        canvas.create_image(0, 0, 'paddle.jpg')


def create_play_screen_elements(canvas, key, items):
    """
    Function to create elements based on dictionary.
    """
    value = items[key]
    play_screen_element = canvas.create_rectangle(
        value[0], # x1-coord
        value[1], # y1-coord
        value[5], # x2-coord
        value[6], # y2-coord
        value[3]  # color
    )
    value[7] = play_screen_element # Canvas ObjectID
    return play_screen_element


def get_random_direction():
    """
    Function to return a random value for change_x/y.
    """
    movement = [-1.5,-1,0.5,1,1.5]
    return random.choice(movement)

def get_start_screen_key(items, x, y):
    """
    Function to return the key at start screen.
    Checks with dictionary to see it the user clicked
    within boundaries and respective key is returned.
    """
    for key, value in items.items():
        if key in ROUNDS or key == 'Exit':
            x1 = value[0]
            y1 = value[1]
            x2 = value[5]
            y2 = value[6]

            if x1 <= x <= x2 and y1 <= y <= y2:
                return key
    return None


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


if __name__ == '__main__':
    main()