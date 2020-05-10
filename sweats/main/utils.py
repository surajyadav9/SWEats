import os
import secrets
from PIL import Image
from flask import current_app

def save_picture(form_picture, folder, size_x, size_y):
    # Giving each picture to its own unique id
    random_hex = secrets.token_hex(8)
    _ , f_ext = os.path.splitext( form_picture.filename )
    picture_filename = random_hex + f_ext

    # app.root_path = /home/suraj/Desktop/SWEats/sweats
    picture_path = os.path.join( current_app.root_path, folder, picture_filename )
    
    # Resizing the profile picture
    output_size = (size_x, size_y)
    im = Image.open(form_picture)
    im.thumbnail(output_size)
    im.save(picture_path)

    return picture_filename

def delete_old_picture(picture_filename, folder):
    picture_path = os.path.join( current_app.root_path, 'static/'+folder, picture_filename )
    os.remove(picture_path)