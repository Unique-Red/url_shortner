import pytest
from redroute import app, db


@pytest.fixture()
def app():
    with app.app_context():
        db.create_all()

    print ("app created")
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()
    