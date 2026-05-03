USE QuizAppDB;
GO

IF OBJECT_ID('dbo.test_attempts', 'U') IS NULL
BEGIN
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
END
GO

IF COL_LENGTH('dbo.questions', 'subject') IS NULL
BEGIN
    ALTER TABLE questions ADD subject VARCHAR(120) NOT NULL CONSTRAINT DF_questions_subject DEFAULT 'Computer Science';
END
GO

IF COL_LENGTH('dbo.questions', 'topic') IS NULL
BEGIN
    ALTER TABLE questions ADD topic VARCHAR(120) NOT NULL CONSTRAINT DF_questions_topic DEFAULT 'General';
END
GO

IF COL_LENGTH('dbo.questions', 'solution') IS NULL
BEGIN
    ALTER TABLE questions ADD solution VARCHAR(MAX) NULL;
END
GO

IF OBJECT_ID('dbo.test_series', 'U') IS NULL
BEGIN
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
END
GO

IF OBJECT_ID('dbo.test_series_questions', 'U') IS NULL
BEGIN
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
END
GO

IF OBJECT_ID('dbo.test_series_attempts', 'U') IS NULL
BEGIN
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
END
GO

IF OBJECT_ID('dbo.test_series_answers', 'U') IS NULL
BEGIN
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
END
GO
