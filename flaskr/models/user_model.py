class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    
    def is_valid(self):
        if not self.username:
            raise ValueError("A user must have a username.")
        elif not self.password:
            raise ValueError("A user must have a password.")
        elif len(self.username) < 2:
            raise ValueError("Username must be at least 2 characters long.")
        elif len(self.password) < 2:
            raise ValueError("The password must be at least 2 characters long.")
        else:
            return True