from abc import ABC, abstractmethod

class DataManagerInterface(ABC):
    """
    Base class for managing users and movies.
    """

    @abstractmethod
    def get_all_users(self):
        """Return a list of all users."""
        pass

    @abstractmethod
    def get_user_movies(self, user_id):
        """Return a list of movies for a specific user."""
        pass

    @abstractmethod
    def add_movie(self, user_id, name, director, year, rating):
        """Add a new movie for a user."""
        pass

    @abstractmethod
    def update_movie(self, user_id, movie_id, name, director, year, rating):
        """Update a movie's details for a user."""
        pass

    @abstractmethod
    def delete_movie(self, user_id, movie_id):
        """Delete a movie for a user."""
        pass
