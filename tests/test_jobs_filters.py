from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.schemas import JobStatus

# Separate SQLite test DB
TEST_DB_URL = "sqlite:///./test_filters.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_status_enum_validation():
    bad = {"title":"X","company":"Y","status":"HIRED"}  # not in enum
    r = client.post("/jobs", json=bad)
    assert r.status_code == 422, r.text  # Pydantic enum validation triggers 422

def test_filter_by_status_and_company_and_pagination():
    # seed
    data = [
        {"title":"BE","company":"Acme","status":JobStatus.APPLIED.value},
        {"title":"FE","company":"Acme Labs","status":JobStatus.INTERVIEW.value},
        {"title":"Data","company":"Globex","status":JobStatus.INTERVIEW.value},
        {"title":"Ops","company":"Initech","status":JobStatus.REJECTED.value},
    ]
    for d in data:
        assert client.post("/jobs", json=d).status_code == 201

    # filter by status
    r = client.get("/jobs", params={"status": JobStatus.INTERVIEW.value})
    assert r.status_code == 200
    items = r.json()
    assert all(i["status"] == JobStatus.INTERVIEW.value for i in items)
    assert len(items) == 2

    # company contains
    r = client.get("/jobs", params={"company": "Acme"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 2  # "Acme" and "Acme Labs"

    # search q across fields
    r = client.get("/jobs", params={"q": "Glob"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["company"] == "Globex"

    # pagination
    r = client.get("/jobs", params={"limit": 2, "offset": 0, "sort":"id"})
    first_page = r.json()
    assert len(first_page) == 2

    r = client.get("/jobs", params={"limit": 2, "offset": 2, "sort":"id"})
    second_page = r.json()
    # pages should be disjoint
    first_ids = {i["id"] for i in first_page}
    second_ids = {i["id"] for i in second_page}
    assert first_ids.isdisjoint(second_ids)
