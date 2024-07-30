def test_register_user(client, app):
    user_data = {
        "username": "tester1",
        "password": "1234"
    }
    
    response = client.post('/register', json=user_data)
    
    assert response.status_code == 201
    
    assert b'User registered successfully' in response.data


def test_get_empty_email_db(client):
    # Initially, the database should have no emails
    response = client.get('/emails')
    assert response.status_code == 200
    assert response.is_json
    emails = response.get_json()
    assert isinstance(emails, list)
    assert len(emails) == 0

def test_get_all_emails(client, populate_emails):
    num_of_emails = populate_emails
    response = client.get('/emails')
    assert response.status_code == 200
    
    emails = response.get_json()
    assert (num_of_emails) == len(emails)
    
def test_get_indexed_emails(client, populate_emails):
    _ = populate_emails
    start = 3
    stop = 7
    num_of_emails = stop-start
    
    response = client.get(f'/emails?start={start}&stop={stop}')
    emails = response.get_json()
    
    ### TODO make more asserts
    assert num_of_emails == len(emails)

def test_send_email(client, register_users):
    _, _ = register_users
    
    new_email = {
        'message_subject': 'Test Subject',
        'body': 'Test Body',
        'sender_id': 1,
        'recipient_id': 2,
    }
    client.post('/emails', json=new_email)
    
    response = client.get('/emails')
    emails = response.get_json()
    
    ### TODO change the assert
    assert any(email['message_subject'] == 'Test Subject' for email in emails)
    
def test_delete_email(client, register_users):
    _, _ = register_users
    
    new_email = {
        'message_subject': 'Test Subject',
        'body': 'Test Body',
        'sender_id': 1,
        'recipient_id': 2,
    }
    client.post('/emails', json=new_email)

    response = client.get('/emails')
    email = response.get_json()[0]
    print(response)
    email_id = email['id']
    
    response = client.delete('/emails', json={'id': email_id})
    assert response.status_code == 200
    
    response = client.get('/emails')
    emails = response.get_json()
    assert not any(e['id'] == email_id for e in emails)
        

def test_register(client):
    new_user = {
        'username': 'testuser',
        'password': 'testpassword'
    }
    response = client.post('/register', json=new_user)
    assert response.status_code == 201
    assert response.get_json() == {"message": "User registered successfully"}