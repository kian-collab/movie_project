import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import socket

app = Flask(__name__)

# Get database connection from environment (Docker Stack will inject these)
DB_USERNAME = os.environ.get('DB_USERNAME', 'movie_user')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')  # Will come from Docker secrets
DB_ENDPOINT = os.environ.get('DB_ENDPOINT', 'mysql')  # Service name in stack
DB_NAME = os.environ.get('DB_NAME', 'movies_db')
DB_PORT = os.environ.get('DB_PORT', '3306')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_ENDPOINT}:{DB_PORT}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Model
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def index():
    # Get hostname to show which container is serving the request
    hostname = socket.gethostname()
    movies = Movie.query.order_by(Movie.year.desc()).all()
    return render_template('index.html', movies=movies, hostname=hostname)

@app.route('/add', methods=['POST'])
def add_movie():
    title = request.form.get('title')
    genre = request.form.get('genre')
    year = request.form.get('year')
    
    if title and genre and year:
        new_movie = Movie(title=title, genre=genre, year=int(year))
        db.session.add(new_movie)
        db.session.commit()
    
    return redirect(url_for('index'))

@app.route('/health')
def health():
    return {"status": "healthy", "service": "flask-app", "host": socket.gethostname()}

@app.route('/api/movies')
def api_movies():
    movies = Movie.query.all()
    return jsonify([{
        'title': m.title,
        'genre': m.genre,
        'year': m.year
    } for m in movies])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)
