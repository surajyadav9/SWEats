from flask import url_for
from flask_mail import Message
from sweats import mail

def send_request_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender="noreply@demo.com",
                     recipients=[user.email])
    # _external = True is used to give the full URL instead of relative to the user in mail
    msg.body = f'''To reset your password, visit the following link -
{url_for('customers.reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email. Hence no changes will be made.
'''
    mail.send(msg)