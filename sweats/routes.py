import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from sweats import app, db, bcrypt
from sweats.forms import RegistrationForm, LoginForm, UpdateAccountForm
from sweats.models import Customer, Order, Cart, Item, Shipment, Warehouse
from flask_login import login_user, current_user, logout_user, login_required


items = [
    {
        'category':'Cloths',
        'description':'Wool cloths for children.',
        'unit_price':1500,
        'image_file':'default.jpg'
    },
    {
        'category':'Mobile',
        'description':'Smartphones with blah blah specifications.',
        'unit_price':9999,
        'image_file':'default.jpg'
    },
    {
        'category':'Watch',
        'description':'Water proof watches.',
        'unit_price':2600,
        'image_file':'default.jpg'
    },
]

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', items=items)

@app.route('/about')
def about():
    return render_template('about.html', title='About')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        pw_hash = bcrypt.generate_password_hash(form.password.data)
        customer = Customer(name=form.name.data, email=form.email.data, password=pw_hash, city=form.city.data)
        db.session.add(customer)
        db.session.commit()

        # here 'success' is a bootstrap class for flash messages
        flash('Account created successfully. Now you can log in.', 'success')
        # again 'home' is the function name
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        customer = Customer.query.filter_by(email=form.email.data).first()
        if customer and bcrypt.check_password_hash(customer.password, form.password.data):
            login_user(customer, remember=form.remember.data)
            
            # The page user attempting to access w/o authorization will be passed in the next query string variable
            # Here get return 'None' if query string variable 'next' is not found in the args dictionary
            next_page = request.args.get('next')

            # Python Ternary operation
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password!', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):

    # Giving each picture to its own unique id
    random_hex = secrets.token_hex(8)
    _ , f_ext = os.path.splitext( form_picture.filename )
    picture_filename = random_hex + f_ext

    # app.root_path = /home/suraj/Desktop/SWEats/sweats
    picture_path = os.path.join( app.root_path, 'static/profile_pics', picture_filename )
    
    # Resizing the profile picture
    output_size = (125, 125)
    im = Image.open(form_picture)
    im.thumbnail(output_size)
    im.save(picture_path)

    return picture_filename

def delete_old_picture(picture_filename):
    picture_path = os.path.join( app.root_path, 'static/profile_pics', picture_filename )
    os.remove(picture_path)


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            
            # Delete old pictures
            if current_user.image_file != 'default.png':
                delete_old_picture(current_user.image_file)

            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.city = form.city.data
        db.session.commit()
        flash('Account updated successfully!', 'success')

        # After submiting a form, if we reload a page w/o redirecting, the browser tries to send a POST request again(i.e tries to submit the form again)
        # redirect causes the browser to send a GET request( POST/REDIRECT/GET Pattern )
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
        form.city.data = current_user.city
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)