CREATE DATABASE QuizAppDB;
GO

USE QuizAppDB;
GO

CREATE TABLE users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT GETDATE()
);
GO

CREATE TABLE questions (
    id INT IDENTITY(1,1) PRIMARY KEY,
    subject VARCHAR(120) NOT NULL DEFAULT 'Computer Science',
    topic VARCHAR(120) NOT NULL DEFAULT 'General',
    question_text VARCHAR(500) NOT NULL,
    option_a VARCHAR(200) NOT NULL,
    option_b VARCHAR(200) NOT NULL,
    option_c VARCHAR(200) NOT NULL,
    option_d VARCHAR(200) NOT NULL,
    correct_answer CHAR(1) NOT NULL CHECK (correct_answer IN ('A', 'B', 'C', 'D')),
    solution VARCHAR(MAX) NULL,
    created_at DATETIME NOT NULL DEFAULT GETDATE()
);
GO

CREATE TABLE test_attempts (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    total_questions INT NOT NULL,
    correct_answers INT NOT NULL,
    wrong_answers INT NOT NULL,
    unanswered INT NOT NULL,
    score INT NOT NULL,
    max_score INT NOT NULL,
    percentage DECIMAL(5,2) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT GETDATE(),
    CONSTRAINT FK_test_attempts_users FOREIGN KEY (user_id) REFERENCES users(id)
);
GO

CREATE TABLE test_series (
    id INT IDENTITY(1,1) PRIMARY KEY,
    title VARCHAR(180) NOT NULL,
    subject VARCHAR(120) NOT NULL,
    section_name VARCHAR(120) NULL,
    unit_name VARCHAR(120) NULL,
    chapter_name VARCHAR(120) NULL,
    topic VARCHAR(120) NULL,
    description VARCHAR(800) NULL,
    time_limit_minutes INT NOT NULL DEFAULT 30,
    positive_marks DECIMAL(6,2) NOT NULL DEFAULT 1,
    negative_marks DECIMAL(6,2) NOT NULL DEFAULT 0,
    cutoff_marks DECIMAL(7,2) NOT NULL DEFAULT 0,
    manager_name VARCHAR(120) NULL,
    created_at DATETIME NOT NULL DEFAULT GETDATE()
);
GO

CREATE TABLE test_series_questions (
    id INT IDENTITY(1,1) PRIMARY KEY,
    test_series_id INT NOT NULL,
    question_order INT NOT NULL,
    question_text VARCHAR(1000) NOT NULL,
    option_a VARCHAR(500) NOT NULL,
    option_b VARCHAR(500) NOT NULL,
    option_c VARCHAR(500) NOT NULL,
    option_d VARCHAR(500) NOT NULL,
    correct_answer CHAR(1) NOT NULL CHECK (correct_answer IN ('A', 'B', 'C', 'D')),
    solution VARCHAR(MAX) NULL,
    CONSTRAINT FK_test_series_questions_series FOREIGN KEY (test_series_id) REFERENCES test_series(id)
);
GO

CREATE TABLE test_series_attempts (
    id INT IDENTITY(1,1) PRIMARY KEY,
    test_series_id INT NOT NULL,
    user_id INT NOT NULL,
    total_questions INT NOT NULL,
    correct_answers INT NOT NULL,
    wrong_answers INT NOT NULL,
    unanswered INT NOT NULL,
    attempted INT NOT NULL,
    skipped INT NOT NULL,
    positive_score DECIMAL(7,2) NOT NULL,
    negative_score DECIMAL(7,2) NOT NULL,
    score DECIMAL(7,2) NOT NULL,
    max_score DECIMAL(7,2) NOT NULL,
    percentage DECIMAL(5,2) NOT NULL,
    cutoff_marks DECIMAL(7,2) NOT NULL,
    passed BIT NOT NULL,
    time_limit_minutes INT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT GETDATE(),
    CONSTRAINT FK_test_series_attempts_series FOREIGN KEY (test_series_id) REFERENCES test_series(id),
    CONSTRAINT FK_test_series_attempts_users FOREIGN KEY (user_id) REFERENCES users(id)
);
GO

CREATE TABLE test_series_answers (
    id INT IDENTITY(1,1) PRIMARY KEY,
    attempt_id INT NOT NULL,
    question_id INT NOT NULL,
    selected_answer CHAR(1) NULL,
    is_correct BIT NOT NULL,
    marks DECIMAL(7,2) NOT NULL,
    CONSTRAINT FK_test_series_answers_attempt FOREIGN KEY (attempt_id) REFERENCES test_series_attempts(id),
    CONSTRAINT FK_test_series_answers_question FOREIGN KEY (question_id) REFERENCES test_series_questions(id)
);
GO

INSERT INTO questions
    (subject, topic, question_text, option_a, option_b, option_c, option_d, correct_answer)
VALUES
    ('Class 11 Computer Science', 'Python', 'Which language is used with Flask?', 'Python', 'Java', 'C++', 'Ruby', 'A'),
    ('Class 10 Computer Applications', 'HTML', 'What does HTML stand for?', 'Hyper Trainer Marking Language', 'Hyper Text Markup Language', 'High Text Machine Language', 'Hyper Tool Multi Language', 'B'),
    ('Class 12 Computer Science', 'SQL', 'Which SQL command reads data from a table?', 'INSERT', 'UPDATE', 'SELECT', 'DELETE', 'C');
GO
