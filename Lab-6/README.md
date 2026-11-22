# Lab 6: Code and Branch Coverage

Tests for `ski_resort_pass.py` (resort pass pricing and chairlift wind audit).
Assigned repo: `L6_L7_08_ski_resort_pass`.

| File | Description |
|------|-------------|
| `ski_resort_pass.py` | Module under test (provided) |
| `test_ski_resort.py` | Starter tests (47% line / 44% branch coverage) |
| `CodeCoverageTest_ski_resort_pass.py` | 18 tests, 100% line coverage |
| `BranchCoverageTest_ski_resort_pass.py` | 68 tests, 100% branch coverage (42 of 42 branches) |
| `PES2UG24AM010_AdarshD_LAB6.pdf` | Report |
| `screenshots/` | Terminal output after reaching the coverage targets |

```
coverage run -m pytest CodeCoverageTest_ski_resort_pass.py
coverage report -m

coverage run --branch -m pytest BranchCoverageTest_ski_resort_pass.py
coverage report -m
```
