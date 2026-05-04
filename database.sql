-- SQLite Database Schema for Quiz Application

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT DEFAULT 'Computer Science',
    topic TEXT DEFAULT 'General',
    question_text TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_answer TEXT NOT NULL CHECK (correct_answer IN ('A', 'B', 'C', 'D')),
    solution TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE test_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    total_questions INTEGER NOT NULL,
    correct_answers INTEGER NOT NULL,
    wrong_answers INTEGER NOT NULL,
    unanswered INTEGER NOT NULL,
    score REAL NOT NULL,
    max_score REAL NOT NULL,
    percentage REAL NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE test_series (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    subject TEXT NOT NULL,
    section_name TEXT,
    unit_name TEXT,
    chapter_name TEXT,
    topic TEXT,
    description TEXT,
    time_limit_minutes INTEGER DEFAULT 30,
    positive_marks REAL DEFAULT 1.0,
    negative_marks REAL DEFAULT 0.0,
    cutoff_marks REAL DEFAULT 0.0,
    manager_name TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE test_series_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_series_id INTEGER NOT NULL,
    question_order INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_answer TEXT NOT NULL CHECK (correct_answer IN ('A', 'B', 'C', 'D')),
    solution TEXT,
    FOREIGN KEY (test_series_id) REFERENCES test_series(id)
);

CREATE TABLE test_series_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_series_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    total_questions INTEGER NOT NULL,
    correct_answers INTEGER NOT NULL,
    wrong_answers INTEGER NOT NULL,
    unanswered INTEGER NOT NULL,
    attempted INTEGER NOT NULL,
    skipped INTEGER NOT NULL,
    positive_score REAL NOT NULL,
    negative_score REAL NOT NULL,
    score REAL NOT NULL,
    max_score REAL NOT NULL,
    percentage REAL NOT NULL,
    cutoff_marks REAL NOT NULL,
    passed INTEGER NOT NULL,
    time_limit_minutes INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_series_id) REFERENCES test_series(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE test_series_answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    attempt_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    selected_answer TEXT,
    is_correct INTEGER NOT NULL,
    marks REAL NOT NULL,
    FOREIGN KEY (attempt_id) REFERENCES test_series_attempts(id),
    FOREIGN KEY (question_id) REFERENCES test_series_questions(id)
);

INSERT INTO questions
    (subject, topic, question_text, option_a, option_b, option_c, option_d, correct_answer)
VALUES
    ('Class 11 Computer Science', 'Python', 'Which language is used with Flask?', 'Python', 'Java', 'C++', 'Ruby', 'A'),
    ('Class 10 Computer Applications', 'HTML', 'What does HTML stand for?', 'Hyper Trainer Marking Language', 'Hyper Text Markup Language', 'High Text Machine Language', 'Hyper Tool Multi Language', 'B'),
    ('Class 12 Computer Science', 'SQL', 'Which SQL command reads data from a table?', 'INSERT', 'UPDATE', 'SELECT', 'DELETE', 'C');
