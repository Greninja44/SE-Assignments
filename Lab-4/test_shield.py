import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from game.game_engine import SHIELD_COOLDOWN_FRAMES
from game.renderer import HEIGHT
from test_game_engine import make_engine, obstacle_at_helicopter


def deadly_engine():
    return make_engine(gap_y=HEIGHT / 2 + 150)      # the helicopter is inside the top wall


class TestShield(unittest.TestCase):
    def test_shield_starts_off_but_can_be_raised(self):
        engine = make_engine()
        self.assertFalse(engine.shield_active)
        engine.handle_keydown(pygame.K_SPACE)
        self.assertTrue(engine.shield_active)

    def test_shield_absorbs_one_collision(self):
        engine = deadly_engine()
        engine.handle_keydown(pygame.K_SPACE)
        engine.update()
        self.assertFalse(engine.game_over)

    def test_shield_switches_off_when_it_absorbs_a_hit(self):
        engine = deadly_engine()
        engine.handle_keydown(pygame.K_SPACE)
        engine.update()
        self.assertFalse(engine.shield_active)

    def test_flying_on_through_the_same_obstacle_is_safe_after_the_hit(self):
        engine = deadly_engine()
        engine.handle_keydown(pygame.K_SPACE)
        for _ in range(60):
            engine.update()
        self.assertFalse(engine.game_over)

    def test_helicopter_is_vulnerable_again_after_the_hit(self):
        engine = deadly_engine()
        engine.handle_keydown(pygame.K_SPACE)
        engine.update()
        engine.obstacles.append(obstacle_at_helicopter(engine, HEIGHT / 2 + 150))
        engine.update()
        self.assertTrue(engine.game_over)

    def test_unused_shield_stays_active(self):
        engine = make_engine(gap_y=HEIGHT / 2)
        engine.handle_keydown(pygame.K_SPACE)
        for _ in range(30):
            engine.update()
        self.assertTrue(engine.shield_active)

    def test_no_shield_means_no_protection(self):
        engine = deadly_engine()
        engine.update()
        self.assertTrue(engine.game_over)

    def test_cannot_raise_shield_during_cooldown(self):
        engine = deadly_engine()
        engine.handle_keydown(pygame.K_SPACE)
        engine.update()
        engine.handle_keydown(pygame.K_SPACE)
        self.assertFalse(engine.shield_active)

    def test_shield_can_be_raised_again_after_cooldown(self):
        engine = deadly_engine()
        engine.handle_keydown(pygame.K_SPACE)
        engine.update()
        engine.obstacles = []
        for _ in range(SHIELD_COOLDOWN_FRAMES):
            engine.update()
        engine.handle_keydown(pygame.K_SPACE)
        self.assertTrue(engine.shield_active)

    def test_space_after_game_over_does_not_raise_shield(self):
        engine = deadly_engine()
        engine.update()
        engine.handle_keydown(pygame.K_SPACE)
        self.assertFalse(engine.shield_active)

    def test_new_game_resets_shield(self):
        engine = deadly_engine()
        engine.handle_keydown(pygame.K_SPACE)
        engine.update()
        engine.game_over = True
        engine.handle_keydown(pygame.K_r)
        self.assertFalse(engine.shield_active)
        self.assertEqual(engine.shield_cooldown, 0)

    def test_shield_status_text_and_drawing(self):
        pygame.init()
        font = pygame.font.SysFont("consolas", 22)
        surface = pygame.Surface((700, 500))
        engine = make_engine()
        self.assertIn("ready", engine._shield_status())
        engine.handle_keydown(pygame.K_SPACE)
        self.assertIn("ACTIVE", engine._shield_status())
        engine.draw(surface, font)          # draws the shield ring
        engine.shield_active = False
        engine.shield_cooldown = 61
        self.assertIn("recharging (2s)", engine._shield_status())


if __name__ == "__main__":
    unittest.main()
