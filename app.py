from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv
from datetime import datetime

app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv('SECRET_KEY')

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = 'local_service_finder'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# ─── File Upload Config ─────────────────────────────────────────────────────
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB

mysql = MySQL(app)

# ─── Admin Credentials ──────────────────────────────────────────────────────
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ══════════════════════════════════════════════════════════════════════════════
# PUBLIC ROUTES
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    cur = mysql.connection.cursor()

    # Top-rated services for hero showcase
    cur.execute("""
        SELECT * FROM services
        ORDER BY rating DESC, total_reviews DESC
        LIMIT 6
    """)
    featured = cur.fetchall()

    # Stats for landing page
    cur.execute("SELECT COUNT(*) AS cnt FROM services")
    total_services = cur.fetchone()['cnt']

    cur.execute("SELECT COUNT(*) AS cnt FROM users")
    total_users = cur.fetchone()['cnt']

    cur.execute("SELECT COUNT(*) AS cnt FROM bookings")
    total_bookings = cur.fetchone()['cnt']

    # Unique categories
    cur.execute("SELECT DISTINCT service_type FROM services ORDER BY service_type")
    categories = [row['service_type'] for row in cur.fetchall()]

    cur.close()
    return render_template('index.html',
                           featured=featured,
                           total_services=total_services,
                           total_users=total_users,
                           total_bookings=total_bookings,
                           categories=categories)


# ─── Register ───────────────────────────────────────────────────────────────
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user' in session:
        return redirect('/dashboard')

    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        if not name or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')

        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('register.html')

        hashed = generate_password_hash(password)

        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                        (name, email, hashed))
            mysql.connection.commit()
            cur.close()
            flash('Account created successfully! Please log in.', 'success')
            return redirect('/login')
        except Exception as e:
            flash('Email already exists. Please use a different email.', 'danger')
            return render_template('register.html')

    return render_template('register.html')


# ─── Login ──────────────────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect('/dashboard')

    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user['password'], password):
            session['user']    = user['name']
            session['user_id'] = user['id']
            session['email']   = user['email']
            flash(f"Welcome back, {user['name']}!", 'success')
            return redirect('/dashboard')
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')


# ─── Logout ─────────────────────────────────────────────────────────────────
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect('/')


# ══════════════════════════════════════════════════════════════════════════════
# PROTECTED USER ROUTES
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        flash('Please log in to access the dashboard.', 'warning')
        return redirect('/login')

    cur = mysql.connection.cursor()

    # User's own services
    cur.execute("SELECT * FROM services WHERE user_id = %s ORDER BY created_at DESC",
                (session['user_id'],))
    my_services = cur.fetchall()

    # User's bookings
    cur.execute("""
        SELECT b.*, s.service_type, s.rating
        FROM bookings b
        LEFT JOIN services s ON b.service_id = s.id
        WHERE b.user_email = %s
        ORDER BY b.booking_date DESC
        LIMIT 5
    """, (session['email'],))
    my_bookings = cur.fetchall()

    # Stats
    cur.execute("SELECT COUNT(*) AS cnt FROM services WHERE user_id = %s",
                (session['user_id'],))
    service_count = cur.fetchone()['cnt']

    cur.execute("SELECT COUNT(*) AS cnt FROM bookings WHERE user_email = %s",
                (session['email'],))
    booking_count = cur.fetchone()['cnt']

    cur.close()
    return render_template('dashboard.html',
                           my_services=my_services,
                           my_bookings=my_bookings,
                           service_count=service_count,
                           booking_count=booking_count)


# ─── Add Service ─────────────────────────────────────────────────────────────
@app.route('/add_service', methods=['GET', 'POST'])
def add_service():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        name         = request.form.get('name', '').strip()
        service_type = request.form.get('service_type', '').strip()
        location     = request.form.get('location', '').strip()
        description  = request.form.get('description', '').strip()
        price_range  = request.form.get('price_range', '').strip()

        if not name or not service_type or not location:
            flash('Please fill all required fields.', 'danger')
            return render_template('add_service.html')

        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO services (user_id, name, service_type, location, description, price_range, image_filename)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (session['user_id'], name, service_type, location, description, price_range, image_filename))
        mysql.connection.commit()
        cur.close()

        flash('Service added successfully!', 'success')
        return redirect('/dashboard')

    return render_template('add_service.html')


