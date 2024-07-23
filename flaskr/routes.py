from flask import jsonify, request
from flaskr.db import get_db
from flaskr.services.email_services import EmailService

def init_app(app):
    @app.route('/')
    def hello():
        return 'Hello, World!'

    @app.route('/emails', methods=['GET', 'POST', 'DELETE'])
    def emails():
        db = get_db()

        if request.method == 'GET':
            response = get_emails(db)

        elif request.method == 'POST':
            response = send_email(request, db)

        elif request.method == 'DELETE':
            response = delete_email(request, db)

        return response

    @app.route('/register', methods=['POST'])
    def register():
        data = request.json
        db = get_db()
        db.execute('INSERT INTO user (username, password) VALUES (?, ?)', (data.get("username"), data.get("password")))

        db.commit()
        return jsonify({"message": "User registered successfully"}), 201

def delete_email(request, db):
    id = request.json.get("id")
    db.execute('DELETE FROM email WHERE id = ?', (id,))
    db.commit()
    return jsonify({"message": f"Successfully deleted email with id {id}"}), 200

def send_email(request, db):
    data = request.json
    subject = data.get('message_subject')
    body = data.get('body')
    sender_id = data.get('sender_id')
    recipient_id = data.get('recipient_id')

    db.execute(
        'INSERT INTO email (message_subject, body, sender_id, recipient_id) VALUES (?, ?, ?, ?)',
        (subject, body, sender_id, recipient_id)
    )
    db.commit()
    return jsonify({"message": "Email sent successfully"}), 201

def get_emails(db):
    email_service = EmailService(db)

    start = request.args.get('start', default=None, type=int)
    stop = request.args.get('stop', default=None, type=int)
    emails_list = email_service.get_emails(start, stop)
    return jsonify(emails_list), 200