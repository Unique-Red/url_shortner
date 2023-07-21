from redroute import app, db
from redroute.models import User, Url

def test_home():
    response = app.test_client().get('/')
    assert response.status_code == 200

def test_register():
    response = app.test_client().post('/register', data={'username': 'test', 'email': 'test@gmail.com', 'password': 'test', 'confirm_password': 'test'})

    with app.app_context():
        assert User.query.count() == 1
        assert User.query.first().username == 'test'

