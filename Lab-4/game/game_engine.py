"""
GameEngine: owns the helicopter and all obstacles.

The helicopter moves, obstacles scroll by, and touching either wall of
an obstacle ends the game. Press R after a game over to start again.
The distance flown is the score: it grows every frame while playing and
is reset by a new game.
Press SPACE to raise the shield: it absorbs exactly one obstacle hit,
switches off, and needs SHIELD_COOLDOWN_FRAMES before it can be raised
again.
"""

import random

import pygame

from game.helicopter import Helicopter
from game.obstacle import Obstacle
from game.renderer import WIDTH, HEIGHT

SPAWN_INTERVAL_FRAMES = 90
GAP_HEIGHT = 150
WALL_WIDTH = 60
SCROLL_SPEED = 3
PIXELS_PER_METER = 10
SHIELD_COOLDOWN_FRAMES = 300


class GameEngine:
    def __init__(self):
        self.helicopter = Helicopter(x=100, y=HEIGHT / 2)
        self.obstacles = []
        self.frames_until_spawn = 0
        self.game_over = False
        self.distance = 0.0     # in pixels scrolled
        self.shield_active = False
        self.shield_cooldown = 0    # frames until the shield can be raised again

    @property
    def score(self):
        return int(self.distance / PIXELS_PER_METER)

    def _spawn_obstacle(self):
        margin = 60
        gap_y = random.randint(margin + GAP_HEIGHT // 2, HEIGHT - margin - GAP_HEIGHT // 2)
        self.obstacles.append(Obstacle(
            x=WIDTH, gap_y=gap_y, gap_height=GAP_HEIGHT,
            wall_width=WALL_WIDTH, screen_height=HEIGHT, speed=SCROLL_SPEED,
        ))

    def handle_input(self, keys_pressed):
        self.helicopter.handle_input(keys_pressed)

    def handle_keydown(self, key):
        if key == pygame.K_r and self.game_over:
            self.reset()
        elif key == pygame.K_SPACE:
            self.activate_shield()

    def activate_shield(self):
        if self.game_over or self.shield_active or self.shield_cooldown > 0:
            return
        self.shield_active = True

    def reset(self):
        self.__init__()

    def _hit_obstacle(self):
        """The first obstacle being touched that has not already hit the shield."""
        heli_rect = self.helicopter.get_rect()
        for obstacle in self.obstacles:
            if obstacle.shield_hit:
                continue
            if heli_rect.colliderect(obstacle.get_top_rect()) or heli_rect.colliderect(obstacle.get_bottom_rect()):
                return obstacle
        return None

    def _handle_collision(self):
        obstacle = self._hit_obstacle()
        if obstacle is None:
            return
        if self.shield_active:
            self.shield_active = False
            self.shield_cooldown = SHIELD_COOLDOWN_FRAMES
            obstacle.shield_hit = True      # one hit per obstacle, even while still overlapping it
        else:
            self.game_over = True

    def update(self):
        if self.game_over:
            return

        self.helicopter.update(HEIGHT)

        self.frames_until_spawn -= 1
        if self.frames_until_spawn <= 0:
            self._spawn_obstacle()
            self.frames_until_spawn = SPAWN_INTERVAL_FRAMES

        for obstacle in self.obstacles:
            obstacle.update()
        self.obstacles = [o for o in self.obstacles if not o.is_off_screen()]
        self.distance += SCROLL_SPEED

        if self.shield_cooldown > 0:
            self.shield_cooldown -= 1
        self._handle_collision()

    def _shield_status(self):
        if self.shield_active:
            return "Shield: ACTIVE"
        if self.shield_cooldown > 0:
            seconds = -(-self.shield_cooldown // 60)
            return f"Shield: recharging ({seconds}s)"
        return "Shield: ready (SPACE)"

    def draw(self, surface, font):
        from game import renderer
        renderer.draw_scene(surface, self.helicopter, self.obstacles, self.shield_active)
        renderer.draw_text(surface, font, f"Distance: {self.score} m", (10, 10))
        renderer.draw_text(surface, font, self._shield_status(), (10, 38))
        if self.game_over:
            renderer.draw_banner(surface, font, f"GAME OVER - final distance {self.score} m")
            renderer.draw_text(surface, font, "Press R to restart", (270, 280))
