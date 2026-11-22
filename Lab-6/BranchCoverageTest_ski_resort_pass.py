# Name: Adarsh D | SRN: PES2UG24AM010
# Test cases to reach 90%+ branch coverage of ski_resort_pass.py (every decision taken both ways,
# plus the boundary values on either side of each comparison)
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


def test_dict_instead_of_list_is_rejected():
    with pytest.raises(ValueError):
        process_resort_bookings({"is_active": True}, 15.0)


def test_negative_facility_fee_rejected():
    with pytest.raises(ValueError):
        process_resort_bookings([group([skier(30)])], -1.0)


def test_zero_facility_fee_is_allowed():
    result = process_resort_bookings([group([skier(30)], locker=True)], 0.0)
    assert result == {"total_revenue": 80.0, "status": "COMPLETED"}


def test_empty_group_list_is_valid_and_has_no_sales():
    assert process_resort_bookings([], 15.0) == {"total_revenue": 0.0, "status": "ZERO_SALES"}


# ---------- groups: active, inactive and missing keys ----------
def test_inactive_group_is_skipped():
    result = process_resort_bookings([group([skier(30)], active=False)], 15.0)
    assert result == {"total_revenue": 0.0, "status": "ZERO_SALES"}


def test_group_without_is_active_defaults_to_inactive():
    result = process_resort_bookings([{"duration": "full_day", "skiers": [skier(30)]}], 15.0)
    assert result["status"] == "ZERO_SALES"


def test_group_without_duration_defaults_to_full_day():
    result = process_resort_bookings([{"is_active": True, "skiers": [skier(30)]}], 15.0)
    assert result["total_revenue"] == 80.0


def test_group_without_skiers_sells_nothing():
    result = process_resort_bookings([{"is_active": True, "duration": "season"}], 15.0)
    assert result == {"total_revenue": 0.0, "status": "ZERO_SALES"}


def test_group_without_skiers_still_pays_locker_fee():
    result = process_resort_bookings([group([], locker=True)], 15.0)
    assert result == {"total_revenue": 15.0, "status": "COMPLETED"}


# ---------- pass types ----------
def test_season_pass_rate():
    result = process_resort_bookings([group([skier(30)], duration="season")], 15.0)
    assert result["total_revenue"] == 300.0


def test_half_day_pass_rate():
    result = process_resort_bookings([group([skier(30)], duration="half_day")], 15.0)
    assert result["total_revenue"] == 50.0


def test_unknown_duration_is_rejected():
    result = process_resort_bookings([group([skier(30)], duration="weekend")], 15.0)
    assert result == {"total_revenue": 0.0, "status": "ZERO_SALES"}


def test_empty_string_duration_is_rejected():
    result = process_resort_bookings([group([skier(30)], duration="")], 15.0)
    assert result["status"] == "ZERO_SALES"


@pytest.mark.parametrize("duration, adult, child, senior", [
    ("season", 300.0, 180.0, 210.0),
    ("full_day", 80.0, 48.0, 56.0),
    ("half_day", 50.0, 30.0, 35.0),
])
def test_each_pass_type_for_each_age_category(duration, adult, child, senior):
    for age, expected in ((30, adult), (8, child), (70, senior)):
        result = process_resort_bookings([group([skier(age)], duration=duration)], 15.0)
        assert result["total_revenue"] == expected


# ---------- age categories and their boundaries ----------
@pytest.mark.parametrize("age, expected", [
    (1, 48.0),     # youngest valid age, child rate
    (11, 48.0),    # last child age
    (12, 80.0),    # first adult age
    (64, 80.0),    # last adult age
    (65, 56.0),    # first senior age
    (100, 56.0),
])
def test_age_boundaries_on_full_day(age, expected):
    assert process_resort_bookings([group([skier(age)])], 15.0)["total_revenue"] == expected


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


def test_negative_age_is_rejected():
    result = process_resort_bookings([group([skier(-5)])], 15.0)
    assert result["status"] == "ZERO_SALES"


def test_skier_without_age_is_rejected():
    result = process_resort_bookings([group([{"gear_rental": True}])], 15.0)
    assert result["status"] == "ZERO_SALES"


