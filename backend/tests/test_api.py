
"""
API endpoint tests
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override database dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Setup and teardown test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "name" in response.json()
    assert "version" in response.json()


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_strategy():
    """Test strategy creation"""
    strategy_data = {
        "name": "Test SMA Crossover",
        "description": "Test strategy",
        "config": {
            "indicators": [
                {"type": "SMA", "period": 20, "column": "Close"},
                {"type": "SMA", "period": 50, "column": "Close"}
            ],
            "entry_rules": {
                "condition": "SMA_20 > SMA_50"
            },
            "exit_rules": {
                "condition": "SMA_20 < SMA_50"
            }
        },
        "risk_level": "MEDIUM",
        "tags": ["test", "sma"]
    }
    
    response = client.post("/api/v1/strategies/", json=strategy_data)
    assert response.status_code == 201
    assert response.json()["name"] == "Test SMA Crossover"
    assert response.json()["id"] is not None


def test_list_strategies():
    """Test listing strategies"""
    # Create a strategy first
    strategy_data = {
        "name": "Test Strategy",
        "config": {
            "indicators": [{"type": "SMA", "period": 20}],
            "entry_rules": {"condition": "SMA_20 > Close"},
            "exit_rules": {"condition": "SMA_20 < Close"}
        }
    }
    client.post("/api/v1/strategies/", json=strategy_data)
    
    # List strategies
    response = client.get("/api/v1/strategies/")
    assert response.status_code == 200
    assert response.json()["total"] >= 1


def test_get_strategy():
    """Test getting a specific strategy"""
    # Create a strategy
    strategy_data = {
        "name": "Test Strategy",
        "config": {
            "indicators": [{"type": "SMA", "period": 20}],
            "entry_rules": {"condition": "SMA_20 > Close"},
            "exit_rules": {"condition": "SMA_20 < Close"}
        }
    }
    create_response = client.post("/api/v1/strategies/", json=strategy_data)
    strategy_id = create_response.json()["id"]
    
    # Get strategy
    response = client.get(f"/api/v1/strategies/{strategy_id}")
    assert response.status_code == 200
    assert response.json()["id"] == strategy_id


def test_update_strategy():
    """Test updating a strategy"""
    # Create a strategy
    strategy_data = {
        "name": "Original Name",
        "config": {
            "indicators": [{"type": "SMA", "period": 20}],
            "entry_rules": {"condition": "SMA_20 > Close"},
            "exit_rules": {"condition": "SMA_20 < Close"}
        }
    }
    create_response = client.post("/api/v1/strategies/", json=strategy_data)
    strategy_id = create_response.json()["id"]
    
    # Update strategy
    update_data = {"name": "Updated Name"}
    response = client.put(f"/api/v1/strategies/{strategy_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"


def test_delete_strategy():
    """Test deleting a strategy"""
    # Create a strategy
    strategy_data = {
        "name": "To Delete",
        "config": {
            "indicators": [{"type": "SMA", "period": 20}],
            "entry_rules": {"condition": "SMA_20 > Close"},
            "exit_rules": {"condition": "SMA_20 < Close"}
        }
    }
    create_response = client.post("/api/v1/strategies/", json=strategy_data)
    strategy_id = create_response.json()["id"]
    
    # Delete strategy
    response = client.delete(f"/api/v1/strategies/{strategy_id}")
    assert response.status_code == 204
    
    # Verify deletion
    get_response = client.get(f"/api/v1/strategies/{strategy_id}")
    assert get_response.status_code == 404
