from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    session,
    redirect,
    url_for
)

import os
import sqlite3
from datetime import datetime


# =========================================
# FLASK APP
# =========================================

app = Flask(__name__)


# =========================================
# SECRET KEY
# =========================================

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "local-development-secret-key"
)


# =========================================
# ADMIN PASSWORD
# =========================================

ADMIN_PASSWORD = os.environ.get(
    "ADMIN_PASSWORD",
    "sagar123"
)


# =========================================
# DATABASE SETTINGS
# =========================================

DATABASE_URL = os.environ.get(
    "DATABASE_URL"
)


# =========================================
# SQLITE CONNECTION
# USED FOR LOCAL TESTING
# =========================================

def get_sqlite_connection():

    connection = sqlite3.connect(
        "responses.db"
    )

    connection.row_factory = sqlite3.Row

    return connection


# =========================================
# CREATE DATABASE TABLE
# =========================================

def create_database_table():

    # -------------------------------------
    # LOCAL SQLITE DATABASE
    # -------------------------------------

    if not DATABASE_URL:

        connection = get_sqlite_connection()

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS responses (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                answer TEXT NOT NULL,

                selected_date TEXT,

                selected_food TEXT,

                created_at TEXT NOT NULL

            )
            """
        )

        connection.commit()

        connection.close()

        print(
            "Using local SQLite database."
        )

        return


    # -------------------------------------
    # RENDER POSTGRESQL DATABASE
    # -------------------------------------

    try:

        import psycopg2

        connection = psycopg2.connect(
            DATABASE_URL
        )

        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS responses (

                id SERIAL PRIMARY KEY,

                answer TEXT NOT NULL,

                selected_date TEXT,

                selected_food TEXT,

                created_at TIMESTAMP NOT NULL

            )
            """
        )

        connection.commit()

        cursor.close()

        connection.close()

        print(
            "Using Render PostgreSQL database."
        )

    except Exception as error:

        print(
            "Database initialization error:",
            error
        )


# =========================================
# INITIALIZE DATABASE
# =========================================

create_database_table()


# =========================================
# HOME PAGE
# =========================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================
# SAVE RESPONSE
# =========================================

@app.route(
    "/save-response",
    methods=["POST"]
)
def save_response():

    try:

        data = request.get_json(
            silent=True
        )

        if not data:

            return jsonify({
                "success": False,
                "message": "No data received."
            }), 400


        # ---------------------------------
        # GET DATA FROM WEBSITE
        # ---------------------------------

        answer = str(
            data.get(
                "answer",
                ""
            )
        ).strip().upper()


        selected_date = str(
            data.get(
                "selected_date",
                ""
            )
        ).strip()


        selected_food = str(
            data.get(
                "selected_food",
                ""
            )
        ).strip()


        # ---------------------------------
        # VALIDATE ANSWER
        # ---------------------------------

        if answer not in [
            "YES",
            "NO"
        ]:

            return jsonify({
                "success": False,
                "message": "Invalid answer."
            }), 400


        # ---------------------------------
        # CURRENT TIME
        # ---------------------------------

        created_at = datetime.now()


        # =================================
        # LOCAL SQLITE
        # =================================

        if not DATABASE_URL:

            connection = get_sqlite_connection()

            connection.execute(
                """
                INSERT INTO responses
                (
                    answer,
                    selected_date,
                    selected_food,
                    created_at
                )

                VALUES (?, ?, ?, ?)
                """,

                (
                    answer,
                    selected_date,
                    selected_food,
                    created_at.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                )
            )

            connection.commit()

            connection.close()


        # =================================
        # RENDER POSTGRESQL
        # =================================

        else:

            import psycopg2

            connection = psycopg2.connect(
                DATABASE_URL
            )

            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO responses
                (
                    answer,
                    selected_date,
                    selected_food,
                    created_at
                )

                VALUES (%s, %s, %s, %s)
                """,

                (
                    answer,
                    selected_date,
                    selected_food,
                    created_at
                )
            )

            connection.commit()

            cursor.close()

            connection.close()


        # ---------------------------------
        # SUCCESS
        # ---------------------------------

        return jsonify({
            "success": True,
            "message": "Response saved successfully."
        })


    except Exception as error:

        print(
            "Error while saving response:",
            error
        )

        return jsonify({
            "success": False,
            "message": "Could not save response."
        }), 500


# =========================================
# ADMIN LOGIN
# =========================================

@app.route(
    "/admin",
    methods=["GET", "POST"]
)
def admin():

    # -------------------------------------
    # ALREADY LOGGED IN
    # -------------------------------------

    if session.get(
        "admin_logged_in"
    ):

        return redirect(
            url_for(
                "admin_dashboard"
            )
        )


    # -------------------------------------
    # LOGIN FORM SUBMISSION
    # -------------------------------------

    if request.method == "POST":

        password = request.form.get(
            "password",
            ""
        )


        if password == ADMIN_PASSWORD:

            session[
                "admin_logged_in"
            ] = True

            return redirect(
                url_for(
                    "admin_dashboard"
                )
            )


        return render_template(
            "admin.html",
            error="Incorrect password."
        )


    # -------------------------------------
    # SHOW LOGIN PAGE
    # -------------------------------------

    return render_template(
        "admin.html"
    )


# =========================================
# ADMIN DASHBOARD
# =========================================

@app.route(
    "/admin/dashboard"
)
def admin_dashboard():

    # -------------------------------------
    # CHECK LOGIN
    # -------------------------------------

    if not session.get(
        "admin_logged_in"
    ):

        return redirect(
            url_for(
                "admin"
            )
        )


    responses = []


    # =====================================
    # LOCAL SQLITE
    # =====================================

    if not DATABASE_URL:

        connection = get_sqlite_connection()

        rows = connection.execute(
            """
            SELECT
                id,
                answer,
                selected_date,
                selected_food,
                created_at
            FROM responses
            ORDER BY id DESC
            """
        ).fetchall()

        connection.close()

        responses = [
            dict(row)
            for row in rows
        ]


    # =====================================
    # RENDER POSTGRESQL
    # =====================================

    else:

        try:

            import psycopg2

            connection = psycopg2.connect(
                DATABASE_URL
            )

            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT
                    id,
                    answer,
                    selected_date,
                    selected_food,
                    created_at
                FROM responses
                ORDER BY id DESC
                """
            )

            rows = cursor.fetchall()

            for row in rows:

                responses.append({

                    "id": row[0],

                    "answer": row[1],

                    "selected_date": row[2],

                    "selected_food": row[3],

                    "created_at": row[4]

                })


            cursor.close()

            connection.close()


        except Exception as error:

            print(
                "Error loading responses:",
                error
            )


    # -------------------------------------
    # SHOW DASHBOARD
    # -------------------------------------

    return render_template(
        "admin_dashboard.html",
        responses=responses
    )


# =========================================
# ADMIN LOGOUT
# =========================================

@app.route(
    "/admin/logout"
)
def admin_logout():

    session.clear()

    return redirect(
        url_for(
            "admin"
        )
    )


# =========================================
# RUN FLASK
# =========================================

if __name__ == "__main__":

    app.run(
        debug=True
    )