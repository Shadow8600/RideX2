/**
 * RideX – Ride Fare Comparison Platform (Pune · Live Fares)
 * Core Frontend Interactions & Validations
 */

document.addEventListener('DOMContentLoaded', function () {
    initMobileNav();
    initFlashAlerts();
    initLoginInteractions();
    initRegisterValidation();
    initProfileInteractions();
    initDashboardFareComparison();
    initVehiclePreferences();
});

/* ==========================================================================
   1. Mobile Navigation Menu Toggle
   ========================================================================== */
function initMobileNav() {
    const toggleBtn = document.getElementById('mobile-menu-toggle');
    const navMenu = document.getElementById('nav-menu');

    if (toggleBtn && navMenu) {
        toggleBtn.addEventListener('click', function () {
            navMenu.classList.toggle('show');
        });

        // Close on clicking outside
        document.addEventListener('click', function (e) {
            if (!toggleBtn.contains(e.target) && !navMenu.contains(e.target)) {
                navMenu.classList.remove('show');
            }
        });
    }
}

/* ==========================================================================
   2. Flash Alerts Auto-Dismissal
   ========================================================================== */
function initFlashAlerts() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        // Auto dismiss after 6 seconds if it's a success alert
        if (alert.classList.contains('alert-success')) {
            setTimeout(function () {
                if (alert.parentElement) {
                    alert.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
                    alert.style.opacity = '0';
                    alert.style.transform = 'translateY(-10px)';
                    setTimeout(() => alert.remove(), 400);
                }
            }, 5000);
        }
    });
}

/* ==========================================================================
   3. Feature One: Login Page Interactions & Validation
   ========================================================================== */
function initLoginInteractions() {
    const loginForm = document.getElementById('login-form');
    const specialIdInput = document.getElementById('special_id');
    const passwordInput = document.getElementById('password');
    const togglePwBtn = document.getElementById('toggle-password-btn');
    const eyeShow = document.getElementById('eye-icon-show');
    const eyeHide = document.getElementById('eye-icon-hide');
    const btnDemoFill = document.getElementById('btn-demo-fill');

    // Show / Hide Password toggle
    if (togglePwBtn && passwordInput) {
        togglePwBtn.addEventListener('click', function () {
            const isPassword = passwordInput.getAttribute('type') === 'password';
            passwordInput.setAttribute('type', isPassword ? 'text' : 'password');
            if (eyeShow && eyeHide) {
                eyeShow.classList.toggle('hidden', isPassword);
                eyeHide.classList.toggle('hidden', !isPassword);
            }
        });
    }

    // Auto-fill Demo Credentials
    if (btnDemoFill && specialIdInput && passwordInput) {
        btnDemoFill.addEventListener('click', function () {
            specialIdInput.value = 'RIDEX-7001';
            passwordInput.value = 'Password@123';
            clearErrors();
            
            // Visual highlight
            specialIdInput.classList.add('bg-highlight');
            passwordInput.classList.add('bg-highlight');
            setTimeout(() => {
                specialIdInput.classList.remove('bg-highlight');
                passwordInput.classList.remove('bg-highlight');
            }, 800);
        });
    }

    // Form submission validation
    if (loginForm && specialIdInput && passwordInput) {
        loginForm.addEventListener('submit', function (e) {
            clearErrors();
            let isValid = true;

            const specialIdVal = specialIdInput.value.trim();
            const passwordVal = passwordInput.value;

            if (!specialIdVal) {
                showFieldError('special_id', 'Special ID is required.');
                specialIdInput.classList.add('is-invalid');
                isValid = false;
            }

            if (!passwordVal) {
                showFieldError('password', 'Password is required.');
                passwordInput.classList.add('is-invalid');
                isValid = false;
            }

            if (!isValid) {
                e.preventDefault();
            }
        });
    }

    function clearErrors() {
        document.querySelectorAll('.form-error-msg').forEach(el => el.textContent = '');
        document.querySelectorAll('.form-control').forEach(el => el.classList.remove('is-invalid'));
    }

    function showFieldError(fieldId, message) {
        const errEl = document.getElementById(fieldId + '-error');
        if (errEl) errEl.textContent = message;
    }
}

/* ==========================================================================
   Supporting Step: Register Form Validation
   ========================================================================== */