# ---------- blackout override ----------
def test_blackout_override_pays_half_on_full_day():
    # 80 * 0.50 = 40
    result = process_resort_bookings([group([skier(30, blackout=True)])], 15.0)
    assert result == {"total_revenue": 40.0, "status": "COMPLETED"}


def test_blackout_override_on_season_pass_pays_half():
    result = process_resort_bookings([group([skier(30, blackout=True)], duration="season")], 15.0)
    assert result["total_revenue"] == 150.0


def test_blackout_override_on_half_day_voids_the_group():
    # adult 50, then the blackout skier resets the group total to 0
    result = process_resort_bookings(
        [group([skier(30), skier(30, blackout=True)], duration="half_day")], 15.0)
    assert result == {"total_revenue": 0.0, "status": "ZERO_SALES"}


def test_half_day_blackout_stops_the_remaining_skiers_in_that_group():
    skiers = [skier(30, blackout=True), skier(30), skier(30)]
    result = process_resort_bookings([group(skiers, duration="half_day")], 15.0)
    assert result["total_revenue"] == 0.0


def test_half_day_blackout_only_voids_its_own_group():
    groups = [
        group([skier(30), skier(30, blackout=True)], duration="half_day"),
        group([skier(30)]),
    ]
    result = process_resort_bookings(groups, 15.0)
    assert result == {"total_revenue": 80.0, "status": "COMPLETED"}


def test_half_day_blackout_group_still_pays_locker_fee():
    skiers = [skier(30), skier(30, blackout=True)]
    result = process_resort_bookings([group(skiers, duration="half_day", locker=True)], 15.0)
    assert result == {"total_revenue": 15.0, "status": "COMPLETED"}


# ---------- gear rental on and off ----------
def test_gear_rental_adds_35():
    # 80 + 35 = 115
    result = process_resort_bookings([group([skier(30, gear=True)])], 15.0)
    assert result["total_revenue"] == 115.0


def test_gear_rental_on_a_child():
    assert process_resort_bookings([group([skier(8, gear=True)])], 15.0)["total_revenue"] == 83.0


def test_gear_rental_on_a_senior():
    assert process_resort_bookings([group([skier(70, gear=True)])], 15.0)["total_revenue"] == 91.0


def test_gear_rental_on_a_full_day_blackout_skier_is_still_charged():
    # 40 + 35 = 75
    result = process_resort_bookings([group([skier(30, gear=True, blackout=True)])], 15.0)
    assert result["total_revenue"] == 75.0


def test_half_day_blackout_skips_gear_rental_and_voids_the_group():
    skiers = [skier(30, gear=True), skier(30, gear=True, blackout=True)]
    result = process_resort_bookings([group(skiers, duration="half_day")], 15.0)
    assert result["total_revenue"] == 0.0


# ---------- locker fee and several groups ----------
def test_lodge_locker_adds_facility_fee():
    # 80 + 15 = 95
    result = process_resort_bookings([group([skier(30)], locker=True)], 15.0)
    assert result["total_revenue"] == 95.0


def test_locker_fee_is_charged_once_per_group_not_per_skier():
    result = process_resort_bookings([group([skier(30), skier(30)], locker=True)], 15.0)
    assert result["total_revenue"] == 175.0


def test_locker_fee_on_every_group_that_asks_for_it():
    groups = [group([skier(30)], locker=True), group([skier(30)]), group([skier(30)], locker=True)]
    assert process_resort_bookings(groups, 15.0)["total_revenue"] == 270.0


def test_inactive_group_does_not_pay_locker_fee():
    result = process_resort_bookings([group([skier(30)], locker=True, active=False)], 15.0)
    assert result["status"] == "ZERO_SALES"


def test_unknown_duration_group_does_not_pay_locker_fee():
    result = process_resort_bookings([group([skier(30)], duration="weekend", locker=True)], 15.0)
    assert result["total_revenue"] == 0.0


def test_revenue_is_summed_over_active_groups_only():
    groups = [group([skier(30)]), group([skier(30)], active=False), group([skier(8)], duration="half_day")]
    assert process_resort_bookings(groups, 15.0)["total_revenue"] == 110.0


