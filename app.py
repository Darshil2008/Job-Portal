
from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = "change-this-secret-key"
DB = "database.db"


def get_db():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    return db


def initialize_db():
    db = get_db()

    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recruiter_id INTEGER,
            title TEXT,
            company TEXT,
            location TEXT,
            salary TEXT,
            description TEXT,
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

    # Add new columns safely to an existing database
    existing_columns = [
        row["name"] for row in db.execute("PRAGMA table_info(jobs)").fetchall()
    ]

    new_columns = {
        "skills": "TEXT DEFAULT ''",
        "job_type": "TEXT DEFAULT 'Full-time'",
        "work_mode": "TEXT DEFAULT 'On-site'",
        "experience": "TEXT DEFAULT 'Fresher'"
    }

    for column, definition in new_columns.items():
        if column not in existing_columns:
            db.execute(f"ALTER TABLE jobs ADD COLUMN {column} {definition}")

    admin = db.execute(
        "SELECT id FROM users WHERE email=?",
        ("admin@jobportal.com",)
    ).fetchone()

    if not admin:
        db.execute("""
            INSERT INTO users (name,email,password,role)
            VALUES (?,?,?,?)
        """, (
            "Admin",
            "admin@jobportal.com",
            generate_password_hash("admin123"),
            "admin"
        ))

    # Insert demo jobs only if the jobs table is empty
    count = db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]

    if count == 0:
        demo_jobs = [
            ("Python Developer", "TechNova", "Bangalore",
             "₹4-8 LPA", "Build backend applications and APIs.",
             "Python, Flask, Django, SQL", "Full-time", "Hybrid", "0-2 years"),

            ("Frontend Developer", "PixelCraft", "Remote",
             "₹5-9 LPA", "Create responsive and user-friendly web interfaces.",
             "HTML, CSS, JavaScript, React", "Full-time", "Remote", "0-2 years"),

            ("Java Developer", "CodeSphere", "Pune",
             "₹5-10 LPA", "Develop scalable enterprise applications.",
             "Java, Spring Boot, MySQL, Git", "Full-time", "On-site", "1-3 years"),

            ("Data Analyst Intern", "DataBridge", "Jaipur",
             "₹15k-25k/month", "Analyze business data and prepare reports.",
             "Python, SQL, Excel, Power BI", "Internship", "Hybrid", "Fresher"),

            ("AI/ML Engineer", "NeuralWorks", "Hyderabad",
             "₹7-14 LPA", "Develop machine learning models and AI solutions.",
             "Python, TensorFlow, PyTorch, Scikit-learn", "Full-time", "Hybrid", "1-3 years"),

            ("Full Stack Developer", "WebNest", "Remote",
             "₹6-12 LPA", "Build complete web applications.",
             "React, Node.js, Express, MongoDB", "Full-time", "Remote", "1-3 years"),

            ("UI/UX Designer", "DesignHive", "Mumbai",
             "₹4-7 LPA", "Design intuitive digital experiences.",
             "Figma, UI Design, UX Research, Prototyping", "Full-time", "On-site", "0-2 years"),

            ("C++ Developer", "LogicLabs", "Delhi",
             "₹5-9 LPA", "Work on performance-focused software.",
             "C++, DSA, OOP, STL, Git", "Full-time", "Hybrid", "0-2 years"),

            ("Cloud Engineer", "CloudMatrix", "Bangalore",
             "₹8-15 LPA", "Manage cloud infrastructure and deployments.",
             "AWS, Docker, Kubernetes, Linux", "Full-time", "Hybrid", "2-4 years"),

            ("Mobile App Developer", "AppForge", "Remote",
             "₹5-10 LPA", "Develop cross-platform mobile applications.",
             "Flutter, Dart, Firebase, REST API", "Full-time", "Remote", "0-2 years"),

            ("Backend Developer Intern", "DevOrbit", "Jodhpur",
             "₹10k-18k/month", "Assist in building and testing backend services.",
             "Python, FastAPI, PostgreSQL, Git", "Internship", "On-site", "Fresher"),

            ("Cybersecurity Analyst", "SecureStack", "Gurgaon",
             "₹6-11 LPA", "Monitor systems and identify security vulnerabilities.",
             "Linux, Networking, Python, Security", "Full-time", "Hybrid", "1-3 years"),

            ("Senior Python Developer", "Zyphra Labs", "Remote",
             "₹12-20 LPA", "Architect and build high-traffic APIs and microservices.",
             "Python, Django, Redis, Celery", "Full-time", "Remote", "3-5 years"),

            ("React Developer", "InterfaceHQ", "Bangalore",
             "₹6-11 LPA", "Build dynamic single-page applications with React and TypeScript.",
             "React, TypeScript, Redux, Tailwind CSS", "Full-time", "Hybrid", "1-3 years"),

            ("DevOps Engineer", "DeployKit", "Pune",
             "₹8-14 LPA", "Automate CI/CD pipelines and manage cloud infrastructure.",
             "Docker, Kubernetes, AWS, GitHub Actions", "Full-time", "Hybrid", "2-4 years"),

            ("Data Scientist", "InsightCore", "Hyderabad",
             "₹10-18 LPA", "Extract insights from large datasets using statistical modelling.",
             "Python, Pandas, SQL, Scikit-learn", "Full-time", "On-site", "2-4 years"),

            ("PHP Developer", "WebCrate", "Noida",
             "₹3-6 LPA", "Maintain and extend e-commerce platforms built with Laravel.",
             "PHP, Laravel, MySQL, REST API", "Full-time", "On-site", "0-2 years"),

            ("Angular Developer", "FormStack", "Remote",
             "₹5-9 LPA", "Build enterprise dashboards and internal tools with Angular.",
             "Angular, TypeScript, RxJS, Material UI", "Full-time", "Remote", "1-3 years"),

            ("Blockchain Developer", "ChainBridge", "Bangalore",
             "₹10-16 LPA", "Develop smart contracts and decentralized applications.",
             "Solidity, Ethereum, Web3.js, Node.js", "Full-time", "Hybrid", "1-3 years"),

            ("Go Developer", "StreamOps", "Remote",
             "₹9-15 LPA", "Build high-performance backend services and distributed systems.",
             "Go, gRPC, PostgreSQL, Docker", "Full-time", "Remote", "2-4 years"),

            ("QA Automation Engineer", "TestPilot", "Chennai",
             "₹5-9 LPA", "Design automated test suites for web and mobile applications.",
             "Selenium, Python, Jenkins, Postman", "Full-time", "On-site", "1-3 years"),

            ("Machine Learning Intern", "CortexAI", "Remote",
             "₹20k-35k/month", "Assist in training and evaluating ML models on real-world datasets.",
             "Python, PyTorch, NumPy, Jupyter", "Internship", "Remote", "Fresher"),

            ("Rust Developer", "IronForge Systems", "Bangalore",
             "₹10-18 LPA", "Build memory-safe systems software and tooling.",
             "Rust, Linux, Git, WebAssembly", "Full-time", "On-site", "2-4 years"),

            ("Node.js Developer", "ApiLayer", "Mumbai",
             "₹5-10 LPA", "Design and ship RESTful APIs for client-facing products.",
             "Node.js, Express, MongoDB, Redis", "Full-time", "Hybrid", "1-3 years")
        ]

        for job in demo_jobs:
            db.execute("""
                INSERT INTO jobs
                (recruiter_id,title,company,location,salary,description,
                 skills,job_type,work_mode,experience,status)
                VALUES (NULL,?,?,?,?,?,?,?,?,?,'approved')
            """, job)

    db.commit()
    db.close()


