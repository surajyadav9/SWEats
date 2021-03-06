from flask import render_template, url_for, flash, redirect, request, abort, Blueprint
from flask_login import current_user, login_required
from sweats import db
from sweats.admin.forms import ItemForm, UpdateItemForm, WarehouseForm, UpdateWarehouseForm
from sweats.models import Item, Warehouse,OrderItem
from sweats.main.utils import save_picture, delete_old_picture

# Initializing Blueprint
admin = Blueprint('admin', '__name__')

@admin.route('/admin/home')
@login_required
def admin_home():
    if not current_user.admin:
        abort(403)
    return render_template('admin/home.html', title='Admin Home')

@admin.route('/admin/<model_name>')
@login_required
def model(model_name):
    if not current_user.admin:
        abort(403)
    # Init
    model_instance = ''
    if model_name == "item":
        model_instance = Item
        title = "Items"
        template_name = 'items.html'
    elif model_name == "warehouse":
        model_instance = Warehouse
        title = "Warehouses"
        template_name = 'warehouses.html'

    # Quering all items from database
    items = model_instance.query.all()
    return render_template('admin/'+template_name, title=title, items=items)

@admin.route('/admin/<model_name>/new', methods=['GET', 'POST'])
@login_required
def new_model(model_name):
    if not current_user.admin:
        abort(403)
    # Init
    legend=''
    if model_name == 'item':
        form  = ItemForm()
        template_name = 'new_item.html'
        title = 'New Item'
    if model_name == 'warehouse':
        form  = WarehouseForm()
        template_name = 'create_update_warehouse.html'
        title = 'New Warehouse'
        legend = "Add New Warehouse To Database"

    if form.validate_on_submit():
        if model_name == 'item':
            picture_file = save_picture(form.picture.data, "static/product_pics", 250, 320)
            item = Item(category=form.category.data, description=form.description.data, unit_price=form.unit_price.data, image_file=picture_file)
        elif model_name == 'warehouse':
            item = Warehouse(city=form.city.data)
            
        # Insert to database
        db.session.add(item)
        db.session.commit()
        flash(f'{model_name.capitalize()} added to the database!', 'success')
        return redirect(url_for('admin.new_model', model_name=model_name))
    return render_template('admin/'+template_name, title=title, legend=legend, form=form)

@admin.route('/admin/item/<int:item_id>/update', methods=['GET', 'POST'])
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
        return redirect(url_for('admin.update_item', item_id = item.id))
    elif request.method == 'GET':
        form.category.data = item.category
        form.description.data = item.description
        form.unit_price.data = item.unit_price
    image_file = url_for('static', filename='product_pics/' + item.image_file)
    return render_template('admin/update_item.html', title='Update Item', image_file=image_file, form=form)

@admin.route('/admin/warehouse/<int:warehouse_id>/update', methods=['GET', 'POST'])
@login_required
def update_warehouse(warehouse_id):
    if not current_user.admin:
        abort(403)
    form = UpdateWarehouseForm()
    warehouse = Warehouse.query.get_or_404(warehouse_id)
    if form.validate_on_submit():
        warehouse.city = form.city.data
        db.session.commit()
        flash('Warehouse updated successfully!', 'success')
        return redirect(url_for('admin.update_warehouse', warehouse_id=warehouse.id))
    elif request.method == 'GET':
        form.city.data = warehouse.city
    return render_template('admin/create_update_warehouse.html', title="Update Warehouse", legend="Update Warehouse To Database", form=form)
        

@admin.route('/admin/<model_name>/<int:instance_id>/delete', methods=['POST'])
@login_required
def delete_model_instance(model_name, instance_id):
    if not current_user.admin:
        abort(403)
    if model_name == 'item':
        item = Item.query.get_or_404(instance_id)
        oi = OrderItem.query.filter_by(item_id=item.id).first()
        if oi:
            flash("This item has relations with past orders. So can't be deletd due to history issues!", 'danger')
            return redirect(url_for('admin.model', model_name='item'))
        delete_old_picture(item.image_file, 'product_pics')
    elif model_name == 'warehouse':
        item = Warehouse.query.get_or_404(instance_id)
        if item.shipments:
            flash("This warehouse has relations with past orders. So can't be deletd due to history issues!", 'danger')
            return redirect(url_for('admin.model', model_name='warehouse'))

    # Delete Item
    db.session.delete(item)
    db.session.commit()
    flash(f'{model_name.capitalize()} have been successfully deleted from database!', 'success')
    return redirect(url_for('admin.model', model_name=model_name))
