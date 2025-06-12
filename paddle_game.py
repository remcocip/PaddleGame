"""
File: paddle_game.py
Author: Remco (remco.cip@gmail.com)
Repository: https://github.com/remcocip/PaddleGame
Version date: 12 june 2025

This is my 'final project' for Code in Place 2025.

In this game two players will pass the ball to each other,
if a player misses the ball, a point goes to the other.

The bottom player needs to use the Left and Right arrow key.
The top player needs to use the mouse.

What work is still to be done to improve the game:

Todo: bonus items
With bonus items a player can earn extra points. Bonus items are
given at launch and provided after point and after amount of successful paddle touches

Todo: show score
Show the score in the play screen
Show the score at the end_screen (with the haiku)

Todo: start_screen options
Color of the paddle
Color of the ball
Confetti

Todo: changeable selection at start_screen
After the user clicked an item and another item is clicked, the latter is kept

Todo: confetti end_screen
give Code in Place user option to show confetti too
"""
from graphics import Canvas
import time
import random
import sys
import os

DEBUG = True
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
ROUNDS = ['9', '3', '5']  # keep odd and single digit
CONFETTI = 200  # amount of confetti
PADDLE_WIDTH = 80
PADDLE_HEIGHT = 15


def get_items_dict(color=''):
    """
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
    """
    title_size = 30
    subtitle_size = 15
    no_size = 0
    piller_size = 10
    color = get_random_color()
    flip_color = 'red'

    items = {
        # Title:
        'Paddle Game': [100, 50, title_size, color, flip_color, 300, 100, None, 'start'],
        # Menu items for number_of_rounds
        'Rounds':   [50,    150, subtitle_size, color, flip_color, 125, 180, None, 'start'],
        ROUNDS[0]:  [175,   155, subtitle_size, "white", color, 205, 185, None, 'start'],
        ROUNDS[1]:  [225,   155, subtitle_size, "white", color, 255, 185, None, 'start'],
        ROUNDS[2]:  [275,   155, subtitle_size, "white", color, 305, 185, None, 'start'],
        ' ':        [80,    250, subtitle_size, 'white', 'white', 80, 280, None, 'start'],
        'Exit':     [50,    250, subtitle_size, color, flip_color, 125, 280, None, 'start'],
        # Paddles
        'paddle_1': [160, PADDLE_Y1, no_size, 'black', 'red', 160 + PADDLE_WIDTH, PADDLE_Y1 + PADDLE_HEIGHT, None, 'play'],
        'paddle_2': [160, PADDLE_Y2, no_size, 'black', 'red', 160 + PADDLE_WIDTH, PADDLE_Y2 + PADDLE_HEIGHT, None, 'play'],
        # Bonus items
        ## Start
        'pillar_1': [100-piller_size, 100-piller_size, no_size, 'black', 'green', 100+piller_size, 100+piller_size, None, 'play'],
        'pillar_2': [300-piller_size, 100-piller_size, no_size, 'black', 'green', 300+piller_size, 100+piller_size, None, 'play'],
        'pillar_3': [100-piller_size, 300-piller_size, no_size, 'black', 'green', 100+piller_size, 300+piller_size, None, 'play'],
        'pillar_4': [300-piller_size, 300-piller_size, no_size, 'black', 'green', 300+piller_size, 300+piller_size, None, 'play']
    }
    return items


def main():
    canvas = Canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    items = get_items_dict()
    while True:
        key = start(canvas, items)
        if key in ROUNDS:
            rounds_to_play = int(key)
            score = play(canvas, rounds_to_play, items)
            end(canvas, score)
        elif key in [' ', 'Exit']:
            canvas.clear()
            if not RUN_IN_CODE_IN_PLACE:
                sys.exit()
            else:
                exit_screen(canvas)


def play(canvas, rounds_to_play, items):
    """
    Loops to play the game.
    change_x: the direction of the x-coordinates.
    change_y: the direction of the y-coordinates.
    """
    global ball, change_x, change_y, counter, score

    create_play_screen(canvas, items)
    score = [0,0]

    for i in range(rounds_to_play):
        ball = create_ball(canvas)
        canvas.wait_for_click()
        # initial movement of ball in random direction
        change_x = get_random_direction()
        change_y = get_random_direction()
        counter = 0
        while True:
            canvas.move(ball, change_x, change_y)
            move_paddle_mouse(canvas)
            move_paddle_keys(canvas)
            point_scored = colliders(canvas, items)
            if counter % 10 == 0:
                create_bonus_items(canvas, 'rounds10')
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


