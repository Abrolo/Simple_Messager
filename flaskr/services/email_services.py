class EmailService:
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
            start, stop, recipient_username = self.get_request_args(request)
            
            if not recipient_username:
                return {"error": "Recipient username is required."}, 400

            if not self.user_exists(recipient_username):
                return {"error": "Username does not exist."}, 404
            
            if start is not None and stop is not None:
                limit, offset = self.get_limit_and_offset(start, stop)
                emails = self.fetch_paginated_emails(limit, offset, recipient_username)
            else:
                emails = self.fetch_all_emails_to_user(recipient_username)

            return [dict(email) for email in emails], 200

        except ValueError as ve:
            return {"error": str(ve)}, 400

        except Exception as e:
            print(f"Exception: {e}", flush=True)
            return {"error": "An error occurred while fetching emails."}, 500

    def user_exists(self, username):
        """
        Check if a user exists in the database.

        Args:
            username: The username to check.

        Returns:
            A result indicating if the user exists.
        """
        query = "SELECT 1 FROM user WHERE username = ?"
        result = self.db.execute(query, (username,)).fetchone()
        return result

    def get_request_args(self, request):
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

    def fetch_all_emails_to_user(self, recipient_username):
        """
        Fetch all emails sent to a specific user, ordered by creation date.

        Args:
            recipient_username: The username of the recipient.

        Returns:
            A list of emails for the specified user.
        """
        query = """
            SELECT * FROM email
            WHERE recipient_username = ?
            ORDER BY created_at DESC
        """
        return self.db.execute(query, (recipient_username,)).fetchall()

    def fetch_all_emails(self):
        """
        Fetch all emails in the database, ordered by creation date.

        Returns:
            A list of all emails in the database.
        """
        query = """
            SELECT * FROM email
            ORDER BY created_at DESC
        """
        return self.db.execute(query).fetchall()

    def fetch_paginated_emails(self, limit, offset, recipient_username):
        """
        Fetch a paginated list of emails sent to a specific user.

        Args:
            limit: The maximum number of emails to return.
            offset: The starting point for fetching emails.
            recipient_username: The username of the recipient.

        Returns:
            A list of emails for the specified user within the given range.
        """
        query = '''
            SELECT *
            FROM email e
            WHERE recipient_username = ?
            ORDER BY e.created_at DESC
            LIMIT ? OFFSET ?
        '''
        return self.db.execute(query, (recipient_username, limit, offset)).fetchall()
