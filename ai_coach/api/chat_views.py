from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

# ===== SIMPLE CONVERSATION STATE (IN-MEMORY) =====
# key = session_key, value = context dict
USER_CONTEXT = {}

class AIChatAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        message = request.data.get("message", "").lower().strip()

        # Lấy context cũ
        context = USER_CONTEXT.get(session_key, {
            "goal": None,      # tăng cơ / giảm mỡ
            "topic": None      # ăn / tập / supplement
        })

        reply = ""

        # ===== XÁC ĐỊNH MỤC TIÊU =====
        if "tăng cơ" in message or "tăng cân" in message:
            context["goal"] = "tăng cơ"
            reply = (
                "🏋️ **Mục tiêu: Tăng cơ (lean bulk)**\n\n"
                "Bạn muốn mình tư vấn:\n"
                "👉 **Thực đơn**\n"
                "👉 **Lịch tập**\n"
                "👉 **Thực phẩm chức năng**"
            )

        elif "giảm mỡ" in message or "giảm cân" in message:
            context["goal"] = "giảm mỡ"
            reply = (
                "🔥 **Mục tiêu: Giảm mỡ – giữ cơ**\n\n"
                "Bạn muốn mình tư vấn:\n"
                "👉 **Thực đơn**\n"
                "👉 **Lịch tập**\n"
                "👉 **Thực phẩm chức năng**"
            )

        # ===== XÁC ĐỊNH CHỦ ĐỀ =====
        elif "thực đơn" in message or "ăn" in message:
            context["topic"] = "ăn"

            if context["goal"] == "tăng cơ":
                reply = (
                    "🍽️ **Thực đơn mẫu tăng cơ (1 ngày)**\n\n"
                    "🥣 Sáng: Yến mạch + sữa + 2 trứng\n"
                    "🍚 Trưa: Cơm + ức gà / bò + rau\n"
                    "🥤 Xế: Whey + chuối\n"
                    "🐟 Tối: Cá hồi / thịt nạc + khoai lang\n\n"
                    "👉 Muốn mình **tính theo cân nặng** không?"
                )

            elif context["goal"] == "giảm mỡ":
                reply = (
                    "🥗 **Thực đơn mẫu giảm mỡ (1 ngày)**\n\n"
                    "🍳 Sáng: Trứng + bánh mì đen\n"
                    "🍚 Trưa: Cơm ít + ức gà + rau\n"
                    "🥛 Xế: Sữa chua Hy Lạp\n"
                    "🐟 Tối: Cá / thịt nạc + salad\n\n"
                    "👉 Muốn **low-carb hay balanced**?"
                )

            else:
                reply = "❗ Trước tiên cho mình biết mục tiêu: **tăng cơ hay giảm mỡ**?"

        elif "lịch tập" in message or "tập" in message:
            context["topic"] = "tập"

            if context["goal"] == "tăng cơ":
                reply = (
                    "📅 **Lịch tập tăng cơ (5 buổi/tuần)**\n\n"
                    "• Day 1: Push (Ngực – Vai – Tay sau)\n"
                    "• Day 2: Pull (Lưng – Tay trước)\n"
                    "• Day 3: Legs (Chân – Mông)\n"
                    "• Day 4: Nghỉ / Cardio nhẹ\n"
                    "• Day 5: Upper body\n\n"
                    "👉 Bạn tập **phòng gym hay tại nhà**?"
                )

            elif context["goal"] == "giảm mỡ":
                reply = (
                    "🔥 **Lịch tập giảm mỡ – giữ cơ**\n\n"
                    "• 3–4 buổi tạ / tuần\n"
                    "• 2–3 buổi cardio (HIIT / chạy)\n"
                    "• Nghỉ ít nhất 1 ngày\n\n"
                    "👉 Bạn muốn **HIIT hay cardio nhẹ**?"
                )

            else:
                reply = "❗ Bạn đang muốn **tăng cơ hay giảm mỡ**?"

        elif "whey" in message or "tp chức năng" in message or "supplement" in message:
            context["topic"] = "supplement"

            reply = (
                "💊 **Supplement nên dùng**\n\n"
                "✔ Whey Protein\n"
                "✔ Creatine Monohydrate\n"
                "✔ Omega-3\n"
                "✔ Multivitamin\n\n"
                "👉 Muốn mình **đề xuất sản phẩm trong shop** không?"
            )

        else:
            reply = (
                "🤖 **AI Coach – HLV gym cá nhân**\n\n"
                "Bạn có thể hỏi:\n"
                "• Tăng cơ / giảm mỡ\n"
                "• Thực đơn\n"
                "• Lịch tập\n"
                "• Thực phẩm chức năng"
            )

        # Lưu context
        USER_CONTEXT[session_key] = context

        return Response({"reply": reply})
