import random

def get_health_tip(condition, temp):
    condition = condition.lower()

    tips_hot = [
        "💧 Stay hydrated — drink plenty of water today.",
        "🧴 Apply sunscreen if you're heading outdoors.",
        "🧢 Wear a hat and light clothing to avoid heatstroke.",
        "❄️ Stay in the shade or indoors during peak heat hours."
    ]

    tips_cold = [
        "🧣 Dress in layers to stay warm and prevent colds.",
        "🔥 Keep warm drinks handy — great for boosting circulation.",
        "🚶‍♂️ Light exercise can help you stay warm indoors.",
        "🧤 Don't forget gloves and a hat if you're going out."
    ]

    tips_rainy = [
        "☔ Don’t forget your umbrella — stay dry and warm.",
        "🧼 Keep your hands clean to avoid catching colds.",
        "👟 Wear waterproof shoes to avoid slipping or wet socks."
    ]

    tips_clear = [
        "🌞 Take a short walk outside for vitamin D and mood boost.",
        "🕶️ Wear sunglasses to protect your eyes from UV rays.",
        "😊 Enjoy some fresh air — it's great for mental health!"
    ]

    tips_general = [
        "📴 Take breaks from screens to rest your eyes.",
        "🥗 Eat something green today — your body will thank you.",
        "😴 Try to wind down early for better sleep quality.",
        "🧘 Take 5 deep breaths — relax your shoulders."
    ]

    # Decision logic
    if "rain" in condition:
        tips = tips_rainy
    elif "clear" in condition or "sun" in condition:
        tips = tips_clear
    elif "cold" in condition or temp <= 10:
        tips = tips_cold
    elif temp >= 30:
        tips = tips_hot
    else:
        tips = tips_general

    return random.choice(tips)
