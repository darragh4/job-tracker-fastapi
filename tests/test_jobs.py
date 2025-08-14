from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# Use a separate SQLite DB for tests
TEST_DB_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override dependency before creating schema
app.dependency_overrides[get_db] = override_get_db
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_create_and_list_jobs():
    payload = {
        "title": "Backend Engineer",
        "company": "Acme",
        "status": "APPLIED",
        "notes": "Found via LinkedIn"
    }
    r = client.post("/jobs", json=payload)
    assert r.status_code == 201, r.text
    created = r.json()
    assert created["id"] >= 1
    assert created["title"] == "Backend Engineer"
    assert created["company"] == "Acme"

    r = client.get("/jobs")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1
    assert any(i["title"] == "Backend Engineer" for i in items)

def test_get_update_delete_job():
    # create one
    r = client.post("/jobs", json={"title": "DevOps", "company": "Globex"})
    assert r.status_code == 201
    job_id = r.json()["id"]

    # get it
    r = client.get(f"/jobs/{job_id}")
    assert r.status_code == 200
    assert r.json()["title"] == "DevOps"

    # update
    r = client.put(f"/jobs/{job_id}", json={"status": "INTERVIEW", "notes": "Phone screen"})
    assert r.status_code == 200
    assert r.json()["status"] == "INTERVIEW"

    # delete
    r = client.delete(f"/jobs/{job_id}")
    assert r.status_code == 204

    # confirm gone
    r = client.get(f"/jobs/{job_id}")
    assert r.status_code == 404

def test_missing_returns_404():
    r = client.get("/jobs/999999")
    assert r.status_code == 404
