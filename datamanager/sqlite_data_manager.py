from flask_sqlalchemy import SQLAlchemy
from datamanager.data_manager_interface import DataManagerInterface

# Initialize database

db = SQLAlchemy()


class User(db.Model):
    """User model representing application users."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    movies = db.relationship('Movie', backref='user', lazy=True)


class Movie(db.Model):
    """Movie model representing movies added by users."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    director = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class SQLiteDataManager(DataManagerInterface):
    """SQLite implementation of the DataManagerInterface."""

    def __init__(self, app):
        """Initialize the database with the Flask app."""
        self.db = db
        self.db.init_app(app)
        with app.app_context():
            self.db.create_all()  # Create tables if they don't exist

    def get_all_users(self):
        """Retrieve all users from the database."""
        return User.query.all()

    def get_user_movies(self, user_id):
        """Retrieve all movies associated with a specific user."""
        return Movie.query.filter_by(user_id=user_id).all()

    def add_user(self, name):
        """Add a new user to the database."""
        new_user = User(name=name)
        self.db.session.add(new_user)
        self.db.session.commit()

    def add_movie(self, user_id, name, director, year, rating):
        """Add a new movie to the database."""
        new_movie = Movie(
            name=name,
            director=director,
            year=year,
            rating=rating,
            user_id=user_id
        )
        self.db.session.add(new_movie)
        self.db.session.commit()

    def update_movie(self, user_id, movie_id, name, director, year, rating):
        """Update details of a movie."""
        movie = Movie.query.filter_by(id=movie_id, user_id=user_id).first()
        if movie:
            movie.name = name
            movie.director = director
            movie.year = year
            movie.rating = rating
            self.db.session.commit()

    def delete_movie(self, user_id, movie_id):
        """Delete a movie from the database."""
        movie = Movie.query.filter_by(id=movie_id, user_id=user_id).first()
        if movie:
            self.db.session.delete(movie)
            self.db.session.commit()
