import os
import re
import sqlite3
from functools import wraps

from flask import Flask, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("JOB_PORTAL_SECRET_KEY", "change-this-secret-key-before-deployment")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE_DIR, "database.db")
DEFAULT_ADMIN_EMAIL = "admin@jobportal.com"
DEFAULT_ADMIN_PASSWORD = "admin123"


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def validate_email(email):
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email))


def initialize_db():
    db = get_db()

    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recruiter_id INTEGER,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT,
            salary TEXT,
            description TEXT NOT NULL,
            status TEXT DEFAULT 'pending'
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER,
            user_id INTEGER,
            status TEXT DEFAULT 'Applied',
            UNIQUE(job_id, user_id)
        )
    """)

    admin = db.execute(
        "SELECT id FROM users WHERE email = ?",
        (DEFAULT_ADMIN_EMAIL,)
    ).fetchone()

    if not admin:
        db.execute(
            """
            INSERT INTO users (name, email, password, role)
            VALUES (?, ?, ?, ?)
            """,
            (
                "Admin",
                DEFAULT_ADMIN_EMAIL,
                generate_password_hash(DEFAULT_ADMIN_PASSWORD),
                "admin",
            ),
        )

    db.commit()
    db.close()


initialize_db()


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first.")
            return redirect("/login")
        return func(*args, **kwargs)

    return wrapper


def role_required(*allowed_roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if session.get("role") not in allowed_roles:
                flash("Access denied.")
                return redirect("/")
            return func(*args, **kwargs)

        return wrapper

    return decorator


@app.route("/")
def index():
    search = request.args.get("search", "").strip()
    db = get_db()
    jobs = db.execute("""
        SELECT jobs.*, users.name AS recruiter
        FROM jobs
        JOIN users ON jobs.recruiter_id = users.id
        WHERE jobs.status = 'approved'
          AND (jobs.title LIKE ? OR jobs.company LIKE ?)
        ORDER BY jobs.id DESC
    """, (f"%{search}%", f"%{search}%")).fetchall()
    db.close()
    return render_template("index.html", jobs=jobs, search=search)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "")

        if not name or not validate_email(email) or len(password) < 8:
            flash("Enter your full name, a valid email, and a password of at least 8 characters.")
            return redirect("/register")

        if role not in ["job_seeker", "recruiter"]:
            flash("Please select a valid account type.")
            return redirect("/register")

        db = get_db()
        try:
            db.execute(
                """
                INSERT INTO users (name, email, password, role)
                VALUES (?, ?, ?, ?)
                """,
                (name, email, generate_password_hash(password), role),
            )
            db.commit()
            flash("Account created successfully. Please login.")
            return redirect("/login")
        except sqlite3.IntegrityError:
            flash("That email address is already registered.")
        finally:
            db.close()

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email and password are required.")
            return render_template("login.html")

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,),
        ).fetchone()
        db.close()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["role"] = user["role"]
            return redirect("/dashboard")

        flash("Invalid email or password.")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/dashboard")
@login_required
def dashboard():
    db = get_db()

    if session["role"] == "recruiter":
        jobs = db.execute(
            "SELECT * FROM jobs WHERE recruiter_id = ? ORDER BY id DESC",
            (session["user_id"],)
        ).fetchall()

        applications = db.execute("""
            SELECT applications.*, jobs.title, users.name AS applicant
            FROM applications
            JOIN jobs ON applications.job_id = jobs.id
            JOIN users ON applications.user_id = users.id
            WHERE jobs.recruiter_id = ?
            ORDER BY applications.id DESC
        """, (session["user_id"],)).fetchall()

    elif session["role"] == "job_seeker":
        jobs = []
        applications = db.execute("""
            SELECT applications.*, jobs.title, jobs.company
            FROM applications
            JOIN jobs ON applications.job_id = jobs.id
            WHERE applications.user_id = ?
            ORDER BY applications.id DESC
        """, (session["user_id"],)).fetchall()

    else:
        jobs = db.execute(
            "SELECT * FROM jobs ORDER BY id DESC"
        ).fetchall()
        applications = []

    db.close()
    return render_template("dashboard.html", jobs=jobs, applications=applications)


@app.route("/post-job", methods=["GET", "POST"])
@login_required
@role_required("recruiter")
def post_job():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        company = request.form.get("company", "").strip()
        description = request.form.get("description", "").strip()

        if not title or not company or not description:
            flash("Please fill in the job title, company, and description.")
            return redirect("/post-job")

        db = get_db()
        db.execute("""
            INSERT INTO jobs
            (recruiter_id, title, company, location, salary, description)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            session["user_id"],
            title,
            company,
            request.form.get("location", "").strip(),
            request.form.get("salary", "").strip(),
            description
        ))
        db.commit()
        db.close()

        flash("Job submitted for admin approval.")
        return redirect("/dashboard")

    return render_template("post_job.html")


@app.route("/delete-job/<int:job_id>", methods=["POST"])
@login_required
@role_required("recruiter")
def delete_job(job_id):
    db = get_db()
    db.execute(
        "DELETE FROM applications WHERE job_id = ? AND job_id IN (SELECT id FROM jobs WHERE recruiter_id = ?)",
        (job_id, session["user_id"]),
    )
    db.execute(
        "DELETE FROM jobs WHERE id = ? AND recruiter_id = ?",
        (job_id, session["user_id"]),
    )
    db.commit()
    db.close()
    flash("Job deleted.")
    return redirect("/dashboard")


@app.route("/apply/<int:job_id>", methods=["POST"])
@login_required
@role_required("job_seeker")
def apply(job_id):
    db = get_db()
    job = db.execute("""
        SELECT id FROM jobs WHERE id = ? AND status = 'approved'
    """, (job_id,)).fetchone()

    if not job:
        flash("This job is not available.")
    else:
        try:
            db.execute(
                "INSERT INTO applications (job_id, user_id) VALUES (?, ?)",
                (job_id, session["user_id"])
            )
            db.commit()
            flash("Application submitted successfully.")
        except sqlite3.IntegrityError:
            flash("You have already applied for this job.")

    db.close()
    return redirect("/")


@app.route("/admin")
@login_required
@role_required("admin")
def admin():
    db = get_db()
    jobs = db.execute("""
        SELECT jobs.*, users.name AS recruiter
        FROM jobs
        JOIN users ON jobs.recruiter_id = users.id
        ORDER BY jobs.id DESC
    """).fetchall()
    users = db.execute(
        "SELECT id, name, email, role FROM users ORDER BY id DESC"
    ).fetchall()
    db.close()
    return render_template("admin.html", jobs=jobs, users=users)


@app.route("/approve/<int:job_id>/<action>", methods=["POST"])
@login_required
@role_required("admin")
def approve(job_id, action):
    if action not in ["approved", "rejected"]:
        flash("Invalid action.")
        return redirect("/admin")

    db = get_db()
    db.execute(
        "UPDATE jobs SET status = ? WHERE id = ?",
        (action, job_id)
    )
    db.commit()
    db.close()
    flash(f"Job {action}.")
    return redirect("/admin")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
