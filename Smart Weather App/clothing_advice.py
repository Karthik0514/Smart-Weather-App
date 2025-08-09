import cohere
from config import COHERE_API_KEY

co = cohere.Client(COHERE_API_KEY)

def get_clothing_advice(temp, condition):
    try:
        prompt = (
            f"Based on the temperature of {temp}°C and weather condition '{condition}', "
            f"give me smart clothing recommendations in 2-3 short sentences."
        )

        response = co.generate(
            model="command-light",  # fast, free, accurate
            prompt=prompt,
            max_tokens=100,
            temperature=0.7
        )

        return response.generations[0].text.strip()

    except Exception as e:
        print("AI Clothing Advice Error:", e)
        return "🤖 Unable to generate AI advice at the moment."