initialize_db()


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first")
            return redirect("/login")
        return func(*args, **kwargs)
    return wrapper


def role_required(role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if session.get("role") != role:
                flash("Access denied")
                return redirect("/")
            return func(*args, **kwargs)
        return wrapper
    return decorator


@app.route("/")
def index():
    search = request.args.get("search", "").strip()
    location = request.args.get("location", "").strip()
    job_type = request.args.get("job_type", "").strip()
    work_mode = request.args.get("work_mode", "").strip()

    query = """
        SELECT * FROM jobs
        WHERE status='approved'
        AND (title LIKE ? OR company LIKE ? OR skills LIKE ?)
    """
    params = [f"%{search}%"] * 3

    if location:
        query += " AND location LIKE ?"
        params.append(f"%{location}%")

    if job_type:
        query += " AND job_type=?"
        params.append(job_type)

    if work_mode:
        query += " AND work_mode=?"
        params.append(work_mode)

    query += " ORDER BY id DESC"

    db = get_db()
    jobs = db.execute(query, params).fetchall()
    db.close()

    return render_template(
        "index.html",
        jobs=jobs,
        search=search,
        location=location,
        job_type=job_type,
        work_mode=work_mode
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        role = request.form["role"]

        if role not in ["job_seeker", "recruiter"]:
            flash("Invalid role")
            return redirect("/register")

        if len(password) < 8:
            flash("Password must contain at least 8 characters")
            return redirect("/register")

        db = get_db()

        try:
            db.execute("""
                INSERT INTO users (name,email,password,role)
                VALUES (?,?,?,?)
            """, (name, email, generate_password_hash(password), role))

            db.commit()
            flash("Account created successfully")
            return redirect("/login")

        except sqlite3.IntegrityError:
            flash("Email already exists")

        finally:
            db.close()

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        ).fetchone()
        db.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["role"] = user["role"]
            return redirect("/dashboard")

        flash("Invalid email or password")

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
            "SELECT * FROM jobs WHERE recruiter_id=?",
            (session["user_id"],)
        ).fetchall()

        applications = db.execute("""
            SELECT applications.*, jobs.title, users.name AS applicant
            FROM applications
            JOIN jobs ON applications.job_id=jobs.id
            JOIN users ON applications.user_id=users.id
            WHERE jobs.recruiter_id=?
        """, (session["user_id"],)).fetchall()

    elif session["role"] == "job_seeker":
        jobs = []
        applications = db.execute("""
            SELECT applications.*, jobs.title, jobs.company
            FROM applications
            JOIN jobs ON applications.job_id=jobs.id
            WHERE applications.user_id=?
        """, (session["user_id"],)).fetchall()

    else:
        jobs = db.execute(
            "SELECT * FROM jobs ORDER BY id DESC"
        ).fetchall()
        applications = []

    db.close()

    return render_template(
        "dashboard.html",
        jobs=jobs,
        applications=applications
    )


