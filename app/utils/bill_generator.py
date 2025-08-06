import google.generativeai as genai
import os
from flask import current_app
import requests
import json
from datetime import datetime
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import re

# Configure the Gemini API
def configure_gemini():
    api_key = current_app.config.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY not configured in application settings")
    genai.configure(api_key=api_key)

# System prompt for the nutritionist persona
NUTRITIONIST_SYSTEM_PROMPT = """
You are an expert Indian nutritionist and meal planning specialist who provides detailed, personalized dietary recommendations.
Your task is to analyze the user's current food inventory and provide specific recommendations for a balanced Indian diet.
All prices should be in Indian Rupees (₹).

Instructions for recommendations:

1. Protein Sources (Weekly Requirements):
   - Pulses and Legumes:
     Toor Dal (2 kg) - ₹240

2. Fresh Vegetables (Weekly):
   - Leafy Greens:
     Spinach/Palak (2 bunches) - ₹40
     Methi (1 bunch) - ₹20
   - Regular Vegetables:
     Tomatoes (1 kg) - ₹40
     Onions (1 kg) - ₹30
     Mixed Vegetables (2 kg) - ₹120
     Bell Peppers (500g) - ₹60

3. Fruits (Weekly):
   - Seasonal Indian Fruits:
     Apples (1 kg) - ₹160
     Bananas (12 pieces) - ₹60
     Oranges (1 kg) - ₹80
     Pomegranate (500g) - ₹100

4. Whole Grains:
   - Staples:
     Brown Rice (2 kg) - ₹160
     Whole Wheat Atta (5 kg) - ₹250
     Oats (1 kg) - ₹180
     Quinoa (500g) - ₹200

5. Healthy Fats:
   - Nuts and Seeds:
     Mixed Nuts (500g) - ₹400
     Flax Seeds (100g) - ₹60
     Chia Seeds (100g) - ₹120
   - Oils:
     Cold Pressed Coconut Oil (500ml) - ₹250
     Extra Virgin Olive Oil (500ml) - ₹450

6. Indian Spices and Seasonings:
   - Essential Spices:
     Turmeric Powder (100g) - ₹40
     Garam Masala (100g) - ₹60
     Cumin Seeds (100g) - ₹40
     Coriander Powder (100g) - ₹40

For each recommended item, include:
- Brand recommendations (e.g., Tata, Fortune, 24 Mantra Organic)
- Quantity for weekly purchase
- Storage tips specific to Indian climate
- Nutritional benefits with focus on Indian dietary needs
- Recipe suggestions for Indian meals

Format the recommendations section clearly using the following structure for each item:
[Item Name] ([Quantity]) - ₹[Price]
Nutritional benefits: [List benefits]
Storage tips: [Provide tips]

Example:
Toor Dal (2 kg) - ₹240
Nutritional benefits: High protein, good source of fiber
Storage tips: Store in an airtight container in a cool, dry place.

Include a weekly Indian meal planning suggestion based on the recommendations.
"""

def initialize_chat():
    """Initialize and return a Gemini chat instance with appropriate settings"""
    # Configure the model
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.8,
        "top_k": 40,
        "max_output_tokens": 2048,
    }

    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }

    # Initialize the model
    model = genai.GenerativeModel(
        model_name="gemini-pro",
        generation_config=generation_config,
        safety_settings=safety_settings
    )

    # Start a chat
    chat = model.start_chat(history=[])
    return chat

def get_product_price_from_openfood(product_name):
    """Fetch product price from Open Food Facts API"""
    try:
        # Clean the product name for search
        search_term = product_name.lower().replace(' ', '+')
        
        # Make API request to Open Food Facts
        url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={search_term}&search_simple=1&action=process&json=1"
        response = requests.get(url)
        data = response.json()
        
        if data.get('products') and len(data['products']) > 0:
            # Get the first product match
            product = data['products'][0]
            
            # Try to get price information
            # Note: Open Food Facts might not always have price data
            # We'll return None if no price is found
            if 'price' in product:
                return float(product['price'])
            elif 'price_100g' in product:
                return float(product['price_100g']) * 10  # Convert to per kg
        
        return None
    except Exception as e:
        print(f"Error fetching price for {product_name}: {str(e)}")
        return None

def update_item_prices(food_items):
    """Update prices for food items using Open Food Facts data"""
    updated_items = []
    for item in food_items:
        if not hasattr(item, 'price') or item.price is None:
            price = get_product_price_from_openfood(item.product_name)
            if price:
                item.price = price
        updated_items.append(item)
    return updated_items

