import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import logout_user, current_user, login_required
from sweats import app, db, bcrypt
from sweats.forms import ItemForm, UpdateItemForm
from sweats.models import Item, Warehouse
from sweats.routes.customer_routes import save_picture, delete_old_picture


@app.route('/admin/home')
@login_required
def admin():
    if not current_user.admin:
        abort(403)
    return render_template('admin/home.html', title='Admin Home')

@app.route('/admin/<model_name>')
@login_required
def model(model_name):
    if not current_user.admin:
        abort(403)
    model_instance = ''
    if model_name == "items":
        model_instance = Item
        title = "Items"
        template_name = 'items.html'

    # Quering all items from database
    items = model_instance.query.all()

    return render_template('admin/'+template_name, title=title, items=items)

@app.route('/admin/<model_name>/new', methods=['GET', 'POST'])
@login_required
def new_model(model_name):
    if not current_user.admin:
        abort(403)
    if model_name == 'item':
        form  = ItemForm()
        template_name = 'new_item.html'
        title = 'New Item'

    if form.validate_on_submit():
        if model_name == 'item':
            picture_file = save_picture(form.picture.data, "static/product_pics", 286, 180)
            item = Item(category=form.category.data, description=form.description.data, unit_price=form.unit_price.data, image_file=picture_file)
            
        # Insert to database
        db.session.add(item)
        db.session.commit()
        flash(f'{model_name.capitalize()} added to the database!', 'success')
        return redirect(url_for('new_model', model_name=model_name))
    return render_template('admin/'+template_name, title=title, form=form)

@app.route('/admin/item/<int:item_id>/update', methods=['GET', 'POST'])
@login_required
def update_item(item_id):
    if not current_user.admin:
        abort(403)
    form = UpdateItemForm()
    item = Item.query.get_or_404(item_id)
    if form.validate_on_submit():
        if form.picture.data:
            # Delete old picture
            delete_old_picture(item.image_file, 'product_pics')
            picture_file = save_picture(form.picture.data, "static/product_pics", 286, 180)
            
            # Assigining new values
            item.image_file = picture_file
        
        item.category = form.category.data
        item.description = form.description.data
        item.unit_price = form.unit_price.data

        # Commit changes
        db.session.commit()
        flash('Item updated successfully!', 'success')
        return redirect(url_for('update_item', item_id = item.id))
    elif request.method == 'GET':
        form.category.data = item.category
        form.description.data = item.description
        form.unit_price.data = item.unit_price
    image_file = url_for('static', filename='product_pics/' + item.image_file)
    return render_template('admin/update_item.html', title='Update Item', image_file=image_file, form=form)

@app.route('/admin/item/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_item(item_id):
    if not current_user.admin:
        abort(403)
    item = Item.query.get_or_404(item_id)
    delete_old_picture(item.image_file, 'product_pics')
    # Delete Item
    db.session.delete(item)
    db.session.commit()
    flash('Item have been successfully deleted from database!', 'success')
    return redirect(url_for('model', model_name='items'))