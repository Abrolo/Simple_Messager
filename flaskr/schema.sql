DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS email;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE email (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  sender_id INTEGER NOT NULL,
  recipient_id INTEGER NOT NULL,
  created_at TEXT NOT NULL DEFAULT current_timestamp,
  message_subject TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY (sender_id) REFERENCES user (id)
  FOREIGN KEY (recipient_id) REFERENCES user (id)
);