# Lab 4: Vibe Coding

Updated code for the Helicopter game (`08_helicopter`, scenario 8). The four tasks were done one at a
time, each in its own commit:

| Commit | Task | What changed |
|--------|------|--------------|
| 1 | Movement and boundary bug | Speed was never capped and nothing slowed the helicopter, so reversing took a long time; only the top edge was checked, so it flew off the bottom. Speed is now capped (`MAX_SPEED`), pressing the opposite key reverses at once, speed fades when no key is held, and the helicopter is kept fully on screen at both the top and the bottom. |
| 2 | Obstacle collision and game over | Touching either wall of an obstacle ends the game and shows a game-over message. Flying through the gap never does. Press `R` to start again. |
| 3 | Distance scoring | Distance (in metres) grows every frame while playing, is shown on screen and in the game-over message, and resets to zero on a new game. |
| 4 | Shield | Press `SPACE` to raise a shield. It is drawn as a ring round the helicopter, absorbs exactly one obstacle hit and then switches off. It can be raised again after a 5 second recharge, shown in the status line. |

```
pip install -r requirements.txt
python main.py
python -m unittest
```

**Controls:** Up/Down arrows to move, `SPACE` for the shield, `R` to restart after a game over.

36 unit tests cover the speed cap, reversing, both screen edges, collisions with the top and bottom wall,
flying through the gap, the score, restarting, and the shield (one hit only, one hit per obstacle, recharge,
and reset on a new game).

## Videos

`videos/before.mp4` and `videos/after.mp4` are 10 second clips of the starter code and the finished game. They were
rendered by running the game headlessly with scripted key presses (no screen recording), so they show the same
code and behaviour as `python main.py`: the helicopter flying off the bottom of the screen and through obstacles in
the starter, and the capped movement, score, shield ring, recharge text and game-over message in the final game.
