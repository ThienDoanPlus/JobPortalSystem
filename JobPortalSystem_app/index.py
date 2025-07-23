from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)

# Config database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Admin%40123@localhost/jobportal'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
@app.route("/")
def index():
    return "<h1>Welcome to Job Portal System</h1>"


if __name__ == '__main__':
    app.run(debug=True, port=2004)