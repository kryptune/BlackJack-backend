from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
import os
from datetime import datetime

app = Flask(__name__)
CORS(app, origins=["https://blckjck2.netlify.app"], supports_credentials=True)


# Auto-convert postgres:// to postgresql:// for SQLAlchemy compatibility
uri = os.environ.get("DATABASE_URL", "sqlite:///blackjack.db")
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = uri

db = SQLAlchemy(app)
# Database Model
class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    balance = db.Column(db.Integer, default=1000)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime)

# Create tables
with app.app_context():
    db.create_all()

# Get Player Info
@app.route('/player/<username>', methods=['GET'])
def get_player(username):
    player = Player.query.filter_by(username=username).first()
    if not player:
        player = Player(username=username)
        db.session.add(player)
        db.session.commit()
    return jsonify({
        'username': player.username,
        'email': player.email,
        'balance': player.balance,
        'wins': player.wins,
        'losses': player.losses
    })

# Update Balance
@app.route('/player/<username>/balance', methods=['POST'])
def update_balance(username):
    data = request.json
    amount = data.get('amount', 0)
    player = Player.query.filter_by(username=username).first()
    if player:
        player.balance += amount
        db.session.commit()
        return jsonify({'balance': player.balance})
    return jsonify({'error': 'Player not found'}), 404

@app.route('/player/<username>/update_winloss', methods=['POST'])
def update_win(username):
    data = request.json
    win = data.get('win', False)

    player = Player.query.filter_by(username=username).first()

    if player:
        if win:
            player.wins += 1
        else:
            player.losses += 1

        db.session.commit()

        return jsonify({'wins': player.wins, 'losses': player.losses})
    
    return jsonify({'error': 'Player not found'}), 404

@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    player = Player.query.filter_by(username=username).first()
    if player and check_password_hash(player.password_hash, password):
        return jsonify({"status": "success", "username": username})
    else:
        return jsonify({"status": "error", "message": "Invalid credentials"}), 401

@app.route('/register', methods=['POST', 'OPTIONS'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username or not password or not email:
        return jsonify({"status": "error", "message": "Missing fields"}), 400

    existing_user = Player.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"status": "error", "message": "Username already exists"}), 400

    # Hash the password before saving
    hashed_password = generate_password_hash(password)

    # Create new user
    new_user = Player(username=username, password_hash=hashed_password, email=email)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"status": "success", "username": username})



if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
