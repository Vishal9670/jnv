# JNV Quiz and Test Series App

JNV - Joint NextVenture is a Flask web application for CBSE Computer Science and CUET preparation. It provides student login, manager login, test-series creation, real exam style test attempts, scoring, rank analysis, cutoff tracking, and question-wise solutions.

## Main Features

- Student signup, login, OTP verification, and result history.
- Manager login with access code and OTP verification.
- Manager test-series builder for section-wise, unit-wise, chapter-wise, and topic-wise papers.
- Editable test papers after creation.
- Time limit, positive marks, negative marks, and cutoff marks for every test.
- One-question-at-a-time exam interface with next, back, skip, question palette, attempted count, remaining count, and timer.
- Detailed result analysis with score, rank, cutoff status, positive marks, negative marks, skipped questions, and solutions.
- Home page with purpose, contact details, student feedback, faculty team, and exam preparation motive.

## Tech Stack

- Python Flask
- SQL Server through `pyodbc`
- HTML templates with Jinja
- CSS and JavaScript in `static/`

## Important Files

- `app.py` - Main Flask application, routes, authentication, test-series logic, and database schema checks.
- `database.sql` - Fresh database setup script.
- `update_database.sql` - Existing database update script.
- `templates/` - HTML pages.
- `static/style.css` - Main design and responsive styling.
- `static/script.js` - Manager question blocks and exam screen behavior.
- `run_dev_5001.py` - Helper script to run the app on port 5001.

## Manager Access

Default manager access code:

```text
JNV-MANAGER-2026
```

You can override it with the `MANAGER_ACCESS_CODE` environment variable.

## Run Locally

Install dependencies if needed:

```bash
pip install flask pyodbc werkzeug
```

Start the development server:

```bash
python run_dev_5001.py
```

Open:

```text
http://127.0.0.1:5001/
```

## Database

The app expects SQL Server database `QuizAppDB` by default. You can configure connection values with environment variables:

- `DB_SERVER`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_DRIVER`
- `FLASK_SECRET_KEY`
- `MANAGER_ACCESS_CODE`

Run `database.sql` for a fresh setup, or `update_database.sql` to update an existing database.
