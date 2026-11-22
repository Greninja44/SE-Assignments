# Name: Adarsh D | SRN: PES2UG24AM010
# Hypothesis fuzz tests: each function is given random text (and None) and must
# never crash. When it returns a value, the value must also make sense; invalid
# input is signalled by returning None.
import datetime
import math
import re

import pytest
from hypothesis import given, strategies as st
from processor import parse_season_pass_validity, compute_trail_gradient, calculate_lift_access_tier

EXPIRY_FORMAT = re.compile(r"Pass Expiry: (\d{4})-(\d{2})-(\d{2}) \((VALID|EXPIRED)\)")


def check_parse_season_pass_validity(s):
    try:
        result = parse_season_pass_validity(s)
    except Exception as e:
        assert False, f"parse_season_pass_validity crashed with: {e!r}"
    # either rejected, or a real calendar date with the right VALID / EXPIRED label
    if result is not None:
        match = EXPIRY_FORMAT.fullmatch(result)
        assert match, f"unexpected output format: {result!r}"
        year, month, day = int(match[1]), int(match[2]), int(match[3])
        datetime.date(year, month, day)          # raises if the date does not exist
        assert (match[4] == "VALID") == (year >= 2026)


def check_compute_trail_gradient(s):
    try:
        result = compute_trail_gradient(s)
    except Exception as e:
        assert False, f"compute_trail_gradient crashed with: {e!r}"
    # either rejected, or an ordinary finite, non-negative percentage
    if result is not None:
        assert isinstance(result, float) and math.isfinite(result) and result >= 0


def check_calculate_lift_access_tier(s):
    try:
        result = calculate_lift_access_tier(s)
    except Exception as e:
        assert False, f"calculate_lift_access_tier crashed with: {e!r}"
    # either rejected, or one of the four published prices
    if result is not None:
        assert result in (35.0, 60.0, 85.0, 110.0)


@given(st.text() | st.none())
def test_parse_season_pass_validity_no_crash(s):
    check_parse_season_pass_validity(s)


@given(st.text() | st.none())
def test_compute_trail_gradient_safe(s):
    check_compute_trail_gradient(s)


@given(st.text() | st.none())
def test_calculate_lift_access_tier_safe(s):
    check_calculate_lift_access_tier(s)


# ---------- known awkward inputs, kept as fixed regression cases ----------
@pytest.mark.parametrize("s", [
    "2026/13/45",       # month and day out of range
    "2026/02/30",       # day that does not exist in that month
    "2026/12",          # missing day
    "2026-12-15",       # wrong separator
    "-5/1/1",           # negative year
    "2026/1_2/15",      # int() accepts underscores
])
def test_parse_season_pass_validity_known_bad_inputs(s):
    check_parse_season_pass_validity(s)


@pytest.mark.parametrize("s", [
    "250:0",            # zero distance
    "250:-100",         # negative distance
    "-50:100",          # negative drop
    "nan:1",            # float() accepts these
    "inf:1",
    "1e999:1",
    "250",              # no colon
    "1:2:3",            # too many colons
])
def test_compute_trail_gradient_known_bad_inputs(s):
    check_compute_trail_gradient(s)


@pytest.mark.parametrize("s", [
    "",                 # empty zone code
    "XYZ",              # unknown zone
    "BEGXYZ",           # starts with a real code but is not one
    "\u0131nt",         # dotless i upper-cases to a plain I
])
def test_calculate_lift_access_tier_known_bad_inputs(s):
    check_calculate_lift_access_tier(s)


# ---------- fuzzing with valid-looking input: the answers must be right ----------
@given(st.dates(min_value=datetime.date(1, 1, 1), max_value=datetime.date(9999, 12, 31)))
def test_every_real_date_is_accepted_with_the_right_label(d):
    result = parse_season_pass_validity(f"{d.year:04d}/{d.month}/{d.day}")
    label = "VALID" if d.year >= 2026 else "EXPIRED"
    assert result == f"Pass Expiry: {d.year:04d}-{d.month:02d}-{d.day:02d} ({label})"


@given(st.integers(min_value=0, max_value=10 ** 6), st.integers(min_value=1, max_value=10 ** 6))
def test_gradient_of_whole_numbers_is_drop_over_distance(drop, distance):
    assert compute_trail_gradient(f"{drop}:{distance}") == round(drop / distance * 100.0, 2)


@given(st.sampled_from(["BEG", "INT", "ADV", "ALL"]), st.booleans())
def test_zone_code_case_and_spaces_do_not_matter(code, lower):
    text = f"  {code.lower() if lower else code}  "
    assert calculate_lift_access_tier(text) == calculate_lift_access_tier(code)


# ---------- the fixes must not reject good input ----------
def test_parse_season_pass_validity_valid():
    assert parse_season_pass_validity("2026/12/15") == "Pass Expiry: 2026-12-15 (VALID)"
    assert parse_season_pass_validity("2025/1/5") == "Pass Expiry: 2025-01-05 (EXPIRED)"
    assert parse_season_pass_validity(" 2028 / 02 / 29 ") == "Pass Expiry: 2028-02-29 (VALID)"


def test_compute_trail_gradient_valid():
    assert compute_trail_gradient("250:1000") == 25.0
    assert compute_trail_gradient("100:300") == 33.33
    assert compute_trail_gradient(" 12.5 : 50 ") == 25.0
    assert compute_trail_gradient("0:500") == 0.0


def test_calculate_lift_access_tier_valid():
    assert calculate_lift_access_tier("BEG") == 35.0
    assert calculate_lift_access_tier("int") == 60.0
    assert calculate_lift_access_tier(" Adv ") == 85.0
    assert calculate_lift_access_tier("ALL") == 110.0
    assert calculate_lift_access_tier("Beginner") == 35.0


def test_invalid_input_is_rejected_with_none():
    assert parse_season_pass_validity("2027/02/29") is None      # 2027 is not a leap year
    assert parse_season_pass_validity("2026/12/15/1") is None
    assert parse_season_pass_validity("2026/1_2/15") is None      # int() would accept the underscore
    assert compute_trail_gradient("250:0") is None
    assert compute_trail_gradient("a:b") is None
    assert calculate_lift_access_tier("XYZ") is None
    assert calculate_lift_access_tier("BEGXYZ") is None           # only the first 3 letters used to be checked
    assert calculate_lift_access_tier("\u0131nt") is None          # dotless i upper-cases to a plain I
    assert calculate_lift_access_tier(None) is None
