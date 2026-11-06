# Job Portal – Features

## 1. Project Overview

Job Portal is a full-stack web application that connects job seekers with recruiters. It provides a platform where users can discover job opportunities, apply for positions, and manage recruitment activities.

The platform has three user roles: Job Seeker, Recruiter, and Admin.

## 2. User Roles

### 2.1 Job Seeker
- Register and log in to the platform.
- Create and manage a personal profile.
- Browse and search available jobs.
- View detailed job descriptions.
- Apply for job openings.
- Track application status.

### 2.2 Recruiter
- Register and log in to the platform.
- Create and manage a recruiter profile.
- Create new job listings.
- Edit or delete their own job listings.
- View applicants for published jobs.
- Update application statuses.

### 2.3 Admin
- Access the admin dashboard.
- View and manage registered users.
- Review submitted job listings.
- Approve or reject job postings.
- Manage platform activity.

## 3. MVP Features

The following features will be implemented in the initial version.

| No. | Feature | Description |
|---|---|---|
| 1 | User Authentication | Registration and login with secure password hashing. |
| 2 | Role-Based Access | Separate permissions for Job Seekers, Recruiters, and Admins. |
| 3 | User Profiles | Create and update user information. |
| 4 | Job Management | Recruiters can create, edit, and delete job listings. |
| 5 | Job Browsing | Job seekers can view available job openings. |
| 6 | Job Search | Search jobs using keywords and relevant filters. |
| 7 | Job Applications | Job seekers can apply for available positions. |
| 8 | Application Management | Recruiters can view applicants and update application statuses. |
| 9 | Application Tracking | Job seekers can track their application progress. |
| 10 | Role-Based Dashboards | Different dashboards for each user role. |

## 4. Job Posting Approval Workflow

1. Recruiter creates a job listing.
2. The job listing is submitted for admin review.
3. Admin reviews the submitted listing.
4. Admin approves or rejects the listing.
5. Only approved job listings become visible to job seekers.

## 5. Future Features

These features are outside the initial MVP scope and may be considered for future versions.

- AI-powered resume analysis.
- Personalized job recommendations.
- Email notifications.
- Advanced job filtering.
- Interview scheduling.
- Real-time messaging between recruiters and applicants.

## 6. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| FastAPI | REST API development |
| PostgreSQL | Database management |
| React | Frontend development |
| JavaScript | Frontend functionality |
| Tailwind CSS | UI styling |
| JWT | Authentication |
| Git & GitHub | Version control |

## 7. Project Scope

**Initial Goal:** Build a functional job portal with authentication, job management, job applications, and role-based access.

**Development Duration:** 15 Days (ALTA Builder 30 – Track A).

**Out of Scope:** AI-based features, advanced recommendation systems, and real-time communication in the initial version.

---

*Part of ALTA Builder 30 – Full-Stack Development Track.*
