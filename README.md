# Trekking Management Application (V2) - MAD-2

A strict, barebone implementation of the IIT Madras **Modern Application Development - II (MAD-2)** project specification.

---

## 🛠 Frameworks Used (Strictly Allowed Only)

* **Backend:** Flask for API (JSON endpoints only)
* **Frontend:** Vue.js 3 for UI (Single Page Application)
* **CSS & Styling:** Bootstrap 5 (No other CSS framework)
* **Database:** SQLite via Flask-SQLAlchemy (Programmatically created)
* **Caching:** Redis for frequently accessed treks
* **Batch Jobs:** Redis and Celery for scheduled and async tasks

---

## 👥 Roles & Functionalities

### 1. Admin
* Pre-seeded programmatically upon app start (`admin / admin@123`).
* Dashboard displays required counters:
  * Total number of treks
  * Total number of users and staff
  * Total number of bookings
* Can add and manage trek staff (Staff cannot self-register).
* Can assign staff to treks.
* Can view and manage all users, staff, and treks.
* Can search users, staff, or treks.
* Can deactivate or blacklist users or staff.
* Can view all historical trekking bookings.

### 2. Trek Staff
* Can log in only after being created by Admin.
* Can view assigned treks by admin.
* Can manage trek details: available slots and trek status (`Open`, `Closed`, `Started`, `Completed`).
* Can view list of registered participants for assigned treks.

### 3. User (Trekker)
* Self-registration and login.
* Can view approved/open treks.
* Can search and filter treks based on **difficulty**, **location**, and **duration (in days)**.
* Can book treks (with overbooking guard and duplicate booking guard).
* Can view booking status and trekking history.
* Can cancel bookings (slot released).
* Can update profile.

---

## ⚙️ Backend Jobs (Using Celery & Redis)

1. **Scheduled Job – Daily Reminders (Celery Beat):**
   * Runs daily to send reminders to users about upcoming treks, start dates, and instructions.
2. **Scheduled Job – Monthly Activity Report (Celery Beat):**
   * Runs on the 1st of every month. Generates an HTML activity report for the Admin (number of treks conducted, users participated, popular treks).
3. **User-Triggered Async Job – Export Booking History as CSV (Celery Worker):**
   * Trekkers trigger an export from their dashboard.
   * Background batch job compiles a CSV containing: User ID, Trek Name, Location, Difficulty, Duration, Dates, and Booking Status.

---

## 🚀 How to Run

### Step 1: Start Flask API Backend
```bash
cd backend
venv\Scripts\activate
python app.py
```
*(Runs on `http://127.0.0.1:5000`)*

### Step 2: Start Vue.js Frontend
```bash
cd frontend
npm run dev
```
*(Runs on `http://127.0.0.1:5173`)*

### Step 3: Start Celery Worker & Beat (Optional/For batch jobs)
```bash
# Terminal 1: Celery Worker
cd backend
venv\Scripts\activate
celery -A celery_app.celery worker --loglevel=info -P solo

# Terminal 2: Celery Beat Scheduler
cd backend
venv\Scripts\activate
celery -A celery_app.celery beat --loglevel=info
```

---

## 🔑 Initial Admin Account

* **Username:** `admin`
* **Password:** `admin@123`
*(Staff accounts are created by the Admin from the Admin Dashboard. Trekkers self-register via the Register page).*
