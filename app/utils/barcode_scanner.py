from PIL import Image
import io
import re
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from flask import current_app

def extract_barcode(image_file):
    """
    Extract barcode from image using multiple methods for better accuracy.
    """
    try:
        # Method 1: Use pyzbar library for direct barcode detection
        image_bytes = image_file.read()
        image_file.seek(0)  # Reset file pointer for reuse
        
        # Convert to OpenCV format
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Try different preprocessing techniques to improve barcode detection
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply different thresholds to handle various image qualities
        thresholds = [
            cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1],
            cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        ]
        
        # Try to decode with different preprocessed images
        for thresh in thresholds:
            barcodes = decode(thresh)
            if barcodes:
                for barcode in barcodes:
                    barcode_data = barcode.data.decode('utf-8')
                    if re.match(r'^\d{8,14}$', barcode_data):  # Valid barcode formats are 8-14 digits
                        return barcode_data
        
        # If pyzbar fails, try with original image
        barcodes = decode(img)
        if barcodes:
            for barcode in barcodes:
                barcode_data = barcode.data.decode('utf-8')
                if re.match(r'^\d{8,14}$', barcode_data):
                    return barcode_data
        
        # Method 2: Use Azure Computer Vision API as backup
        subscription_key = current_app.config['AZURE_VISION_KEY']
        endpoint = current_app.config['AZURE_VISION_ENDPOINT']
        
        # Authenticate client
        client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))
        
        # Read image content
        image_file.seek(0)  # Reset file pointer
        image_content = image_file.read()
        
        # Call API with image content to detect text
        detected_text = client.recognize_printed_text_in_stream(io.BytesIO(image_content))
        
        # Extract text from response
        extracted_text = ""
        for region in detected_text.regions:
            for line in region.lines:
                for word in line.words:
                    extracted_text += word.text + " "
        
        # Look for barcode patterns (EAN-13, UPC-A, etc.)
        barcode_patterns = [
            r'\b\d{13}\b',  # EAN-13
            r'\b\d{12}\b',  # UPC-A
            r'\b\d{8}\b',   # EAN-8
            r'\b\d{14}\b',  # GTIN-14
        ]
        
        for pattern in barcode_patterns:
            matches = re.findall(pattern, extracted_text)
            if matches:
                return matches[0]
        
        # If no barcode pattern found, try to use OCR to detect digits that might be a barcode
        digits_only = re.sub(r'\D', '', extracted_text)
        if len(digits_only) >= 8:  # Minimum barcode length
            # Extract potential barcode segments of appropriate lengths
            for length in [13, 12, 14, 8]:
                if len(digits_only) >= length:
                    return digits_only[:length]
        
        return None
    
    except Exception as e:
        print(f"Error in barcode extraction: {str(e)}")
        return None
