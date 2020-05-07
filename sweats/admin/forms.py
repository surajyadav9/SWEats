from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, NumberRange
from sweats.models import Warehouse

class ItemMixin():
    category = StringField('Category', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    unit_price = IntegerField('Unit Price', validators=[DataRequired(), NumberRange(min=100, max=10000)])

class ItemForm(FlaskForm, ItemMixin):
    picture = FileField('Product Image', validators=[DataRequired(), FileAllowed(['jpg','png'])])
    submit = SubmitField('Add Item')

class UpdateItemForm(FlaskForm, ItemMixin):
    picture = FileField('Product Image', validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Update Item')

class WarehouseMixin():
    city = StringField('City', validators=[DataRequired()])

    def validate_city(self, city):
        warehouse = Warehouse.query.filter_by(city=city.data).first()
        if warehouse:
            raise ValidationError('This warehouse is already added. Please choose another.')

class WarehouseForm(FlaskForm, WarehouseMixin):
    submit = SubmitField('Add Warehouse')

class UpdateWarehouseForm(FlaskForm, WarehouseMixin):
    submit = SubmitField('Update Warehouse')