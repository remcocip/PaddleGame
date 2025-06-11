"""
File: paddle_game.py
Author: Remco (remco.cip@gmail.com)
Version date: 11 june 2025

This is my 'final project' for Code in Place 2025.

In this game two players will pass the ball to each other,
if the player misses the ball, a point goes to the other.

The bottom player needs to use the Left and Right arrow key.
The top player needs to use the mouse.
"""
# True if run in Code in Place
RUN_IN_CODE_IN_PLACE = False

from graphics import Canvas
import time
import random
import sys
import os
if RUN_IN_CODE_IN_PLACE:
    from ai import call_gpt

# CONSTANTS NOT TO CHANGE
CANVAS_WIDTH = 400
CANVAS_HEIGHT = 400
PADDLE_Y1 = CANVAS_HEIGHT - 30      # bottom paddle
PADDLE_Y2 = 15                      # top paddle
PADDLE_WIDTH = 80
PADDLE_HEIGHT = 15
BALL_RADIUS = 10
offset = 8
box_size = 30

# CHANGEABLE CONSTANTS
SPEED = 0.0000000001        # closer to 0 is faster
ROUNDS = ['9', '3', '5']    # keep odd and single digit

def main():
    canvas = Canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    while True:
        key = start_screen(canvas)
        if key in ROUNDS:
            rounds_to_play = int(key)
            score = play(canvas, rounds_to_play)
            end_screen(canvas, score)
        elif key in [' ', 'Exit']:
            canvas.clear()
            if not RUN_IN_CODE_IN_PLACE:
                sys.exit()
            else:
                exit_screen(canvas)


def start_screen(canvas):
    items, info, color = build_start_screen(canvas)
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

            for key in items:
                if key in ['Paddle Game', 'Rounds']:
                    continue

                x1 = items[key][0]-offset
                y1 = items[key][1]-offset
                x2 = x1 + box_size
                y2 = y1 + box_size

                if x >= x1 and x <= x2 and y >= y1 and y <= y2:
                    if key in [' ', 'Exit']:
                        return key
                    canvas.delete(key)
                    canvas.create_rectangle(                # 0 - 4
                        x1,
                        y1,
                        x2,
                        y2,
                        color = 'red'
                    )
                    canvas.create_text(
                        items[key][0],
                        items[key][1],
                        text = key,
                        font = 'Arial',
                        font_size = items[key][2],
                        color = 'black'
                    )
                    click_to_continue(canvas, info, color=color)
                    canvas.clear()
                    if not RUN_IN_CODE_IN_PLACE:
                        canvas.update()
                    return key
        if not RUN_IN_CODE_IN_PLACE:
            canvas.update()


def play(canvas, rounds_to_play):
    """
    Loops to play the game.
    change_x: the direction of the x-coordinates.
    change_y: the direction of the y-coordinates.
    """
    show_image(canvas, 'soft')
    paddle_1 = launch_paddle(canvas, 'paddle_1')
    paddle_2 = launch_paddle(canvas, 'paddle_2')
    score = [0,0]

    for i in range(rounds_to_play):
        ball = launch_ball(canvas)
        # initial movement of ball in random direction
        change_x = random.choice([-1, 1])
        change_y = random.choice([-1, 1])
        while True:
            canvas.move(ball, change_x, change_y)
            move_paddle_1(canvas, paddle_1)
            move_paddle_2(canvas, paddle_2)
            change_y = paddle_touched(canvas, paddle_1, paddle_2, ball, change_y)

            # ball bounces at the walls
            x = canvas.get_left_x(ball)
            if x < 0 or x > CANVAS_WIDTH - BALL_RADIUS * 2:
                change_x = -change_x

            # if ball not catched
            y_top = canvas.get_top_y(ball)
            y_bottom = y_top + BALL_RADIUS*2 - 1
            y_top += 1
            ## at player one's side:
            if (y_bottom > PADDLE_Y1) and (y_top > CANVAS_HEIGHT/2):
                canvas.delete(ball)
                score[1] += 1
                break
            ## at player two's side:
            elif (y_top < PADDLE_Y2 + PADDLE_HEIGHT) and (y_top < CANVAS_HEIGHT/2):
                canvas.delete(ball)
                score[0] += 1
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


