def calculate_bmi(height_cm, weight_kg):
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 2)


def calculate_bmr(gender, height_cm, weight_kg, age):
    """
    Harris-Benedict Equation
    """
    if gender == "male":
        return round(
            88.36 + (13.4 * weight_kg) + (4.8 * height_cm) - (5.7 * age), 2
        )
    else:
        return round(
            447.6 + (9.2 * weight_kg) + (3.1 * height_cm) - (4.3 * age), 2
        )


def calculate_tdee(bmr, activity_level):
    activity_multiplier = {
        "low": 1.2,
        "medium": 1.55,
        "high": 1.75
    }
    return round(bmr * activity_multiplier.get(activity_level, 1.2), 2)