def generate_recommendations(current_items):
    """Generate personalized food recommendations using Gemini model"""
    try:
        # Initialize chat
        chat = initialize_chat()

        # Create a more detailed prompt that analyzes current items
        current_items_str = "\n".join([f"- {item['name']} ({item['quantity']})" for item in current_items])
        
        prompt = f"""As an expert Indian nutritionist, analyze the following current food inventory:

{current_items_str}

Based on this inventory, provide 5-7 personalized recommendations that:
1. Complement existing items
2. Fill nutritional gaps
3. Consider Indian dietary preferences
4. Account for seasonal availability
5. Optimize for budget and nutrition

For each recommendation, provide:
1. Item name and weekly quantity
2. Price in ₹ (based on current Indian market rates)
3. Specific nutritional benefits that complement the existing inventory
4. Storage tips for Indian climate
5. Brief explanation of why this item is recommended

Format each recommendation exactly as:
* Item Name (Quantity) - ₹Price
Benefits: [List specific nutritional benefits and why it complements current inventory]
Storage: [Provide detailed storage tips]

Consider these factors:
- Balance between proteins, carbs, and healthy fats
- Seasonal availability and freshness
- Common Indian cooking requirements
- Budget-friendly options
- Local availability
- Nutritional completeness
"""

        # Get response from Gemini
        response = chat.send_message(prompt)
        recommendations_text = response.text

        # Parse the recommendations
        recommendations = []
        current_item = {}
        
        for line in recommendations_text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('*'):
                # Save previous item if exists
                if current_item:
                    recommendations.append(current_item)
                    current_item = {}
                
                # Parse item, quantity, and price
                match = re.match(r'\*\s+(.+?)\s*\((.*?)\)\s*-\s*₹(\d+(\.\d{1,2})?)', line)
                if match:
                    name, quantity, price = match.groups()[:3]
                    current_item = {
                        'name': name.strip(),
                        'quantity': quantity.strip(),
                        'price': float(price),
                        'benefits': '',
                        'storage': ''
                    }
            elif 'Benefits:' in line:
                current_item['benefits'] = line.split('Benefits:')[1].strip()
            elif 'Storage:' in line:
                current_item['storage'] = line.split('Storage:')[1].strip()
        
        # Add the last item
        if current_item:
            recommendations.append(current_item)

        # Add seasonal recommendations based on current month
        month = datetime.now().month
        season = ""
        seasonal_items = []
        
        if 3 <= month <= 6:  # Summer
            season = "summer"
            seasonal_items = [
                {
                    'name': 'Watermelon',
                    'quantity': '1 medium',
                    'price': 50.0,
                    'benefits': 'Natural hydration, rich in antioxidants, perfect for summer',
                    'storage': 'Keep whole at room temperature until cut, then refrigerate'
                },
                {
                    'name': 'Mango',
                    'quantity': '500g',
                    'price': 100.0,
                    'benefits': 'Rich in Vitamins A and C, good source of fiber',
                    'storage': 'Ripen at room temperature, then refrigerate'
                }
            ]
        elif 7 <= month <= 10:  # Monsoon
            season = "monsoon"
            seasonal_items = [
                {
                    'name': 'Corn',
                    'quantity': '2 pieces',
                    'price': 40.0,
                    'benefits': 'Good source of fiber and antioxidants, suitable for monsoon',
                    'storage': 'Keep in cool, dry place with husk on'
                },
                {
                    'name': 'Ginger',
                    'quantity': '100g',
                    'price': 30.0,
                    'benefits': 'Immunity booster, anti-inflammatory properties',
                    'storage': 'Store in a dry, cool place or refrigerate'
                }
            ]
        else:  # Winter
            season = "winter"
            seasonal_items = [
                {
                    'name': 'Sweet Potato',
                    'quantity': '500g',
                    'price': 40.0,
                    'benefits': 'Rich in beta-carotene and fiber, perfect for winter',
                    'storage': 'Store in a cool, dark place'
                },
                {
                    'name': 'Carrots',
                    'quantity': '500g',
                    'price': 35.0,
                    'benefits': 'High in Vitamin A and antioxidants',
                    'storage': 'Refrigerate in a plastic bag'
                }
            ]

        # Get additional seasonal recommendations from Gemini
        seasonal_prompt = f"""Based on the current {season} season in India, suggest 2-3 additional seasonal items that would complement the existing recommendations. Consider local availability and traditional Indian dietary practices for {season}.

Format each recommendation as before:
* Item Name (Quantity) - ₹Price
Benefits: [Seasonal benefits]
Storage: [Storage tips]"""

        seasonal_response = chat.send_message(seasonal_prompt)
        
        # Parse and add seasonal recommendations
        current_item = {}
        for line in seasonal_response.text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('*'):
                if current_item:
                    seasonal_items.append(current_item)
                    current_item = {}
                
                match = re.match(r'\*\s+(.+?)\s*\((.*?)\)\s*-\s*₹(\d+(\.\d{1,2})?)', line)
                if match:
                    name, quantity, price = match.groups()[:3]
                    current_item = {
                        'name': name.strip(),
                        'quantity': quantity.strip(),
                        'price': float(price),
                        'benefits': '',
                        'storage': ''
                    }
            elif 'Benefits:' in line:
                current_item['benefits'] = line.split('Benefits:')[1].strip()
            elif 'Storage:' in line:
                current_item['storage'] = line.split('Storage:')[1].strip()
        
        if current_item:
            seasonal_items.append(current_item)
        
        # Combine all recommendations
        recommendations.extend(seasonal_items)
        
        return recommendations

    except Exception as e:
        print(f"Error generating recommendations: {str(e)}")
        # Return default recommendations if Gemini fails
        return [
            {
                'name': 'Rice',
                'quantity': '1kg',
                'price': 60.0,
                'benefits': 'Essential carbohydrate source, provides energy',
                'storage': 'Store in airtight container in a cool, dry place'
            },
            {
                'name': 'Dal',
                'quantity': '500g',
                'price': 80.0,
                'benefits': 'High protein content, rich in fiber',
                'storage': 'Keep in airtight container away from moisture'
            },
            {
                'name': 'Mixed Vegetables',
                'quantity': '1kg',
                'price': 100.0,
                'benefits': 'Various vitamins and minerals, balanced nutrition',
                'storage': 'Refrigerate in crisper drawer'
            },
            {
                'name': 'Milk',
                'quantity': '1L',
                'price': 65.0,
                'benefits': 'Calcium and protein source',
                'storage': 'Keep refrigerated at 4°C'
            },
            {
                'name': 'Eggs',
                'quantity': '12 pieces',
                'price': 90.0,
                'benefits': 'Complete protein source, vitamin D',
                'storage': 'Refrigerate, avoid storing in door'
            }
        ]
