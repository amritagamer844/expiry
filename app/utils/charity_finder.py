import requests

def find_nearby_charities(latitude, longitude, radius=5000):
    """Find nearby old age homes and food donation centers"""
    try:
        # Use Overpass API to find relevant locations
        overpass_url = "http://overpass-api.de/api/interpreter"
        
        # Query for old age homes, food banks, and charitable organizations
        overpass_query = f"""
        [out:json][timeout:25];
        (
          node["social_facility"="nursing_home"](around:{radius},{latitude},{longitude});
          node["amenity"="social_facility"]["social_facility"="food_bank"](around:{radius},{latitude},{longitude});
          node["social_facility"="shelter"](around:{radius},{latitude},{longitude});
          node["amenity"="social_centre"](around:{radius},{latitude},{longitude});
        );
        out body;
        >;
        out skel qt;
        """
        
        response = requests.get(overpass_url, params={'data': overpass_query})
        data = response.json()
        
        charities = []
        for element in data.get('elements', []):
            if element.get('type') == 'node':
                tags = element.get('tags', {})
                name = tags.get('name', 'Unnamed Facility')
                facility_type = tags.get('social_facility', tags.get('amenity', 'Unknown'))
                
                charity = {
                    'name': name,
                    'type': facility_type.replace('_', ' ').title(),
                    'latitude': element.get('lat'),
                    'longitude': element.get('lon'),
                    'address': tags.get('addr:full', 'Address not available'),
                    'phone': tags.get('phone', 'Phone not available'),
                    'website': tags.get('website', '')
                }
                charities.append(charity)
        
        return charities
    except Exception as e:
        print(f"Error finding charities: {str(e)}")
        return [] 