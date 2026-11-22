import unittest
from collections import defaultdict

import pygame

from game.helicopter import Helicopter, MAX_SPEED
from game.renderer import HEIGHT


def keys(up=False, down=False):
    pressed = defaultdict(bool)
    pressed[pygame.K_UP] = up
    pressed[pygame.K_DOWN] = down
    return pressed


class TestHelicopterMovement(unittest.TestCase):
    def setUp(self):
        self.heli = Helicopter(x=100, y=HEIGHT / 2)

    def test_speed_is_capped_going_up(self):
        for _ in range(500):
            self.heli.handle_input(keys(up=True))
        self.assertEqual(self.heli.vy, -MAX_SPEED)

    def test_speed_is_capped_going_down(self):
        for _ in range(500):
            self.heli.handle_input(keys(down=True))
        self.assertEqual(self.heli.vy, MAX_SPEED)

    def test_reverses_immediately_after_long_up_hold(self):
        for _ in range(200):
            self.heli.handle_input(keys(up=True))
        self.heli.handle_input(keys(down=True))
        self.assertGreater(self.heli.vy, 0)

    def test_reverses_immediately_after_long_down_hold(self):
        for _ in range(200):
            self.heli.handle_input(keys(down=True))
        self.heli.handle_input(keys(up=True))
        self.assertLess(self.heli.vy, 0)

    def test_still_speeds_up_while_held(self):
        self.heli.handle_input(keys(up=True))
        first = abs(self.heli.vy)
        self.heli.handle_input(keys(up=True))
        self.assertGreater(abs(self.heli.vy), first)

    def test_slows_down_when_keys_released(self):
        for _ in range(50):
            self.heli.handle_input(keys(down=True))
        for _ in range(60):
            self.heli.handle_input(keys())
        self.assertLess(abs(self.heli.vy), 0.01)

    def test_never_leaves_screen_at_the_bottom(self):
        for _ in range(2000):
            self.heli.handle_input(keys(down=True))
            self.heli.update(HEIGHT)
            self.assertLessEqual(self.heli.get_rect().bottom, HEIGHT)
        self.assertEqual(self.heli.get_rect().bottom, HEIGHT)

    def test_never_leaves_screen_at_the_top(self):
        for _ in range(2000):
            self.heli.handle_input(keys(up=True))
            self.heli.update(HEIGHT)
            self.assertGreaterEqual(self.heli.get_rect().top, 0)
        self.assertEqual(self.heli.get_rect().top, 0)

    def test_can_move_away_from_the_edge_again(self):
        for _ in range(300):
            self.heli.handle_input(keys(down=True))
            self.heli.update(HEIGHT)
        self.heli.handle_input(keys(up=True))
        self.heli.update(HEIGHT)
        self.assertLess(self.heli.get_rect().bottom, HEIGHT)


if __name__ == "__main__":
    unittest.main()
