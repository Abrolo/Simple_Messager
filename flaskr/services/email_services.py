from flaskr.models.email_model import Email
from flaskr.models.user_model import User
from flaskr.protocols.email_protocol import EmailModelProtocol
from flaskr.repositories.email_repo import EmailRepository
from flaskr.repositories.user_repo import UserRepository

class EmailServices:
    """
    A service class for handling email-related operations, including fetching,
    sending, and checking emails in the database.

    Attributes:
        db: The database connection object.
    """
    
    def __init__(self, db):
        """
        Initialize the EmailService with a database connection.

        Args:
            db: The database connection object.
        """
        self.db = db
        self.email_repo = EmailRepository(db)
        self.user_repo = UserRepository(db)

    def get_limit_and_offset(self, start_index=0, stop_index=0):
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

    def get_emails(self, request):
        """
        Retrieve emails based on the request parameters. Handles pagination and error cases.

        Args:
            request: The Flask request object containing query parameters.

        Returns:
            A tuple containing a list of emails and the HTTP status code.

        Raises:
            ValueError: If recipient_username is not provided or invalid.
        """
        try:
            start, stop, recipient_username = self.fetch_get_request_args(request)
            
            if not recipient_username:
                return {"error": "Recipient username is required."}, 400

            if not self.user_repo.user_exists(recipient_username):
                return {"error": "Username does not exist."}, 404
            
            if start is not None and stop is not None:
                limit, offset = self.get_limit_and_offset(start, stop)
                emails = self.email_repo.get_indexed_emails_to_user(limit, offset, recipient_username)
            else:
                emails = self.email_repo.get_all_emails_to_user(recipient_username)
                
            return [dict(email) for email in emails], 200

        except ValueError as ve:
            return {"error": str(ve)}, 400

        except Exception as e:
            return {"error": "An error occurred while fetching emails."}, 500

    def fetch_send_request_args(self, request):
        data = request.json
        subject = data.get('message_subject')
        body = data.get('body')
        sender_username = data.get('sender_username')
        recipient_username = data.get('recipient_username')
        
        return subject, body, sender_username, recipient_username

    def send_email(self, request):
        subject, body, sender_username, recipient_username = self.fetch_send_request_args(request)
        response, status_code = self.check_valid_users(recipient_username, sender_username)
        if status_code != 200:
            return response, status_code
        try:
            email = Email(self.db, subject, body, sender_username, recipient_username)
            if email.is_valid():
                self.email_repo.send_email(email)
                return{"message": "Email was successfully sent."}, 201
            
        except ValueError as ve:
            return{"error": str(ve)}, 400
        except Exception:
            return{"error": "An error occurred while sending the email."}, 500
        
            
    def check_valid_users(self, recipient_username, sender_username):
        if not self.user_repo.user_exists(recipient_username):
            return {"error": "Recipient does not exist."}, 404
        if not self.user_repo.user_exists(sender_username):
            return {"error": "Sender does not exist."}, 404
        return {}, 200
    

    def fetch_get_request_args(self, request):
        """
        Extract and validate request arguments for fetching emails.

        Args:
            request: The Flask request object containing query parameters.

        Returns:
            A tuple containing start, stop, and recipient_username.

        Raises:
            ValueError: If the request parameters are invalid.
        """
        try:
            start = request.args.get('start', default=None, type=int)
            stop = request.args.get('stop', default=None, type=int)
            recipient_username = request.args.get('recipient_username', default=None, type=str)

            if (start is not None and start < 0) or (stop is not None and stop < 0):
                raise ValueError("Start and stop indices must be non-negative integers.")

            return start, stop, recipient_username
        except ValueError as ve:
            raise ValueError(ve)
        
    def delete_email(self, request):
        try:
            email_id = request.get("id", default=None, type=int)
            if not email_id:
                raise ValueError("Email ID cannot be empty.")
            if not self.email_repo.email_exists(email_id):
                raise LookupError("Email not found in database.")
            response = self.email_repo.delete_email(email_id)
            
            if response.rowcount > 0:
                return{"message": f"Email with id {email_id} was successfully deleted from the database."}, 200
            else:
                raise ValueError("The email could not be deleted.")
        except ValueError as ve:
            return {"error": str(ve)}, 400
        except LookupError as le:
            return {"error": str(le)}, 404
        except Exception as e:
            return {"error": "An error occurred while deleting the email." + str(e)}, 500