from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Allow frontend to connect

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
    balance = db.Column(db.Integer, default=1000)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)

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



if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