def end_screen(canvas, score):
    """
    Function that creates the endscreen
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
    colors = get_endscreen_colors()
    for i in range(len(colors)):
        screen = canvas.create_rectangle(0,0,CANVAS_WIDTH,CANVAS_HEIGHT,colors[i])

        score_dict = {
            'player1':  [str(score[0]), 80],
            '-':        [' - ',         CANVAS_WIDTH/2-35],
            'player2':  [str(score[1]), 280]
        }
        for key in score_dict:
            canvas.create_text(
                score_dict[key][1],
                CANVAS_HEIGHT/2-40,
                text = score_dict[key][0],
                font = 'Arial',
                font_size = 60,
                color = 'white'
            )
        time.sleep(0.1)
        canvas.delete(screen)
    if not RUN_IN_CODE_IN_PLACE:
        canvas.update()

    show_image(canvas, 'soft')
    haiku_color = get_random_color()
    for i in range(len(haiku)):
        canvas.create_text(
            50,
            85 + i*60,
            text = haiku[i],
            font = 'Arial',
            font_size = 20,
            color = haiku_color
        )
    canvas.wait_for_click()
    canvas.clear()
    if not RUN_IN_CODE_IN_PLACE:
        canvas.update()


def exit_screen(canvas):
    """
    Function to show exitscreen, only used when
    RUN_IN_CODE_IN_PLACE = True
    """
    show_image(canvas, 'soft')
    canvas.create_text(
        20,
        CANVAS_HEIGHT/2-30,
        text = "You can check out any time you like,",
        font = 'Arial',
        font_size = 15,
        color = 'black'
        )
    canvas.create_text(
        20,
        CANVAS_HEIGHT/2,
        text = "but you can never leave.",
        font = 'Arial',
        font_size = 15,
        color = 'black'
        )
    canvas.wait_for_click()
    canvas.clear()


def build_start_screen(canvas):
    show_image(canvas)
    color = get_random_color()

    """
    The items dict contains all the menu items:
    key : the text shown on screen
    value[0] : the x-coordinate
    value[1] : the y-coordinate
    value[2] : the font size
    value[3] : the text color
    value[4] : the box color    
    """

    items = {

        # Title:
        'Paddle Game':  [100,   50,     30, color, 'white'],

        # Menu items for number_of_rounds
        'Rounds':   [50,    150,    30, color, ''],
        ROUNDS[0]:  [175,   155,    20, 'white', color],
        ROUNDS[1]:  [225,   155,    20, 'white', color],
        ROUNDS[2]:  [275,   155,    20, 'white', color],
        ' ':        [80,    250,    30, 'white', 'white'],
        'Exit':     [50,    250,    30, color, 'white']
        }

    for key in items:
        if key in ROUNDS:
            canvas.create_rectangle(                # 0 - 4
                items[key][0]-offset,
                items[key][1]-offset,
                items[key][0]-offset+box_size,
                items[key][1]-offset+box_size,
                color = items[key][4]
            )
        canvas.create_text(                     # 5 - 9
            items[key][0],
            items[key][1],
            text = key,
            font = 'Arial',
            font_size = items[key][2],
            color = items[key][3]
        )

    info = canvas.create_text(
        15,
        CANVAS_HEIGHT-50,
        "Player 1 (bottom) uses arrow keys, player 2 (top) uses the mouse.",
        color = color
        )
    return items, info, color


def show_image(canvas, pic_type='hard'):
    """
    Function to show the background image
    """
    filepath = os.listdir(os.getcwd())
    if pic_type == 'soft':
        image = canvas.create_image(0, 0, 'paddle_soft.jpg')
    else:
        image = canvas.create_image(0, 0, 'paddle.jpg')


def click_to_continue(canvas, info, color=''):
    """
    Function to update the info box
    and wait for the user to click.
    """
    if RUN_IN_CODE_IN_PLACE:
        canvas.change_text(info, "    Click to continue...")
    else:
        info = canvas.create_text(
            15,
            CANVAS_HEIGHT - 50,
            "    Click to continue...",
            color=color
        )
    canvas.wait_for_click()


def paddle_touched(canvas, paddle_1, paddle_2, ball, change_y):
    """
    Function to handle the collision with paddle.
    Returns a swapped change_y if the paddle is toched.
    """
    x1 = canvas.get_left_x(ball)
    y1 = canvas.get_top_y(ball)
    x2 = x1 + 2 * BALL_RADIUS
    y2 = y1 + 2 * BALL_RADIUS

    colliders = canvas.find_overlapping(x1, y1, x2, y2)
    if paddle_1 in colliders or paddle_2 in colliders:
        # paddle touched
        change_y = -change_y
    return change_y


def move_paddle_1(canvas, paddle_1):
    """
    Function to move the paddle with the keys.
    """
    # get the x position of the paddle
    paddle_x = canvas.get_left_x(paddle_1)
    # determine the movement
    if RUN_IN_CODE_IN_PLACE:
        key = canvas.get_last_key_press()
    else:
        key = 'ArrowLeft'
    if key == 'ArrowLeft' and paddle_x > 0:
        paddle_x -= 10
    elif key == 'ArrowRight' and paddle_x < CANVAS_WIDTH - PADDLE_WIDTH:
        paddle_x += 10

    # and move the paddle to the new location
    canvas.moveto(paddle_1, paddle_x, PADDLE_Y1)


def move_paddle_2(canvas, paddle_2):
    """
    Function to move the paddle with the mouse
    relative to the middle of the paddle.
    """
    # get the x position of the paddle
    paddle_x = canvas.get_left_x(paddle_2)

    # determine the movement
    mouse_x = canvas.get_mouse_x()
    if mouse_x < (paddle_x + PADDLE_WIDTH / 2):
        if paddle_x > 0:
            paddle_x -= 1
    elif mouse_x > paddle_x:
        paddle_x += 1
        if paddle_x + PADDLE_WIDTH > CANVAS_WIDTH:
            paddle_x = CANVAS_WIDTH - PADDLE_WIDTH
    canvas.moveto(paddle_2, paddle_x, PADDLE_Y2)


def launch_paddle(canvas, paddle_id):
    """
    Function to create the paddle
    """
    # determine the lef_x and top_y positions:
    paddle_x = CANVAS_WIDTH / 2 - PADDLE_WIDTH / 2
    paddle_y = PADDLE_Y1 if paddle_id == 'paddle_1' else PADDLE_Y2

    # create the paddle:
    paddle = canvas.create_rectangle(
        paddle_x,
        paddle_y,
        paddle_x + + PADDLE_WIDTH,
        paddle_y + PADDLE_HEIGHT,
        "black")
    return paddle


def launch_ball(canvas):
    """
    Function to create the ball
    """
    ball_x1 = CANVAS_WIDTH/2 - BALL_RADIUS
    ball_y1 = CANVAS_HEIGHT/2 - BALL_RADIUS
    ball_x2 = ball_x1 + BALL_RADIUS*2
    ball_y2 = ball_y1 + BALL_RADIUS*2
    ball = canvas.create_oval(ball_x1, ball_y1, ball_x2, ball_y2, "black")
    return ball


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


def get_endscreen_colors():
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
        'medium violet red', 'violet red', 'medium orchid',
        'dark orchid', 'dark violet', 'blue violet', 'purple',
        'medium purple',
        ]
    return colors


if __name__ == '__main__':
    main()