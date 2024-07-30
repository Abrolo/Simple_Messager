### Activate local environment

. .venv/Scripts/Activate

### Run the server

flask --app flaskr run --debug

### Initialize an empty database

flask --app flaskr init-db

### Populate database with emails

curl http://127.0.0.1:5000/emails -H "Content-Type: application/json" -d'{"message_subject": "test", "body": "hello", "sender_id": "1", "recipient_id": "2"}'
curl http://127.0.0.1:5000/emails -H "Content-Type: application/json" -d'{"message_subject": "re:test", "body": "hello back", "sender_id": "2", "recipient_id": "1"}'
curl http://127.0.0.1:5000/emails -H "Content-Type: application/json" -d'{"message_subject": "re:test", "body": "hello back again", "sender_id": "1", "recipient_id": "2"}'
curl http://127.0.0.1:5000/emails -H "Content-Type: application/json" -d'{"message_subject": "re:test", "body": "hello back to you too", "sender_id": "2", "recipient_id": "1"}'

### Register users

curl http://127.0.0.1:5000/register -H "Content-Type: application/json" -d'{"username": "tester", "password": "1234"}'
curl http://127.0.0.1:5000/register -H "Content-Type: application/json" -d'{"username": "tester2", "password": "1234"}'

### Get all emails

curl http://127.0.0.1:5000/emails # GET

### Get emails with indexing

curl -X GET "http://127.0.0.1:5000/emails?start=0&stop=1"

curl -X GET "http://127.0.0.1:5000/emails" -d"start=0" -d"stop=1"

### Delete email

curl -X DELETE http://127.0.0.1:5000/emails -H "Content-Type: application/json" -d'{"id": 2}'
