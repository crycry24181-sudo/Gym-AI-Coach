def coach_reply(message, ai_data):
    msg = message.lower()

    bmi = ai_data.get("bmi")
    goal = ai_data.get("goal")

    # =========================
    # TĂNG CÂN / TĂNG CƠ
    # =========================
    if "tăng cân" in msg or "ăn gì" in msg and goal == "tăng cơ":
        if bmi and bmi < 18.5:
            return (
                "🏋️ **Mục tiêu: Tăng cân – Tăng cơ**\n\n"
                "Bạn đang hơi gầy, vì vậy cần **ăn dư calo + tập tạ**.\n\n"
                "🍽 **Cách ăn đúng:**\n"
                "• 5–6 bữa/ngày\n"
                "• Ưu tiên tinh bột + protein\n\n"
                "🥩 **Nên ăn:**\n"
                "- Cơm, mì, khoai lang\n"
                "- Thịt bò, ức gà, trứng\n"
                "- Sữa, chuối, bơ đậu phộng\n\n"
                "💊 **Gợi ý TPCN:**\n"
                "- Whey Protein (sau tập)\n"
                "- Mass Gainer (nếu ăn yếu)\n\n"
                "👉 Muốn tôi **lập thực đơn 1 ngày** không?"
            )

        return (
            "🏋️ **Tăng cân là tăng cơ, không phải tăng mỡ.**\n\n"
            "🍽 Ăn dư ~300–500 kcal/ngày\n"
            "🥩 Protein: 1.8–2.2g/kg cân nặng\n"
            "🏋️ Tập tạ 4–5 buổi/tuần\n\n"
            "👉 Bạn muốn **lịch tập hay thực đơn**?"
        )

    # =========================
    # TẬP LUYỆN
    # =========================
    if "tập" in msg or "lịch tập" in msg:
        return (
            "🏋️ **Lịch tập đề xuất cho tăng cơ:**\n\n"
            "• Thứ 2: Ngực – Tay sau\n"
            "• Thứ 3: Lưng – Tay trước\n"
            "• Thứ 4: Nghỉ / Cardio nhẹ\n"
            "• Thứ 5: Chân – Mông\n"
            "• Thứ 6: Vai – Bụng\n\n"
            "👉 Bạn muốn **chi tiết từng bài tập** không?"
        )

    # =========================
    # MẶC ĐỊNH
    # =========================
    return (
        "🤖 **AI Coach – Huấn luyện viên gym cá nhân**\n\n"
        "Tôi có thể giúp bạn:\n"
        "• Lập lịch tập theo mục tiêu\n"
        "• Tư vấn ăn uống tăng cơ / giảm mỡ\n"
        "• Gợi ý thực phẩm chức năng phù hợp\n\n"
        "👉 Hãy nói rõ mục tiêu của bạn."
    )
