import os
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
from flask import current_app
import time
import io

def extract_text_from_image(image_file):
    # Get credentials from app config
    subscription_key = current_app.config['AZURE_VISION_KEY']
    endpoint = current_app.config['AZURE_VISION_ENDPOINT']
    
    # Authenticate client
    client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))
    
    # Read image content
    image_content = image_file.read()
    
    # Call API with image content
    read_response = client.read_in_stream(io.BytesIO(image_content), raw=True)
    
    # Get the operation location (URL with an ID at the end)
    read_operation_location = read_response.headers["Operation-Location"]
    operation_id = read_operation_location.split("/")[-1]
    
    # Wait for the operation to complete
    while True:
        read_result = client.get_read_result(operation_id)
        if read_result.status not in [OperationStatusCodes.running, OperationStatusCodes.not_started]:
            break
        time.sleep(1)
    
    # Extract the text
    extracted_text = ""
    if read_result.status == OperationStatusCodes.succeeded:
        for text_result in read_result.analyze_result.read_results:
            for line in text_result.lines:
                extracted_text += line.text + "\n"
    
    return extracted_text
