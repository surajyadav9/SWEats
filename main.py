from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Create DB Instance 
db = SQLAlchemy(app)

# Setting Up Development DB
db.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dev.db'



@app.route("/")
def home():
    return '<h1>Home Page</h1>'


if __name__=='__main__':
    app.run(debug=True)