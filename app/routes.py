from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app import db
from app.models import FoodItem
from app.forms import FoodItemForm
from app.utils.azure_vision import extract_text_from_image
from app.utils.date_parser import extract_expiry_date
from app.utils.barcode_scanner import extract_barcode
from app.utils.nutrition_analyzer import get_nutritional_info
from app.utils.recipe_finder import get_recipes
from app.utils.email_sender import schedule_expiry_alert
from app.utils.bill_generator import generate_recommendations
from datetime import datetime
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
import uuid
import re


main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET', 'POST'])
def index():
    form = FoodItemForm()
    
    if form.validate_on_submit():
        # Process expiry date image
        expiry_date = form.expiry_date.data
        if form.expiry_image.data:
            extracted_text = extract_text_from_image(form.expiry_image.data)
            extracted_date = extract_expiry_date(extracted_text)
            if extracted_date:
                expiry_date = extracted_date
        
        # Process barcode image
        barcode = form.barcode.data
        if form.barcode_image.data:
            extracted_barcode = extract_barcode(form.barcode_image.data)
            if extracted_barcode:
                barcode = extracted_barcode
        
        # Get nutrition data
        nutrition_data = {}
        if barcode:
            nutrition_data = get_nutritional_info(barcode)
        
        # Create new food item
        food_item = FoodItem(
            product_name=form.product_name.data,
            expiry_date=expiry_date,
            barcode=barcode,
            category=form.category.data,
            alert_days=form.alert_days.data,
            email=form.email.data
        )
        
        if nutrition_data:
            food_item.set_nutrition_data(nutrition_data)
        
        db.session.add(food_item)
        db.session.commit()
        
        # Schedule email alert
        schedule_expiry_alert(food_item)
        
        flash('Food item added successfully!', 'success')
        return redirect(url_for('main.saved_items'))
    
    return render_template('index.html', form=form)

@main_bp.route('/saved_items')
def saved_items():
    items = FoodItem.query.order_by(FoodItem.expiry_date).all()
    return render_template('saved_items.html', items=items)

@main_bp.route('/delete_item/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    item = FoodItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted successfully!', 'success')
    return redirect(url_for('main.saved_items'))

@main_bp.route('/get_nutrition/<int:item_id>')
def get_nutrition(item_id):
    item = FoodItem.query.get_or_404(item_id)
    return jsonify(item.get_nutrition_data())

@main_bp.route('/get_recipes/<int:item_id>')
def get_recipes_for_item(item_id):
    item = FoodItem.query.get_or_404(item_id)
    recipes = get_recipes(item.product_name)
    return jsonify(recipes)

