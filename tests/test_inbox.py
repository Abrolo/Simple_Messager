def test_register_user(client, app):
    """
    Test the user registration endpoint.

    Args:
        client: The test client for making requests.
        app: The application instance.

    Steps:
        1. Prepare user data with a username and password.
        2. Make a POST request to the '/register' endpoint with the user data.
        3. Assert that the response status code is 201 (Created).
        4. Assert that the response data contains the message 'User registered successfully'.
    """
    user_data = {
        "username": "tester1",
        "password": "1234"
    }
    
    response = client.post('/register', json=user_data)
    
    assert response.status_code == 201
    assert b'User registered successfully' in response.data


def test_get_empty_email_db(client, register_users):
    """
    Test the email fetching endpoint when the database is empty.

    Args:
        client: The test client for making requests.
        register_users: Fixture to register users before the test.

    Steps:
        1. Ensure users are registered.
        2. Make a GET request to the '/emails' endpoint for a specific recipient.
        3. Assert that the response status code is 200 (OK).
        4. Assert that the response is in JSON format.
        5. Assert that the emails list is empty.
    """
    _ = register_users
    recipient_username = "tester2"
    response = client.get(f'/emails?recipient_username={recipient_username}')
    
    assert response.status_code == 200
    assert response.is_json
    
    emails = response.get_json()
    assert isinstance(emails, list)
    assert len(emails) == 0


def test_get_indexed_emails(client, populate_emails, register_users):
    """
    Test fetching a range of emails from the database.

    Args:
        client: The test client for making requests.
        populate_emails: Fixture to populate the database with emails.
        register_users: Fixture to register users before the test.

    Steps:
        1. Ensure the database is populated with emails and users are registered.
        2. Define the range (start, stop) of emails to fetch.
        3. Make a GET request to the '/emails' endpoint with the start, stop, and recipient username.
        4. Assert that the number of emails fetched matches the defined range.
        5. Assert that the emails are sorted by the 'created_at' field in descending order.
    """
    _ = populate_emails
    _ = register_users
    start, stop = 3, 5
    num_of_emails = stop - start
    recipient_username = "tester2"
    
    response = client.get(f'/emails?start={start}&stop={stop}&recipient_username={recipient_username}')
    emails = response.get_json()
    
    assert num_of_emails == len(emails)
    for i in range(len(emails) - 1):
        assert emails[i]["created_at"] <= emails[i + 1]["created_at"]


def test_get_all_emails_to_user_x(client, populate_emails, register_users):
    """
    Test fetching all emails sent to a specific user.

    Args:
        client: The test client for making requests.
        populate_emails: Fixture to populate the database with emails.
        register_users: Fixture to register users before the test.

    Steps:
        1. Ensure the database is populated with emails and users are registered.
        2. Define the recipient username.
        3. Make a GET request to the '/emails' endpoint for the specified recipient.
        4. Assert that the response status code is 200 (OK).
        5. Assert that all fetched emails have the correct recipient username.
    """
    _ = populate_emails
    _ = register_users
    recipient_username = "tester1"
    
    response = client.get(f'/emails?recipient_username={recipient_username}')
    emails = response.get_json()
    
    assert response.status_code == 200
    for email in emails:
        assert email["recipient_username"] == recipient_username

def test_get_emails_with_empty_recipient(client, populate_emails, register_users):
    """
    Test the behavior when querying emails with an empty recipient username.

    Args:
        client: The test client for sending HTTP requests.
        populate_emails: Fixture to populate the database with test emails.
        register_users: Fixture to register test users.
    """
    _ = populate_emails
    _ = register_users
    
    # Send a GET request with an empty recipient_username
    response = client.get('/emails?recipient_username=')
    
    # Check if the status code is 400 Bad Request
    assert response.status_code == 400

    # Check if the response is JSON
    assert response.is_json
    
    # Get the response JSON data
    response_data = response.get_json()
    
    # Verify the error message in the response
    assert "error" in response_data
    assert response_data["error"] == "Recipient username is required."
    
def test_get_emails_to_non_existing_users(client, populate_emails, register_users):
    """
    Test the behavior when querying emails with a non-existent username.

    Args:
        client: The test client for sending HTTP requests.
        populate_emails: Fixture to populate the database with test emails.
        register_users: Fixture to register test users.
    """
    _ = populate_emails
    _ = register_users
    
    # Send a GET request with an empty recipient_username
    response = client.get('/emails?recipient_username=thisUserDoesNotExist')
    
    # Check if the status code is 404 Not Found
    assert response.status_code == 404

    # Check if the response is JSON
    assert response.is_json
    
    # Get the response JSON data
    response_data = response.get_json()
    
    # Verify the error message in the response
    assert "error" in response_data
    assert response_data["error"] == "Username does not exist."



def test_send_email(client, register_users):
    """
    Test the email sending functionality.

    Args:
        client: The test client for making requests.
        register_users: Fixture to register users before the test.

    Steps:
        1. Ensure users are registered.
        2. Define the email data to be sent.
        3. Make a POST request to the '/emails' endpoint with the email data.
        4. Make a GET request to the '/emails' endpoint for the recipient.
        5. Assert that the sent email is present in the fetched emails.
    """
    _, _ = register_users
    recipient_username = "tester2"
    
    new_email = {
        'message_subject': 'Test Subject',
        'body': 'Test Body',
        'sender_username': "tester1",
        'recipient_username': recipient_username,
    }
    client.post('/emails', json=new_email)
    
    response = client.get(f'/emails?recipient_username={recipient_username}')
    emails = response.get_json()
    
    assert any(email['message_subject'] == 'Test Subject' for email in emails)


def test_delete_email(client, register_users):
    """
    Test the email deletion functionality.

    Args:
        client: The test client for making requests.
        register_users: Fixture to register users before the test.

    Steps:
        1. Ensure users are registered.
        2. Define the email data to be sent and send the email.
        3. Make a GET request to fetch the email and extract its ID.
        4. Make a DELETE request to the '/emails' endpoint with the email ID.
        5. Assert that the response status code is 200 (OK).
        6. Make another GET request to ensure the email has been deleted.
        7. Assert that the deleted email is no longer present in the fetched emails.
    """
    _, _ = register_users
    recipient_username = "tester2"
    
    new_email = {
        'message_subject': 'Test Subject',
        'body': 'Test Body',
        'sender_username': "tester1",
        'recipient_username': recipient_username,
    }
    client.post('/emails', json=new_email)

    response = client.get(f'/emails?recipient_username={recipient_username}')
    email = response.get_json()[0]
    email_id = email['id']
    
    response = client.delete('/emails', json={'id': email_id})
    assert response.status_code == 200
    
    response = client.get(f'/emails?recipient_username={recipient_username}')
    emails = response.get_json()
    assert not any(e['id'] == email_id for e in emails)

def test_delete_non_existent_email(client):
    response = client.delete('/emails', json={'id': -1})
    assert response.status_code == 404