function initRegisterValidation() {
    const regForm = document.getElementById('register-form');
    if (!regForm) return;

    regForm.addEventListener('submit', function (e) {
        let isValid = true;
        document.querySelectorAll('.form-error-msg').forEach(el => el.textContent = '');
        document.querySelectorAll('.form-control').forEach(el => el.classList.remove('is-invalid'));

        const fullName = document.getElementById('full_name');
        const specialId = document.getElementById('reg_special_id');
        const email = document.getElementById('reg_email');
        const password = document.getElementById('reg_password');
        const confirmPw = document.getElementById('confirm_password');

        if (fullName && !fullName.value.trim()) {
            setErr(fullName, 'Please enter your full name.');
            isValid = false;
        }

        if (specialId) {
            const val = specialId.value.trim();
            if (!val) {
                setErr(specialId, 'Please choose a Special ID.');
                isValid = false;
            } else if (!/^[A-Za-z0-9_-]{4,20}$/.test(val)) {
                setErr(specialId, 'Must be 4–20 alphanumeric characters (e.g. RIDEX-101).');
                isValid = false;
            }
        }

        if (email) {
            const val = email.value.trim();
            if (!val) {
                setErr(email, 'Please enter your email address.');
                isValid = false;
            } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val)) {
                setErr(email, 'Please enter a valid email format.');
                isValid = false;
            }
        }

        if (password) {
            const val = password.value;
            if (!val) {
                setErr(password, 'Password is required.');
                isValid = false;
            } else if (val.length < 6) {
                setErr(password, 'Password must be at least 6 characters.');
                isValid = false;
            }
        }

        if (confirmPw && password) {
            if (confirmPw.value !== password.value) {
                setErr(confirmPw, 'Passwords do not match.');
                isValid = false;
            }
        }

        if (!isValid) {
            e.preventDefault();
        }
    });

    function setErr(inputEl, msg) {
        inputEl.classList.add('is-invalid');
        const errEl = document.getElementById(inputEl.id + '-error');
        if (errEl) errEl.textContent = msg;
    }
}

/* ==========================================================================
   4. Feature Two: Profile Management Interactions
   ========================================================================== */
function initProfileInteractions() {
    const profileForm = document.getElementById('profile-form');
    const btnEdit = document.getElementById('btn-edit-profile');
    const btnCancel = document.getElementById('btn-cancel-edit');
    const btnSave = document.getElementById('btn-save-profile');
    const modeBadge = document.getElementById('profile-mode-badge');

    if (!profileForm || !btnEdit) return;

    const editableFields = [
        document.getElementById('full_name'),
        document.getElementById('email'),
        document.getElementById('phone'),
        document.getElementById('emergency_contact'),
        document.getElementById('home_address'),
        document.getElementById('work_address'),
        document.getElementById('preferred_payment')
    ].filter(Boolean);

    // Switch to Edit Mode
    btnEdit.addEventListener('click', function () {
        setEditMode(true);
    });

    // Cancel Edit Mode and restore original data
    if (btnCancel) {
        btnCancel.addEventListener('click', function () {
            // Restore values
            editableFields.forEach(function (field) {
                const originalVal = field.getAttribute('data-original');
                if (originalVal !== null) {
                    field.value = originalVal;
                }
                field.classList.remove('is-invalid');
            });
            clearProfileErrors();
            setEditMode(false);
        });
    }

    // Client-side validation before saving
    profileForm.addEventListener('submit', function (e) {
        clearProfileErrors();
        let isValid = true;

        const fullName = document.getElementById('full_name');
        const email = document.getElementById('email');
        const phone = document.getElementById('phone');
        const emergency = document.getElementById('emergency_contact');

        if (fullName && !fullName.value.trim()) {
            showProfileErr(fullName, 'Full Name cannot be empty.');
            isValid = false;
        }

        if (email) {
            const emailVal = email.value.trim();
            if (!emailVal) {
                showProfileErr(email, 'Email Address cannot be empty.');
                isValid = false;
            } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailVal)) {
                showProfileErr(email, 'Please provide a valid email format.');
                isValid = false;
            }
        }

        if (phone && phone.value.trim()) {
            const pVal = phone.value.trim().replace(/[\s-]/g, '');
            if (!/^\d{10}$/.test(pVal)) {
                showProfileErr(phone, 'Phone number must be a 10-digit number.');
                isValid = false;
            }
        }

        if (emergency && emergency.value.trim()) {
            const eVal = emergency.value.trim().replace(/[\s-]/g, '');
            if (!/^\d{10}$/.test(eVal)) {
                showProfileErr(emergency, 'Emergency contact must be a 10-digit number.');
                isValid = false;
            }
        }

        if (!isValid) {
            e.preventDefault();
        }
    });

    function setEditMode(isEditing) {
        editableFields.forEach(field => {
            field.disabled = !isEditing;
        });

        if (isEditing) {
            btnEdit.classList.add('hidden');
            if (btnCancel) btnCancel.classList.remove('hidden');
            if (btnSave) btnSave.classList.remove('hidden');
            if (modeBadge) {
                modeBadge.textContent = 'Editing Mode';
                modeBadge.classList.add('mode-edit');
            }
            if (editableFields[0]) editableFields[0].focus();
        } else {
            btnEdit.classList.remove('hidden');
            if (btnCancel) btnCancel.classList.add('hidden');
            if (btnSave) btnSave.classList.add('hidden');
            if (modeBadge) {
                modeBadge.textContent = 'View Mode';
                modeBadge.classList.remove('mode-edit');
            }
        }
    }

    function clearProfileErrors() {
        document.querySelectorAll('#profile-form .form-error-msg').forEach(el => el.textContent = '');
        document.querySelectorAll('#profile-form .form-control').forEach(el => el.classList.remove('is-invalid'));
    }

    function showProfileErr(fieldEl, msg) {
        fieldEl.classList.add('is-invalid');
        const errEl = document.getElementById(fieldEl.id + '-error');
        if (errEl) errEl.textContent = msg;
    }
}

