import google.generativeai as genai
from ai_coach.logic import recommend_plan

genai.configure(api_key="YOUR_GEMINI_API_KEY")

model = genai.GenerativeModel("gemini-pro")

SYSTEM_PROMPT = """
Bạn là huấn luyện viên gym cá nhân chuyên nghiệp.
- Kiến thức khoa học thể hình
- Tư vấn ăn uống, tập luyện, thực phẩm chức năng
- Trả lời rõ ràng, thực tế, không lan man
- Luôn hướng tới an toàn và hiệu quả
"""

def ai_coach_chat(user_message, user_data=None):
    context = ""

    if user_data:
        plan = recommend_plan(**user_data)
        context = f"""
        Thông tin người tập:
        - BMI: {plan['bmi']}
        - TDEE: {plan['tdee']}
        - Mục tiêu: {user_data['goal']}
        - Lịch tập gợi ý: {plan['workout_plan']}
        """

    prompt = f"""
    {SYSTEM_PROMPT}

    {context}

    Người dùng hỏi:
    "{user_message}"

    Hãy trả lời như huấn luyện viên gym chuyên nghiệp.
    """

    response = model.generate_content(prompt)
    return response.text
