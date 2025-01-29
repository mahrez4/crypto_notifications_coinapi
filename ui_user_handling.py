import json

class UserManager:
    FILE_PATH = "users.json"

    def __init__(self):
        self.users = self._load_users()

    def _load_users(self):
        try:
            with open(self.FILE_PATH, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_users(self):
        with open(self.FILE_PATH, 'w') as file:
            json.dump(self.users, file, indent=4)

    def sign_up(self, username, password):
        if username in self.users:
            return False, "Username already exists."
        self.users[username] = password
        self.save_users()
        return True, "Sign-up successful!"

    def login(self, username, password):
        if self.users.get(username) == password:
            return True, "Login successful!"
        return False, "Invalid username or password."