/* ==========================================================================
   5. Feature Three: Ride Fare Comparison (Dashboard)
   ========================================================================== */
function initDashboardFareComparison() {
    const pickupInput = document.getElementById('pickup-input');
    const destInput = document.getElementById('destination-input');
    const btnSearch = document.getElementById('btn-search-rides');
    const btnSwap = document.getElementById('btn-swap-locations');
    const prefToggle = document.getElementById('preferred-only-toggle');
    const sortSelect = document.getElementById('sort-select');
    const cardsContainer = document.getElementById('ride-cards-container');
    const emptyStateCard = document.getElementById('empty-state-card');
    const btnResetFilter = document.getElementById('btn-reset-filter');
    const displayDist = document.getElementById('display-distance');
    const displayDur = document.getElementById('display-duration');
    const summaryPickup = document.getElementById('summary-pickup');
    const summaryDest = document.getElementById('summary-dest');
    const countBadge = document.getElementById('results-count-badge');
    const searchBtnText = document.getElementById('search-btn-text');

    if (!btnSearch || !pickupInput || !destInput) return;

    // Swap Locations Handler
    if (btnSwap) {
        btnSwap.addEventListener('click', function () {
            const temp = pickupInput.value;
            pickupInput.value = destInput.value;
            destInput.value = temp;

            if (pickupInput.value && destInput.value) {
                fetchFareComparison();
            }
        });
    }

    // Quick Route Chips
    document.querySelectorAll('.quick-route-chip').forEach(function (chip) {
        chip.addEventListener('click', function () {
            const p = chip.getAttribute('data-pickup');
            const d = chip.getAttribute('data-dest');
            if (p && d) {
                pickupInput.value = p;
                destInput.value = d;
                fetchFareComparison();
            }
        });
    });

    // Search Rides on Click
    btnSearch.addEventListener('click', function () {
        fetchFareComparison();
    });

    // Enter key triggers search inside input fields
    [pickupInput, destInput].forEach(function (input) {
        input.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                fetchFareComparison();
            }
        });
    });

    // Preferred Only Filter Toggle
    if (prefToggle) {
        prefToggle.addEventListener('change', function () {
            fetchFareComparison();
        });
    }

    // Sort Select Change
    if (sortSelect) {
        sortSelect.addEventListener('change', function () {
            fetchFareComparison();
        });
    }

    // Reset filter button in empty state
    if (btnResetFilter && prefToggle) {
        btnResetFilter.addEventListener('click', function () {
            prefToggle.checked = false;
            fetchFareComparison();
        });
    }

    // Main fetch function for dynamic comparison
    function fetchFareComparison() {
        const pickupVal = pickupInput.value.trim();
        const destVal = destInput.value.trim();
        const preferredOnly = prefToggle ? prefToggle.checked : false;
        const sortBy = sortSelect ? sortSelect.value : 'lowest_fare';

        if (!pickupVal || !destVal) {
            alert('Please enter both pickup and destination locations in Pune.');
            return;
        }

        if (pickupVal.toLowerCase() === destVal.toLowerCase()) {
            alert('Pickup and destination cannot be the same location.');
            return;
        }

        // Loading state
        btnSearch.disabled = true;
        if (searchBtnText) searchBtnText.textContent = 'Comparing...';

        fetch('/api/compare-rides', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({
                pickup: pickupVal,
                destination: destVal,
                preferred_only: preferredOnly,
                sort_by: sortBy
            })
        })
        .then(res => res.json())
        .then(data => {
            btnSearch.disabled = false;
            if (searchBtnText) searchBtnText.textContent = 'Search Rides';

            if (data.error) {
                alert(data.error);
                return;
            }

            // Update journey metrics
            if (displayDist) displayDist.textContent = `${data.distance_km} km`;
            if (displayDur) displayDur.textContent = `${data.duration_min} min`;
            if (summaryPickup) summaryPickup.textContent = pickupVal;
            if (summaryDest) summaryDest.textContent = destVal;
            if (countBadge) countBadge.textContent = `${data.cards_count} options`;

            renderRideCards(data.cards);
        })
        .catch(err => {
            btnSearch.disabled = false;
            if (searchBtnText) searchBtnText.textContent = 'Search Rides';
            console.error('Error fetching ride fares:', err);
        });
    }

    function renderRideCards(cards) {
        if (!cardsContainer) return;

        if (!cards || cards.length === 0) {
            cardsContainer.innerHTML = '';
            if (emptyStateCard) emptyStateCard.classList.remove('hidden');
            return;
        }

        if (emptyStateCard) emptyStateCard.classList.add('hidden');

        let html = '';
        cards.forEach(function (ride) {
            const lowestClass = ride.is_lowest ? 'card-lowest-price' : '';
            const lowestBadge = ride.is_lowest ? `
                <div class="lowest-price-badge">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
                    <span>Lowest Price</span>
                </div>
            ` : '';

            const prefTag = ride.is_preferred ? `
                <span class="user-pref-tag" title="Matches your vehicle preferences">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
                    Preferred
                </span>
            ` : '';

            const providerClass = 'provider-' + ride.provider.toLowerCase();
            const diffNote = ride.is_lowest ? '<span class="text-cheapest">Best value on this route</span>' : '<span>Standard rate</span>';

            html += `
            <div class="ride-card ${lowestClass}">
                ${lowestBadge}
                <div class="ride-card-top">
                    <div class="ride-provider-group">
                        <div class="provider-pill ${providerClass}">${ride.provider}</div>
                        <div class="ride-vehicle-info">
                            <h3 class="vehicle-title">${ride.vehicle}</h3>
                            <span class="vehicle-category-sub">${ride.category}</span>
                        </div>
                    </div>
                    ${prefTag}
                </div>

                <div class="ride-card-body">
                    <div class="ride-fare-block">
                        <span class="fare-currency">₹</span>
                        <span class="fare-amount">${ride.fare}</span>
                        <span class="fare-note">demo estimate</span>
                    </div>

                    <div class="ride-metrics-list">
                        <div class="ride-metric-row">
                            <span class="metric-icon">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                            </span>
                            <span class="metric-title">Pickup ETA:</span>
                            <strong class="metric-text">${ride.eta}</strong>
                        </div>
                        <div class="ride-metric-row">
                            <span class="metric-icon">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
                            </span>
                            <span class="metric-title">Journey:</span>
                            <strong class="metric-text">${ride.duration}</strong>
                        </div>
                        <div class="ride-metric-row">
                            <span class="metric-icon">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
                            </span>
                            <span class="metric-title">Driver Rating:</span>
                            <strong class="metric-text">${ride.rating}</strong>
                        </div>
                    </div>
                </div>

                <div class="ride-card-footer">
                    <span class="fare-status-tag">Demo Pune Fare</span>
                    <span class="fare-diff-note">${diffNote}</span>
                </div>
            </div>
            `;
        });

        cardsContainer.innerHTML = html;
    }
}

