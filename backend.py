from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)


# =====================================================
# MYSQL SETTINGS
# =====================================================

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "1234"

DATABASE_NAME = "localconnect"


# =====================================================
# CREATE DATABASE
# =====================================================

def create_database():

    try:

        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD
        )

        cursor = connection.cursor()

        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}"
        )

        cursor.close()
        connection.close()

        print("Database checked successfully.")

    except Error as error:

        print("--------------------------------")
        print("MYSQL DATABASE ERROR:")
        print(error)
        print("--------------------------------")

        raise


# =====================================================
# DATABASE CONNECTION
# =====================================================

def get_db_connection():

    print("Connecting to MySQL...")

    connection = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="1234",
        database="localconnect"
    )

    print("Connected to MySQL!")

    return connection


# =====================================================
# CREATE USERS TABLE
# =====================================================

def create_users_table():

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(150) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """

        cursor.execute(query)

        connection.commit()

        cursor.close()
        connection.close()

        print("Users table checked successfully.")

    except Error as error:

        print("--------------------------------")
        print("USERS TABLE ERROR:")
        print(error)
        print("--------------------------------")

        raise


# =====================================================
# TEST DATABASE
# =====================================================

@app.route("/test-db", methods=["GET"])
def test_db():

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT 1")

        result = cursor.fetchone()

        cursor.close()
        connection.close()

        return jsonify({
            "success": True,
            "message": "MySQL connection successful",
            "result": result
        })

    except Error as error:

        print("DATABASE TEST ERROR:", error)

        return jsonify({
            "success": False,
            "message": "MySQL connection failed",
            "error": str(error)
        }), 500


# =====================================================
# REGISTER
# =====================================================

@app.route("/register", methods=["POST"])
def register():

    try:
        data = request.get_json()

        print("\n========== REGISTER REQUEST ==========")
        print("Data received:", data)

        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        if not name or not email or not password:
            print("Missing registration fields")

            return jsonify({
                "success": False,
                "message": "All fields are required"
            }), 400

        print("Trying MySQL connection...")

        connection = get_db_connection()

        print("MySQL connection SUCCESS!")

        cursor = connection.cursor(dictionary=True)

        print("Checking email...")

        cursor.execute(
            "SELECT id FROM users WHERE email = %s",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:

            cursor.close()
            connection.close()

            return jsonify({
                "success": False,
                "message": "Email already registered"
            }), 409

        print("Hashing password...")

        hashed_password = generate_password_hash(password)

        print("Inserting user...")

        cursor.execute(
            """
            INSERT INTO users (name, email, password)
            VALUES (%s, %s, %s)
            """,
            (name, email, hashed_password)
        )

        connection.commit()

        print("USER INSERTED SUCCESSFULLY!")

        cursor.close()
        connection.close()

        return jsonify({
            "success": True,
            "message": "Registration successful"
        }), 201

    except Exception as error:

        import traceback

        print("\n========================================")
        print("       ACTUAL REGISTER ERROR")
        print("========================================")

        print("ERROR:", error)

        traceback.print_exc()

        print("========================================\n")

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500
# =====================================================
# LOGIN
# =====================================================

@app.route("/login", methods=["POST"])
def login():

    try:

        data = request.get_json()

        email = data.get("email")
        password = data.get("password")

        if not email or not password:

            return jsonify({
                "success": False,
                "message": "Email and password are required"
            }), 400

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, name, email, password
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if not user:

            return jsonify({
                "success": False,
                "message": "Invalid email or password"
            }), 401

        if check_password_hash(user["password"], password):

            return jsonify({
                "success": True,
                "message": "Login successful",
                "user": {
                    "id": user["id"],
                    "name": user["name"],
                    "email": user["email"]
                }
            }), 200

        return jsonify({
            "success": False,
            "message": "Invalid email or password"
        }), 401

    except Error as error:

        print("--------------------------------")
        print("LOGIN MYSQL ERROR:")
        print(error)
        print("--------------------------------")

        return jsonify({
            "success": False,
            "message": "Database error",
            "error": str(error)
        }), 500


# =====================================================
# START SERVER
# =====================================================

if __name__ == "__main__":

    print("")
    print("========================================")
    print("       LOCALCONNECT BACKEND")
    print("========================================")
    print("")

    try:

        # Create database
        create_database()

        # Create users table
        create_users_table()

        print("")
        print("MySQL is ready!")
        print("Database:", DATABASE_NAME)
        print("")

    except Exception as error:

        print("")
        print("MYSQL SETUP FAILED")
        print("ERROR:", error)
        print("")
        print("Check your MySQL username/password.")
        print("")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )