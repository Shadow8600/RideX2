# RideX – Pune Ride Fare Comparison Platform

**RideX** is a modern, responsive, and lightweight ride fare comparison web application built with **HTML5, CSS3, JavaScript, Python (Flask), and SQLite**.

Tagline: **"Pune · Live Fares"**

---

## Key Features

The platform focuses on four core transportation features:

1. **Login Page**
   - Clean, branded login interface with Pune tagline.
   - Special ID authentication (e.g., `RIDEX-7001`).
   - Show / Hide password toggle.
   - "Remember Me" checkbox with session persistence.
   - Instant "Auto-Fill Demo Credentials" button for quick evaluation.
   - Supporting user account registration.

2. **Profile Management**
   - Personal details view: Full Name, Special ID (permanent identifier), Email, Phone, Emergency Contact.
   - Saved Pune commute locations: Home Address and Work Address.
   - Preferred Payment Method (saved preference only: UPI, Cash, Card, Net Banking).
   - Interactive **Edit Profile**, **Save Changes**, and **Cancel** workflow with instant data restoration.
   - Secure SQLite persistence without exposing passwords.

3. **Ride Fare Comparison**
   - Pickup & Destination inputs with Pune landmark autocomplete (Pune Station, Swargate, Hinjewadi, Viman Nagar, Airport, Kothrud, Baner, etc.).
   - Quick route shortcut chips for instant one-click route comparisons.
   - Instant calculation of estimated distance (km) and journey duration (min).
   - Demonstration fare comparison cards across major Pune providers: **Rapido, Ola, Uber, and InDrive**.
   - Automatic highlighting of the **Lowest Price** option with a distinct badge.
   - Sort options: Lowest Fare First, Fastest Pickup ETA, or Vehicle Category.
   - Integration with user's vehicle preferences.

4. **Vehicle Choice Preference**
   - Six selectable vehicle category cards:
     1. **Bike / Moto** (Rapido, Uber Moto, Ola Bike)
     2. **Auto Rickshaw** (Ola Auto, Uber Auto, Rapido Auto)
     3. **Economy Sedan** (Uber Go, InDrive, Ola Mini)
     4. **Premium Sedan** (Uber Premier, Ola Prime Sedan)
     5. **SUV** (Uber XL, Ola Prime SUV)
     6. **Electric Vehicle** (Uber Green EV, Ola Electric Ride)
   - Visual vector icons, short descriptions, and selection indicators.
   - "Select All" and "Clear All" utility buttons.
   - Saved directly to SQLite database and loaded upon subsequent logins.
   - Filter toggle on dashboard to show only preferred vehicles.

---

## Design System & Theme

- **Main background:** White (`#FFFFFF`)
- **Section backgrounds:** Light gray (`#F7F9FC`)
- **Primary color:** Soft blue (`#3B82F6`)
- **Secondary accent:** Light cyan (`#06B6D4`)
- **Primary text:** Dark charcoal (`#1F2937`)
- **Secondary text:** Gray (`#6B7280`)
- **Cards:** Rounded corners (`16px`), subtle drop shadows, smooth transitions, and hover elevation.
- **Responsive:** Optimized for mobile phones, tablets, and desktop viewports.

---

## Technology Stack

- **Frontend:** HTML5, Vanilla CSS3 (Custom Design System), Vanilla JavaScript (No React, Vue, or heavy dependencies).
- **Backend:** Python 3 (Flask framework, Flask sessions, Werkzeug security).
- **Database:** SQLite (`database/ridex.db`) with automatic table creation and default demo user seeding.

---

## Project Structure

```
RideX/
├── app.py                  # Core Flask server, routing, auth & comparison engine
├── test_suite.py           # Comprehensive end-to-end unit test suite
├── requirements.txt        # Python dependency specifications
├── .env.example            # Environment configuration template
├── .env                    # Local environment settings
├── database/
│   └── ridex.db            # SQLite database (auto-created on startup)
├── templates/
│   ├── base.html           # Master layout with responsive navbar & alerts
│   ├── login.html          # Feature 1: Login page
│   ├── register.html       # Supporting step: Account creation
│   ├── dashboard.html      # Feature 3: Ride fare comparison dashboard
│   ├── profile.html        # Feature 2: Profile management
│   └── preferences.html    # Feature 4: Vehicle choice preference
└── static/
    ├── css/
    │   └── style.css       # Clean light-theme design system and CSS styling
    └── js/
        └── script.js       # Client-side validation and dynamic comparison logic
```

---

## Installation & Setup Instructions

### 1. Prerequisites
- Python 3.10+ (or Python 3.13)
- pip

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env` (already configured by default):
```bash
cp .env.example .env
```

### 4. Run the Application
```bash
python app.py
```
*(On Windows systems where the Python launcher is used, you can also run `py app.py`)*

The server will start at:
```
http://127.0.0.1:5000
```

---

## Pre-configured Demo Account

A demonstration commuter profile is pre-seeded in the database:
- **Special ID:** `RIDEX-7001`
- **Password:** `Password@123`
- **Name:** Aarav Sharma
- **City:** Pune, Maharashtra
- **Pre-selected Preferences:** Bike / Moto, Auto Rickshaw, Economy Sedan

*(You can also click the **"Auto-Fill Demo Credentials"** button on the login screen or click **"Create an account"** to register a new Special ID)*

---

## Running Automated Tests

Run the full end-to-end verification suite:
```bash
py test_suite.py
```
This tests all 4 core features, session authentication, profile editing, dynamic fare calculation, sorting, and vehicle filtering.
