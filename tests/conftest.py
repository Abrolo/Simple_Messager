import os
import tempfile
import pytest
from flask import Flask, jsonify, request
from flaskr import create_app
from flaskr.db import get_db, init_db

@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })

    with app.app_context():
        init_db()

    yield app

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def register_users(client):
    # Define and register users
    user1 = {
        "username": "tester1",
        "password": "1234"
    }
    user2 = {
        "username": "tester2",
        "password": "1234"
    }

    client.post('/register', json=user1)
    client.post('/register', json=user2)
    
    # Optionally, you can return user data if needed
    return user1, user2