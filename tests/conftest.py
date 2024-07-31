import os
import tempfile
import pytest
from flask import Flask, jsonify, request
from flaskr import create_app
from flaskr.db import get_db, init_db
from faker import Faker

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

    response = client.post('/register', json=user1)
    assert response.status_code == 201
    
    response = client.post('/register', json=user2)
    assert response.status_code == 201
    
    # Optionally, you can return user data if needed
    return user1, user2

@pytest.fixture
def populate_emails(client, register_users):
    _, _ = register_users
    fake = Faker()
    num_of_emails = 10
    for _ in range(num_of_emails):
        email = {
                "message_subject": fake.sentence(), "body": fake.text(), "sender_username": "tester1", "recipient_username": "tester2"
        }
        response = client.post('/emails', json=email)
        assert response.status_code == 201
    return num_of_emails