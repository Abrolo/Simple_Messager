from typing import List, Tuple, Dict, Any
import json
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

    def normalize_data(self, request: Request) -> Dict[str, Any]:
        """
        Normalize input data from a Flask request into a dictionary format.

        Args:
            request: The Flask request object.

        Returns:
            A dictionary with standardized data.

        Raises:
            DataNormalizationError: If the request data is not in JSON or form data format.
        """
        if request.is_json:
            return request.get_json()
        
        if request.form:
            return request.form.to_dict()
        
        try:
            raw_data = request.data.decode('utf-8')
            if raw_data:
                return json.loads(raw_data)
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass
        
        # Handle query parameters for GET requests
        if request.args:
            return request.args.to_dict()
        
        else:
            raise ValueError("Wrong format.")

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

    def get_emails(self, request: Request) -> Tuple[List[dict[str, Any]], int]:
        """
        Retrieve emails based on the request parameters. Handles pagination and error cases.

        Args:
            data: The JSON data containing the parameters for fetching emails.

        Returns:
            A tuple containing a list of emails and the HTTP status code.

        Raises:
            ValueError: If recipient_username is not provided or invalid.
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
            data: The JSON payload containing parameters for fetching emails.

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
            raise ValueError("Invalid value for 'recipient_username'. Must be a string.")
        
        # Return parameters as tuple
        return start, stop, recipient_username 
    
    def retrieve_emails(self, start: int=None, stop: int=None, recipient_username: str=None) -> Any:
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

    def fetch_send_args(self, data) -> Tuple[str, str, str, str]:
        """
        Extract email parameters from the JSON payload.

        Args:
            data: The JSON payload containing email data.

        Returns:
            A tuple of (subject, body, sender_username, recipient_username).

        Raises:
            ValueError: If required parameters are missing or invalid.
        """
        print(data, flush=True)
        message_subject = data.get('message_subject', '')
        body = data.get('body', '')
        sender_username = data.get('sender_username', '')
        recipient_username = data.get('recipient_username', '')
        
        return message_subject, body, sender_username, recipient_username

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

    def send_email(self, json_data) -> Tuple[Dict[str, str], int]:
        """
        Send an email based on the JSON payload.

        Args:
            data: The JSON payload containing email data.

        Returns:
            A tuple containing a message and the HTTP status code.
        """
        try:
            message_subject, body, sender_username, recipient_username = self.fetch_send_args(json_data)
            self._validate_send_args(message_subject, sender_username, recipient_username)
            self.check_valid_users(recipient_username, sender_username)
            email = Email(self.db, message_subject, body, sender_username, recipient_username)
            self.email_repo.send_email(email)
            return {"message": "Email was successfully sent."}, 201
            
        except ValueError as ve:
            return {"error": str(ve)}, 400
        except LookupError as le:
            return {"error": str(le)}, 404
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500
        
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



    def delete_email(self, email_id: int) -> Tuple[Dict[str, str], int]:
        """
        Deletes an email by its ID from the database.

        Args:
            data: The JSON payload containing the email ID.

        Returns:
            A tuple with a success message or error and the corresponding HTTP status code.
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

    def _extract_email_id(self, data: Dict[str, str]) -> int:
        """
        Extracts the email ID from the JSON payload.

        Args:
            data: The JSON payload containing the email ID.

        Returns:
            The extracted email ID.

        Raises:
            ValueError: If the email ID is missing or invalid.
        """
        email_id = data.get("id", None)
        if email_id is None or not isinstance(email_id, int):
            raise ValueError("Email ID cannot be empty or invalid.")
        return email_id

    def _validate_email_exists(self, email_id: int) -> None:
        """
        Validates if the email exists in the database.

        Args:
            email_id: The ID of the email to validate.

        Raises:
            LookupError: If the email does not exist in the database.
        """
        if not self.email_repo.email_exists(email_id):
            raise LookupError(f"Email with ID {email_id} not found in database.")

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
