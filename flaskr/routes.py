from flask import jsonify, request
from flaskr.db import get_db
from flaskr.services.email_services import EmailService

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

        if request.method == 'GET':
            response = get_emails(request, db)

        elif request.method == 'POST':
            response = send_email(request, db)

        elif request.method == 'DELETE':
            response = delete_email(request, db)

        return response

    @app.route('/register', methods=['POST'])
    def register():
        """
        Register a new user with provided username and password.

        Methods:
            POST: Register a user.

        Returns:
            A success message with status code 201 if the user is registered successfully.
        """
        data = request.json
        db = get_db()
        result = db.execute('INSERT INTO user (username, password) VALUES (?, ?)', 
                   (data.get("username"), data.get("password")))

        db.commit()
        
        if result.rowcount > 0:
            return jsonify({"message": "User registered successfully"}), 201
        else:
            return jsonify({"error": f"Bad Request"}), 400
    
    
def delete_email(request, db):
    """
    Delete an email from the database based on the provided ID and return a response.

    Args:
        request: The Flask request object containing the email ID in JSON format.
        db: The database connection object.

    Returns:
        A JSON response indicating the success or failure of the delete operation.
    """
    id = request.json.get("id")
    
    # Execute the DELETE statement and get the number of affected rows
    result = db.execute('DELETE FROM email WHERE id = ?', (id,))
    db.commit()

    # Check if any rows were affected
    if result.rowcount > 0:
        return jsonify({"message": f"Successfully deleted email with id {id}"}), 200
    else:
        return jsonify({"error": f"Email with id {id} not found"}), 404

        

def send_email(request, db):
    """
    Send a new email by inserting it into the database.

    Args:
        request: The Flask request object containing the email data.
        db: The database connection.

    Returns:
        A success message with status code 201 if the email is sent successfully.
    """
    email_service = EmailService(db)
    message, status_code = email_service.send_email(request)
    return jsonify(message), status_code

def get_emails(request, db):
    """
    Fetch emails based on query parameters.

    Args:
        request: The Flask request object containing query parameters.
        db: The database connection.

    Returns:
        A JSON response containing the list of emails and the status code.
    """
    email_service = EmailService(db)
    emails_list, status_code = email_service.get_emails(request)
    return jsonify(emails_list), status_code
