from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from sweats.models import Customer

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    city = StringField('City', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        customer = Customer.query.filter_by(email=email.data).first()
        if customer:
            raise ValidationError('This email is taken. Please choose another.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    city = StringField('City', validators=[DataRequired(), Length(min=2, max=20)])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Update')

    def validate_email(self, email):
        if email.data != current_user.email:
            customer = Customer.query.filter_by(email=email.data).first()
            if customer:
                raise ValidationError('This email is taken. Please choose another.')

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

class WarehouseForm(FlaskForm, WarehouseMixin):
    submit = SubmitField('Add Warehouse')

class UpdateWarehouseForm(FlaskForm, WarehouseMixin):
    submit = SubmitField('Update Warehouse')