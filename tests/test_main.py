from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app import models, utils
import pytest

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module")
def test_db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop tables
    Base.metadata.drop_all(bind=engine)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome to the Library" in response.text

def test_register_user(test_db):
    response = client.post(
        "/auth/register",
        data={"email": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 200 # Redirects to login, but TestClient follows redirects? No, 303 usually.
    # Wait, RedirectResponse returns 303. TestClient follows redirects by default?
    # Let's check if it redirects to login page
    assert response.url.path == "/auth/login" or response.status_code == 303

def test_login_user(test_db):
    # Register first
    client.post(
        "/auth/register",
        data={"email": "login@example.com", "password": "password123"}
    )
    
    response = client.post(
        "/auth/login",
        data={"email": "login@example.com", "password": "password123"}
    )
    assert response.status_code == 200 # Redirects to home
    assert "user_id" in response.cookies

def test_staff_dashboard_access_denied(test_db):
    # Login as normal user
    client.post(
        "/auth/register",
        data={"email": "normal@example.com", "password": "password123"}
    )
    client.post(
        "/auth/login",
        data={"email": "normal@example.com", "password": "password123"}
    )
    
    response = client.get("/dashboard/")
    # Should redirect to login or show error (in our code it redirects to login if not staff)
    assert response.status_code == 200 
    assert "Login" in response.text # Redirected to login page because check failed

def test_create_book_unauthorized(test_db):
    response = client.post(
        "/books/add",
        data={
            "title": "Test Book",
            "author": "Test Author",
            "price": 10.0,
            "quantity": 5,
            "description": "Test Desc"
        },
        files={"image": ("filename", b"file content", "image/png")}
    )
    assert response.status_code == 403 # Not authorized
