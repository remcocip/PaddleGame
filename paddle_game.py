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
from typing import Optional, List, Any, Dict
from graphics import Canvas
import time
import random
import sys
import os
from settings import *


class PaddleGame:
    def __init__(self) -> None:
        self.RUN_IN_CODE_IN_PLACE: bool = True if (os.getcwd() == '/home/pyodide') else False
        self.SPEED: float = 0.0 if self.RUN_IN_CODE_IN_PLACE else 0.01

        if self.RUN_IN_CODE_IN_PLACE:
            from ai import call_gpt
            self.call_gpt = call_gpt
            print("Running in Code in Place!")
            
        self.canvas: Canvas = Canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
        self.items: Dict[str, Dict[str, Any]] = get_items_dict()
        
        # Instance state variables
        self.ball: Optional[int] = None
        self.change_x: float = 0.0
        self.change_y: float = 0.0
        self.paddle_1: Optional[int] = None
        self.paddle_2: Optional[int] = None
        self.pillar_1: Optional[int] = None
        self.pillar_3: Optional[int] = None
        self.pillar_5: Optional[int] = None
        self.pillar_7: Optional[int] = None
        self.pillar_8: Optional[int] = None
        self.score: List[int] = [0, 0]

    def run(self) -> None:
        """
        Function to handle the main loop.
        """
        while True:
            key = self.start()
            if key in ROUNDS:
                rounds_to_play = int(key)
                self.play(rounds_to_play)
                self.end()
            elif key == 'Exit':
                self.exit_game()

    def play(self, rounds_to_play: int) -> List[int]:
        """
        Function to handle the game loop.
        """
        self.create_play_screen()
        self.score = [0, 0]

        for i in range(rounds_to_play):
            self.ball = self.create_ball()
            self.canvas.wait_for_click()
            
            self.change_x = self.get_random_direction()
            self.change_y = self.get_random_direction()
            
            while True:
                self.canvas.move(self.ball, self.change_x, self.change_y)
                self.move_paddle_mouse()
                self.move_paddle_keys()
                point_scored = self.colliders()
                if point_scored:
                    break
                time.sleep(self.SPEED)
                self.update_canvas()
            if i == rounds_to_play:
                break
                
        self.canvas.clear()
        self.update_canvas()
        return self.score

    def _check_wall_collisions(self, x1_ball: float, x2_ball: float) -> bool:
        if x1_ball <= 0 or x2_ball > CANVAS_WIDTH:
            self.change_x = -self.change_x
            return True
        return False

    def _check_scoring(self, y1_ball: float, y2_ball: float) -> bool:
        if (y2_ball > CANVAS_HEIGHT) and (y1_ball > CANVAS_HEIGHT / 2):
            self.canvas.delete(self.ball)
            self.score[1] += 1
            return True
        elif (y1_ball < 0) and (y1_ball < CANVAS_HEIGHT / 2):
            self.canvas.delete(self.ball)
            self.score[0] += 1
            return True
        return False

    def _check_item_collisions(self, colliding_with: List[int]) -> None:
        for key, value in self.items.items():
            if value['object_id'] in colliding_with:
                if key in ['paddle_1', 'paddle_2']:
                    self.change_y = -self.change_y
                elif key.startswith('pillar_'):
                    self.change_x = self.get_random_direction()
                    self.change_y = self.get_random_direction()

    def colliders(self) -> bool:
        """
        Function to handle the collision with paddles and pillars.
        Updates the score if a point is made.
        Returns False if ball kept playing, True if point evaluated.
        """
        glue_fixer = 0
        x1_ball = self.canvas.get_left_x(self.ball) - glue_fixer
        y1_ball = self.canvas.get_top_y(self.ball) - glue_fixer
        x2_ball = x1_ball + 2 * BALL_RADIUS + glue_fixer
        y2_ball = y1_ball + 2 * BALL_RADIUS + glue_fixer
        
        colliding_with = self.canvas.find_overlapping(x1_ball, y1_ball, x2_ball, y2_ball)

        if self._check_wall_collisions(x1_ball, x2_ball):
            return False

        if self._check_scoring(y1_ball, y2_ball):
            return True

        self._check_item_collisions(colliding_with)
        return False

    def start(self) -> Optional[str]:
        """
        Function to handle the start menu loop.
        """
        info = self.create_start_screen()
        while True:
            click = self.wait_and_get_click()
            if click:
                x, y = click[0], click[1]
                key = self.get_start_screen_key(x, y)
                if key in ROUNDS:
                    self.start_screen_updater(key, info)
                return key
            self.update_canvas()

    def start_screen_updater(self, key: str, info: int) -> None:
        """
        Function to update the start screen elements.
        """
        self.canvas.delete(key)
        value = self.items[key]
        rect_id = self.canvas.create_rectangle(
            value['x1'], value['y1'], value['x2'], value['y2'], color='red'
        )
        value['object_id'] = rect_id
        
        self.canvas.create_text(
            value['x1'] + OFFSET, value['y1'] + OFFSET,
            text=key, font='Arial', font_size=value['font_size'], color='white'
        )
        self.start_screen_wait_for_user(info)
        self.update_canvas()

    def start_screen_wait_for_user(self, info: int) -> None:
        """
        Function to update the info box & wait
        """
        if self.RUN_IN_CODE_IN_PLACE:
            self.canvas.change_text(info, "Click to continue...")
            self.canvas.wait_for_click()
        else:
            self.canvas.delete(info)
            self.click_to_continue()

    def click_to_continue(self) -> None:
        self.canvas.create_text(
            CANVAS_WIDTH / 2, CANVAS_HEIGHT - 50,
            "Click to continue...", color='lime green', anchor='center'
        )
        self.canvas.wait_for_click()
        self.canvas.clear()
        self.update_canvas()

    def end(self) -> None:
        """
        Function to create the end_screen.
        """
        winner = 'player 1' if self.score[0] > self.score[1] else 'player 2'
        topic = 'winner'

        haiku = self.get_haiku(winner, topic)

        self.create_end_screen_confetti_frame()
        self.create_background_image('soft')
        for i in range(len(haiku)):
            self.canvas.create_text(
                50, 85 + i*60, text=haiku[i], font='Arial', font_size=20, color="lime green"
            )
            time.sleep(1.5)
        self.click_to_continue()

    def exit_screen(self) -> None:
        self.create_background_image('soft')
        self.canvas.create_text(
            20, CANVAS_HEIGHT / 2 - 30, text="You can check out any time you like,", font='Arial', font_size=15, color='lime green'
        )
        self.canvas.create_text(
            20, CANVAS_HEIGHT / 2, text="but you can never leave.", font='Arial', font_size=15, color='lime green'
        )
        self.click_to_continue()

    def move_paddle_keys(self) -> None:
        """
        Function to move the paddle with the keys.
        """
        paddle_x = self.canvas.get_left_x(self.paddle_1)
        pressed_key = self.get_key_press()
        if pressed_key == 'ArrowLeft' and paddle_x > 0:
            paddle_x -= 10
        elif pressed_key == 'ArrowRight' and paddle_x < CANVAS_WIDTH - PADDLE_WIDTH:
            paddle_x += 10
        self.canvas.moveto(self.paddle_1, paddle_x, PADDLE_Y1)

    def move_paddle_mouse(self) -> None:
        """
        Function to move the paddle with the mouse.
        """
        paddle_x = self.canvas.get_left_x(self.paddle_2)
        mouse_x = self.canvas.get_mouse_x()
        
        if mouse_x < (paddle_x + PADDLE_WIDTH / 2):
            if paddle_x > 0:
                paddle_x -= 3
        elif mouse_x > paddle_x:
            paddle_x += 3
            if paddle_x + PADDLE_WIDTH > CANVAS_WIDTH:
                paddle_x = CANVAS_WIDTH - PADDLE_WIDTH
        self.canvas.moveto(self.paddle_2, paddle_x, PADDLE_Y2)

    def create_start_screen(self) -> int:
        self.create_background_image()

        for key, value in self.items.items():
            if key in ROUNDS:
                rect_id = self.canvas.create_rectangle(
                    value['x1'], value['y1'], value['x2'], value['y2'], value['box_color']
                )
                value['object_id'] = rect_id
            if value['font_size'] != 0 and value['screen_type'] == 'start':
                self.canvas.create_text(
                    value['x1'] + OFFSET, value['y1'] + OFFSET,
                    text=key, font='Arial', font_size=value['font_size'], color=value['text_color']
                )

        info = self.canvas.create_text(
            CANVAS_WIDTH / 2, CANVAS_HEIGHT - 50,
            "Player 1: arrow keys        Player 2: mouse.", color='lime green', anchor='center'
        )
        return info

    def create_play_screen(self) -> None:
        self.create_background_image('soft')

        self.paddle_1 = self.create_play_screen_elements('paddle_1')
        self.paddle_2 = self.create_play_screen_elements('paddle_2')
        self.pillar_1 = self.create_play_screen_elements('pillar_1')
        self.pillar_3 = self.create_play_screen_elements('pillar_3')
        self.pillar_5 = self.create_play_screen_elements('pillar_5')
        self.pillar_7 = self.create_play_screen_elements('pillar_7')
        self.pillar_8 = self.create_play_screen_elements('pillar_8')

    def create_ball(self) -> int:
        ball_x1 = CANVAS_WIDTH / 2 - BALL_RADIUS
        ball_y1 = CANVAS_HEIGHT / 2 - BALL_RADIUS
        ball_x2 = ball_x1 + BALL_RADIUS * 2
        ball_y2 = ball_y1 + BALL_RADIUS * 2
        color = get_color()

        return self.canvas.create_oval(ball_x1, ball_y1, ball_x2, ball_y2, color)

    def create_end_screen_confetti_frame(self) -> None:
        self.create_background_image('soft')
        for i in range(CONFETTI):
            self.create_score_text()
            color = get_color()
            size = random.randint(1, 20)
            x_coordinate = random.randint(0, CANVAS_WIDTH - size)
            y_coordinate = random.randint(0, CANVAS_HEIGHT - size)
            function = random.choice(["circle", "rectangle", "line"])
            
            if function == "circle":
                self.create_confetti_circle(x_coordinate, y_coordinate, size, color)
            elif function == "rectangle":
                self.create_confetti_square(x_coordinate, y_coordinate, size, color)
            elif function == "line":
                length = random.randint(50, 250)
                self.create_confetti_line(x_coordinate, y_coordinate, color, length, size)
            
            self.update_canvas()
            time.sleep(0.1)
        self.click_to_continue()

    def create_confetti_line(self, x1: float, y1: float, color: str, length: int = 100, width: int = 1) -> None:
        x2 = x1 + width
        y2 = y1 + length
        self.canvas.create_line(x1, y1, x2, y2, color)

    def create_confetti_square(self, x1: float, y1: float, size: int, color: str) -> None:
        x2 = x1 + size
        y2 = y1 + size
        self.canvas.create_rectangle(x1, y1, x2, y2, color)

    def create_confetti_circle(self, x1: float, y1: float, size: int, color: str) -> None:
        x2 = x1 + size
        y2 = y1 + size
        self.canvas.create_oval(x1, y1, x2, y2, color)

    def create_score_text(self) -> None:
        score_dict = {
            'player1': [str(self.score[0]), 80],
            '-': [' - ', CANVAS_WIDTH / 2 - 35],
            'player2': [str(self.score[1]), 280]
        }
        for key in score_dict:
            self.canvas.create_text(
                score_dict[key][1], CANVAS_HEIGHT / 2 - 40,
                text=score_dict[key][0], font='Arial', font_size=60, color='white'
            )

    def create_background_image(self, pic_type: str = 'hard') -> None:
        if pic_type == 'soft':
            self.canvas.create_image(0, 0, 'paddle_soft.jpg')
        else:
            self.canvas.create_image(0, 0, 'paddle.jpg')

    def create_play_screen_elements(self, key: str) -> int:
        value = self.items[key]
        play_screen_element = self.canvas.create_rectangle(
            value['x1'], value['y1'], value['x2'], value['y2'], value['text_color']
        )
        value['object_id'] = play_screen_element
        return play_screen_element

    def get_random_direction(self) -> float:
        movement = [-1.5, -1.0, 0.5, 1.0, 1.5]
        return random.choice(movement)

    def get_start_screen_key(self, x: float, y: float) -> Optional[str]:
        for key, value in self.items.items():
            if key in ROUNDS or key == 'Exit':
                x1, y1, x2, y2 = value['x1'], value['y1'], value['x2'], value['y2']
                if x1 <= x <= x2 and y1 <= y <= y2:
                    return key
        return None

    def update_canvas(self) -> None:
        if not self.RUN_IN_CODE_IN_PLACE:
            self.canvas.update()

    def wait_and_get_click(self) -> Optional[List[float]]:
        if self.RUN_IN_CODE_IN_PLACE:
            self.canvas.wait_for_click()
            return self.canvas.get_last_click()
        return self.canvas.wait_for_click()

    def get_key_press(self) -> Optional[str]:
        if self.RUN_IN_CODE_IN_PLACE:
            return self.canvas.get_last_key_press()
        
        pressed_keys = self.canvas.get_new_key_presses()
        if pressed_keys:
            keysym = pressed_keys[0].keysym
            if keysym == 'Left': return 'ArrowLeft'
            if keysym == 'Right': return 'ArrowRight'
        return None

    def exit_game(self) -> None:
        self.canvas.clear()
        if not self.RUN_IN_CODE_IN_PLACE:
            sys.exit()
        self.exit_screen()

    def get_haiku(self, winner: str, topic: str) -> List[str]:
        if self.RUN_IN_CODE_IN_PLACE:
            haiku = self.call_gpt(f"Create a haiku with the words {winner} {topic}")
            return [line.strip() for line in haiku.split(',')]
        return ["In a pixel world", f"{winner.title()} claims the crown", "Victory's sweet sound."]


def main() -> None:
    try:
        game = PaddleGame()
        game.run()
    except Exception:
        # Ignore tkinter destroyed errors when user manually closes canvas window
        pass

if __name__ == '__main__':
    main()