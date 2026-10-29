import os
import re
import sqlite3
import hashlib
from datetime import timedelta
from functools import wraps
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify,
    g
)
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'ridex-super-secret-key-pune-2025')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
DATABASE = os.getenv('DATABASE_PATH', os.path.join(os.path.dirname(__file__), 'database', 'ridex.db'))

# Ensure database directory exists
os.makedirs(os.path.dirname(DATABASE), exist_ok=True)

# Standard vehicle categories required by specification
VEHICLE_CATEGORIES = [
    {
        'id': 'bike',
        'name': 'Bike / Moto',
        'desc': 'Fast, agile, and budget-friendly solo ride for beating Pune traffic.',
        'icon': 'bike'
    },
    {
        'id': 'auto',
        'name': 'Auto Rickshaw',
        'desc': 'Classic city 3-wheeler for quick, reliable hops across Pune neighborhoods.',
        'icon': 'auto'
    },
    {
        'id': 'economy_sedan',
        'name': 'Economy Sedan',
        'desc': 'Pocket-friendly air-conditioned 4-seater hatchback/sedan for everyday trips.',
        'icon': 'car-economy'
    },
    {
        'id': 'premium_sedan',
        'name': 'Premium Sedan',
        'desc': 'High-comfort executive sedans with top-rated drivers and spacious legroom.',
        'icon': 'car-premium'
    },
    {
        'id': 'suv',
        'name': 'SUV',
        'desc': 'Spacious 6-7 seater rides ideal for group travel, family outings, and luggage.',
        'icon': 'suv'
    },
    {
        'id': 'ev',
        'name': 'Electric Vehicle',
        'desc': 'Eco-friendly zero-emission ride delivering quiet, green city commuting.',
        'icon': 'leaf-car'
    }
]

# Popular Pune Landmarks for instant search and smart distance simulation
PUNE_LOCATIONS = [
    'Pune Railway Station',
    'Swargate Bus Stand',
    'Hinjewadi IT Park (Phase 1)',
    'Hinjewadi IT Park (Phase 3)',
    'Viman Nagar (Symbiosis / Airport Rd)',
    'Pune Airport (Lohegaon)',
    'Kothrud Stand (Paud Road)',
    'Baner High Street',
    'Hadapsar (Magarpatta City)',
    'Shivajinagar Bus & Metro Station',
    'Koregaon Park (North Main Road)',
    'Aundh (Parihar Chowk)',
    'Wakad (Datta Mandir Chowk)',
    'Kharadi (EON Free Zone)',
    'Katraj (Snake Park Chowk)'
]

# Database helpers
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize database tables and seed demo user if not present."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            special_id TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            emergency_contact TEXT,
            home_address TEXT,
            work_address TEXT,
            preferred_payment TEXT DEFAULT 'UPI',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # User Vehicle Preferences Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            vehicle_category TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            UNIQUE(user_id, vehicle_category)
        )
    ''')

    # Seed initial demo user if database is empty
    cursor.execute('SELECT COUNT(*) FROM users')
    count = cursor.fetchone()[0]
    if count == 0:
        demo_special_id = 'RIDEX-7001'
        demo_password = generate_password_hash('Password@123')
        demo_full_name = 'Aarav Sharma'
        demo_email = 'aarav.sharma@example.com'
        demo_phone = '9876543210'
        demo_emergency = '9876500000'
        demo_home = 'Flat 402, Green Meadows, Kothrud, Pune'
        demo_work = 'Tech Park, Phase 1, Hinjewadi, Pune'
        demo_payment = 'UPI'

        cursor.execute('''
            INSERT INTO users (special_id, password_hash, full_name, email, phone,
                               emergency_contact, home_address, work_address, preferred_payment)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (demo_special_id, demo_password, demo_full_name, demo_email, demo_phone,
              demo_emergency, demo_home, demo_work, demo_payment))
        
        user_id = cursor.lastrowid
        # Seed default preferred vehicle categories
        default_prefs = ['Bike / Moto', 'Auto Rickshaw', 'Economy Sedan']
        for pref in default_prefs:
            cursor.execute('''
                INSERT INTO user_preferences (user_id, vehicle_category)
                VALUES (?, ?)
            ''', (user_id, pref))
        
        conn.commit()

    conn.close()

