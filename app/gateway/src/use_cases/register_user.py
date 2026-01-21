from src.domain.entities import User
from src.ports.interfaces import UserRepository

class RegisterUserUseCase:
    def __init__(self, user_repo: UserRepository, password_hasher):
        self.user_repo = user_repo
        self.hasher = password_hasher

    def execute(self, username: str, password: str) -> User:
        if self.user_repo.get_by_username(username):
            raise ValueError("Username already exists")
        
        hashed = self.hasher(password)
        new_user = User(username=username, password=hashed)
        return self.user_repo.create(new_user)
