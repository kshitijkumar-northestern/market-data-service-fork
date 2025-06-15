import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.models.database import get_db, Base
from app.services.kafka_service import KafkaService
from unittest.mock import Mock

# Test database - use environment variable or default to SQLite
SQLALCHEMY_DATABASE_URL = (
    os.getenv("TEST_DATABASE_URL") or 
    os.getenv("DATABASE_URL") or 
    "sqlite:///./test.db"
)

# Different connection args for SQLite vs PostgreSQL
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Mock Kafka service for testing
def mock_kafka_service():
    mock_service = Mock(spec=KafkaService)
    mock_service.produce_price_event = Mock()
    return mock_service

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def db():
    return next(override_get_db())