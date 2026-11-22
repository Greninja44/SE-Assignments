# Name: Adarsh D | SRN: PES2UG24AM010
# Test cases to reach 90%+ line (code) coverage of ski_resort_pass.py
import pytest
from ski_resort_pass import process_resort_bookings, check_chairlift_anemometer


def group(skiers, duration="full_day", locker=False, active=True):
    return {
        "is_active": active,
        "duration": duration,
        "includes_lodge_locker": locker,
        "skiers": skiers,
    }


def skier(age=30, gear=False, blackout=False):
    return {"age": age, "gear_rental": gear, "blackout_override": blackout}


# ---------- process_resort_bookings ----------
def test_single_adult_full_day():
    result = process_resort_bookings([group([skier(30)])], 15.0)
    assert result == {"total_revenue": 80.0, "status": "COMPLETED"}


def test_groups_must_be_a_list():
    with pytest.raises(ValueError):
        process_resort_bookings("not a list", 15.0)


def test_negative_facility_fee_rejected():
    with pytest.raises(ValueError):
        process_resort_bookings([group([skier(30)])], -1.0)


def test_inactive_group_is_skipped():
    result = process_resort_bookings([group([skier(30)], active=False)], 15.0)
    assert result == {"total_revenue": 0.0, "status": "ZERO_SALES"}


def test_season_pass_rate():
    result = process_resort_bookings([group([skier(30)], duration="season")], 15.0)
    assert result["total_revenue"] == 300.0


def test_half_day_pass_rate():
    result = process_resort_bookings([group([skier(30)], duration="half_day")], 15.0)
    assert result["total_revenue"] == 50.0


def test_unknown_duration_is_rejected():
    result = process_resort_bookings([group([skier(30)], duration="weekend")], 15.0)
    assert result == {"total_revenue": 0.0, "status": "ZERO_SALES"}


def test_child_pays_sixty_percent():
    # 80 * 0.60 = 48
    result = process_resort_bookings([group([skier(8)])], 15.0)
    assert result["total_revenue"] == 48.0


def test_senior_pays_seventy_percent():
    # 80 * 0.70 = 56
    result = process_resort_bookings([group([skier(70)])], 15.0)
    assert result["total_revenue"] == 56.0


def test_invalid_age_is_rejected_and_not_charged():
    result = process_resort_bookings([group([skier(0, gear=True)])], 15.0)
    assert result == {"total_revenue": 0.0, "status": "ZERO_SALES"}


def test_blackout_override_pays_half_on_full_day():
    # 80 * 0.50 = 40
    result = process_resort_bookings([group([skier(30, blackout=True)])], 15.0)
    assert result == {"total_revenue": 40.0, "status": "COMPLETED"}


def test_blackout_override_on_half_day_voids_the_group():
    # adult 50, then the blackout skier resets the group total to 0
    result = process_resort_bookings(
        [group([skier(30), skier(30, blackout=True)], duration="half_day")], 15.0)
    assert result == {"total_revenue": 0.0, "status": "ZERO_SALES"}


def test_gear_rental_adds_35():
    # 80 + 35 = 115
    result = process_resort_bookings([group([skier(30, gear=True)])], 15.0)
    assert result["total_revenue"] == 115.0


def test_lodge_locker_adds_facility_fee():
    # 80 + 15 = 95
    result = process_resort_bookings([group([skier(30)], locker=True)], 15.0)
    assert result["total_revenue"] == 95.0


def test_more_than_four_rejections_triggers_audit_review():
    skiers = [skier(0)] * 5 + [skier(30)]
    result = process_resort_bookings([group(skiers)], 15.0)
    assert result == {"total_revenue": 80.0, "status": "AUDIT_REVIEW"}


# ---------- check_chairlift_anemometer ----------
def test_no_wind_data():
    assert check_chairlift_anemometer([]) == "NO_DATA"


def test_two_gusts_in_a_row_suspend_the_lift():
    assert check_chairlift_anemometer([[10, 50, 60]]) == "SUSPEND_LIFT"


def test_calm_wind_is_safe():
    assert check_chairlift_anemometer([[10, 20, 30]]) == "SAFE_OPERATION"
