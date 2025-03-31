from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.models import UserCreate as pydantic_models  # Pydantic models for request/response
from api.schemas import User  as db_schemas 
from api.utils import security


def test_register_user(client: TestClient, db: Session):
    email = "test1@test.com"
    password = "testPassword"
    user_in = pydantic_models.UserCreate(email=email, password=password)
    response = client.post("/register", json=user_in.dict())
    assert response.status_code == status.HTTP_201_CREATED
    created_user = response.json()
    assert created_user["email"] == email
    assert "id" in created_user
    assert "is_active" in created_user
    assert created_user["is_active"] is True
    assert "is_superuser" in created_user
    assert created_user["is_superuser"] is False


def test_register_user_existing_email(client: TestClient, db: Session):
    email = "test1@test.com"
    password = "testPassword"
    user_in = pydantic_models.UserCreate(email=email, password=password)
    response = client.post("/register", json=user_in.dict())
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Email already registered"


def test_login_access_token(client: TestClient, db: Session):
    email = "test2@test.com"
    password = "testPassword2"
    user = db_schemas.User(email=email, hashed_password=security.get_password_hash(password))
    db.add(user)
    db.commit()
    data = {"username": email, "password": password}
    response = client.post("/login", data=data)
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert "access_token" in content
    assert content["token_type"] == "bearer"


def test_login_incorrect_password(client: TestClient, db: Session):
    email = "test2@test.com"
    password = "testPassword2"
    wrong_password = "testPassword3"
    user = db_schemas.User(email=email, hashed_password=security.get_password_hash(password))
    db.add(user)
    db.commit()
    data = {"username": email, "password": wrong_password}
    response = client.post("/login", data=data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect username or password"


def test_login_inactive_user(client: TestClient, db: Session):
    email = "test4@test.com"
    password = "testPassword4"
    user = db_schemas.User(
        email=email, hashed_password=security.get_password_hash(password), is_active=False
    )
    db.add(user)
    db.commit()
    data = {"username": email, "password": password}
    response = client.post("/login", data=data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect username or password" # Inactive users are treated as incorrect credentials for security


def test_get_users_me_unauthorized(client: TestClient, db: Session):
    response = client.get("/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Not authenticated"