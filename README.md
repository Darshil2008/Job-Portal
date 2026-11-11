# Job Portal

A full-stack job portal designed to connect job seekers with recruiters through a single platform.

Job seekers can discover opportunities, apply for jobs, and track their applications. Recruiters can publish job openings and manage applicants, while administrators oversee platform activity and approve job listings.

## 🎯 Problem Statement

Finding relevant job opportunities and managing applications can be difficult for job seekers. At the same time, recruiters need an organized platform to publish openings and manage applications.

Job Portal aims to simplify this process by bringing job seekers, recruiters, and administrators together in one platform.

## 👥 User Roles

- **Job Seeker:** Create a profile, browse jobs, apply for opportunities, and track applications.
- **Recruiter:** Create and manage job listings and review applicants.
- **Admin:** Manage users, review job listings, and approve or reject job postings.

## ✨ Planned Features

### MVP Features

1. User registration and login.
2. Role-based authentication.
3. Job seeker profiles.
4. Recruiter profiles.
5. Create, edit, and delete job listings.
6. Browse and search available jobs.
7. Apply for job openings.
8. View and manage applications.
9. Track application status.
10. Role-based dashboards.

### Future Improvements

- AI-powered resume analysis.
- Personalized job recommendations.
- Email notifications.
- Advanced job filters.
- Interview scheduling.
- Real-time messaging.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| FastAPI | REST API development |
| PostgreSQL | Database |
| React | Frontend development |
| JavaScript | Frontend logic |
| Tailwind CSS | UI styling |
| JWT | Authentication |
| Git & GitHub | Version control |

## 🏗️ Project Development

This project is being developed as part of **ALTA Builder 30**, a 30-day building challenge.

- **Track:** Full-Stack Development
- **Duration:** 15 Days
- **Project:** Job Portal
- **Development Approach:** Plan, build, test, and deploy.

## 📌 Current Status

**Day 1 – Planning**

- [x] Project selected.
- [x] Problem statement defined.
- [x] User roles identified.
- [x] MVP features planned.
- [ ] Database schema designed.
- [ ] Backend development.
- [ ] Frontend development.
- [ ] Testing and deployment.

## 🚀 Project Goal

Build a functional, user-friendly job portal while learning and applying full-stack development concepts through hands-on implementation.

---

*Built as part of ALTA Builder 30.*

## Run on macOS

1. Open Terminal and move into this folder:
   ```bash
   cd Job-Portal
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the app:
   ```bash
   python app.py
   ```
5. Open http://127.0.0.1:5000 in your browser.

The SQLite database (`database.db`) is created automatically on first run.

## Demo admin login
- Email: `admin@jobportal.com`
- Password: `admin123`