# Initialize DB at startup
init_db()

# Authentication Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in with your Special ID to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Context processor to make logged in user available to templates
@app.context_processor
def inject_user():
    if 'user_id' in session:
        db = get_db()
        user = db.execute('SELECT id, special_id, full_name, email FROM users WHERE id = ?',
                          (session['user_id'],)).fetchone()
        return {'current_user': user}
    return {'current_user': None}

# Calculation helper for realistic Pune demo fares
def calculate_journey_metrics(pickup, destination):
    """Estimate distance and duration between pickup and destination."""
    p_norm = pickup.strip().lower()
    d_norm = destination.strip().lower()

    # Coordinate / distance simulation logic
    known_distances = {
        ('swargate', 'hinjewadi'): (21.5, 48),
        ('hinjewadi', 'swargate'): (21.5, 48),
        ('pune railway station', 'hinjewadi'): (19.0, 42),
        ('hinjewadi', 'pune railway station'): (19.0, 42),
        ('pune railway station', 'viman nagar'): (8.2, 22),
        ('viman nagar', 'pune railway station'): (8.2, 22),
        ('kothrud', 'hinjewadi'): (17.5, 36),
        ('hinjewadi', 'kothrud'): (17.5, 36),
        ('swargate', 'airport'): (14.0, 38),
        ('airport', 'swargate'): (14.0, 38),
        ('baner', 'magarpatta'): (23.0, 52),
        ('magarpatta', 'baner'): (23.0, 52),
        ('kothrud', 'viman nagar'): (16.0, 40),
        ('viman nagar', 'kothrud'): (16.0, 40),
        ('shivajinagar', 'airport'): (10.5, 28),
        ('airport', 'shivajinagar'): (10.5, 28),
        ('aundh', 'kharadi'): (18.5, 45),
        ('kharadi', 'aundh'): (18.5, 45)
    }

    # Check approximate known route matches
    matched_distance = None
    matched_duration = None
    for (k1, k2), (dist, dur) in known_distances.items():
        if k1 in p_norm and k2 in d_norm:
            matched_distance, matched_duration = dist, dur
            break

    if matched_distance is None:
        # Deterministic hash calculation for any custom input strings
        combined = f"{p_norm}::{d_norm}"
        h_val = int(hashlib.md5(combined.encode('utf-8')).hexdigest()[:8], 16)
        matched_distance = round(4.5 + (h_val % 260) / 10.0, 1) # between 4.5 km and 30.5 km
        matched_duration = int(matched_distance * 2.2 + 6) # estimated Pune city travel time

    return matched_distance, matched_duration

