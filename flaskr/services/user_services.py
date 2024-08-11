from flaskr.models.user_model import User
from flaskr.repositories.user_repo import UserRepository


class UserServices:
    def __init__(self, db):
        """
        Initialize the UserService with a database connection.
        Args:
            db: The database connection object.
        """
        self.db = db
        self.user_repo = UserRepository(db)
    
    def format_register_request(self, json_data):
        return json_data.get("username"), json_data.get("password")
    
    def register_user(self, data):
        try: 
            username = data["username"]
            password = data["password"]
            user = User(username, password)
            if user.is_valid():
                if self.user_repo.user_exists(username):
                    raise ValueError("Username already exists.")
            
                response = self.user_repo.register_user(user)
                print(response, flush=True)
                if response.rowcount > 0:
                    return{"message": f"User {username} registered sucessfully."}, 201
                else:
                    raise ValueError("Could not register user.")
        except ValueError as ve:
            return {"error": str(ve)}, 400 # Bad Request
        except Exception:
            return {"error": "There was an error when registering a user."}, 500
    