def colliders(canvas, items):
    """
    Function to handle the collision with paddles and pillars.
    Returns a swapped change_y if the paddle is touched.
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
    if (y2_ball > PADDLE_Y1 + 1) and (y1_ball > CANVAS_HEIGHT / 2):
        # player 1
        canvas.delete(ball)
        score[1] += 1
        create_bonus_items(canvas, 'player_1')
        return True
    elif (y1_ball < PADDLE_Y2 + PADDLE_HEIGHT - 1) and (y1_ball < CANVAS_HEIGHT / 2):
        # player 2
        canvas.delete(ball)
        score[0] += 1
        create_bonus_items(canvas, 'player_2')
        return True

    for key, value in items.items():
        if value[7] in colliding_with:
            if key in ['paddle_1', 'paddle_2']:
                # ball caught with paddle
                change_y = -change_y
            elif key in ['pillar_1', 'pillar_2', 'pillar_3', 'pillar_4']:
                change_x = get_random_direction()
                change_y = get_random_direction()
    return False


def start(canvas, items):
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
            else:
                continue
        if not RUN_IN_CODE_IN_PLACE:
            canvas.update()


def start_screen_updater(canvas, items, key, info):
    canvas.delete(key)
    value = items[key]
    canvas.create_rectangle(
        value[0],
        value[1],
        value[5],
        value[6],
        color='red'
    )
    canvas.create_text(
        value[0],
        value[1],
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
        canvas.change_text(info, "    Click to continue...")
    else:
        canvas.delete(info)
        canvas.create_text(
            15,
            CANVAS_HEIGHT - 50,
            "    Click to continue...",
            color='red'
        )
    canvas.wait_for_click()


def end(canvas, score):
    """
    Function that creates the end_screen
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

    # lol
    if RUN_IN_CODE_IN_PLACE:
        create_end_screen_colors_frame(canvas, score)
    else:
        create_end_screen_confetti_frame(canvas, score)
        canvas.update()
    canvas.wait_for_click()
    create_background_image(canvas, 'soft')
    haiku_color = get_random_color()
    for i in range(len(haiku)):
        canvas.create_text(
            50,
            85 + i * 60,
            text=haiku[i],
            font='Arial',
            font_size=20,
            color=haiku_color
        )
    canvas.wait_for_click()
    canvas.clear()
    if not RUN_IN_CODE_IN_PLACE:
        canvas.update()


def exit_screen(canvas):
    """
    Function to show exit_screen, only used when
    RUN_IN_CODE_IN_PLACE = True
    """
    create_background_image(canvas, 'soft')
    canvas.create_text(
        20,
        CANVAS_HEIGHT / 2 - 30,
        text="You can check out any time you like,",
        font='Arial',
        font_size=15,
        color='black'
    )
    canvas.create_text(
        20,
        CANVAS_HEIGHT / 2,
        text="but you can never leave.",
        font='Arial',
        font_size=15,
        color='black'
    )
    canvas.wait_for_click()
    canvas.clear()


def move_paddle_keys(canvas):
    """
    Function to move the paddle with the keys.
    """
    global paddle_1, pressed_key

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


def move_paddle_left(canvas):
    global paddle_1

    paddle_x = canvas.get_left_x(paddle_1)
    x = paddle_x - 10
    print("Left", paddle_x, x)
    if paddle_x > 0:
        canvas.moveto(paddle_1, x, PADDLE_Y1)


def move_paddle_right(canvas):
    global paddle_1

    paddle_x = canvas.get_left_x(paddle_1)
    x = paddle_x + 10
    print("Right", paddle_x, x)
    if paddle_x < CANVAS_WIDTH - PADDLE_WIDTH:
        canvas.moveto(paddle_1, x, PADDLE_Y1)


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
    create_background_image(canvas)

    for key, value in items.items():
        if key in ROUNDS:
            create_square(canvas, items, key)
        if value[2] != 0 and value[8] == 'start':
            canvas.create_text(
                value[0],
                value[1],
                text=key,
                font='Arial',
                font_size=value[2],
                color=value[3]
            )

    info = canvas.create_text(
        15,
        CANVAS_HEIGHT - 50,
        "Player 1: arrow keys - Player 2: mouse.",
        color='red'
    )
    return info


def create_play_screen(canvas, items):
    global paddle_1, paddle_2, pillar_1, pillar_2, pillar_3, pillar_4

    create_background_image(canvas, 'soft')
    create_bonus_items(canvas, 'start')

    paddle_1 = create_play_screen_elements(canvas, 'paddle_1', items)
    paddle_2 = create_play_screen_elements(canvas, 'paddle_2', items)
    pillar_1 = create_play_screen_elements(canvas, 'pillar_1', items)
    pillar_2 = create_play_screen_elements(canvas, 'pillar_2', items)
    pillar_3 = create_play_screen_elements(canvas, 'pillar_3', items)
    pillar_4 = create_play_screen_elements(canvas, 'pillar_4', items)


def create_play_screen_elements(canvas, element, items):
    play_screen_element = canvas.create_rectangle(
        items[element][0],
        items[element][1],
        items[element][5],
        items[element][6],
        items[element][3]
    )
    items[element][7] = play_screen_element
    return play_screen_element


def create_ball(canvas):
    """
    Function to create the ball
    """

    ball_x1 = CANVAS_WIDTH / 2 - BALL_RADIUS
    ball_y1 = CANVAS_HEIGHT / 2 - BALL_RADIUS
    ball_x2 = ball_x1 + BALL_RADIUS * 2
    ball_y2 = ball_y1 + BALL_RADIUS * 2
    ball = canvas.create_oval(ball_x1, ball_y1, ball_x2, ball_y2, "black")
    return ball