def test_revenue_is_rounded_to_two_decimals():
    result = process_resort_bookings([group([skier(30)], locker=True)], 0.333)
    assert result["total_revenue"] == 80.33


# ---------- the audit threshold: 4 rejected is fine, 5 is not ----------
def test_four_rejected_passes_is_not_an_audit():
    skiers = [skier(0)] * 4 + [skier(30)]
    assert process_resort_bookings([group(skiers)], 15.0)["status"] == "COMPLETED"


def test_five_rejected_passes_is_an_audit():
    skiers = [skier(0)] * 5 + [skier(30)]
    assert process_resort_bookings([group(skiers)], 15.0) == {"total_revenue": 80.0, "status": "AUDIT_REVIEW"}


def test_audit_review_beats_zero_sales():
    result = process_resort_bookings([group([skier(0)] * 5)], 15.0)
    assert result == {"total_revenue": 0.0, "status": "AUDIT_REVIEW"}


def test_rejections_are_counted_across_groups():
    groups = [group([skier(0)] * 2), group([skier(30)], duration="weekend"), group([skier(30, blackout=True)] * 2)]
    assert process_resort_bookings(groups, 15.0)["status"] == "AUDIT_REVIEW"


def test_blackout_overrides_count_as_rejected_passes():
    groups = [group([skier(30, blackout=True)] * 5)]
    result = process_resort_bookings(groups, 15.0)
    assert result == {"total_revenue": 200.0, "status": "AUDIT_REVIEW"}


def test_inactive_groups_do_not_count_towards_the_audit():
    groups = [group([skier(0)] * 10, active=False), group([skier(30)])]
    assert process_resort_bookings(groups, 15.0)["status"] == "COMPLETED"


# ---------- check_chairlift_anemometer ----------
def test_no_wind_data():
    assert check_chairlift_anemometer([]) == "NO_DATA"


def test_none_streams_count_as_no_data():
    assert check_chairlift_anemometer(None) == "NO_DATA"


def test_two_gusts_in_a_row_suspend_the_lift():
    assert check_chairlift_anemometer([[10, 50, 60]]) == "SUSPEND_LIFT"


def test_calm_wind_is_safe():
    assert check_chairlift_anemometer([[10, 20, 30]]) == "SAFE_OPERATION"


def test_gust_exactly_at_the_limit_is_not_a_gust():
    assert check_chairlift_anemometer([[45, 45, 45]]) == "SAFE_OPERATION"


def test_one_mph_over_the_limit_twice_suspends_the_lift():
    assert check_chairlift_anemometer([[46, 46]]) == "SUSPEND_LIFT"


def test_single_gust_is_safe():
    assert check_chairlift_anemometer([[10, 80, 10]]) == "SAFE_OPERATION"


def test_a_single_reading_over_the_limit_is_safe():
    assert check_chairlift_anemometer([[90]]) == "SAFE_OPERATION"


def test_calm_reading_resets_the_gust_streak():
    assert check_chairlift_anemometer([[50, 10, 50, 10, 50]]) == "SAFE_OPERATION"


def test_streak_starts_again_after_a_calm_reading():
    assert check_chairlift_anemometer([[50, 10, 50, 60]]) == "SUSPEND_LIFT"


def test_gusts_on_different_lifts_do_not_add_up():
    assert check_chairlift_anemometer([[10, 50], [50, 10]]) == "SAFE_OPERATION"


def test_a_later_lift_can_suspend_operation():
    assert check_chairlift_anemometer([[10, 20], [60, 70]]) == "SUSPEND_LIFT"


def test_a_lift_with_no_readings_is_skipped():
    assert check_chairlift_anemometer([[], [10, 20]]) == "SAFE_OPERATION"


def test_all_lifts_empty_is_safe():
    assert check_chairlift_anemometer([[], []]) == "SAFE_OPERATION"


def test_streak_at_the_very_start_of_the_readings():
    assert check_chairlift_anemometer([[50, 50, 10, 10]]) == "SUSPEND_LIFT"
