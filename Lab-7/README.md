# Lab 7: Fuzzing for Input Validation Bugs

Hypothesis fuzz tests for `processor.py` (pass expiry dates, trail gradients, lift zone codes), and the fixes they led to.
Assigned repo: `L6_L7_08_ski_resort_pass`.

| File | Description |
|------|-------------|
| `processor_original.py` | The original buggy module (provided), kept for reference |
| `processor.py` | Fixed module: invalid input returns `None` instead of crashing |
| `test_processor.py` | Fuzz tests (one per function), regression cases and valid-input checks |
| `PES2UG24AM010_AdarshD_LAB7.pdf` | Screenshots SS1-SS4 and notes on the bugs and fixes |
| `screenshots/` | SS1 buggy run, SS2 tests failing, SS3 fixed run, SS4 tests passing |

```
python processor.py
pytest test_processor.py
```
