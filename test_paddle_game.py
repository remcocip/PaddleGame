import unittest
from unittest.mock import MagicMock, patch
import paddle_game

class TestPaddleGameOOP(unittest.TestCase):

    @patch('paddle_game.Canvas')
    def setUp(self, MockCanvas):
        paddle_game.os.getcwd = MagicMock(return_value='/local/dir')
        self.game = paddle_game.PaddleGame()
        self.mock_canvas = self.game.canvas
        
    def test_get_color(self):
        valid_colors = [
            'orange', 'green', 'blue', 'coral', 'tomato', 'red', 
            'hot pink', 'deep pink', 'maroon', 'medium purple', 'purple'
        ]
        color = paddle_game.get_color()
        self.assertIn(color, valid_colors)

    def test_get_items_dict(self):
        items = paddle_game.get_items_dict()
        self.assertIn(paddle_game.ROUNDS[0], items)
        self.assertIn('Exit', items)
        self.assertIn('paddle_1', items)

    def test_get_random_direction(self):
        direction = self.game.get_random_direction()
        self.assertIn(direction, [-1.5, -1, 0.5, 1, 1.5])

    def test_get_start_screen_key(self):
        key = self.game.get_start_screen_key(50, 290)
        self.assertEqual(key, 'Exit')
        key = self.game.get_start_screen_key(0, 0)
        self.assertIsNone(key)

    def test_create_background_image(self):
        self.game.create_background_image('soft')
        self.mock_canvas.create_image.assert_called_with(0, 0, 'paddle_soft.jpg')
        self.game.create_background_image('hard')
        self.mock_canvas.create_image.assert_called_with(0, 0, 'paddle.jpg')

    def test_create_score_text(self):
        self.game.score = [5, 3]
        self.game.create_score_text()
        self.assertEqual(self.mock_canvas.create_text.call_count, 3)

    def test_create_confetti_shapes(self):
        self.game.create_confetti_circle(10, 10, 5, 'red')
        self.mock_canvas.create_oval.assert_called_with(10, 10, 15, 15, 'red')
        
        self.game.create_confetti_square(20, 20, 10, 'blue')
        self.mock_canvas.create_rectangle.assert_called_with(20, 20, 30, 30, 'blue')
        
        self.game.create_confetti_line(5, 5, 'green', 100, 2)
        self.mock_canvas.create_line.assert_called_with(5, 5, 7, 105, 'green')

    @patch('paddle_game.get_color', return_value='orange')
    def test_create_ball(self, mock_get_color):
        self.mock_canvas.create_oval.return_value = 'mock_ball_id'
        ball = self.game.create_ball()
        self.assertEqual(ball, 'mock_ball_id')
        self.mock_canvas.create_oval.assert_called_once()
        
    def test_create_play_screen_elements(self):
        self.mock_canvas.create_rectangle.return_value = 'mock_rect_id'
        rect_id = self.game.create_play_screen_elements('paddle_1')
        self.assertEqual(rect_id, 'mock_rect_id')
        self.assertEqual(self.game.items['paddle_1']['object_id'], 'mock_rect_id')

    @patch.object(paddle_game.PaddleGame, 'create_play_screen_elements')
    @patch.object(paddle_game.PaddleGame, 'create_background_image')
    def test_create_play_screen(self, mock_bg, mock_elements):
        self.game.create_play_screen()
        mock_bg.assert_called_once()
        self.assertEqual(mock_elements.call_count, 7)

    def test_create_start_screen(self):
        self.mock_canvas.create_rectangle.return_value = 'mock_rect_id'
        self.mock_canvas.create_text.return_value = 'mock_info_id'
        info = self.game.create_start_screen()
        self.assertEqual(info, 'mock_info_id')
        self.assertTrue(self.mock_canvas.create_rectangle.call_count > 0)
        self.assertTrue(self.mock_canvas.create_text.call_count > 0)

    @patch('paddle_game.PADDLE_WIDTH', 80)
    @patch('paddle_game.CANVAS_WIDTH', 400)
    def test_move_paddle_mouse(self):
        self.game.paddle_2 = 'paddle_2_id'
        self.mock_canvas.get_left_x.return_value = 100
        
        self.mock_canvas.get_mouse_x.return_value = 50 
        self.game.move_paddle_mouse()
        self.mock_canvas.moveto.assert_called_with('paddle_2_id', 97, paddle_game.PADDLE_Y2)
        
        self.mock_canvas.get_mouse_x.return_value = 200 
        self.game.move_paddle_mouse()
        self.mock_canvas.moveto.assert_called_with('paddle_2_id', 103, paddle_game.PADDLE_Y2)

    @patch('paddle_game.PADDLE_WIDTH', 80)
    @patch('paddle_game.CANVAS_WIDTH', 400)
    def test_move_paddle_keys(self):
        self.game.paddle_1 = 'paddle_1_id'
        self.mock_canvas.get_left_x.return_value = 100
        self.game.RUN_IN_CODE_IN_PLACE = False
        
        mock_key = MagicMock()
        mock_key.keysym = 'Left'
        self.mock_canvas.get_new_key_presses.return_value = [mock_key]
        
        self.game.move_paddle_keys()
        self.mock_canvas.moveto.assert_called_with('paddle_1_id', 90, paddle_game.PADDLE_Y1)

    def test_exit_screen(self):
        self.game.exit_screen()
        self.mock_canvas.create_text.assert_called()
        self.mock_canvas.wait_for_click.assert_called()

    @patch('time.sleep')
    @patch.object(paddle_game.PaddleGame, 'create_end_screen_confetti_frame')
    def test_end(self, mock_confetti, mock_sleep):
        self.game.RUN_IN_CODE_IN_PLACE = False
        self.game.score = [5, 2]
        self.game.end()
        mock_confetti.assert_called_once()
        self.mock_canvas.create_text.assert_called()
        
    def test_click_to_continue(self):
        self.game.RUN_IN_CODE_IN_PLACE = False
        self.game.click_to_continue()
        self.mock_canvas.create_text.assert_called()
        self.mock_canvas.wait_for_click.assert_called()
        self.mock_canvas.clear.assert_called()

    def test_start_screen_updater(self):
        key = 'Exit'
        self.game.RUN_IN_CODE_IN_PLACE = False
        self.game.items[key]['object_id'] = 'old_rect_id'
        
        self.game.start_screen_updater(key, 'info_id')
        self.mock_canvas.delete.assert_any_call('Exit')
        self.mock_canvas.create_rectangle.assert_called()

    @patch.object(paddle_game.PaddleGame, 'get_start_screen_key', return_value='Exit')
    @patch.object(paddle_game.PaddleGame, 'create_start_screen', return_value='info_id')
    def test_start(self, mock_create, mock_get_key):
        self.game.RUN_IN_CODE_IN_PLACE = False
        self.mock_canvas.wait_for_click.return_value = [50, 290]
        result = self.game.start()
        self.assertEqual(result, 'Exit')

    @patch.object(paddle_game.PaddleGame, 'get_random_direction', return_value=1)
    def test_colliders_wall_bounce(self, mock_dir):
        self.game.ball = 'ball_id'
        self.game.change_x = 1
        self.game.change_y = 1
        
        self.mock_canvas.get_left_x.return_value = 0 # Out of bounds
        self.mock_canvas.get_top_y.return_value = 50
        
        result = self.game.colliders()
        self.assertFalse(result)
        self.assertEqual(self.game.change_x, -1) 

    def test_colliders_score_player2(self):
        self.game.ball = 'ball_id'
        self.game.change_x = 1
        self.game.change_y = -1
        
        self.mock_canvas.get_left_x.return_value = 50
        self.mock_canvas.get_top_y.return_value = -10
        self.mock_canvas.find_overlapping.return_value = []
        
        result = self.game.colliders()
        self.assertTrue(result)
        self.assertEqual(self.game.score[0], 1)
        self.mock_canvas.delete.assert_called_with('ball_id')
        
    def test_colliders_paddle_bounce(self):
        self.game.ball = 'ball_id'
        self.game.change_x = 1
        self.game.change_y = 1
        
        self.mock_canvas.get_left_x.return_value = 50
        self.mock_canvas.get_top_y.return_value = 50
        
        self.game.items['paddle_1']['object_id'] = 'paddle_1_id'
        self.mock_canvas.find_overlapping.return_value = ['paddle_1_id']
        
        result = self.game.colliders()
        self.assertFalse(result)
        self.assertEqual(self.game.change_y, -1)
        
    @patch('time.sleep')
    @patch.object(paddle_game.PaddleGame, 'colliders', return_value=True) 
    @patch.object(paddle_game.PaddleGame, 'move_paddle_keys')
    @patch.object(paddle_game.PaddleGame, 'move_paddle_mouse')
    @patch.object(paddle_game.PaddleGame, 'create_ball')
    @patch.object(paddle_game.PaddleGame, 'create_play_screen')
    def test_play_loop_termination(self, mock_screen, mock_ball, mock_mouse, mock_keys, mock_colliders, mock_sleep):
        self.game.RUN_IN_CODE_IN_PLACE = False
        
        score = self.game.play(1)
        self.assertEqual(score, [0, 0])
        mock_ball.assert_called_once()
        self.mock_canvas.clear.assert_called_once()

if __name__ == '__main__':
    unittest.main()
