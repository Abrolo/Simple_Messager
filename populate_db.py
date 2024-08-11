import requests
import json
import random

# Define the base URL for the API
BASE_URL = 'http://127.0.0.1:5000'

# Function to register a user
def register_user(username, password):
    url = f"{BASE_URL}/register"
    payload = json.dumps({
        "username": username,
        "password": password
    })
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, data=payload)
    print(f"Register User Response: {response.status_code} - {response.text}")

# Function to send an email
def send_email(subject, body, sender, recipient):
    url = f"{BASE_URL}/emails"
    payload = json.dumps({
        "message_subject": subject,
        "body": body,
        "sender_username": sender,
        "recipient_username": recipient
    })
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, data=payload)
    print(f"Send Email Response: {response.status_code} - {response.text}")

# Generate random data
def generate_random_data():
    subjects = ["Hello", "Test Email", "Random Subject", "Another Email"]
    bodies = ["This is a test email body.", "Another body text.", "Yet another message.", "Body content."]
    
    usernames = [f"user{i}" for i in range(1, 11)]  # Create 10 unique users
    passwords = ["password" + str(i) for i in range(1, 11)]  # Corresponding passwords

    # Register users
    for username, password in zip(usernames, passwords):
        register_user(username, password)
    
    # Send 10 messages to each user
    for sender in usernames:
        recipients = [recipient for recipient in usernames if recipient != sender]
        for _ in range(10):  # Send 10 emails per user
            recipient = random.choice(recipients)
            subject = random.choice(subjects)
            body = random.choice(bodies)
            send_email(subject, body, sender, recipient)

if __name__ == "__main__":
    generate_random_data()
