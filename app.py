import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Database configuration
DB_USERNAME = os.environ.get('DB_USERNAME', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
DB_ENDPOINT = os.environ.get('DB_ENDPOINT', 'localhost')
DB_NAME = os.environ.get('DB_NAME', 'movies_db')
DB_PORT = os.environ.get('DB_PORT', '5432')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_ENDPOINT}:{DB_PORT}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Model
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'genre': self.genre,
            'year': self.year,
            'created_at': self.created_at.isoformat()
        }

# Routes
@app.route('/')
def index():
    movies = Movie.query.order_by(Movie.year.desc()).all()
    return render_template('index.html', movies=movies)

@app.route('/add', methods=['POST'])
def add_movie():
    title = request.form.get('title')
    genre = request.form.get('genre')
    year = request.form.get('year')
    
    if not title or not genre or not year:
        return redirect(url_for('index'))
    
    new_movie = Movie(title=title, genre=genre, year=int(year))
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('index'))

# Optional: API endpoint for AJAX requests
@app.route('/api/movies', methods=['GET'])
def get_movies():
    movies = Movie.query.all()
    return jsonify([movie.to_dict() for movie in movies])

@app.route('/api/movies', methods=['POST'])
def add_movie_api():
    data = request.json
    new_movie = Movie(
        title=data['title'],
        genre=data['genre'],
        year=int(data['year'])
    )
    db.session.add(new_movie)
    db.session.commit()
    return jsonify(new_movie.to_dict()), 201

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
