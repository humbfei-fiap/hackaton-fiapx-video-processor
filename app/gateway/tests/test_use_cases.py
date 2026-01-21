import pytest
from src.use_cases.register_user import RegisterUserUseCase
from src.domain.entities import User
from unittest.mock import MagicMock

def test_register_user_success():
    # Arrange
    mock_repo = MagicMock()
    mock_repo.get_by_username.return_value = None
    mock_repo.create.side_effect = lambda user: user
    
    mock_hasher = MagicMock(return_value="hashed_password")
    
    use_case = RegisterUserUseCase(mock_repo, mock_hasher)
    
    # Act
    result = use_case.execute("testuser", "test@example.com", "password123")
    
    # Assert
    assert result.username == "testuser"
    assert result.email == "test@example.com"
    assert result.password == "hashed_password"
    mock_repo.create.assert_called_once()
    mock_hasher.assert_called_once_with("password123")

def test_register_user_already_exists():
    # Arrange
    mock_repo = MagicMock()
    mock_repo.get_by_username.return_value = User(username="existing", email="old@example.com", password="xxx")
    
    use_case = RegisterUserUseCase(mock_repo, MagicMock())
    
    # Act & Assert
    with pytest.raises(ValueError) as excinfo:
        use_case.execute("existing", "new@example.com", "password123")
    
    assert str(excinfo.value) == "Username already exists"
