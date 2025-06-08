
from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///data.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class VehicleApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.String(20), nullable=False)
    vehicle_type = db.Column(db.String(10))
    plate_number = db.Column(db.String(20))
    expected_date = db.Column(db.Date)
    location = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    reward = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    app_entry = VehicleApplication(
        owner_id=data['owner_id'],
        vehicle_type=data['vehicle_type'],
        plate_number=data['plate_number'],
        expected_date=data['expected_date'],
        location=data['location'],
        phone=data['phone'],
        reward=data['reward']
    )
    db.session.add(app_entry)
    db.session.commit()
    return jsonify({"message": "success"}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
