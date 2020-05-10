from flask import Blueprint, render_template

errors = Blueprint('errors', __name__)

# app_errorhandler handles errors across the application
# Not Found Eror
@errors.app_errorhandler(404)
def error_404(error):
    # return template, status_code
    return render_template('errors/404.html'), 404

# Forbidden Error
@errors.app_errorhandler(403)
def error_403(error):
    # return template, status_code
    return render_template('errors/403.html'), 403

# Internal Server Error
@errors.app_errorhandler(500)
def error_500(error):
    # return template, status_code
    return render_template('errors/500.html'), 500