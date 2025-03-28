"""This module implements many different secure hash and message digest algorithms."""
import hashlib
import uuid
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.sql.expression import func
# pip install flask flask_sqlalchemy psycopg2 flask_cors

app = Flask(__name__)
CORS(app)

# Connection: MAKE SURE TO REPLACE USERNAME:PASSWORD WITH THE ONE SET UP ON YOUR OWN DEVICE
# SSH Tunnel Forward to Local Port: ssh -L 5433:127.0.0.1:5432 USERNAME@128.113.126.87
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://knighk4:1234@localhost/backlog_manager'

db = SQLAlchemy(app)

API_KEY = "1af69e1cf8664df59d23e49cd5aca2ea"

'''
example use of RAWG API call
url = f"https://api.rawg.io/api/platforms?key={API_KEY}"
response = requests.get(url)
data = response.json()
print(data)
'''

class Users(db.Model):
    """Define basic users table with columns: email, name, hashed passwords, and session token."""
    email = db.Column(db.String(100), unique=True, nullable=False, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    session_token = db.Column(db.String(200), unique=True, nullable=True)

    def __repr__(self):
        return f'<User {self.email}>'

    def set_password(self, password: str):
        """Hashes and stores the password."""
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, input_password: str) -> bool:
        """Checks if the given password matches the stored hash."""
        return self.password_hash == hashlib.sha256(input_password.encode()).hexdigest()

class Preferences(db.Model):
    """Temporary table for user preferences."""
    email = db.Column(db.String(100), unique=True, nullable=False, primary_key=True)
    prefer = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<User {self.email}>'

class Library(db.Model):
    """Game Library table with columns: email and gameid."""
    email = db.Column(db.String(100), nullable=False, primary_key=True)
    gameid = db.Column(db.String(100), nullable=False, primary_key=True)

    def __repr__(self):
        return f'<Library {self.email}>'

class Game(db.Model):
    """Game table with columns:
    id, name, platform, genre, release date, description, and a image.
    """
    id = db.Column(db.String(100), unique=True, nullable=False, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    platform = db.Column(db.String(200), nullable=False)
    genre = db.Column(db.String(200), nullable=False)
    release_date = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    image = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<Game {self.name}>'

# Creates tables in the database (one-time setup for now)
with app.app_context():
    db.create_all()

# Allow requests from frontend
CORS(app, resources={r"/*": {"origins": "http://128.113.126.87:3000"}})

@app.route('/register', methods=['POST'])
def register():
    """API route to register a new user: http://127.0.0.1:5000/register."""
    data = request.json
    # Checks if user exists first
    existing_user = Users.query.filter((Users.email == data['email'])).first()
    if existing_user:
        return jsonify({"error": "User already exists!"}), 400
    # Adding new user
    new_user = Users(email=data['email'], name=data['name'])
    new_user.set_password(data['password'])
    token = generate_token()
    db.session.add(new_user)
    new_user.session_token = token
    db.session.commit()
    return jsonify({'token': token}), 201

@app.route('/login', methods=['POST'])
def login():
    """API route to login a user: http://127.0.0.1:5000/login."""
    data = request.json
    user = Users.query.filter_by(email=data['email']).first()
    # Checks if users and their password matches
    if user and user.verify_password(data['password']):
        token = generate_token()
        user.session_token = token
        db.session.commit()
        return jsonify({'token': token}), 200
    return jsonify({'error': 'Invalid email or password'}), 401

@app.route('/add_game', methods=['POST'])
def add_game():
    """WPI API route to add game for a user: http://127.0.0.1:5000/add_game."""
    data = request.json
    return data

def create_ranking():
    """Creates a game ranking."""
    random_ranking = Game.query.order_by(func.random()).limit(10).all()
    return random_ranking

def generate_token():
    """Generates a new session token."""
    return str(uuid.uuid4())

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=False)
