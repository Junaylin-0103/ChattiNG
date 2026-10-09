# ChattiNG

A lightweight real-time chat application built with Flask, Flask-SocketIO, SQLite, HTML, CSS, and JavaScript.

## Features

- User registration and login
- Real-time message broadcasting with Socket.IO
- Image sharing
- Voice message sharing
- Admin ban functionality
- SQLite-backed user and message storage
- CSRF protection on login/logout/ban
- Secure password hashing using Werkzeug

## Project structure

```text
ChattiNG/
├── app.py
├── database.db
├── requirements.txt
├── .env.example
├── .gitignore
├── static/
│   ├── uploads/
│   └── script.js
├── templates/
│   └── index.html
└── README.md
```

## Quick start

1. Clone or open the project.
2. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure environment variables.

```bash
cp .env.example .env
```

Then edit `.env` with your own values.

5. Run the app:

```bash
python app.py
```

6. Open the app in your browser:

```text
http://127.0.0.1:5000
```

## Environment variables

Example:

```bash
SECRET_KEY=your_super_secret_key_here
ADMIN_USERNAME=Junaylin
ADMIN_PASSWORD=your_strong_admin_password_here
```

## Admin account

The app creates an admin user automatically if it does not exist.

Default values:

- Username: `Junaylin`
- Password: `change_this_password`

It is strongly recommended to set your own values using environment variables before deployment.

## Security notes

- Passwords are hashed before storage.
- CSRF tokens are required for login/logout/ban requests.
- File uploads are limited to image/audio types and size limits.
- The app is not production-ready for public deployment without HTTPS and additional hardening.

## License

This project is provided as-is for learning and local development.
