from typing import List, Tuple, Dict, Any
from flask import Request
from flaskr.models.email_model import Email
from flaskr.repositories.email_repo import EmailRepository
from flaskr.repositories.user_repo import UserRepository


class EmailServices:
    """
    A service class for handling email-related operations, including fetching,
    sending, and checking emails in the database.

    Attributes:
        db: The database connection object.
        email_repo: Repository for email operations.
        user_repo: Repository for user operations.
    """

    def __init__(self, db: Any) -> None:
        """
        Initialize the EmailService with a database connection.

        Args:
            db: The database connection object.
        """
        self.db = db
        self.email_repo = EmailRepository(db)
        self.user_repo = UserRepository(db)

    def handle_get_emails(self, request: Request) -> Tuple[Dict[str, Any], int]:
        """
        Retrieve emails based on the request parameters. Handles pagination and error cases.

        Args:
            request: The Flask Request object containing the parameters for fetching emails.

        Returns:
            A tuple containing a dictionary with a list of emails and the HTTP status code.

        Raises:
            ValueError: If recipient_username is not provided or invalid.
            LookupError: If the requested emails cannot be found.
            Exception: For other unexpected errors.
        """
        try:
            start, stop, recipient_username = self.fetch_get_args(request)
            self.is_valid_user(recipient_username)

            emails = self.retrieve_emails(start, stop, recipient_username)

            return {"emails": [dict(email) for email in emails]}, 200

        except ValueError as ve:
            return {"error": str(ve)}, 400

        except LookupError as le:
            return {"error": str(le)}, 404

        except Exception as e:
            return {"error": "An error occurred while fetching emails."}, 500

    def fetch_get_args(self, request: Request) -> Tuple[int, int, str]:
        """
        Extract and validate request arguments for fetching emails from JSON payload.

        Args:
            request: The Flask Request object containing parameters for fetching emails.

        Returns:
            A tuple containing start, stop, and recipient_username.

        Raises:
            ValueError: If the request parameters are invalid.
        """
        start = request.args.get('start', default=None, type=int)
        stop = request.args.get('stop', default=None, type=int)
        recipient_username = request.args.get('recipient_username')

        # Validate parameters
        if start is not None and not isinstance(start, int):
            raise ValueError("Invalid value for 'start'. Must be an integer.")
        if stop is not None and not isinstance(stop, int):
            raise ValueError("Invalid value for 'stop'. Must be an integer.")
        if not recipient_username or type(recipient_username) != str:
            raise ValueError(
                "Invalid value for 'recipient_username'. Must be a string.")

        # Return parameters as tuple
        return start, stop, recipient_username

    def retrieve_emails(self, start: int = None, stop: int = None, recipient_username: str = None) -> List[Email]:
        """
        Retrieve emails based on pagination and username.

        Args:
            start: The start index for pagination.
            stop: The stop index for pagination.
            recipient_username: The recipient's username.

        Returns:
            A list of emails.
        """
        if start is not None and stop is not None:
            limit, offset = self.get_limit_and_offset(start, stop)
            return self.email_repo.get_indexed_emails_to_user(limit, offset, recipient_username)
        else:
            return self.email_repo.get_all_emails_to_user(recipient_username)

    def get_limit_and_offset(self, start_index: int = 0, stop_index: int = 0) -> Tuple[int, int]:
        """
        Calculate the limit and offset for pagination based on start and stop indices.

        Args:
            start_index: The starting index for pagination.
            stop_index: The stopping index for pagination.

        Returns:
            A tuple containing the limit and offset for pagination.

        Raises:
            ValueError: If the start_index or stop_index are invalid.
        """
        if isinstance(start_index, int) and isinstance(stop_index, int):
            if stop_index > start_index:
                return stop_index - start_index, start_index
        raise ValueError("Invalid start or stop index")

    def handle_get_email(self, email_id: int) -> Dict[str, Any]:
        """
        Retrieve a single email by its ID.

        Args:
            email_id: The ID of the email to retrieve.

        Returns:
            A dictionary containing the email data or an error message.

        Raises:
            ValueError: If email_id is invalid.
            LookupError: If the email does not exist.
        """
        try:
            self.check_email_id(email_id)
            return {"email": self._get_email(email_id)}, 201
        except ValueError as ve:
            return {"error": str(ve)}, 400
        except LookupError as le:
            return {"error": str(le)}, 404

    def check_email_id(self, email_id: int) -> None:
        """
        Validate the email ID.

        Args:
            email_id: The ID of the email to validate.

        Raises:
            ValueError: If email_id is None or not an integer.
        """
        if email_id is None:
            raise ValueError("Email ID cannot be None.")
        if type(email_id) != int:
            raise ValueError("Email ID must be an integer.")
        elif email_id < 0:
            raise ValueError("Email ID must be larger than 0.")

    def _get_email(self, email_id: int) -> Email:
        """
        Fetch a single email by its ID.

        Args:
            email_id: The ID of the email to fetch.

        Returns:
            The Email object corresponding to the provided ID.

        Raises:
            LookupError: If the email is not found.
        """
        response = self.email_repo.get_email(email_id)
        if response is None:
            raise LookupError(
                "The email with the provided ID could not be found.")
        return response

    def _validate_send_args(self, message_subject: str, sender_username: str, recipient_username: str) -> None:
        """
        Validate email request arguments.

        Args:
            message_subject: The email subject.
            sender_username: The email sender's username.
            recipient_username: The email recipient's username.

        Raises:
            ValueError: If any of the arguments are invalid.
        """
        if not message_subject:
            raise ValueError("Message subject cannot be empty.")
        if not sender_username:
            raise ValueError("The email must have a sender.")
        if not recipient_username:
            raise ValueError("The email must have a recipient.")

    def is_valid_user(self, username: str) -> None:
        """
        Check if the user exists in the database.

        Args:
            username: The username to check.

        Raises:
            LookupError: If the user does not exist.
        """
        if not self.user_repo.user_exists(username):
            raise LookupError("User not found in database.")

    def handle_send_email(self, json_data: Dict[str, Any]) -> Tuple[Dict[str, str], int]:
        """
        Send an email based on the JSON payload.

        Args:
            json_data: The JSON payload containing email data.

        Returns:
            A tuple containing a message and the HTTP status code.

        Raises:
            ValueError: If any required data is invalid.
            LookupError: If a user cannot be found.
            Exception: For other unexpected errors.
        """
        try:
            email = self.create_email(json_data)
            self.email_repo.send_email(email)
            return {"message": "Email was successfully sent."}, 201

        except ValueError as ve:
            return {"error": str(ve)}, 400
        except LookupError as le:
            return {"error": str(le)}, 404
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    def create_email(self, json_data: Dict[str, Any]) -> Email:
        """
        Create an Email object from JSON payload.

        Args:
            json_data: The JSON payload containing email data.

        Returns:
            An Email object constructed from the provided data.

        Raises:
            ValueError: If any required data is invalid.
            LookupError: If a user cannot be found.
        """
        message_subject, body, sender_username, recipient_username = self.fetch_send_args(
            json_data)
        self._validate_send_args(
            message_subject, sender_username, recipient_username)
        self.check_valid_users(recipient_username, sender_username)

        return Email(message_subject, body, sender_username, recipient_username)

    def fetch_send_args(self, data: Dict[str, Any]) -> Tuple[str, str, str, str]:
        """
        Extract email parameters from the JSON payload.

        Args:
            data: The JSON payload containing email data.

        Returns:
            A tuple of (subject, body, sender_username, recipient_username).

        Raises:
            ValueError: If required parameters are missing or invalid.
        """
        message_subject = data.get('message_subject', '')
        body = data.get('body', '')
        sender_username = data.get('sender_username', '')
        recipient_username = data.get('recipient_username', '')

        return message_subject, body, sender_username, recipient_username

    def check_valid_users(self, recipient_username: str, sender_username: str) -> None:
        """
        Check if both the recipient and sender users are valid.

        Args:
            recipient_username: The recipient's username.
            sender_username: The sender's username.

        Raises:
            LookupError: If either user does not exist.
        """
        if not self.user_repo.user_exists(recipient_username):
            raise LookupError("The recipient does not exist in the database.")
        if not self.user_repo.user_exists(sender_username):
            raise LookupError("The sender does not exist in the database.")

    def handle_delete_email(self, email_id: int) -> Tuple[Dict[str, str], int]:
        """
        Deletes an email by its ID from the database.

        Args:
            email_id: The ID of the email to delete.

        Returns:
            A tuple with a success message or error and the corresponding HTTP status code.

        Raises:
            ValueError: If email_id is invalid or the email cannot be deleted.
            LookupError: If the email does not exist.
            Exception: For other unexpected errors.
        """
        try:
            self._validate_email_exists(email_id)
            self._delete_email_from_db(email_id)

            return {"message": f"Email with id {email_id} was successfully deleted from the database."}, 200

        except ValueError as ve:
            return {"error": str(ve)}, 400
        except LookupError as le:
            return {"error": str(le)}, 404
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    def _validate_email_exists(self, email_id: int) -> None:
        """
        Validates if the email exists in the database.

        Args:
            email_id: The ID of the email to validate.

        Raises:
            LookupError: If the email does not exist in the database.
        """
        if not self.email_repo.email_exists(email_id):
            raise LookupError(
                f"Email with ID {email_id} not found in database.")

    def _delete_email_from_db(self, email_id: int) -> None:
        """
        Deletes the email from the database.

        Args:
            email_id: The ID of the email to delete.

        Raises:
            ValueError: If the email could not be deleted.
        """
        response = self.email_repo.delete_email(email_id)
        if response.rowcount <= 0:
            raise ValueError("The email could not be deleted.")
