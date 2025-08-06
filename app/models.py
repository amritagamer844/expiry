from datetime import datetime
from app import db
import json

class FoodItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    expiry_date = db.Column(db.DateTime, nullable=False)
    barcode = db.Column(db.String(20), nullable=True)
    category = db.Column(db.String(50), nullable=False)
    alert_days = db.Column(db.Integer, default=3)
    email = db.Column(db.String(120), nullable=False)
    nutrition_data = db.Column(db.Text, nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    
    def is_expired(self):
        return datetime.utcnow() > self.expiry_date
    
    def days_until_expiry(self):
        if self.is_expired():
            return -1
        delta = self.expiry_date - datetime.utcnow()
        return delta.days
    
    def get_nutrition_data(self):
        if self.nutrition_data:
            return json.loads(self.nutrition_data)
        return {}
    
    def set_nutrition_data(self, data):
        self.nutrition_data = json.dumps(data)
