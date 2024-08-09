from flaskr.models.user_model import User

class UserRepository:
    def __init__(self, db) -> None:
        self.db = db
    
    def user_exists(self, username):
        """
        Check if a user exists in the database.

        Returns:
            A boolean indicating if the user exists.
        """
        query = "SELECT 1 FROM user WHERE username = ?"
        result = self.db.execute(query, (username,)).fetchone()
        return result is not None
    
    def register_user(self, user: User):
        response = self.db.execute('INSERT INTO user (username, password) VALUES (?, ?)', 
                    (user.username, user.password))
        self.db.commit()
        return response
