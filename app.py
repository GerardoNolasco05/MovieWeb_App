from flask import Flask, render_template, request, redirect, url_for, flash
from datamanager.sqlite_data_manager import SQLiteDataManager, User, Movie
import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()
OMDB_API_KEY = os.getenv('OMDB_API_KEY')

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///MovieWeb_App.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')  # For flash messages

# Initialize database manager
data_manager = SQLiteDataManager(app)


@app.route('/')
def home():
    """Render the home page."""
    return render_template("home.html")


@app.route('/users')
def list_users():
    """Fetch and display all users."""
    users = data_manager.get_all_users()
    return render_template('users.html', users=users)


@app.route("/add_user", methods=["GET", "POST"])
def add_user():
    """Add a new user to the database."""
    if request.method == "POST":
        user_name = request.form.get("name")
        if user_name:
            new_user = User(name=user_name)
            data_manager.db.session.add(new_user)
            data_manager.db.session.commit()
            flash("User added successfully!", "success")
            return redirect(url_for("list_users"))
    return render_template("add_user.html")


@app.route('/users/<int:user_id>')
def user_movies(user_id):
    """Display movies associated with a specific user."""
    user = User.query.get(user_id)
    if not user:
        return "User not found", 404
    movies = data_manager.get_user_movies(user_id)
    return render_template('user_movies.html', user=user, movies=movies, user_id=user_id)


@app.route('/users/<int:user_id>/add_movie', methods=["GET", "POST"])
def add_movie(user_id):
    """Add a movie to a user's list."""
    if request.method == "POST":
        movie_name = request.form['name']
        movie_details = fetch_movie_details(movie_name)

        if movie_details:
            data_manager.add_movie(user_id, movie_name, movie_details['director'],
                                   movie_details['year'], movie_details['rating'])
            flash("Movie added successfully!", "success")
            return redirect(url_for('user_movies', user_id=user_id))
        flash("Movie not found on OMDb.", "error")
    return render_template('add_movie.html', user_id=user_id)


@app.route('/users/<int:user_id>/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    """Update details of a movie associated with a user."""
    movie = Movie.query.get(movie_id)
    if not movie or movie.user_id != user_id:
        return "Movie not found or does not belong to this user", 404

    if request.method == 'POST':
        data_manager.update_movie(user_id, movie_id, request.form.get('name'),
                                  request.form.get('director'), request.form.get('year'),
                                  request.form.get('rating'))
        flash("Movie updated successfully!", "success")
        return redirect(url_for('user_movies', user_id=user_id))
    return render_template('update_movie.html', user_id=user_id, movie=movie)


@app.route('/users/<int:user_id>/delete_movie/<int:movie_id>', methods=["POST"])
def delete_movie(user_id, movie_id):
    """Delete a movie from a user's list."""
    movie = Movie.query.filter_by(id=movie_id, user_id=user_id).first()
    if movie:
        data_manager.db.session.delete(movie)
        data_manager.db.session.commit()
        flash("Movie deleted successfully!", "success")
    return redirect(url_for('user_movies', user_id=user_id))


def fetch_movie_details(movie_name):
    """Fetch movie details from the OMDb API."""
    url = f"http://www.omdbapi.com/?t={movie_name}&apikey={OMDB_API_KEY}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data['Response'] == 'True':
            return {
                'director': data.get('Director', ''),
                'year': data.get('Year', ''),
                'rating': data.get('imdbRating', '')
            }
    return None


# Error Handling
@app.errorhandler(404)
def page_not_found(e):
    """Render a custom 404 error page."""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    """Render a custom 500 error page."""
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True)