/* ==========================================================================
   6. Feature Four: Vehicle Choice Preference Interactions
   ========================================================================== */
function initVehiclePreferences() {
    const prefForm = document.getElementById('preferences-form');
    const counterEl = document.getElementById('selected-count');
    const btnSelectAll = document.getElementById('btn-select-all');
    const btnClearAll = document.getElementById('btn-clear-all');

    if (!prefForm) return;

    const cards = document.querySelectorAll('.vehicle-pref-card');
    const checkboxes = document.querySelectorAll('.vehicle-checkbox');

    // Click handler on card to toggle selection
    cards.forEach(function (card) {
        card.addEventListener('click', function (e) {
            // Avoid double toggle if direct click on input
            if (e.target.tagName.toLowerCase() === 'input') {
                updateCardVisuals(card);
                updateCount();
                return;
            }

            const checkbox = card.querySelector('.vehicle-checkbox');
            if (checkbox) {
                checkbox.checked = !checkbox.checked;
                updateCardVisuals(card);
                updateCount();
            }
        });
    });

    // Select All button
    if (btnSelectAll) {
        btnSelectAll.addEventListener('click', function () {
            checkboxes.forEach(cb => cb.checked = true);
            cards.forEach(card => card.classList.add('selected'));
            updateCount();
        });
    }

    // Clear All button
    if (btnClearAll) {
        btnClearAll.addEventListener('click', function () {
            checkboxes.forEach(cb => cb.checked = false);
            cards.forEach(card => card.classList.remove('selected'));
            updateCount();
        });
    }

    function updateCardVisuals(card) {
        const cb = card.querySelector('.vehicle-checkbox');
        if (cb && cb.checked) {
            card.classList.add('selected');
        } else {
            card.classList.remove('selected');
        }
    }

    function updateCount() {
        if (!counterEl) return;
        const count = Array.from(checkboxes).filter(cb => cb.checked).length;
        counterEl.textContent = count;
    }
}
