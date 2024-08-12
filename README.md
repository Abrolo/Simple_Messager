# Description
This is a simple API that can handle the following:
1. Send messages from one user to another.
2. Fetch messages to one user.
3. Delete a message from the database.
4. Fetch messages between start and stop indices, ordered by time.

# Program overview
![program_chart drawio](https://github.com/user-attachments/assets/57dfc1a0-80dd-4227-b13c-506f9779d658)



# Initializing the server

## Create local environment

```sh
$ python3 -m venv .venv
```

## Activate local environment

### Windows

```sh
$ . .venv/Scripts/Activate
```

### UNIX environment

```sh
$ . .venv/bin/activate
```

### Deactivate local environment (when finished with the program)

```sh
$ deactivate
```

## Install packages

```sh
$ pip install -r requirements.txt
```

## Initialize an empty database

```sh
$ flask --app flaskr init-db
```

## Run test suite

```sh
$ pytest
```

## Run the server

```sh
flask --app flaskr run --debug
```

# cURL Commands

Open a new terminal to pass in requests to the server via cURL. Double-check that the IP addresses match.

## Register users

Users need to be registered before sending and recieving messages.

```sh
curl http://127.0.0.1:5000/register -H "Content-Type: application/json" -d'{"username": "tester1", "password": "1234"}'
curl http://127.0.0.1:5000/register -H "Content-Type: application/json" -d'{"username": "tester2", "password": "1234"}'
```

## Populate database with emails

```sh
curl http://127.0.0.1:5000/emails -H "Content-Type: application/json" -d'{"message_subject": "test", "body": "hello", "sender_username": "tester1", "recipient_username": "tester2"}'
curl http://127.0.0.1:5000/emails -H "Content-Type: application/json" -d'{"message_subject": "re:test", "body": "hello back", "sender_username": "tester2", "recipient_username": "tester1"}'
curl http://127.0.0.1:5000/emails -H "Content-Type: application/json" -d'{"message_subject": "re:test", "body": "hello back again", "sender_username": "tester1", "recipient_username": "tester2"}'
curl http://127.0.0.1:5000/emails -H "Content-Type: application/json" -d'{"message_subject": "re:test", "body": "hello back to you too", "sender_username": "tester2", "recipient_username": "tester1"}'
```

To test that new messages are received:

1. Run the get emails command further down below
2. Send in this new email:

```sh
curl http://127.0.0.1:5000/emails -H "Content-Type: application/json" -d'{"message_subject": "1234", "body": "checking that this new message was received", "sender_username": "tester1", "recipient_username": "tester2"}'
```

3. Make a new GET request and check for new message.

## Get all emails to user X

```sh
curl http://127.0.0.1:5000/emails?recipient_username=tester2
```

## Get emails with indexing

```sh
curl -X GET "http://127.0.0.1:5000/emails?start=0&stop=1&recipient_username=tester2"
```

## Delete email

```sh
curl -X DELETE http://127.0.0.1:5000/emails/2
```
