import os
import socket
import urllib.request
import logging
from flask import Flask, render_template, request, flash, redirect, url_for
import pymysql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret_key_for_dev")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database connection details
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "userdata")

def get_instance_info():
    try:
        req = urllib.request.Request("http://169.254.169.254/latest/api/token", method="PUT")
        req.add_header("X-aws-ec2-metadata-token-ttl-seconds", "21600")
        with urllib.request.urlopen(req, timeout=1) as response:
            token = response.read().decode()
        req2 = urllib.request.Request("http://169.254.169.254/latest/meta-data/instance-id")
        req2.add_header("X-aws-ec2-metadata-token", token)
        with urllib.request.urlopen(req2, timeout=1) as response:
            return response.read().decode()
    except Exception:
        return socket.gethostname()

INSTANCE_NAME = get_instance_info()

def get_db_connection():
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except pymysql.MySQLError as e:
        logging.error(f"Database connection failed: {e}")
        return None

@app.route("/", methods=["GET"])
def index():
    users = []
    connection = get_db_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users ORDER BY id DESC")
                users = cursor.fetchall()
        except Exception as e:
            logging.error(f"Failed to fetch users: {e}")
        finally:
            connection.close()
    
    return render_template("index.html", instance_name=INSTANCE_NAME, users=users)

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name")
    age = request.form.get("age")
    gender = request.form.get("gender")

    # Input validation
    if not name or not age or not gender:
        flash("All fields are required.", "error")
        return redirect(url_for("index"))
    
    try:
        age = int(age)
    except ValueError:
        flash("Age must be a valid number.", "error")
        return redirect(url_for("index"))

    if gender not in ["male", "female"]:
        flash("Invalid gender selection.", "error")
        return redirect(url_for("index"))

    # Database insertion
    connection = get_db_connection()
    if connection is None:
        flash("Internal server error. Please try again later.", "error")
        return redirect(url_for("index"))
    
    try:
        with connection.cursor() as cursor:
            # Parameterized query to prevent SQL injection
            sql = "INSERT INTO users (name, age, gender) VALUES (%s, %s, %s)"
            cursor.execute(sql, (name, age, gender))
        connection.commit()
        logging.info(f"Successfully inserted user data for name: {name}")
        flash("Data submitted successfully!", "success")
    except pymysql.MySQLError as e:
        logging.error(f"Database insertion failed: {e}")
        flash("Failed to submit data.", "error")
    finally:
        connection.close()

    return redirect(url_for("index"))

@app.route("/edit/<int:user_id>", methods=["GET", "POST"])
def edit(user_id):
    connection = get_db_connection()
    if not connection:
        flash("Internal server error. Please try again later.", "error")
        return redirect(url_for("index"))

    try:
        if request.method == "POST":
            name = request.form.get("name")
            age = request.form.get("age")
            gender = request.form.get("gender")

            if not name or not age or not gender:
                flash("All fields are required.", "error")
                return redirect(url_for("edit", user_id=user_id))

            with connection.cursor() as cursor:
                sql = "UPDATE users SET name=%s, age=%s, gender=%s WHERE id=%s"
                cursor.execute(sql, (name, age, gender, user_id))
            connection.commit()
            flash("User updated successfully!", "success")
            return redirect(url_for("index"))
        else:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
                user = cursor.fetchone()
            if not user:
                flash("User not found.", "error")
                return redirect(url_for("index"))
            return render_template("edit.html", instance_name=INSTANCE_NAME, user=user)
    except Exception as e:
        logging.error(f"Error in edit: {e}")
        flash("An error occurred.", "error")
        return redirect(url_for("index"))
    finally:
        connection.close()

@app.route("/delete/<int:user_id>", methods=["POST"])
def delete(user_id):
    connection = get_db_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
            connection.commit()
            flash("User deleted successfully!", "success")
        except Exception as e:
            logging.error(f"Error in delete: {e}")
            flash("Failed to delete user.", "error")
        finally:
            connection.close()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
