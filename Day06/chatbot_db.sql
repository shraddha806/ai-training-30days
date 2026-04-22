CREATE DATABASE chatbot_db;



CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT DEFAULT 'employee',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title TEXT,
    started_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conv_id INTEGER REFERENCES conversations(id),
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    tokens INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE feedback (
    id SERIAL PRIMARY KEY,
    msg_id INTEGER REFERENCES messages(id),
    rating INTEGER,
    comment TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);



INSERT INTO users (email, full_name) VALUES
('shraddha@acme.in', 'Shraddha P'),
('harshini@acme.in', 'Harshini R'),
('rahul@acme.in', 'Rahul K');

INSERT INTO conversations (user_id, title) VALUES
(1, 'Leave policy'),
(2, 'Payroll issue'),
(1, 'Benefits query');

INSERT INTO messages (conv_id, role, content, tokens) VALUES
(1, 'user', 'How many casual leaves?', 10),
(1, 'bot', '12 per year.', 15),
(2, 'user', 'Salary not credited', 9),
(2, 'bot', 'Please raise ticket.', 11),
(3, 'user', 'Tell me insurance benefits', 12),
(3, 'bot', 'Health insurance included.', 14);

INSERT INTO feedback (msg_id, rating, comment) VALUES
(2, 5, 'Helpful'),
(4, 4, 'Good'),
(6, 3, 'Okay');


-- Query 1: Count Messages Per User
SELECT u.full_name, COUNT(m.id) AS msgs
FROM users u
JOIN conversations c ON c.user_id = u.id
JOIN messages m ON m.conv_id = c.id
GROUP BY u.full_name;

-- Query 2: Last 10 Messages in Conversation
SELECT role, content, created_at
FROM messages
WHERE conv_id = 1
ORDER BY created_at DESC
LIMIT 10;

-- Query 3: Average Rating Per Day
SELECT DATE(created_at) AS day,
AVG(rating) AS avg_rating
FROM feedback
GROUP BY DATE(created_at);

--Query 4: Users With No Conversations
SELECT u.full_name
FROM users u
LEFT JOIN conversations c ON c.user_id = u.id
WHERE c.id IS NULL;

--Query 5: Top Rated Reply
SELECT m.content, f.rating
FROM messages m
JOIN feedback f ON f.msg_id = m.id
ORDER BY f.rating DESC
LIMIT 1;




-------Indexes for performance-------
CREATE INDEX idx_messages_conv_id
ON messages(conv_id);