# ─── Delete My Service ──────────────────────────────────────────────────────
@app.route('/delete_my_service/<int:service_id>')
def delete_my_service(service_id):
    if 'user' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM services WHERE id = %s AND user_id = %s",
                (service_id, session['user_id']))
    mysql.connection.commit()
    cur.close()
    flash('Service deleted.', 'info')
    return redirect('/dashboard')


# ─── Services Browse ─────────────────────────────────────────────────────────
@app.route('/services')
def services():
    search   = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    sort     = request.args.get('sort', 'rating')

    cur = mysql.connection.cursor()

    query  = "SELECT * FROM services WHERE 1=1"
    params = []

    if search:
        query += " AND (name LIKE %s OR service_type LIKE %s OR location LIKE %s OR description LIKE %s)"
        like = f'%{search}%'
        params.extend([like, like, like, like])

    if category:
        query += " AND service_type = %s"
        params.append(category)

    order_map = {
        'rating':  'rating DESC, total_reviews DESC',
        'newest':  'created_at DESC',
        'reviews': 'total_reviews DESC',
    }
    query += f" ORDER BY {order_map.get(sort, 'rating DESC')}"

    cur.execute(query, params)
    all_services = cur.fetchall()

    cur.execute("SELECT DISTINCT service_type FROM services ORDER BY service_type")
    categories = [row['service_type'] for row in cur.fetchall()]

    cur.close()
    return render_template('services.html',
                           services=all_services,
                           categories=categories,
                           search=search,
                           selected_category=category,
                           sort=sort)


# ─── Service Detail ──────────────────────────────────────────────────────────
@app.route('/service/<int:service_id>')
def service_detail(service_id):
    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM services WHERE id = %s", (service_id,))
    service = cur.fetchone()
    if not service:
        flash('Service not found.', 'danger')
        return redirect('/services')

    cur.execute("""
        SELECT * FROM reviews WHERE service_id = %s ORDER BY created_at DESC
    """, (service_id,))
    reviews = cur.fetchall()

    cur.close()

    # Trust score calculation
    trust_score = calculate_trust_score(service)

    return render_template('service_detail.html',
                           service=service,
                           reviews=reviews,
                           trust_score=trust_score)


def calculate_trust_score(service):
    """Advanced trust score: weighted combo of rating, reviews, and recency."""
    rating      = float(service['rating'] or 0)
    num_reviews = int(service['total_reviews'] or 0)

    # Bayesian average (prior = 3.0, weight = 5)
    prior    = 3.0
    weight   = 5
    bayesian = (weight * prior + rating * num_reviews) / (weight + num_reviews) if num_reviews else prior

    # Normalize to 100
    score = (bayesian / 5.0) * 100

    # Boost for review count
    review_boost = min(num_reviews * 0.5, 15)
    score = min(score + review_boost, 100)

    return round(score, 1)


