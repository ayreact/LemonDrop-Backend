# LemonDrop - Anonymous Messaging (Backend)

LemonDrop is a great anonymous messaging application. It allows users to register, share their profile links, and receive anonymous messages from others.

## Features

*   **User Management:** Secure registration, login, and profile management.
*   **Social Auth:** Seamless login with Google.
*   **Anonymous Messaging:** Core engine for handling message delivery and retrieval without revealing sender identity.
*   **Security:** Built on Django Rest Framework with JWT authentication.

## Tech Stack

*   **Language:** Python 3.12
*   **Framework:** Django & Django Rest Framework (DRF)
*   **Database:** PostgreSQL (Production) / SQLite(Dev)
*   **Authentication:** SimpleJWT, DJ-Rest-Auth, AllAuth

## Getting Started

### Prerequisites
*   Python 3.8+
*   pip

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd LemonDrop-BackEnd
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv lemonenv
    # Windows
    lemonenv\Scripts\activate
    # Unix/MacOS
    source lemonenv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Setup:**
    Create a `.env` file in the root directory and populate it (see `.env.example` or project settings).
    ```
    SECRET_KEY=your_secret_key
    DEBUG=True
    # ... other settings
    ```

5.  **Run Migrations:**
    ```bash
    python manage.py migrate
    ```

6.  **Start the Server:**
    ```bash
    python manage.py runserver
    ```

## Deployment

The project is configured for deployment with a `PROCFILE` for use with Gunicorn. Ensure you have the necessary environment variables set on your hosting platform.
