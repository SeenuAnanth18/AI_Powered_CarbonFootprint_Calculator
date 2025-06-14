from flask import Flask, render_template, request
from groq import Groq  # Groq client
import os

app = Flask(__name__)

# Set your Groq API key
client = Groq(api_key="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")

def get_ai_advice(data):
    prompt = f"""Give personalized tips to reduce carbon emissions for:
- Travel: {data['travel']} km/day
- Electricity: {data['electricity']} kWh/month
- Diet: {data['diet']}
- Shopping: {data['shopping']} items/month

Return 1 actionable tip per category (Travel, Electricity, Diet, Shopping)."""

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",  # Supported Groq model
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI Tip Error: {e}"


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/calculate", methods=["POST"])
def calculate():
    try:
        km_per_day = float(request.form["km_per_day"])
        electricity = float(request.form["electricity"])
        diet = request.form["diet"]
        shopping = int(request.form["shopping"])
        time_period = request.form["time_period"]

        # Monthly emissions calculation (for Travel, Electricity, Diet, Shopping)
        travel_monthly = km_per_day * 30 * 0.2
        electricity_monthly = electricity * 0.5
        diet_monthly = {"veg": 100, "mixed": 200, "nonveg": 300}[diet]
        shopping_monthly = shopping * 25

        breakdown = {
            "Travel": travel_monthly,
            "Electricity": electricity_monthly,
            "Diet": diet_monthly,
            "Shopping": shopping_monthly
        }

        # Adjust breakdown based on selected time period
        if time_period == "one_day":
            factor = 1 / 30  # Convert to daily values
        elif time_period == "one_week":
            factor = 1 / 4  # Convert to weekly values
        else:
            factor = 1  # Use monthly values directly

        converted = {k: round(v * factor, 2) for k, v in breakdown.items()}
        total = round(sum(converted.values()), 2)

        user_data = {
            "travel": km_per_day,
            "electricity": electricity,
            "diet": diet,
            "shopping": shopping
        }

        tips = get_ai_advice(user_data)

        return render_template("result.html", breakdown=converted, total=total, tips=tips, time_period=time_period)
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    app.run(debug=True)
