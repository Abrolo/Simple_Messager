from flask import jsonify, request, current_app
from flaskr.db import get_db
from flaskr.models.email_model import Email
from flaskr.models.user_model import User
from flaskr.services.email_services import EmailServices
from flaskr.services.user_services import UserServices

def init_app(app):
    """
    Initialize the Flask application with the necessary routes.

    Args:
        app: The Flask application instance.
    """
    @app.route('/')
    def hello():
        """
        A simple route that returns a greeting message.
        
        Returns:
            A greeting message "Hello, World!".
        """
        return 'Hello, World!'

    @app.route('/emails', methods=['GET', 'POST', 'DELETE'])
    def emails():
        """
        Handle email-related requests: fetching, sending, and deleting emails.

        Methods:
            GET: Fetch emails based on query parameters.
            POST: Send a new email with provided data.
            DELETE: Delete an email based on provided ID.

        Returns:
            The response from the corresponding email operation.
        """
        db = get_db()     
        email_service = EmailServices(db)

        if request.method == 'GET':
            message, status_code = email_service.get_emails(request.json)

        elif request.method == 'POST':
            message, status_code = email_service.send_email(request.json)

        elif request.method == 'DELETE':
            message, status_code = email_service.delete_email(request.json)

        return jsonify(message), status_code

    @app.route('/register', methods=['POST'])
    def register():
        """
        Register a new user with provided username and password.

        Methods:
            POST: Register a user.

        Returns:
            A success message with status code 201 if the user is registered successfully.
        """
        db = get_db()
        user_service = UserServices(db)
        
        message, status_code = user_service.register_user(request.json)
        
        return jsonify(message), status_code
    
    
def delete_email(user_request, db, email_service):
    """
    Delete an email from the database based on the provided ID and return a response.

    Args:
        user_request: The Flask request object containing the email ID in JSON format.
        db: The database connection object.

    Returns:
        A JSON response indicating the success or failure of the delete operation.
    """
    message, status_code = email_service.delete_email(user_request)
    return jsonify(message), status_code
    
    id = request.json.get("id")
    
    # Execute the DELETE statement and get the number of affected rows
    result = db.execute('DELETE FROM email WHERE id = ?', (id,))
    db.commit()

    # Check if any rows were affected
    if result.rowcount > 0:
        return jsonify({"message": f"Successfully deleted email with id {id}"}), 200
    else:
        return jsonify({"error": f"Email with id {id} not found"}), 404

        

def send_email(user_request, email_service):
    """
    Send a new email by inserting it into the database.

    Args:
        user_request: The Flask request object containing the email data.
        db: The database connection.

    Returns:
        A success message with status code 201 if the email is sent successfully.
    """
    message, status_code = email_service.send_email(user_request)
    return jsonify(message), status_code

def get_emails(user_request, email_service):
    """
    Fetch emails based on query parameters.

    Args:
        user_request: The Flask request object containing query parameters.
        db: The database connection.

    Returns:
        A JSON response containing the list of emails and the status code.
    """
    emails_list, status_code = email_service.get_emails(user_request)
    return jsonify(emails_list), status_code
