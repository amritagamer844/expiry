from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, DateField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email, NumberRange

class FoodItemForm(FlaskForm):
    expiry_image = FileField('Expiry Date Image', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')
    ])
    barcode_image = FileField('Barcode Image', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')
    ])
    product_name = StringField('Product Name', validators=[DataRequired()])
    expiry_date = DateField('Expiry Date', validators=[DataRequired()])
    barcode = StringField('Barcode')
    category = SelectField('Food Category', choices=[
        ('Grains', 'Grains - Rice, wheat, oats, quinoa, bread, pasta, etc.'),
        ('Proteins', 'Proteins - Meat, fish, eggs, tofu, legumes, nuts, etc.'),
        ('Dairy', 'Dairy - Milk, cheese, yogurt, butter, etc.'),
        ('Fats and Oils', 'Fats and Oils - Olive oil, butter, avocado, nuts, seeds, etc.'),
        ('Sweets', 'Sweets - Candy, chocolate, pastries, cakes, cookies, etc.'),
        ('Beverages', 'Beverages - Water, tea, coffee, juice, soda, alcohol, etc.'),
        ('Spices and Herbs', 'Spices and Herbs - Salt, pepper, basil, oregano, cinnamon, etc.'),
        ('Processed Foods', 'Processed Foods - Canned goods, frozen meals, snacks, etc.')
    ], validators=[DataRequired()])
    alert_days = IntegerField('Alert Days Before Expiry', validators=[
        DataRequired(), NumberRange(min=1, max=30)
    ], default=3)
    email = StringField('Email for Alerts', validators=[DataRequired(), Email()])
    submit = SubmitField('Save Item')
