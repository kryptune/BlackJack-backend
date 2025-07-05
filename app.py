from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow frontend to connect

# Use SQLite for demo
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blackjack.db'
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

@app.route('/update_winloss', methods=['POST'])
def update_win():
    # Get JSON data from the request (like: { "username": "rolando", "win": true })
    data = request.json

    # Extract 'username' and 'win' values from the JSON
    username = data.get('username')
    win = data.get('win', False)

    # Find the player in the database using the username
    player = Player.query.filter_by(username=username).first()

    if player:
        # If win is True, increase wins; otherwise, increase losses
        if win:
            player.wins += 1
        else:
            player.losses += 1

        # Save the change in the database
        db.session.commit()

        # Send back the updated win/loss count
        return jsonify({'wins': player.wins, 'losses': player.losses})
    
    # If player is not found, return an error
    return jsonify({'error': 'Player not found'}), 404


if __name__ == '__main__':
    app.run(debug=True)
