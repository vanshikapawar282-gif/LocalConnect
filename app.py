from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import mysql.connector
import os
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from pathlib import Path

app = Flask(__name__, static_folder=None)
CORS(app)

# ==================================================
# MYSQL SETTINGS
# ==================================================

MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD")
MYSQL_PORT = int(os.environ.get("MYSQL_PORT", "3306"))
DATABASE_NAME = os.environ.get("DATABASE_NAME", "localconnect")


BASE_DIR = Path(__file__).resolve().parent


# ==================================================
# DATABASE CONNECTION
# ==================================================

def get_db_connection():

    return mysql.connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=DATABASE_NAME,
        connection_timeout=15,
        ssl_ca=str(BASE_DIR / "ca.pem"),
        ssl_verify_cert=True,
        ssl_verify_identity=True
    )

# ==================================================
# CREATE TABLES IN THE EXISTING DATABASE
# ==================================================

def setup_database():

    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(150) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Marketplace table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS marketplace (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                product VARCHAR(100) NOT NULL,
                price DECIMAL(10,2) NOT NULL
            )
        """)

        # Park reports table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS park_reports (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                issue TEXT NOT NULL,
                location VARCHAR(200) NOT NULL
            )
        """)

        # Animal adoption table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS adoptions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                animal VARCHAR(100) NOT NULL,
                phone VARCHAR(20) NOT NULL
            )
        """)

        # Senior citizen support table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS senior_support (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                help TEXT NOT NULL,
                phone VARCHAR(20) NOT NULL
            )
        """)

        connection.commit()

        print("All LocalConnect tables are ready!")

    except Error:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()

# ==================================================
# REGISTER
# ==================================================

@app.route("/register", methods=["POST"])
def register():

    connection = None
    cursor = None

    try:

        data = request.get_json(silent=True) or {}

        name = data.get("name", "").strip()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        if not name or not email or not password:

            return jsonify({
                "success": False,
                "message": "Please fill in all fields"
            }), 400

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT id FROM users WHERE email = %s",
            (email,)
        )

        if cursor.fetchone():

            return jsonify({
                "success": False,
                "message": "Email already registered"
            }), 409

        hashed_password = generate_password_hash(password)

        cursor.execute("""
            INSERT INTO users (name, email, password)
            VALUES (%s, %s, %s)
        """, (name, email, hashed_password))

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Registration successful! Please log in."
        }), 201

    except Error:

        if connection:
            connection.rollback()

        app.logger.exception("Registration failed")

        return jsonify({
            "success": False,
            "message": "Registration failed. Check the database connection."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# ==================================================
# LOGIN
# ==================================================

@app.route("/login", methods=["POST"])
def login():

    connection = None
    cursor = None

    try:

        data = request.get_json(silent=True) or {}

        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        if not email or not password:

            return jsonify({
                "success": False,
                "message": "Email and password are required"
            }), 400

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, name, email, password
            FROM users
            WHERE email = %s
        """, (email,))

        user = cursor.fetchone()

        if not user or not check_password_hash(
            user["password"], password
        ):

            return jsonify({
                "success": False,
                "message": "Invalid email or password"
            }), 401

        return jsonify({
            "success": True,
            "message": "Login successful",
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"]
            }
        }), 200

    except Error:

        app.logger.exception("Login failed")

        return jsonify({
            "success": False,
            "message": "Login failed because of a database error"
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# ==================================================
# MARKETPLACE
# ==================================================

@app.route("/add-product", methods=["POST"])
def add_product():

    connection = None
    cursor = None

    try:

        data = request.get_json(silent=True) or {}

        name = data.get("name", "").strip()
        product = data.get("product", "").strip()
        price = data.get("price", "")

        if not name or not product or price == "":

            return jsonify({
                "message": "Please fill in all fields"
            }), 400

        price = float(price)

        if price < 0:
            return jsonify({
                "message": "Price cannot be negative"
            }), 400

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO marketplace (name, product, price)
            VALUES (%s, %s, %s)
        """, (name, product, price))

        connection.commit()

        return jsonify({
            "message": "Product added successfully!"
        }), 201

    except (Error, ValueError):

        if connection:
            connection.rollback()

        app.logger.exception("Marketplace error")

        return jsonify({
            "message": "Could not add product. Check the entered price and database."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# ==================================================
# PARK ISSUE REPORT
# ==================================================

@app.route("/report-issue", methods=["POST"])
def report_issue():

    connection = None
    cursor = None

    try:

        data = request.get_json(silent=True) or {}

        name = data.get("name", "").strip()
        issue = data.get("issue", "").strip()
        location = data.get("location", "").strip()

        if not name or not issue or not location:

            return jsonify({
                "message": "Please fill in all fields"
            }), 400

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO park_reports (name, issue, location)
            VALUES (%s, %s, %s)
        """, (name, issue, location))

        connection.commit()

        return jsonify({
            "message": "Park issue reported successfully!"
        }), 201

    except Error:

        if connection:
            connection.rollback()

        app.logger.exception("Park report error")

        return jsonify({
            "message": "Could not save the park report"
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# ==================================================
# ANIMAL ADOPTION
# ==================================================

@app.route("/adopt", methods=["POST"])
def adopt():

    connection = None
    cursor = None

    try:

        data = request.get_json(silent=True) or {}

        name = data.get("name", "").strip()
        animal = data.get("animal", "").strip()
        phone = data.get("phone", "").strip()

        if not name or not animal or not phone:

            return jsonify({
                "message": "Please fill in all fields"
            }), 400

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO adoptions (name, animal, phone)
            VALUES (%s, %s, %s)
        """, (name, animal, phone))

        connection.commit()

        return jsonify({
            "message": "Adoption request submitted successfully!"
        }), 201

    except Error:

        if connection:
            connection.rollback()

        app.logger.exception("Adoption error")

        return jsonify({
            "message": "Could not save adoption request"
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# ==================================================
# SENIOR CITIZEN SUPPORT
# ==================================================

@app.route("/senior-help", methods=["POST"])
def senior_help():

    connection = None
    cursor = None

    try:

        data = request.get_json(silent=True) or {}

        name = data.get("name", "").strip()
        help_request = data.get("help", "").strip()
        phone = data.get("phone", "").strip()

        if not name or not help_request or not phone:

            return jsonify({
                "message": "Please fill in all fields"
            }), 400

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO senior_support (name, help, phone)
            VALUES (%s, %s, %s)
        """, (name, help_request, phone))

        connection.commit()

        return jsonify({
            "message": "Support request submitted successfully!"
        }), 201

    except Error:

        if connection:
            connection.rollback()

        app.logger.exception("Senior support error")

        return jsonify({
            "message": "Could not save support request"
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# ==================================================
# OPEN YOUR HOMEPAGE
# ==================================================

@app.route("/")
def home():

    if (BASE_DIR / "ty.html").exists():
        return send_from_directory(str(BASE_DIR), "ty.html")

    if (BASE_DIR / "index.html").exists():
        return send_from_directory(str(BASE_DIR), "index.html")

    return jsonify({
        "message": "Backend is running, but homepage HTML was not found"
    })


# Serve HTML, CSS and JS files from the project folder
@app.route("/<path:filename>")
def serve_files(filename):

    return send_from_directory(str(BASE_DIR), filename)


# ==================================================
# RUN SERVER
# ==================================================

if __name__ == "__main__":

    try:
        setup_database()
        print("LocalConnect database tables are ready!")

    except Error:
        app.logger.exception("MySQL setup failed")
        raise SystemExit(1)

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )