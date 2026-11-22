# Name: Adarsh D | SRN: PES2UG24AM010
# Fixed version: every function checks its input and returns None when it is
# invalid, instead of crashing or returning a wrong value.
import calendar
import math
import re

DIGITS = "0123456789"
# a plain decimal number such as 250 or 12.5 (no sign, no exponent, no nan/inf)
_NUMBER_RE = re.compile(r"[0-9]+(?:\.[0-9]+)?")

ZONE_RATES = {
    "BEG": 35.0,
    "INT": 60.0,
    "ADV": 85.0,
    "ALL": 110.0,
}
ZONE_NAMES = {
    "BEGINNER": "BEG",
    "INTERMEDIATE": "INT",
    "ADVANCED": "ADV",
}


def _plain_digits(text, min_len, max_len):
    """True for 1-2 (or 4) plain 0-9 digits; int() would also accept 1_0, +5 and non-English digits."""
    return min_len <= len(text) <= max_len and all(c in DIGITS for c in text)


def parse_season_pass_validity(date_str):
    """
    Reads a pass expiry date written YYYY/MM/DD (e.g. '2026/12/15') and returns
    'Pass Expiry: 2026-12-15 (VALID)', or None if it is not a real calendar date.
    A pass is VALID when its expiry year is 2026 or later, otherwise EXPIRED.
    """
    if not isinstance(date_str, str):
        return None
    parts = [p.strip() for p in date_str.split('/')]
    if len(parts) != 3:
        return None
    year_text, month_text, day_text = parts
    if not (_plain_digits(year_text, 4, 4) and _plain_digits(month_text, 1, 2)
            and _plain_digits(day_text, 1, 2)):
        return None
    year, month, day = int(year_text), int(month_text), int(day_text)
    if year < 1 or not 1 <= month <= 12:
        return None
    if not 1 <= day <= calendar.monthrange(year, month)[1]:
        return None
    return f"Pass Expiry: {year:04d}-{month:02d}-{day:02d} ({'VALID' if year >= 2026 else 'EXPIRED'})"


def compute_trail_gradient(elevation_str):
    """
    Reads 'drop:distance' (e.g. '250:1000') and returns the gradient as a
    percentage (25.0), or None if either number is missing, malformed,
    negative, or the distance is zero.
    """
    if not isinstance(elevation_str, str):
        return None
    parts = [p.strip() for p in elevation_str.split(':')]
    if len(parts) != 2:
        return None
    drop_str, dist_str = parts
    if not (_NUMBER_RE.fullmatch(drop_str) and _NUMBER_RE.fullmatch(dist_str)):
        return None
    drop = float(drop_str)
    distance = float(dist_str)
    if not (math.isfinite(drop) and math.isfinite(distance)) or distance <= 0:
        return None
    gradient_pct = (drop / distance) * 100.0
    if not math.isfinite(gradient_pct):
        return None
    return round(gradient_pct, 2)


def calculate_lift_access_tier(zone_code):
    """
    Reads a zone code (BEG, INT, ADV, ALL) or its full name (e.g. Beginner),
    ignoring case and surrounding spaces, and returns the lift pass price,
    or None if the zone is not one of the four.
    """
    if not isinstance(zone_code, str):
        return None
    code = zone_code.strip()
    if not code.isascii():          # e.g. a dotless i would otherwise upper-case to a plain I
        return None
    code = code.upper()
    code = ZONE_NAMES.get(code, code)
    return ZONE_RATES.get(code)


def main():
    print("==== Running parse_season_pass_validity ====")
    d_input = input("Enter pass expiry (YYYY/MM/DD): ")
    result = parse_season_pass_validity(d_input)
    print(result if result is not None else "Invalid pass expiry: use a real date as YYYY/MM/DD")

    print("\n==== Running compute_trail_gradient ====")
    e_input = input("Enter drop:distance (e.g. 250:1000): ")
    gradient = compute_trail_gradient(e_input)
    if gradient is not None:
        print("Gradient %:", gradient)
    else:
        print("Invalid input: use drop:distance with positive numbers, e.g. 250:1000")

    print("\n==== Running calculate_lift_access_tier ====")
    z_input = input("Enter zone code (e.g. BEG, INT, ALL): ")
    price = calculate_lift_access_tier(z_input)
    if price is not None:
        print("Lift Pass Price: $", price)
    else:
        print("Invalid zone code: use BEG, INT, ADV or ALL")


if __name__ == "__main__":
    main()