def generate_fare_comparison_data(distance_km, duration_min, preferred_only=False, user_prefs=None):
    """
    Generate demonstration fare comparison cards across providers.
    Uses Pune rate factors per vehicle type with realistic sample provider pricing.
    """
    if user_prefs is None:
        user_prefs = []

    # Provider rate matrix (base fare, per_km, per_min, eta_range, icon_tag)
    # Providers: Rapido, Ola, Uber, InDrive
    vehicles_data = [
        {
            'category': 'Bike / Moto',
            'options': [
                {
                    'provider': 'Rapido',
                    'vehicle': 'Rapido Bike',
                    'base': 25,
                    'per_km': 10.5,
                    'eta': '3 min',
                    'eta_num': 3,
                    'rating': '4.8 ★'
                },
                {
                    'provider': 'Uber',
                    'vehicle': 'Uber Moto',
                    'base': 25,
                    'per_km': 11.2,
                    'eta': '5 min',
                    'eta_num': 5,
                    'rating': '4.7 ★'
                },
                {
                    'provider': 'Ola',
                    'vehicle': 'Ola Bike',
                    'base': 28,
                    'per_km': 11.5,
                    'eta': '4 min',
                    'eta_num': 4,
                    'rating': '4.6 ★'
                }
            ]
        },
        {
            'category': 'Auto Rickshaw',
            'options': [
                {
                    'provider': 'Ola',
                    'vehicle': 'Ola Auto',
                    'base': 30,
                    'per_km': 15.0,
                    'eta': '4 min',
                    'eta_num': 4,
                    'rating': '4.7 ★'
                },
                {
                    'provider': 'Uber',
                    'vehicle': 'Uber Auto',
                    'base': 32,
                    'per_km': 15.5,
                    'eta': '6 min',
                    'eta_num': 6,
                    'rating': '4.8 ★'
                },
                {
                    'provider': 'Rapido',
                    'vehicle': 'Rapido Auto',
                    'base': 28,
                    'per_km': 14.8,
                    'eta': '5 min',
                    'eta_num': 5,
                    'rating': '4.6 ★'
                }
            ]
        },
        {
            'category': 'Economy Sedan',
            'options': [
                {
                    'provider': 'Uber',
                    'vehicle': 'Uber Go',
                    'base': 60,
                    'per_km': 20.0,
                    'eta': '6 min',
                    'eta_num': 6,
                    'rating': '4.8 ★'
                },
                {
                    'provider': 'InDrive',
                    'vehicle': 'InDrive Comfort',
                    'base': 50,
                    'per_km': 19.0,
                    'eta': '8 min',
                    'eta_num': 8,
                    'rating': '4.6 ★'
                },
                {
                    'provider': 'Ola',
                    'vehicle': 'Ola Mini',
                    'base': 65,
                    'per_km': 20.5,
                    'eta': '5 min',
                    'eta_num': 5,
                    'rating': '4.7 ★'
                }
            ]
        },
        {
            'category': 'Premium Sedan',
            'options': [
                {
                    'provider': 'Uber',
                    'vehicle': 'Uber Premier',
                    'base': 110,
                    'per_km': 29.0,
                    'eta': '7 min',
                    'eta_num': 7,
                    'rating': '4.9 ★'
                },
                {
                    'provider': 'Ola',
                    'vehicle': 'Ola Prime Sedan',
                    'base': 115,
                    'per_km': 30.0,
                    'eta': '8 min',
                    'eta_num': 8,
                    'rating': '4.8 ★'
                }
            ]
        },
        {
            'category': 'SUV',
            'options': [
                {
                    'provider': 'Uber',
                    'vehicle': 'Uber XL',
                    'base': 150,
                    'per_km': 36.0,
                    'eta': '9 min',
                    'eta_num': 9,
                    'rating': '4.8 ★'
                },
                {
                    'provider': 'Ola',
                    'vehicle': 'Ola Prime SUV',
                    'base': 155,
                    'per_km': 37.0,
                    'eta': '10 min',
                    'eta_num': 10,
                    'rating': '4.7 ★'
                }
            ]
        },
        {
            'category': 'Electric Vehicle',
            'options': [
                {
                    'provider': 'Uber',
                    'vehicle': 'Uber Green EV',
                    'base': 70,
                    'per_km': 21.0,
                    'eta': '6 min',
                    'eta_num': 6,
                    'rating': '4.9 ★'
                },
                {
                    'provider': 'Ola',
                    'vehicle': 'Ola Electric Ride',
                    'base': 65,
                    'per_km': 21.5,
                    'eta': '7 min',
                    'eta_num': 7,
                    'rating': '4.8 ★'
                }
            ]
        }
    ]

    cards = []
    for cat_data in vehicles_data:
        cat_name = cat_data['category']
        
        # If filtering by user preferred vehicles
        if preferred_only and user_prefs and cat_name not in user_prefs:
            continue

        for opt in cat_data['options']:
            # Calculate estimated fare in Indian Rupees (₹)
            calc_fare = round(opt['base'] + (distance_km * opt['per_km']))
            # Add small realistic variance
            cards.append({
                'provider': opt['provider'],
                'vehicle': opt['vehicle'],
                'category': cat_name,
                'fare': calc_fare,
                'fare_display': f"₹{calc_fare}",
                'eta': opt['eta'],
                'eta_num': opt['eta_num'],
                'duration': f"{duration_min} min",
                'rating': opt['rating'],
                'is_preferred': cat_name in user_prefs,
                'is_lowest': False
            })

    # Identify the lowest-priced option among all generated cards
    if cards:
        min_fare = min(c['fare'] for c in cards)
        for c in cards:
            if c['fare'] == min_fare:
                c['is_lowest'] = True
                break

    return cards

