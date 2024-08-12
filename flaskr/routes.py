from flask import jsonify, request
from flaskr.db import get_db
from flaskr.services.email_services import EmailServices
from flaskr.services.user_services import UserServices


def init_app(app):
    """
    Initialize the Flask application with the necessary routes.

    Args:
        app: The Flask application instance.
    """

    # @app.before_request
    # def setup_services():
    #     """
    #     Create and store service objects in Flask's `g` object before each request.
    #     """
    #     g.db = get_db()
    #     g.email_service = EmailServices(g.db)
    #     g.user_service = UserServices(g.db)

    @app.route('/')
    def hello():
        """
        A simple route that returns a greeting message.

        Returns:
            A greeting message "Hello, World!".
        """
        return 'Hello, World!'

    @app.route('/emails', methods=['GET'])
    def get_emails():
        """
        Handle fetching emails based on query parameters.

        Returns:
            The response from the get_emails operation.
        """
        db = get_db()
        email_service = EmailServices(db)
        message, status_code = email_service.handle_get_emails(request)
        return jsonify(message), status_code

    @app.route('/emails/<int:email_id>', methods=['GET'])
    def get_email(email_id):
        """
        Handle fetching emails based on query parameters.

        Returns:
            The response from the get_emails operation.
        """
        db = get_db()
        email_service = EmailServices(db)
        message, status_code = email_service.handle_get_email(email_id)
        return jsonify(message), status_code

    @app.route('/emails', methods=['POST'])
    def send_email():
        """
        Handle sending a new email with provided data.

        Returns:
            The response from the send_email operation.
        """
        db = get_db()
        email_service = EmailServices(db)
        message, status_code = email_service.handle_send_email(request.json)
        return jsonify(message), status_code

    @app.route('/emails/<int:email_id>', methods=['DELETE'])
    def delete_email(email_id):
        """
        Handle deleting an email based on provided ID.

        Returns:
            The response from the delete_email operation.
        """
        db = get_db()
        email_service = EmailServices(db)
        message, status_code = email_service.handle_delete_email(email_id)
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
        message, status_code = user_service.handle_register_user(request.json)
        return jsonify(message), status_code