def create_bonus_items(canvas, event):
    """
    Funtion that creates bonus items on the screen.

    It happens on three occasions:
    - start
    - point scored
    - 10th round played

    """
    pass


def create_end_screen_confetti_frame(canvas, score):
    create_background_image(canvas, 'soft')
    for i in range(CONFETTI):
        create_score_text(canvas, score)
        confetti_color = get_confetti_color()
        # define random size
        size = random.randint(1, 20)
        # define random location on canvas
        x_coordinate = random.randint(0, CANVAS_WIDTH - size)
        y_coordinate = random.randint(0, CANVAS_HEIGHT - size)
        function = random.choice(["circle", "rectangle", "line"])
        if function == "circle":
            create_confetti_circle(canvas, x_coordinate, y_coordinate, size, confetti_color)
        elif function == "rectangle":
            create_confetti_square(canvas, x_coordinate, y_coordinate, size, confetti_color)
        elif function == "line":
            length = random.randint(50, 250)
            create_confetti_line(canvas, x_coordinate, y_coordinate, confetti_color, length, size)
        canvas.update()
        time.sleep(0.1)


def create_confetti_line(canvas, x1, y1, color, length=100, width=1):
    """
    This function draws a line.
    """
    x2 = x1 + width
    y2 = y1 + length
    canvas.create_line(x1, y1, x2, y2, fill=color)


def create_confetti_square(canvas, x1, y1, size, color):
    """
    This function draws a square.
    """
    x2 = x1 + size
    y2 = y1 + size
    canvas.create_rectangle(x1, y1, x2, y2, fill=color)


def create_confetti_circle(canvas, x1, y1, size, color):
    """
    This function draws a circle.
    """
    x2 = x1 + size
    y2 = y1 + size
    canvas.create_oval(x1, y1, x2, y2, color)


def create_end_screen_colors_frame(canvas, score):
    colors = get_end_screen_colors()
    for i in range(len(colors)):
        screen = canvas.create_rectangle(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT, colors[i])
        create_score_text(canvas, score)
        time.sleep(0.1)
        canvas.delete(screen)


def create_score_text(canvas, score):
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


def create_square(canvas, items, key):
    square = canvas.create_rectangle(
        items[key][0],
        items[key][1],
        items[key][5],
        items[key][6],
        color=items[key][4]
    )
    return square


def get_random_direction():
    return random.choice([-1, 1])


def get_start_screen_key(items, x, y):
    for key, value in items.items():
        if key in ROUNDS:
            x1 = value[0]
            y1 = value[1]
            x2 = value[5]
            y2 = value[6]

            if x1 <= x <= x2 and y1 <= y <= y2:
                return key
    return None


def get_random_color():
    """
    Function that returns a random color.
    """
    colors = [
        'orange',
        'green',
        'blue',
        'purple'
    ]
    return random.choice(colors)


def get_confetti_color():
    """
    Function that returns a random color.
    """
    colors = [
        'orange',
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


def get_end_screen_colors():
    """
    Function that returns a list full of colors
    """
    colors = [
        'snow', 'ghost white', 'white smoke',
        'gainsboro', 'floral white', 'old lace', 'linen',
        'antique white', 'papaya whip', 'blanched almond',
        'bisque', 'peach puff', 'navajo white', 'lemon chiffon',
        'mint cream', 'azure', 'alice blue', 'lavender',
        'lavender blush', 'misty rose', 'dark slate gray',
        'dim gray', 'slate gray', 'light slate gray', 'gray',
        'light gray', 'midnight blue', 'navy', 'cornflower blue',
        'dark slate blue', 'slate blue', 'medium slate blue',
        'light slate blue', 'medium blue', 'royal blue',
        'blue', 'dodger blue', 'deep sky blue', 'sky blue',
        'light sky blue', 'steel blue', 'light steel blue',
        'light blue', 'powder blue', 'pale turquoise',
        'dark turquoise', 'medium turquoise', 'turquoise',
        'cyan', 'light cyan', 'cadet blue', 'medium aquamarine',
        'aquamarine', 'dark green', 'dark olive green',
        'dark sea green', 'sea green', 'medium sea green',
        'light sea green', 'pale green', 'spring green',
        'lawn green', 'medium spring green', 'green yellow',
        'lime green', 'yellow green', 'forest green', 'olive drab',
        'dark khaki', 'khaki', 'pale goldenrod',
        'light goldenrod yellow', 'light yellow', 'yellow',
        'gold', 'light goldenrod', 'goldenrod', 'dark goldenrod',
        'rosy brown', 'indian red', 'saddle brown', 'sandy brown',
        'dark salmon', 'salmon', 'light salmon', 'orange',
        'dark orange', 'coral', 'light coral', 'tomato',
        'orange red', 'red', 'hot pink', 'deep pink', 'pink',
        'light pink', 'pale violet red', 'maroon',
        'violet red', 'dark orchid', 'dark violet', 'blue violet', 'purple',
        'medium purple',
    ]
    return colors


if __name__ == '__main__':
    main()