@main_bp.route('/get_storage_tips/<category>')
def get_storage_tips(category):
    storage_tips = {
        'Grains': {
            'Pantry': 'Dry grains like rice, oats, and pasta should be in airtight containers in a cool, dry place (below 75°F or 24°C). They can last 6 months to a year (or more if sealed well).',
            'Refrigerator/Freezer': 'Whole grains (e.g., brown rice) can go in the fridge or freezer to extend shelf life up to 6–12 months due to oil content.'
        },
        'Proteins': {
            'Refrigerator': 'Raw meat, fish, and eggs should be stored at 32–40°F (0–4°C). Meat lasts 1–2 days (fish 1 day), eggs 3–5 weeks.',
            'Freezer': 'For longer storage, freeze meat and fish at 0°F (-18°C) for 3–12 months, depending on type.',
            'Pantry': 'Dried legumes and nuts can be kept in airtight containers in a cool, dry place for 6–12 months. Refrigerate nuts if storing longer to prevent rancidity.'
        },
        'Dairy': {
            'Refrigerator': 'Milk, cheese, and yogurt need to be kept at 35–40°F (2–4°C). Milk lasts about a month unopened, cheese 1–6 months depending on type, yogurt 2–3 weeks.',
            'Freezer': 'Hard cheeses and butter can be frozen for 6 months; avoid freezing milk unless for cooking (texture changes).',
            'Note': 'Store on shelves, not the door, for consistent temp.'
        },
        'Fats and Oils': {
            'Pantry': 'Oils (olive, vegetable) and butter can be stored in a cool, dark place for 3–6 months. Unopened, some oils last up to a year.',
            'Refrigerator': 'Nut oils, avocados, and opened butter do better in the fridge—oils for 6 months, avocados 1–2 weeks.',
            'Freezer': 'Nuts and seeds can be frozen for up to a year.'
        },
        'Sweets': {
            'Pantry': 'Candy, chocolate, and dry baked goods (cookies) can be stored in airtight containers in a cool, dry place. Chocolate lasts 6–12 months, candy longer.',
            'Refrigerator': 'Perishable sweets (cakes with cream) need refrigeration at 35–40°F (2–4°C) for 3–7 days.',
            'Freezer': 'Most sweets freeze well for 2–6 months.'
        },
        'Beverages': {
            'Pantry': 'Unopened juice, soda, and alcohol can be stored at room temp for months (check expiration). Coffee and tea in airtight containers last 6–12 months.',
            'Refrigerator': 'Opened juice or perishable drinks (like fresh juice) should be at 35–40°F (2–4°C) for 1–2 weeks.',
            'Freezer': 'Water and some juices can be frozen; avoid freezing carbonated drinks in cans or bottles (they might burst).'
        },
        'Spices and Herbs': {
            'Pantry': 'Dried spices and herbs should be in airtight containers in a cool, dark, dry place (below 75°F or 24°C). Whole spices last 2–4 years, ground 1–3 years.',
            'Refrigerator': 'Fresh herbs (like basil or parsley) can be kept in the fridge with stems in water or wrapped in a damp towel for 1–2 weeks.',
            'Freezer': 'Fresh herbs can be frozen in ice cube trays with water or oil for 6 months.'
        },
        'Processed Foods': {
            'Pantry': 'Canned goods and dry snacks (chips, crackers) store well in a cool, dry place for 6 months to years (check dates). Unopened frozen meals can stay in the pantry if not refrigerated.',
            'Refrigerator': 'Opened cans or perishable processed foods need 35–40°F (2–4°C) for 3–7 days.',
            'Freezer': 'Frozen meals should be kept at 0°F (-18°C) and used within 3–6 months for best quality.'
        }
    }
    
    return jsonify(storage_tips.get(category, {}))

@main_bp.route('/process_expiry_image', methods=['POST'])
def process_expiry_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    image = request.files['image']
    if not image.filename:
        return jsonify({'error': 'No image selected'}), 400
        
    extracted_text = extract_text_from_image(image)
    extracted_date = extract_expiry_date(extracted_text)
    
    if extracted_date:
        return jsonify({
            'success': True,
            'date': extracted_date.strftime('%Y-%m-%d'),
            'expired': extracted_date < datetime.now(),
            'days_remaining': (extracted_date - datetime.now()).days
        })
    else:
        return jsonify({'success': False, 'error': 'Could not extract date'})

@main_bp.route('/process_barcode_image', methods=['POST'])
def process_barcode_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    image = request.files['image']
    if not image.filename:
        return jsonify({'error': 'No image selected'}), 400
        
    barcode = extract_barcode(image)
    
    if barcode:
        nutrition_data = get_nutritional_info(barcode)
        product_name = nutrition_data.get('product_name', '')
        
        return jsonify({
            'success': True,
            'barcode': barcode,
            'product_name': product_name,
            'nutrition_data': nutrition_data
        })
    else:
        return jsonify({'success': False, 'error': 'Could not extract barcode'})

@main_bp.route('/charity_map')
def charity_map():
    azure_maps_key = current_app.config.get('AZURE_MAPS_KEY')
    if not azure_maps_key:
        flash('Azure Maps API key is not configured.', 'danger')
        return redirect(url_for('main.saved_items'))
    
    return render_template('charity_map.html', azure_maps_key=azure_maps_key)

@main_bp.route('/bill-projection')
def bill_projection():
    # Get all saved food items
    items = FoodItem.query.all()
    
    # Convert items to the format expected by generate_recommendations
    current_items = []
    for item in items:
        current_items.append({
            'name': item.product_name,
            'quantity': '1 unit'  # Default quantity, can be updated based on your needs
        })
    
    # Generate recommendations using the Gemini model
    recommendations = generate_recommendations(current_items)
    
    return render_template('bill_projection.html', 
                         items=items,
                         recommendations=recommendations,
                         datetime=datetime)

@main_bp.route('/nutritional-analysis')
def nutritional_analysis():
    return render_template('nutritional_analysis.html')

@main_bp.route('/food-donation')
def food_donation():
    return render_template('food_donation.html')

@main_bp.route('/api/generate-recipe', methods=['POST'])
def generate_recipe():
    try:
        # Your recipe generation code here
        return jsonify({"recipe": "Sample recipe"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

