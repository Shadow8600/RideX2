import app

def run_tests():
    client = app.app.test_client()

    # 1. Test unauthenticated redirect
    res = client.get('/dashboard', follow_redirects=False)
    assert res.status_code == 302, f"Expected 302, got {res.status_code}"
    print("Check 1: Unauthenticated redirect to /login: PASSED")

    # 2. Test Login page GET
    res = client.get('/login')
    assert res.status_code == 200
    assert b"Welcome to RideX" in res.data
    print("Check 2: Login page renders correctly: PASSED")

    # 3. Test Login with valid credentials
    res = client.post('/login', data={'special_id': 'RIDEX-7001', 'password': 'Password@123'}, follow_redirects=True)
    assert res.status_code == 200
    assert b"Dashboard" in res.data
    assert b"RIDEX-7001" in res.data
    print("Check 3: Login authentication with RIDEX-7001: PASSED")

    # 4. Test Profile view and edit
    res = client.get('/profile')
    assert res.status_code == 200
    assert b"Aarav" in res.data
    res_edit = client.post('/profile', data={
        'full_name': 'Aarav K. Sharma',
        'email': 'aarav.sharma@example.com',
        'phone': '9876543210',
        'emergency_contact': '9876500000',
        'home_address': 'Flat 402, Green Meadows, Kothrud, Pune',
        'work_address': 'Tech Park, Phase 1, Hinjewadi, Pune',
        'preferred_payment': 'UPI'
    }, follow_redirects=True)
    assert res_edit.status_code == 200
    assert b"Aarav K. Sharma" in res_edit.data
    print("Check 4: Profile Management view and update: PASSED")

    # 5. Test Fare Comparison API
    res_fares = client.post('/api/compare-rides', json={
        'pickup': 'Swargate Bus Stand',
        'destination': 'Pune Airport (Lohegaon)',
        'preferred_only': False,
        'sort_by': 'lowest_fare'
    })
    assert res_fares.status_code == 200
    data = res_fares.get_json()
    assert data['success'] is True
    assert len(data['cards']) > 0
    assert any(c['is_lowest'] for c in data['cards'])
    print(f"Check 5: Fare Comparison API returned {len(data['cards'])} options with lowest fare: PASSED")

    # 6. Test Vehicle Preferences GET and POST
    res_pref = client.get('/preferences')
    assert res_pref.status_code == 200
    assert b"Bike / Moto" in res_pref.data
    res_pref_post = client.post('/preferences', data={
        'preferred_vehicles': ['Bike / Moto', 'Auto Rickshaw', 'Electric Vehicle']
    }, follow_redirects=True)
    assert res_pref_post.status_code == 200
    print("Check 6: Vehicle Preferences update: PASSED")

    # 7. Test Fare comparison with preferred_only=True
    res_filtered = client.post('/api/compare-rides', json={
        'pickup': 'Swargate Bus Stand',
        'destination': 'Pune Airport (Lohegaon)',
        'preferred_only': True,
        'sort_by': 'lowest_fare'
    })
    data_filtered = res_filtered.get_json()
    assert all(c['category'] in ['Bike / Moto', 'Auto Rickshaw', 'Electric Vehicle'] for c in data_filtered['cards'])
    print(f"Check 7: Filtered comparison ({len(data_filtered['cards'])} options) matches updated preferences: PASSED")

    # 8. Test Registration supporting step (with unauthenticated client)
    import time
    unique_suffix = str(int(time.time()))[-4:]
    test_special_id = f"RIDEX-8{unique_suffix}"
    test_email = f"user_{unique_suffix}@example.com"
    client.get('/logout') # clear session first
    res_reg = client.post('/register', data={
        'full_name': 'Priya Deshmukh',
        'special_id': test_special_id,
        'email': test_email,
        'phone': '9822001122',
        'password': 'SecurePassword123',
        'confirm_password': 'SecurePassword123'
    }, follow_redirects=True)
    assert res_reg.status_code == 200
    assert b"Account created successfully" in res_reg.data
    print("Check 8: User registration supporting step: PASSED")

    # 9. Test Login with new user
    res_login_new = client.post('/login', data={'special_id': test_special_id, 'password': 'SecurePassword123'}, follow_redirects=True)
    assert res_login_new.status_code == 200
    assert b"Priya Deshmukh" in res_login_new.data
    print("Check 9: New user login and dashboard session: PASSED")

    # 10. Test Logout
    res_logout = client.get('/logout', follow_redirects=True)
    assert res_logout.status_code == 200
    assert b"logged out successfully" in res_logout.data
    print("Check 10: Logout and session termination: PASSED")

    print("\n==========================================")
    print(" ALL 10 END-TO-END FEATURE CHECKS PASSED! ")
    print("==========================================")

if __name__ == '__main__':
    run_tests()
