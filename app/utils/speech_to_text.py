import azure.cognitiveservices.speech as speechsdk
from flask import current_app, jsonify
import tempfile
import os

def recognize_from_audio(audio_data):
    """
    Convert speech to text using Azure Speech Recognition.
    """
    # Get credentials from app config
    speech_key = current_app.config['AZURE_SPEECH_KEY']
    speech_region = current_app.config['AZURE_SPEECH_REGION']
    
    # Save audio data to a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    temp_file.write(audio_data)
    temp_file.close()
    
    try:
        # Create speech config
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
        
        # Create audio config using the temporary file
        audio_config = speechsdk.audio.AudioConfig(filename=temp_file.name)
        
        # Create speech recognizer
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
        
        # Start speech recognition
        result = speech_recognizer.recognize_once_async().get()
        
        # Process the result
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return {"success": True, "text": result.text}
        elif result.reason == speechsdk.ResultReason.NoMatch:
            return {"success": False, "error": "No speech could be recognized"}
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation = result.cancellation_details
            if cancellation.reason == speechsdk.CancellationReason.Error:
                return {"success": False, "error": f"Error: {cancellation.error_details}"}
            else:
                return {"success": False, "error": "Speech recognition canceled"}
    
    finally:
        # Clean up the temporary file
        os.unlink(temp_file.name)
