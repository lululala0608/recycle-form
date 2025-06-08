
from flask import Flask, request, render_template, redirect, session, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "secure123"
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

@app.before_request
def restrict_admin_routes():
    if request.path.startswith('/admin') and not request.path.startswith('/admin/login'):
        if 'admin' not in session:
            return redirect(url_for('admin_login'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == '1234':
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        return "登入失敗", 401
    return render_template("login.html")

@app.route('/admin/dashboard')
def admin_dashboard():
    records = VehicleApplication.query.order_by(VehicleApplication.created_at.desc()).all()
    return render_template("dashboard.html", records=records)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

@app.route('/records')
def get_records():
    records = VehicleApplication.query.order_by(VehicleApplication.created_at.desc()).all()
    return jsonify([
        {
            "owner_id": r.owner_id,
            "vehicle_type": r.vehicle_type,
            "plate_number": r.plate_number,
            "expected_date": r.expected_date.isoformat() if r.expected_date else "",
            "location": r.location,
            "phone": r.phone,
            "reward": r.reward,
            "created_at": r.created_at.isoformat()
        }
        for r in records
    ])

@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "未提供資料"}), 400
        expected_date = datetime.strptime(data.get("expected_date"), "%Y-%m-%d").date()
        entry = VehicleApplication(
            owner_id=data.get("owner_id", ""),
            vehicle_type=data.get("vehicle_type", ""),
            plate_number=data.get("plate_number", ""),
            expected_date=expected_date,
            location=data.get("location", ""),
            phone=data.get("phone", ""),
            reward=data.get("reward", "")
        )
        db.session.add(entry)
        db.session.commit()
        return jsonify({"message": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/init-db')
def init_db():
    with app.app_context():
        db.create_all()
    return "資料表建立完成"

@app.route('/')
def index():
    return render_template("index.html")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
