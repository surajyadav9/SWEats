from flask import render_template, url_for, flash, redirect, request
from sweats import app, db, bcrypt
from sweats.forms import RegistrationForm, LoginForm
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

@app.route('/account')
@login_required
def account():
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file)