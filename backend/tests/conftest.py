import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.session import Base, get_db
from app.main import app
from app.database.init_db import seed_database
from app.core.security import create_access_token
from app.models.customer import Customer

TEST_DATABASE_URL = "sqlite:///./test_nexabank.db"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    seed_database(db)
    db.close()
    yield
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def rajesh_token():
    return create_access_token(data={"sub": "cust_rajesh", "email": "demo.rajesh@nexabank.internal", "name": "Rajesh Kumar"})

@pytest.fixture
def priya_token():
    return create_access_token(data={"sub": "cust_priya", "email": "demo.priya@nexabank.internal", "name": "Priya Sharma"})

@pytest.fixture
def vikram_token():
    return create_access_token(data={"sub": "cust_vikram", "email": "demo.vikram@nexabank.internal", "name": "Vikram Patel"})
