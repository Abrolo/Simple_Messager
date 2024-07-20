from flask import jsonify, request
from flaskr.db import get_db

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
    subject = data.get('subject')
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
    emails = db.execute(
        'SELECT e.id, message_subject, body, created_at, sender_id, username'
        ' FROM email e JOIN user u ON e.sender_id = u.id'
        ' ORDER BY created_at DESC'
    ).fetchall()
    emails_list = [dict(email) for email in emails]
    return jsonify(emails_list), 200