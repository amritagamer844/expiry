import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from flask import current_app
import threading
import time

def send_email(recipient, subject, body):
    """
    Send an email using SMTP.
    """
    # Get email configuration from app config
    mail_server = current_app.config['MAIL_SERVER']
    mail_port = current_app.config['MAIL_PORT']
    mail_username = current_app.config['MAIL_USERNAME']
    mail_password = current_app.config['MAIL_PASSWORD']
    mail_sender = current_app.config['MAIL_DEFAULT_SENDER']
    
    # Create message
    message = MIMEMultipart()
    message['From'] = mail_sender
    message['To'] = recipient
    message['Subject'] = subject
    
    # Attach body
    message.attach(MIMEText(body, 'html'))
    
    try:
        # Connect to server and send email
        with smtplib.SMTP(mail_server, mail_port) as server:
            server.starttls()
            server.login(mail_username, mail_password)
            server.send_message(message)
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False

def schedule_expiry_alert(food_item):
    """
    Schedule an email alert to be sent before the food item expires.
    """
    # Calculate when to send the alert
    alert_date = food_item.expiry_date - timedelta(days=food_item.alert_days)
    
    # If alert date is in the past, don't schedule
    if alert_date < datetime.utcnow():
        return
    
    # Calculate seconds until alert should be sent
    seconds_until_alert = (alert_date - datetime.utcnow()).total_seconds()
    
    # Start a thread to wait and then send the email
    def delayed_email():
        time.sleep(seconds_until_alert)
        
        # Check if item still exists and hasn't been deleted
        from app import db
        from app.models import FoodItem
        
        with current_app.app_context():
            item = FoodItem.query.get(food_item.id)
            if item:
                subject = f"Food Expiry Alert: {item.product_name}"
                body = f"""
                <html>
                <body>
                    <h2>Food Expiry Alert</h2>
                    <p>Your food item <strong>{item.product_name}</strong> will expire in {item.alert_days} days (on {item.expiry_date.strftime('%Y-%m-%d')}).</p>
                    <p>Food Category: {item.category}</p>
                    <p>Please consume it soon to avoid waste!</p>
                    <hr>
                    <p>This is an automated message from your Food Wastage Management System.</p>
                </body>
                </html>
                """
                send_email(item.email, subject, body)
    
    # Start the thread
    thread = threading.Thread(target=delayed_email)
    thread.daemon = True
    thread.start()