# ----------------- ROUTES ----------------- #

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# Feature 1: Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        special_id = request.form.get('special_id', '').strip()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember_me'))

        # Validation
        if not special_id or not password:
            flash('Please enter both your Special ID and Password.', 'error')
            return render_template('login.html', special_id=special_id)

        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE UPPER(special_id) = UPPER(?)',
            (special_id,)
        ).fetchone()

        if user and check_password_hash(user['password_hash'], password):
            # Login successful
            session.clear()
            session['user_id'] = user['id']
            session['special_id'] = user['special_id']
            session['full_name'] = user['full_name']
            session.permanent = remember

            flash(f"Welcome back, {user['full_name']}! You are successfully logged in.", 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid Special ID or Password. Please check your credentials.', 'error')
            return render_template('login.html', special_id=special_id)

    return render_template('login.html')

# Supporting Step: Account Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        special_id = request.form.get('special_id', '').strip().upper()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Server-side validations
        if not full_name or not special_id or not email or not password:
            flash('Please fill in all mandatory fields.', 'error')
            return render_template('register.html', full_name=full_name, special_id=special_id, email=email, phone=phone)

        if not re.match(r'^[A-Z0-9_-]{4,20}$', special_id):
            flash('Special ID must be 4-20 alphanumeric characters (e.g., RIDEX-102).', 'error')
            return render_template('register.html', full_name=full_name, special_id=special_id, email=email, phone=phone)

        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            flash('Please enter a valid email address.', 'error')
            return render_template('register.html', full_name=full_name, special_id=special_id, email=email, phone=phone)

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('register.html', full_name=full_name, special_id=special_id, email=email, phone=phone)

        if password != confirm_password:
            flash('Passwords do not match. Please re-enter.', 'error')
            return render_template('register.html', full_name=full_name, special_id=special_id, email=email, phone=phone)

        db = get_db()
        # Check uniqueness of Special ID & Email
        existing_id = db.execute('SELECT id FROM users WHERE UPPER(special_id) = ?', (special_id,)).fetchone()
        if existing_id:
            flash('This Special ID is already registered. Please choose a different one.', 'error')
            return render_template('register.html', full_name=full_name, email=email, phone=phone)

        existing_email = db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
        if existing_email:
            flash('This email address is already registered. Please log in.', 'error')
            return render_template('register.html', full_name=full_name, special_id=special_id, phone=phone)

        # Create user
        hashed_pw = generate_password_hash(password)
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO users (special_id, password_hash, full_name, email, phone, preferred_payment)
            VALUES (?, ?, ?, ?, ?, 'UPI')
        ''', (special_id, hashed_pw, full_name, email, phone))
        new_user_id = cursor.lastrowid

        # Insert default preferences for newly created user
        default_prefs = ['Bike / Moto', 'Auto Rickshaw', 'Economy Sedan']
        for pref in default_prefs:
            cursor.execute('''
                INSERT INTO user_preferences (user_id, vehicle_category)
                VALUES (?, ?)
            ''', (new_user_id, pref))

        db.commit()

        flash(f'Account created successfully for {special_id}! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

# Feature 3: Ride Fare Comparison (Dashboard)
@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    user_id = session['user_id']
    
    # Fetch user vehicle preferences
    pref_rows = db.execute(
        'SELECT vehicle_category FROM user_preferences WHERE user_id = ?',
        (user_id,)
    ).fetchall()
    user_prefs = [row['vehicle_category'] for row in pref_rows]

    # Default initial search sample
    default_pickup = 'Pune Railway Station'
    default_destination = 'Hinjewadi IT Park (Phase 1)'
    distance, duration = calculate_journey_metrics(default_pickup, default_destination)
    initial_cards = generate_fare_comparison_data(distance, duration, preferred_only=False, user_prefs=user_prefs)

    return render_template(
        'dashboard.html',
        pune_locations=PUNE_LOCATIONS,
        user_prefs=user_prefs,
        default_pickup=default_pickup,
        default_destination=default_destination,
        distance=distance,
        duration=duration,
        rides=initial_cards
    )

# Ride Fare Comparison API for dynamic recalculation
@app.route('/api/compare-rides', methods=['POST'])
@login_required
def api_compare_rides():
    data = request.get_json() or {}
    pickup = data.get('pickup', '').strip()
    destination = data.get('destination', '').strip()
    preferred_only = bool(data.get('preferred_only', False))
    sort_by = data.get('sort_by', 'lowest_fare') # 'lowest_fare', 'lowest_eta', 'provider'

    if not pickup or not destination:
        return jsonify({'error': 'Please enter both pickup and destination locations.'}), 400

    if pickup.lower() == destination.lower():
        return jsonify({'error': 'Pickup and destination cannot be identical.'}), 400

    db = get_db()
    user_id = session['user_id']
    pref_rows = db.execute(
        'SELECT vehicle_category FROM user_preferences WHERE user_id = ?',
        (user_id,)
    ).fetchall()
    user_prefs = [row['vehicle_category'] for row in pref_rows]

    distance, duration = calculate_journey_metrics(pickup, destination)
    cards = generate_fare_comparison_data(distance, duration, preferred_only=preferred_only, user_prefs=user_prefs)

    # Sorting
    if sort_by == 'lowest_fare':
        cards.sort(key=lambda x: x['fare'])
    elif sort_by == 'lowest_eta':
        cards.sort(key=lambda x: x['eta_num'])
    elif sort_by == 'category':
        cards.sort(key=lambda x: x['category'])

    # Re-verify lowest badge after sorting
    if cards:
        min_fare = min(c['fare'] for c in cards)
        for c in cards:
            c['is_lowest'] = (c['fare'] == min_fare)

    return jsonify({
        'success': True,
        'distance_km': distance,
        'duration_min': duration,
        'cards_count': len(cards),
        'cards': cards,
        'preferred_only': preferred_only,
        'user_prefs': user_prefs
    })

# Feature 2: Profile Management
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    db = get_db()
    user_id = session['user_id']

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        emergency_contact = request.form.get('emergency_contact', '').strip()
        home_address = request.form.get('home_address', '').strip()
        work_address = request.form.get('work_address', '').strip()
        preferred_payment = request.form.get('preferred_payment', 'UPI').strip()

        # Input validations
        if not full_name or not email:
            flash('Full Name and Email Address are mandatory.', 'error')
            user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
            return render_template('profile.html', user=user)

        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            flash('Please provide a valid email address.', 'error')
            user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
            return render_template('profile.html', user=user)

        # Check if email is taken by another user
        conflict = db.execute(
            'SELECT id FROM users WHERE email = ? AND id != ?',
            (email, user_id)
        ).fetchone()
        if conflict:
            flash('This email address is already linked to another account.', 'error')
            user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
            return render_template('profile.html', user=user)

        # Update profile (never exposing or touching passwords)
        db.execute('''
            UPDATE users
            SET full_name = ?, email = ?, phone = ?, emergency_contact = ?,
                home_address = ?, work_address = ?, preferred_payment = ?
            WHERE id = ?
        ''', (full_name, email, phone, emergency_contact, home_address, work_address, preferred_payment, user_id))
        db.commit()

        # Update session full name
        session['full_name'] = full_name

        flash('Your profile details have been successfully updated.', 'success')
        return redirect(url_for('profile'))

    # Load current user profile from SQLite
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    return render_template('profile.html', user=user)

# Feature 4: Vehicle Choice Preference
@app.route('/preferences', methods=['GET', 'POST'])
@login_required
def preferences():
    db = get_db()
    user_id = session['user_id']

    if request.method == 'POST':
        # Selected vehicle categories submitted from checkboxes/cards
        selected_categories = request.form.getlist('preferred_vehicles')

        # Replace user preferences in SQLite
        db.execute('DELETE FROM user_preferences WHERE user_id = ?', (user_id,))
        for category in selected_categories:
            db.execute('''
                INSERT INTO user_preferences (user_id, vehicle_category)
                VALUES (?, ?)
            ''', (user_id, category))
        db.commit()

        flash('Your vehicle preferences have been saved successfully and applied to ride comparisons.', 'success')
        return redirect(url_for('preferences'))

    # Load saved preferences from database
    saved_rows = db.execute(
        'SELECT vehicle_category FROM user_preferences WHERE user_id = ?',
        (user_id,)
    ).fetchall()
    saved_prefs = [row['vehicle_category'] for row in saved_rows]

    return render_template(
        'preferences.html',
        categories=VEHICLE_CATEGORIES,
        saved_prefs=saved_prefs
    )

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='127.0.0.1', port=port, debug=True)
