# ATC Application

This repository contains a simple Flask-based air traffic control (ATC) application.
The app stores flight data and user accounts in a MySQL database.

## Prerequisites

- Python 3.9+ (earlier versions might work but aren't tested)
- MySQL server running locally (or accessible remotely)
- A virtual environment for Python (optional but recommended)

## Setup Instructions

1. **Clone the repository**

   ```bash
   git clone <repo-url>  # replace with actual URL
   cd ATC
   ```

2. **Create and activate a virtual environment** (optional but advised)

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS / Linux
   source venv/bin/activate
   ```

3. **Install required Python packages**

   ```bash
   pip install -r requirements.txt
   ```

   If a `requirements.txt` file does not exist yet, create one with the following contents:

   ```text
   Flask
   pymysql
   ```

4. **Configure database credentials**

   - The default connection settings are located in `app.py` and `setup_db.py`.
   - Modify `host`, `user`, `password` as needed, or switch to environment variables.

5. **Create the database structure**

   ```bash
   python setup_db.py
   ```

   You should see output confirming the database and tables have been created and a default admin user added.

6. **Run the application**

   ```bash
   python app.py
   ```

   Open your browser at `http://127.0.0.1:5000` and log in using the default admin credentials (`admin` / `adminpass`).

## Additional Notes

- Do **not** store plaintext passwords in production. Use a hashing library such as `werkzeug.security` or `bcrypt`.
- Customize the templates in the `templates/` directory to change the UI.
- Static assets (images, CSS, etc.) go under the `static/` directory.

---

Happy coding! ✈️