from flask import Flask
from models import db
import models

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Admin%40123@localhost/jobportal'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def index():
    return "<h1>Welcome to Job Portal System!!!</h1>"

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=2004)