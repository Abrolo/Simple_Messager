from typing import Tuple, Dict, Any
from flaskr.models.user_model import User
from flaskr.repositories.user_repo import UserRepository


class UserServices:
    """
    A service class for handling user-related operations, including registration
    and validation of user data.

    Attributes:
        db: The database connection object.
        user_repo: Repository for user operations.
    """

    def __init__(self, db: Any) -> None:
        """
        Initialize the UserService with a database connection.

        Args:
            db: The database connection object.
        """
        self.db = db
        self.user_repo = UserRepository(db)

    def format_register_request(self, json_data: Dict[str, Any]) -> Tuple[str, str]:
        """
        Extracts the username and password from the registration request.

        Args:
            json_data: The JSON data containing the user's registration details.

        Returns:
            A tuple containing the username and password.
        """
        return json_data.get("username"), json_data.get("password")

    def handle_register_user(self, data: Dict[str, Any]) -> Tuple[Dict[str, str], int]:
        """
        Handle the user registration process.

        Args:
            data: The JSON data containing the user's registration details.

        Returns:
            A tuple containing a success message or error and the corresponding HTTP status code.

        Raises:
            ValueError: If any registration data is invalid.
            Exception: For other unexpected errors.
        """
        try:
            user = self.create_user(data)
            self._register_user(user)
            return {"message": f"User {user.username} registered successfully."}, 201
        except ValueError as ve:
            return {"error": str(ve)}, 400  # Bad Request
        except KeyError as ke:
            return {"error": str(ke)}, 400
        except Exception:
            return {"error": "There was an error when registering a user."}, 500

    def create_user(self, data: Dict[str, Any]) -> User:
        """
        Create a User object from registration data.

        Args:
            data: The JSON data containing the user's registration details.

        Returns:
            A User object constructed from the provided data.

        Raises:
            ValueError: If the username or password is invalid.
        """
        username, password = self._fetch_register_args(data)
        self._check_user_validity(username, password)
        return User(username, password)

    def _register_user(self, user: User) -> None:
        """
        Register the user in the database.

        Args:
            user: The User object to register.

        Raises:
            ValueError: If the user could not be registered.
        """
        response = self.user_repo.register_user(user)
        if response.rowcount <= 0:
            raise ValueError("Could not register user.")

    def _fetch_register_args(self, data: Dict[str, Any]) -> Tuple[str, str]:
        """
        Extract the username and password from registration data.

        Args:
            data: The JSON data containing the user's registration details.

        Returns:
            A tuple containing the username and password.

        Raises:
            KeyError: If the username or password is not provided.
        """
        try:
            return data["username"], data["password"]
        except KeyError as ke:
            raise KeyError(f"Missing required field: {str(ke)}") from ke

    def _check_user_validity(self, username: str, password: str) -> None:
        """
        Validate the user's username and password.

        Args:
            username: The user's username.
            password: The user's password.

        Raises:
            ValueError: If the username or password is invalid or already exists.
        """
        self._check_username_validity(username)
        self._check_password_validity(password)
        if self.user_repo.user_exists(username):
            raise ValueError("Username already exists.")

    def _check_username_validity(self, username: str) -> None:
        """
        Validate the username.

        Args:
            username: The username to validate.

        Raises:
            ValueError: If the username is invalid.
        """
        if not username:
            raise ValueError("A user must have a username.")
        elif len(username) < 2:
            raise ValueError("Username must be at least 2 characters long.")

    def _check_password_validity(self, password: str) -> None:
        """
        Validate the password.

        Args:
            password: The password to validate.

        Raises:
            ValueError: If the password is invalid.
        """
        if not password:
            raise ValueError("A user must have a password.")
        elif len(password) < 2:
            raise ValueError(
                "The password must be at least 2 characters long.")
