import os
import unittest
from collections import defaultdict

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from game.game_engine import GameEngine, GAP_HEIGHT, PIXELS_PER_METER, WALL_WIDTH, SCROLL_SPEED
from game.obstacle import Obstacle
from game.renderer import HEIGHT

NO_KEYS = defaultdict(bool)


def obstacle_at_helicopter(engine, gap_y):
    """An obstacle whose walls are exactly over the helicopter."""
    return Obstacle(
        x=engine.helicopter.x - WALL_WIDTH / 2, gap_y=gap_y, gap_height=GAP_HEIGHT,
        wall_width=WALL_WIDTH, screen_height=HEIGHT, speed=SCROLL_SPEED,
    )


def make_engine(gap_y=None):
    """Engine with no random spawns and, optionally, one obstacle on the helicopter."""
    engine = GameEngine()
    engine.frames_until_spawn = 10 ** 9
    if gap_y is not None:
        engine.obstacles = [obstacle_at_helicopter(engine, gap_y)]
    return engine


class TestCollision(unittest.TestCase):
    def test_game_starts_running(self):
        self.assertFalse(GameEngine().game_over)

    def test_touching_the_top_wall_ends_the_game(self):
        engine = make_engine(gap_y=HEIGHT / 2 + 150)     # gap well below the helicopter
        engine.update()
        self.assertTrue(engine.game_over)

    def test_touching_the_bottom_wall_ends_the_game(self):
        engine = make_engine(gap_y=HEIGHT / 2 - 150)     # gap well above the helicopter
        engine.update()
        self.assertTrue(engine.game_over)

    def test_flying_through_the_gap_never_ends_the_game(self):
        for offset in (-GAP_HEIGHT // 2 + 20, -30, 0, 30, GAP_HEIGHT // 2 - 20):
            with self.subTest(offset=offset):
                engine = make_engine(gap_y=HEIGHT / 2 + offset)
                for _ in range(60):
                    engine.update()
                self.assertFalse(engine.game_over)

    def test_obstacle_far_away_is_harmless(self):
        engine = make_engine()
        engine.obstacles = [Obstacle(x=600, gap_y=100, gap_height=GAP_HEIGHT, wall_width=WALL_WIDTH,
                                     screen_height=HEIGHT, speed=0)]
        engine.update()
        self.assertFalse(engine.game_over)

    def test_nothing_moves_after_game_over(self):
        engine = make_engine(gap_y=HEIGHT / 2 + 150)
        engine.update()
        x_before = engine.obstacles[0].x
        engine.update()
        self.assertEqual(engine.obstacles[0].x, x_before)

    def test_game_over_banner_is_drawn(self):
        pygame.init()
        surface = pygame.Surface((700, 500))
        font = pygame.font.SysFont("consolas", 22)
        engine = make_engine(gap_y=HEIGHT / 2 + 150)
        engine.update()
        engine.draw(surface, font)          # must not raise

    def test_r_restarts_after_game_over(self):
        engine = make_engine(gap_y=HEIGHT / 2 + 150)
        engine.update()
        engine.handle_keydown(pygame.K_r)
        self.assertFalse(engine.game_over)
        self.assertEqual(engine.obstacles, [])

    def test_r_does_nothing_while_playing(self):
        engine = make_engine(gap_y=HEIGHT / 2)
        obstacles = engine.obstacles
        engine.handle_keydown(pygame.K_r)
        self.assertIs(engine.obstacles, obstacles)


class TestDistanceScore(unittest.TestCase):
    def test_starts_at_zero(self):
        self.assertEqual(GameEngine().score, 0)

    def test_increases_automatically_while_playing(self):
        engine = make_engine()
        scores = []
        for _ in range(300):
            engine.update()
            scores.append(engine.score)
        self.assertEqual(scores, sorted(scores))
        self.assertGreater(scores[-1], 0)

    def test_distance_matches_scroll_speed(self):
        engine = make_engine()
        for _ in range(100):
            engine.update()
        self.assertEqual(engine.score, 100 * SCROLL_SPEED // PIXELS_PER_METER)

    def test_stops_increasing_after_game_over(self):
        engine = make_engine(gap_y=HEIGHT / 2 + 150)
        engine.update()
        final = engine.distance
        for _ in range(50):
            engine.update()
        self.assertEqual(engine.distance, final)

    def test_final_distance_is_shown_on_game_over(self):
        pygame.init()
        engine = make_engine()
        for _ in range(200):
            engine.update()
        engine.obstacles = [obstacle_at_helicopter(engine, HEIGHT / 2 + 150)]
        engine.update()
        self.assertTrue(engine.game_over)
        shown = []
        font = pygame.font.SysFont("consolas", 22)
        real_render = font.render
        class SpyFont:
            def render(self, text, *a):
                shown.append(text)
                return real_render(text, *a)
        engine.draw(pygame.Surface((700, 500)), SpyFont())
        self.assertTrue(any(str(engine.score) in t and "GAME OVER" in t for t in shown))

    def test_new_game_resets_distance_to_zero(self):
        engine = make_engine()
        for _ in range(200):
            engine.update()
        self.assertGreater(engine.score, 0)
        engine.game_over = True
        engine.handle_keydown(pygame.K_r)
        self.assertEqual(engine.score, 0)
        self.assertEqual(engine.distance, 0)


if __name__ == "__main__":
    unittest.main()
