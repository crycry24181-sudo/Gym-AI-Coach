def bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"


def calorie_by_goal(tdee, goal):
    if goal == "gain_muscle":
        return round(tdee + 300, 2)
    elif goal == "lose_weight":
        return round(tdee - 500, 2)
    else:
        return round(tdee, 2)
