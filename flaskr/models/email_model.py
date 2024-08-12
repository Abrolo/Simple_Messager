class Email:
    def __init__(self, message_subject=None, body=None, sender_username=None, recipient_username=None):
        self.message_subject = message_subject
        self.body = body
        self.sender_username = sender_username
        self.recipient_username = recipient_username

    def is_valid(self):
        """
        Perform validations for the email.

        Returns:
            bool: True if the email is valid, otherwise raises ValueError.

        Raises:
            ValueError: If the subject or body is invalid.
        """
        if not self.message_subject or not self.body:
            raise ValueError("Subject and body cannot be empty.")
        if len(self.message_subject) > 255:
            raise ValueError("Subject cannot exceed 255 characters.")
        if len(self.body) > 5000:
            raise ValueError("Body cannot exceed 5000 characters.")
        return True

    def format_email_from_json(self, response):
        data = response.json
        self.message_subject = data["message_subject"]
