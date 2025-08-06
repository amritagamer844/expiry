from flask import Flask, render_template, jsonify
import openai
from datetime import datetime

app = Flask(__name__)

# Set OpenAI API key
openai.api_key = "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"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/bill-projection')
def bill_projection():
    return render_template('bill_projection.html', datetime=datetime)

@app.route('/nutritional-analysis')
def nutritional_analysis():
    return render_template('nutritional_analysis.html')

@app.route('/food-donation')
def food_donation():
    return render_template('food_donation.html')

@app.route('/api/generate-recipe', methods=['POST'])
def generate_recipe():
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": """You are a professional nutritionist and chef. Generate a healthy recipe that is:
                1. Nutritionally balanced
                2. Easy to prepare
                3. Uses common ingredients
                4. Includes detailed nutritional information
                
                Format the recipe with:
                - Title
                - List of ingredients with quantities
                - Step-by-step instructions
                - Nutritional information per serving (calories, protein, carbs, fats, fiber)
                - Storage and meal prep tips"""
            }, {
                "role": "user",
                "content": "Generate a healthy recipe that aligns with Indian dietary preferences and uses locally available ingredients."
            }]
        )
        
        recipe = response.choices[0].message.content
        return jsonify({"recipe": recipe})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 