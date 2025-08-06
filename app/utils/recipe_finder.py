import requests
from flask import current_app
import logging

def get_recipes(ingredient):
    """
    Fetch recipes that can be made with the given ingredient using the Spoonacular API.
    """
    if not ingredient or ingredient == "Unknown Product":
        return {"error": "No valid product name provided"}
    
    # Get API key from configuration
    api_key = current_app.config.get('RECIPE_API_KEY')
    if not api_key:
        return {"error": "Recipe API key not configured"}
    
    # Clean up the ingredient name
    clean_ingredient = ingredient.split('-')[0].strip()
    clean_ingredient = clean_ingredient.split(',')[0].strip()
    
    # Log what we're searching for
    logging.info(f"Searching recipes for ingredient: {clean_ingredient}")
    
    # Try multiple search strategies
    search_terms = [
        clean_ingredient,  # Try full name first
        clean_ingredient.split(' ')[0] if ' ' in clean_ingredient else None,  # Try first word
        "potato" if "chips" in clean_ingredient.lower() else None,  # Special case for chips
        "snack" if "chips" in clean_ingredient.lower() else None    # Another fallback
    ]
    
    # Filter out None values
    search_terms = [term for term in search_terms if term]
    
    # Using Spoonacular API
    base_url = "https://api.spoonacular.com/recipes/findByIngredients"
    
    all_recipes = []
    
    # Try each search term until we find recipes
    for term in search_terms:
        params = {
            "apiKey": api_key,
            "ingredients": term,
            "number": 5,
            "ranking": 1,
            "ignorePantry": True
        }
        
        try:
            logging.info(f"Making API request with term: {term}")
            response = requests.get(base_url, params=params)
            
            # Log the response for debugging
            logging.info(f"API response status: {response.status_code}")
            
            if response.status_code == 200:
                recipes = response.json()
                
                if recipes:
                    # Format the recipe data
                    formatted_recipes = []
                    for recipe in recipes:
                        formatted_recipes.append({
                            "id": recipe.get("id"),
                            "title": recipe.get("title"),
                            "image": recipe.get("image"),
                            "usedIngredientCount": recipe.get("usedIngredientCount", 0),
                            "missedIngredientCount": recipe.get("missedIngredientCount", 0),
                            "likes": recipe.get("likes", 0)
                        })
                    
                    all_recipes.extend(formatted_recipes)
                    
                    # If we found at least 3 recipes, stop searching
                    if len(all_recipes) >= 3:
                        break
            
            elif response.status_code == 401 or response.status_code == 403:
                return {"error": "API key invalid or quota exceeded"}
            
            elif response.status_code == 404:
                logging.info(f"No recipes found for term: {term}")
                continue
                
        except Exception as e:
            logging.error(f"Error in recipe API request: {str(e)}")
            continue
    
    # If we found any recipes, return them
    if all_recipes:
        return all_recipes
    
    # If all searches failed, try a direct recipe search instead of ingredient search
    try:
        search_url = "https://api.spoonacular.com/recipes/complexSearch"
        params = {
            "apiKey": api_key,
            "query": clean_ingredient,
            "number": 5
        }
        
        response = requests.get(search_url, params=params)
        
        if response.status_code == 200:
            search_results = response.json()
            
            if "results" in search_results and search_results["results"]:
                formatted_recipes = []
                for recipe in search_results["results"]:
                    formatted_recipes.append({
                        "id": recipe.get("id"),
                        "title": recipe.get("title"),
                        "image": recipe.get("image"),
                        "usedIngredientCount": 1,  # Default value
                        "missedIngredientCount": 0,  # Default value
                        "likes": recipe.get("likes", 0)
                    })
                
                return formatted_recipes
    
    except Exception as e:
        logging.error(f"Error in recipe search API request: {str(e)}")
    
    # If all attempts failed
    return {"error": "No recipes found for this product. Try a different search term."}
