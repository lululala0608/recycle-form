from flask import Flask, request, jsonify, render_template
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
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "未提供有效的 JSON 資料"}), 400

        expected_date_obj = None
        if data.get("expected_date"):
            expected_date_obj = datetime.strptime(data["expected_date"], "%Y-%m-%d").date()

        app_entry = VehicleApplication(
            owner_id=data.get("owner_id", ""),
            vehicle_type=data.get("vehicle_type", ""),
            plate_number=data.get("plate_number", ""),
            expected_date=expected_date_obj,
            location=data.get("location", ""),
            phone=data.get("phone", ""),
            reward=data.get("reward", "")
        )

        if not app_entry.owner_id or not app_entry.plate_number:
            return jsonify({"error": "身分證字號與車牌號碼為必填"}), 400

        db.session.add(app_entry)
        db.session.commit()
        return jsonify({"message": "success"}), 200

    except Exception as e:
        return jsonify({"error": f"伺服器錯誤：{str(e)}"}), 500

@app.route('/init-db')
def init_db():
    with app.app_context():
        db.create_all()
    return "資料表建立完成"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
