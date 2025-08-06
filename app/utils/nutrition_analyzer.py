import requests
import json
from flask import current_app

def get_nutritional_info(barcode):
    """
    Fetch nutritional data using the barcode from Open Food Facts API.
    """
    if not barcode or len(barcode) < 8:
        return {"error": "Invalid barcode format"}
    
    # Open Food Facts API URL for the product data in JSON format
    url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
    
    try:
        # Send GET request to fetch data
        response = requests.get(url)
        
        # Check if the response is successful
        if response.status_code == 200:
            product_data = response.json()
            
            # Check if the 'product' field exists
            if "product" in product_data and product_data.get("status") == 1:
                # Extract product name and nutritional information
                product_name = product_data["product"].get("product_name", "N/A")
                nutriments = product_data["product"].get("nutriments", {})
                
                # Create a structured nutrition data dictionary
                nutrition_data = {
                    "product_name": product_name,
                    "barcode": barcode,
                    "energy_kcal": nutriments.get("energy-kcal", "N/A"),
                    "fat": nutriments.get("fat", "N/A"),
                    "saturated_fat": nutriments.get("saturated-fat", "N/A"),
                    "carbohydrates": nutriments.get("carbohydrates", "N/A"),
                    "sugars": nutriments.get("sugars", "N/A"),
                    "fiber": nutriments.get("fiber", "N/A"),
                    "proteins": nutriments.get("proteins", "N/A"),
                    "salt": nutriments.get("salt", "N/A"),
                    "sodium": nutriments.get("sodium", "N/A"),
                    "calcium": nutriments.get("calcium", "N/A"),
                    "iron": nutriments.get("iron", "N/A"),
                    "vitamin_a": nutriments.get("vitamin-a", "N/A"),
                    "vitamin_c": nutriments.get("vitamin-c", "N/A"),
                    "product_image": product_data["product"].get("image_url", "")
                }
                
                return nutrition_data
            else:
                # If product not found in database, create basic info from barcode
                return {
                    "product_name": "Unknown Product",
                    "barcode": barcode,
                    "energy_kcal": "N/A",
                    "fat": "N/A",
                    "carbohydrates": "N/A",
                    "proteins": "N/A",
                    "salt": "N/A",
                    "error": f"Product data not found for barcode {barcode}."
                }
        else:
            return {"error": f"Unable to fetch data for barcode {barcode}. Status code: {response.status_code}"}
    
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
