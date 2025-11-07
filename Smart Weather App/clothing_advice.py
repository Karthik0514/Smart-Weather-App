import cohere
from config import COHERE_API_KEY

co = cohere.Client(COHERE_API_KEY)

def get_clothing_advice(temp, condition):
    try:
        message = (
            f"Based on the temperature of {temp}°C and weather condition '{condition}', "
            f"give me smart clothing recommendations in 2-3 short sentences. "
            f"Be practical and specific about clothing layers and materials."
        )

        response = co.chat(
            model="command-a-03-2025", 
            message=message,
            temperature=0.7
        )

        return response.text.strip()

    except Exception as e:
        print("AI Clothing Advice Error:", e)
        # Fallback to basic advice if API fails
        return generate_basic_advice(temp, condition)

def generate_basic_advice(temp, condition):
    """Fallback function to generate basic clothing advice"""
    try:
        temp = float(temp)
        if "rain" in condition.lower():
            weather_advice = " Don't forget a waterproof jacket or umbrella."
        elif "sun" in condition.lower() or "clear" in condition.lower():
            weather_advice = " Consider sun protection like a hat or sunglasses."
        else:
            weather_advice = ""
            
        if temp >= 30:
            return f"Hot {temp}°C weather! Wear light, breathable fabrics like cotton and linen. Stay hydrated.{weather_advice}"
        elif temp >= 20:
            return f"Warm {temp}°C conditions. T-shirts and light layers work well. You might want a light jacket for breeze.{weather_advice}"
        elif temp >= 10:
            return f"Cool {temp}°C temperatures. Wear layers like sweaters or hoodies. Long pants recommended.{weather_advice}"
        elif temp >= 0:
            return f"Cold {temp}°C weather. Bundle up with a warm coat, scarf, and multiple layers. Warm accessories help.{weather_advice}"
        else:
            return f"Very cold {temp}°C! Heavy winter coat, thermal layers, hat, gloves, and warm boots are essential.{weather_advice}"
            
    except Exception:
        return f"Wear appropriate clothing for {temp}°C and {condition} conditions."