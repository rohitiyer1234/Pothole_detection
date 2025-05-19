from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import json
import time
import os
import uuid

app = Flask(__name__)
app.secret_key = "your-secret-key-change-this"  # Change this to a random string in production

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Data files
DATA_FILE = "pothole_data.json"
USERS_FILE = "users.json"

# Initialize data files if they don't exist
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        # Create a default admin user
        json.dump([{
            "id": str(uuid.uuid4()),
            "username": "admin",
            "password": generate_password_hash("admin123"),
            "role": "admin"  # admin can edit, normal users are view-only
        }], f)

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

# Load users from JSON file
def get_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    users = get_users()
    for user in users:
        if user["id"] == user_id:
            return User(user["id"], user["username"], user["role"])
    return None

# Routes
@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        users = get_users()
        for user in users:
            if user["username"] == username and check_password_hash(user["password"], password):
                user_obj = User(user["id"], user["username"], user["role"])
                login_user(user_obj)
                return redirect(url_for('dashboard'))
        
        flash("Invalid username or password")
    
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Check if username already exists
        users = get_users()
        for user in users:
            if user["username"] == username:
                flash("Username already exists")
                return redirect(url_for('register'))
        
        # Create new user
        new_user = {
            "id": str(uuid.uuid4()),
            "username": username,
            "password": generate_password_hash(password),
            "role": "user"  # Default role is view-only
        }
        
        users.append(new_user)
        with open(USERS_FILE, "w") as f:
            json.dump(users, f, indent=4)
        
        flash("Registration successful! You can now log in.")
        return redirect(url_for('login'))
    
    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)

@app.route("/map")
@login_required
def map_view():
    # Get Google Maps API key from environment or config
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "YOUR_GOOGLE_API_KEY")
    return render_template("map.html", api_key=api_key, user=current_user)

# API endpoints
@app.route("/api/markers", methods=["GET"])
@login_required
def get_markers():
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
    return jsonify(data)

@app.route("/api/markers", methods=["POST"])
@login_required
def add_marker():
    # Check if user has edit permission
    if current_user.role != "admin":
        return jsonify({"status": "error", "message": "Permission denied"}), 403
    
    data = request.json
    if not data or 'lat' not in data or 'lng' not in data:
        return jsonify({"status": "error", "message": "Invalid data"}), 400
    
    marker = {
        "id": str(uuid.uuid4()),
        "lat": data["lat"],
        "lng": data["lng"],
        "confidence": data.get("confidence", "N/A"),
        "reported_by": current_user.username,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(DATA_FILE, "r+") as f:
        existing = json.load(f)
        existing.append(marker)
        f.seek(0)
        f.truncate()
        json.dump(existing, f, indent=4)
    
    return jsonify({"status": "success", "marker": marker})

@app.route("/api/markers/<marker_id>", methods=["DELETE"])
@login_required
def delete_marker(marker_id):
    # Check if user has edit permission
    if current_user.role != "admin":
        return jsonify({"status": "error", "message": "Permission denied"}), 403
    
    with open(DATA_FILE, "r+") as f:
        markers = json.load(f)
        markers = [m for m in markers if m.get("id") != marker_id]
        f.seek(0)
        f.truncate()
        json.dump(markers, f, indent=4)
    
    return jsonify({"status": "success"})

# API endpoint to receive pothole data from your YOLO model
@app.route("/api/report-pothole", methods=["POST"])
def report_pothole():
    data = request.json
    
    if not data or 'lat' not in data or 'lng' not in data:
        return jsonify({"status": "error", "message": "Invalid data"}), 400
    
    marker = {
        "id": str(uuid.uuid4()),
        "lat": data["lat"],
        "lng": data["lng"],
        "confidence": data.get("confidence", "N/A"),
        "reported_by": "AI Detection",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(DATA_FILE, "r+") as f:
        existing = json.load(f)
        existing.append(marker)
        f.seek(0)
        f.truncate()
        json.dump(existing, f, indent=4)
    
    return jsonify({"status": "success", "marker": marker})

if __name__ == "__main__":
    # Use 0.0.0.0 to make the server accessible from other devices on your network
    app.run(host="0.0.0.0", port=5000, debug=True)