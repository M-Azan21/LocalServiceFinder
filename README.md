# 🔧 Local Service Finder with Trust Score
### Final Year Project — Flask + MySQL Web Application

---

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
pip install flask flask-mysqldb werkzeug
```

### 2. Setup MySQL
- Open **XAMPP / WAMP** and start **Apache + MySQL**
- Open **phpMyAdmin** → go to SQL tab
- Run the contents of `database.sql`

Or via MySQL CLI:
```bash
mysql -u root -p < database.sql
```

### 3. Configure Database (if needed)
Edit `app.py` lines 14–17:
```python
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''   # Add your MySQL password here
app.config['MYSQL_DB'] = 'local_service_finder'
```

### 4. Run the App
```bash
python app.py
```

### 5. Open in Browser
```
http://127.0.0.1:5000
```

---

## 🔐 Credentials

| Role  | Username / Email     | Password   |
|-------|---------------------|------------|
| Admin | admin               | admin123   |
| User  | ali@example.com     | (set yours) |

> Admin panel: http://127.0.0.1:5000/admin

---

## 📁 Project Structure

```
LocalServiceFinder/
├── app.py                   # Main Flask backend
├── database.sql             # MySQL schema + sample data
├── requirements.txt         # Python packages
├── README.md                # This file
│
├── templates/
│   ├── base.html            # Base layout with navbar
│   ├── index.html           # Landing page
│   ├── login.html           # User login
│   ├── register.html        # User registration
│   ├── dashboard.html       # User dashboard
│   ├── services.html        # Browse services
│   ├── service_detail.html  # Service detail + reviews
│   ├── add_service.html     # Add new service
│   ├── hire.html            # Booking form
│   ├── admin_login.html     # Admin login
│   ├── admin_dashboard.html # Admin panel
│   ├── admin_bookings.html  # Manage bookings
│   └── admin_users.html     # View all users
│
└── static/
    ├── style.css            # Complete CSS design system
    └── uploads/             # Service images (auto-created)
```

---

## ✨ Features

### User Features
- ✅ Register / Login / Logout with hashed passwords
- ✅ Add services with image upload
- ✅ Browse & search services by name, category, location
- ✅ View service details with trust score breakdown
- ✅ Leave star ratings and written reviews
- ✅ Hire/book any service
- ✅ Personal dashboard with stats

### Trust Score System
- Bayesian-weighted average rating
- Review volume boost
- Visual score bar with color coding (Excellent / Good / Fair)

### Admin Features
- ✅ Secure admin login
- ✅ Dashboard with platform-wide stats
- ✅ View, manage, delete all services
- ✅ View all bookings + update status
- ✅ View all registered users

---

## 🎨 Design
- Modern SaaS aesthetic (Fiverr/Upwork inspired)
- Custom font: Sora + DM Sans (Google Fonts)
- Glassmorphism hero cards
- Smooth hover animations
- Fully mobile-responsive
- Dark navbar + gradient hero section

---

## 📦 Tech Stack
| Layer      | Technology               |
|------------|--------------------------|
| Backend    | Python Flask             |
| Frontend   | HTML5, CSS3, Bootstrap 5 |
| Templates  | Jinja2                   |
| Database   | MySQL                    |
| Auth       | Werkzeug (PBKDF2 hash)   |
| Icons      | Font Awesome 6           |
| Fonts      | Google Fonts             |
