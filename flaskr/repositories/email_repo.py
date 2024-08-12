from typing import List
from flaskr.models.email_model import Email


class EmailRepository:
    def __init__(self, db) -> None:
        self.db = db

    def send_email(self, email: Email):
        self.db.execute(
            'INSERT INTO email (message_subject, body, sender_username, recipient_username) VALUES (?, ?, ?, ?)',
            (email.message_subject, email.body,
             email.sender_username, email.recipient_username)
        )
        self.db.commit()
        return {"message": "Email sent successfully."}

    def email_exists(self, email_id: int) -> bool:
        """
        Check if an email exists in the database.

        Returns:
            A boolean indicating if the email exists.
        """
        query = "SELECT 1 FROM email WHERE id = ?"
        result = self.db.execute(query, (email_id,)).fetchone()
        return result is not None

    def delete_email(self, id: int) -> tuple[dict[str, str], int]:
        response = self.db.execute('DELETE FROM email WHERE id = ?', (id,))
        self.db.commit()
        return response

    def get_email(self, email_id: int) -> tuple[dict[str, str], int]:
        query = "SELECT 1 FROM email WHERE id = ?"
        return self.db.execute(query, (email_id,)).fetchone()

    def get_all_emails_to_user(self, recipient_username: str):
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

    def get_indexed_emails_to_user(self, limit: int, offset: int, recipient_username: str):
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