@app.route("/post-job", methods=["GET", "POST"])
@login_required
@role_required("recruiter")
def post_job():
    if request.method == "POST":
        db = get_db()

        db.execute("""
            INSERT INTO jobs
            (recruiter_id,title,company,location,salary,description,
             skills,job_type,work_mode,experience)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (
            session["user_id"],
            request.form["title"],
            request.form["company"],
            request.form["location"],
            request.form["salary"],
            request.form["description"],
            request.form["skills"],
            request.form["job_type"],
            request.form["work_mode"],
            request.form["experience"]
        ))

        db.commit()
        db.close()

        flash("Job submitted for admin approval")
        return redirect("/dashboard")

    return render_template("post_job.html")


@app.route("/delete-job/<int:job_id>", methods=["POST"])
@login_required
@role_required("recruiter")
def delete_job(job_id):
    db = get_db()

    db.execute("""
        DELETE FROM jobs
        WHERE id=? AND recruiter_id=?
    """, (job_id, session["user_id"]))

    db.commit()
    db.close()

    flash("Job deleted")
    return redirect("/dashboard")


@app.route("/apply/<int:job_id>", methods=["POST", "GET"])
@login_required
@role_required("job_seeker")
def apply(job_id):
    db = get_db()

    job = db.execute("""
        SELECT id FROM jobs
        WHERE id=? AND status='approved'
    """, (job_id,)).fetchone()

    if not job:
        flash("Job not available")
    else:
        try:
            db.execute("""
                INSERT INTO applications (job_id,user_id)
                VALUES (?,?)
            """, (job_id, session["user_id"]))

            db.commit()
            flash("Application submitted successfully")

        except sqlite3.IntegrityError:
            flash("You have already applied")

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
        LEFT JOIN users ON jobs.recruiter_id=users.id
        ORDER BY jobs.id DESC
    """).fetchall()

    users = db.execute(
        "SELECT id,name,email,role FROM users"
    ).fetchall()

    db.close()

    return render_template("admin.html", jobs=jobs, users=users)


@app.route("/approve/<int:job_id>/<action>")
@login_required
@role_required("admin")
def approve(job_id, action):
    if action not in ["approved", "rejected"]:
        return redirect("/admin")

    db = get_db()
    db.execute(
        "UPDATE jobs SET status=? WHERE id=?",
        (action, job_id)
    )
    db.commit()
    db.close()

    return redirect("/admin")


if __name__ == "__main__":
    app.run(debug=True, port=5001)