# ─── Rate / Review ───────────────────────────────────────────────────────────
@app.route('/rate/<int:service_id>', methods=['POST'])
def rate_service(service_id):
    reviewer = request.form.get('reviewer_name', '').strip() or \
               session.get('user', 'Anonymous')
    rating   = request.form.get('rating', 0)
    comment  = request.form.get('comment', '').strip()

    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            raise ValueError
    except ValueError:
        flash('Invalid rating.', 'danger')
        return redirect(f'/service/{service_id}')

    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO reviews (service_id, reviewer_name, rating, comment)
        VALUES (%s, %s, %s, %s)
    """, (service_id, reviewer, rating, comment))

    cur.execute("""
        UPDATE services
        SET rating = (SELECT AVG(rating) FROM reviews WHERE service_id = %s),
            total_reviews = (SELECT COUNT(*) FROM reviews WHERE service_id = %s)
        WHERE id = %s
    """, (service_id, service_id, service_id))

    mysql.connection.commit()
    cur.close()
    flash('Thank you for your review!', 'success')
    return redirect(f'/service/{service_id}')


# ─── Hire / Book ─────────────────────────────────────────────────────────────
@app.route('/hire/<int:service_id>', methods=['GET', 'POST'])
def hire_service(service_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM services WHERE id = %s", (service_id,))
    service = cur.fetchone()
    cur.close()

    if not service:
        flash('Service not found.', 'danger')
        return redirect('/services')

    if request.method == 'POST':
        user_name  = request.form.get('name', '').strip()
        user_email = request.form.get('email', '').strip()
        notes      = request.form.get('notes', '').strip()

        if not user_name or not user_email:
            flash('Please fill all required fields.', 'danger')
            return render_template('hire.html', service=service)

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO bookings (user_name, user_email, service_id, service_name, service_type, location, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_name, user_email, service_id,
              service['name'], service['service_type'],
              service['location'], notes))
        mysql.connection.commit()
        cur.close()

        flash(f"🎉 Booking confirmed for '{service['name']}'! Provider will contact you soon.", 'success')
        return redirect('/services')

    return render_template('hire.html', service=service)


# ══════════════════════════════════════════════════════════════════════════════
# ADMIN ROUTES
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if 'admin' in session:
        return redirect('/admin/dashboard')

    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = True
            flash('Welcome, Admin!', 'success')
            return redirect('/admin/dashboard')
        else:
            flash('Invalid admin credentials.', 'danger')

    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    flash('Admin logged out.', 'info')
    return redirect('/admin')


@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect('/admin')

    cur = mysql.connection.cursor()

    cur.execute("SELECT s.*, u.name AS owner FROM services s LEFT JOIN users u ON s.user_id = u.id ORDER BY s.created_at DESC")
    all_services = cur.fetchall()

    cur.execute("SELECT COUNT(*) AS cnt FROM services")
    total_services = cur.fetchone()['cnt']

    cur.execute("SELECT COUNT(*) AS cnt FROM users")
    total_users = cur.fetchone()['cnt']

    cur.execute("SELECT COUNT(*) AS cnt FROM bookings")
    total_bookings = cur.fetchone()['cnt']

    cur.execute("SELECT COUNT(*) AS cnt FROM reviews")
    total_reviews = cur.fetchone()['cnt']

    cur.close()
    return render_template('admin_dashboard.html',
                           services=all_services,
                           total_services=total_services,
                           total_users=total_users,
                           total_bookings=total_bookings,
                           total_reviews=total_reviews)


@app.route('/admin/delete/<int:service_id>')
def admin_delete(service_id):
    if 'admin' not in session:
        return redirect('/admin')

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM services WHERE id = %s", (service_id,))
    mysql.connection.commit()
    cur.close()
    flash('Service deleted successfully.', 'success')
    return redirect('/admin/dashboard')


@app.route('/admin/bookings')
def admin_bookings():
    if 'admin' not in session:
        return redirect('/admin')

    status_filter = request.args.get('status', '')
    cur = mysql.connection.cursor()

    if status_filter:
        cur.execute("""
            SELECT b.*, s.service_type, s.location
            FROM bookings b LEFT JOIN services s ON b.service_id = s.id
            WHERE b.status = %s
            ORDER BY b.booking_date DESC
        """, (status_filter,))
    else:
        cur.execute("""
            SELECT b.*, s.service_type, s.location
            FROM bookings b LEFT JOIN services s ON b.service_id = s.id
            ORDER BY b.booking_date DESC
        """)
    bookings = cur.fetchall()
    cur.close()

    return render_template('admin_bookings.html',
                           bookings=bookings,
                           status_filter=status_filter)


@app.route('/admin/update_booking_status/<int:booking_id>/<status>')
def update_booking_status(booking_id, status):
    if 'admin' not in session:
        return redirect('/admin')

    valid = ['pending', 'confirmed', 'completed', 'cancelled']
    if status not in valid:
        flash('Invalid status.', 'danger')
        return redirect('/admin/bookings')

    cur = mysql.connection.cursor()
    cur.execute("UPDATE bookings SET status = %s WHERE id = %s", (status, booking_id))
    mysql.connection.commit()
    cur.close()
    flash(f'Booking status updated to {status}.', 'success')
    return redirect('/admin/bookings')


@app.route('/admin/users')
def admin_users():
    if 'admin' not in session:
        return redirect('/admin')

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT u.*, COUNT(s.id) AS service_count
        FROM users u LEFT JOIN services s ON u.id = s.user_id
        GROUP BY u.id ORDER BY u.created_at DESC
    """)
    users = cur.fetchall()
    cur.close()
    return render_template('admin_users.html', users=users)


# ──────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
