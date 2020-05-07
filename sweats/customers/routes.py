from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from sweats import db, bcrypt
from sweats.customers.forms import (RegistrationForm, LoginForm, UpdateAccountForm, 
                            RequestRestForm, ResetPasswordForm)
from sweats.models import Customer
from sweats.customers.utils import send_request_email
from sweats.main.utils import save_picture, delete_old_picture

# Initializing Blueprint
customers = Blueprint('customers', '__name__')


@customers.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        pw_hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        customer = Customer(name=form.name.data, email=form.email.data, password=pw_hash, city=form.city.data)
        db.session.add(customer)
        db.session.commit()

        # here 'success' is a bootstrap class for flash messages
        flash('Account created successfully. Now you can log in.', 'success')
        # again 'home' is the function name
        return redirect(url_for('customers.login'))
    return render_template('register.html', title='Register', form=form)

@customers.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        customer = Customer.query.filter_by(email=form.email.data).first()
        if customer and bcrypt.check_password_hash(customer.password, form.password.data):
            login_user(customer, remember=form.remember.data)
            
            # The page user attempting to access w/o authorization will be passed in the next query string variable
            # Here get return 'None' if query string variable 'next' is not found in the args dictionary
            next_page = request.args.get('next')

            # Python Ternary operation
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password!', 'danger')
    return render_template('login.html', title='Login', form=form)

@customers.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@customers.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            # Delete old pictures
            if current_user.image_file != 'default.png':
                delete_old_picture(current_user.image_file, 'profile_pics')

            picture_file = save_picture(form.picture.data, "static/profile_pics", 125, 125)
            current_user.image_file = picture_file
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.city = form.city.data
        db.session.commit()
        flash('Account updated successfully!', 'success')

        # After submiting a form, if we reload a page w/o redirecting, the browser tries to send a POST request again(i.e tries to submit the form again)
        # redirect causes the browser to send a GET request( POST/REDIRECT/GET Pattern )
        return redirect(url_for('customers.account'))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
        form.city.data = current_user.city
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)


#
# Password Reset Section
#


@customers.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RequestRestForm()
    if form.validate_on_submit():
        customer = Customer.query.filter_by(email=form.email.data).first()
        send_request_email(customer)
        flash(f'An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('customers.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@customers.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    customer = Customer.verify_reset_token(token)
    if customer is None:
        flash("That is an invalid or expired token.", 'warning')
        return redirect(url_for('customers.reset_request'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        pw_hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        customer.password = pw_hash
        db.session.commit()
        flash('Your password has been updated. Now you can log in.', 'success')
        return redirect(url_for('customers.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

