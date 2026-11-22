# SE Assignments

Adarsh D - PES2UG24AM010

Software Engineering lab submissions.

| Folder | Lab | What's inside |
|---|---|---|
| `Lab-4` | Vibe Coding | Updated code for the Helicopter game (`08_helicopter`) with tests and before/after clips |
| `Lab-6` | Code and Branch Coverage | Line and branch coverage tests for `ski_resort_pass.py`, screenshots and report |
| `Lab-7` | Fuzz Testing | Hypothesis fuzz tests, fixed `processor.py`, screenshots SS1-SS4 and report |

`SE-Lab-Concepts_PES2UG24AM010.pdf` has notes explaining the concepts behind each lab.

## Running the tests

```
pip install pytest coverage hypothesis pygame

cd Lab-6
coverage run --branch -m pytest BranchCoverageTest_ski_resort_pass.py
coverage report -m

cd ../Lab-7
pytest test_processor.py

cd ../Lab-4
python -m unittest
```
