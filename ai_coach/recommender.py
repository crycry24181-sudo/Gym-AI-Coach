def recommend_workout_and_supplements(bmi, goal):
    plan = {}

    # ===== WORKOUT =====
    if goal == "tăng cơ":
        if bmi < 18.5:
            plan["workout"] = "Full body 4 buổi/tuần (ưu tiên compound)"
        else:
            plan["workout"] = "Push Pull Legs 5–6 buổi/tuần"

    elif goal == "giảm mỡ":
        plan["workout"] = "Full body + Cardio 4–5 buổi/tuần"

    else:
        plan["workout"] = "Tập duy trì 3–4 buổi/tuần"

    # ===== SUPPLEMENTS =====
    supplements = []

    if goal == "tăng cơ":
        supplements.append("Whey Protein – hỗ trợ phục hồi & phát triển cơ")
        supplements.append("Creatine – tăng sức mạnh & hiệu suất")

    if goal == "giảm mỡ":
        supplements.append("L-Carnitine – hỗ trợ đốt mỡ")
        supplements.append("CLA – kiểm soát mỡ cơ thể")

    supplements.append("Multivitamin – bổ sung vi chất")

    plan["supplements"] = supplements

    return plan
