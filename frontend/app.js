// Configuration
const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

// Default coordinates (will be updated from satellite coverage)
let SATELLITE_CENTER = [20.7489, 73.7294];
let SATELLITE_BOUNDS = [
    [20.5, 73.5],  // Southwest
    [21.0, 74.0]   // Northeast
];

// Global variables
let map;
let drawnItems;
let drawControl;
let currentPolygon = null;
let selectedBounds = null;

// Navigation functions
function goToApp() {
    document.getElementById('landing-page').style.display = 'none';
    document.getElementById('app-page').style.display = 'block';
    document.getElementById('floatingNavBtn').style.display = 'none';

    // Initialize map after showing app page
    setTimeout(initMap, 100);
}

function goToLanding() {
    document.getElementById('app-page').style.display = 'none';
    document.getElementById('landing-page').style.display = 'block';

    // Show floating button if scrolled
    checkFloatingButton();

    // Clean up map
    if (map) {
        map.remove();
        map = null;
    }
}

// Floating Navigation Button
function handleFloatingNav() {
    if (isUserLoggedIn) {
        goToApp();
    } else {
        window.openAuthModal();
    }
}

function checkFloatingButton() {
    const floatingBtn = document.getElementById('floatingNavBtn');
    const landingPage = document.getElementById('landing-page');

    if (landingPage && landingPage.style.display !== 'none') {
        // Show button after scrolling past hero section
        if (window.scrollY > window.innerHeight * 0.8) {
            floatingBtn.style.display = 'block';
            if (isUserLoggedIn) {
                document.getElementById('floatingBtnText').textContent = 'Go to App →';
            } else {
                document.getElementById('floatingBtnText').textContent = 'Sign In →';
            }
        } else {
            floatingBtn.style.display = 'none';
        }
    }
}

// Show/hide floating button on scroll
window.addEventListener('scroll', checkFloatingButton);

// User login state
let isUserLoggedIn = false;

// Initialize map
async function initMap() {
    if (map) return; // Already initialized

    // Fetch satellite coverage from backend
    let mapCenter = SATELLITE_CENTER;
    let mapZoom = 11;
    let satelliteBounds = null;

    try {
        const response = await fetch(`${API_BASE_URL}/satellite-coverage`);
        if (response.ok) {
            const coverage = await response.json();
            mapCenter = [coverage.center.lat, coverage.center.lon];

            // Update global bounds
            SATELLITE_CENTER = mapCenter;
            SATELLITE_BOUNDS = [
                [coverage.bounds.min_lat, coverage.bounds.min_lon],
                [coverage.bounds.max_lat, coverage.bounds.max_lon]
            ];
            satelliteBounds = coverage.bounds;

            // Calculate appropriate zoom level based on area size
            const latDiff = coverage.bounds.max_lat - coverage.bounds.min_lat;
            const lonDiff = coverage.bounds.max_lon - coverage.bounds.min_lon;
            const maxDiff = Math.max(latDiff, lonDiff);

            if (maxDiff > 1.0) mapZoom = 9;
            else if (maxDiff > 0.5) mapZoom = 10;
            else if (maxDiff > 0.2) mapZoom = 11;
            else if (maxDiff > 0.1) mapZoom = 12;
            else mapZoom = 13;

            console.log('✓ Satellite coverage loaded:', coverage);
            console.log('✓ Map will center at:', mapCenter);
            console.log('✓ Zoom level:', mapZoom);

            // Store coverage bounds for validation
            window.satelliteBounds = coverage.bounds;
        } else {
            console.warn('⚠ Could not load satellite coverage, using defaults');
        }
    } catch (error) {
        console.warn('⚠ Could not connect to backend:', error);
    }

    // Create map centered on satellite coverage
    map = L.map('map').setView(mapCenter, mapZoom);

    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 18
    }).addTo(map);

    // Add satellite layer option
    const satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: 'Tiles © Esri',
        maxZoom: 18
    });

    // Layer control
    const baseMaps = {
        "Street Map": L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }),
        "Satellite": satellite
    };

    L.control.layers(baseMaps).addTo(map);

    // Show satellite coverage area with prominent styling
    if (satelliteBounds) {
        const bounds = satelliteBounds;
        const coverageRect = L.rectangle(
            [[bounds.min_lat, bounds.min_lon], [bounds.max_lat, bounds.max_lon]],
            {
                color: '#10b981',
                weight: 3,
                fillColor: '#10b981',
                fillOpacity: 0.15,
                dashArray: '10, 10'
            }
        ).addTo(map);

        coverageRect.bindPopup(
            '<div style="font-family: sans-serif;">' +
            '<b style="color: #10b981; font-size: 14px;">✓ Satellite Image Coverage</b><br><br>' +
            '<b>Draw your polygon INSIDE this green box</b><br><br>' +
            '<span style="color: #666;">Coverage Area:</span><br>' +
            `Lat: ${bounds.min_lat.toFixed(4)}° to ${bounds.max_lat.toFixed(4)}°<br>` +
            `Lon: ${bounds.min_lon.toFixed(4)}° to ${bounds.max_lon.toFixed(4)}°<br><br>` +
            '<span style="color: #666;">Area Size:</span><br>' +
            `${((bounds.max_lat - bounds.min_lat) * 111).toFixed(1)} km × ` +
            `${((bounds.max_lon - bounds.min_lon) * 111 * Math.cos(bounds.min_lat * Math.PI / 180)).toFixed(1)} km` +
            '</div>'
        ).openPopup();

        // Fit map to satellite coverage
        map.fitBounds(SATELLITE_BOUNDS, { padding: [50, 50] });
    }

    // Initialize drawn items layer
    drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    // Add draw control
    drawControl = new L.Control.Draw({
        draw: {
            polygon: {
                allowIntersection: false,
                showArea: true,
                shapeOptions: {
                    color: '#667eea',
                    weight: 3
                }
            },
            polyline: false,
            rectangle: {
                shapeOptions: {
                    color: '#667eea',
                    weight: 3
                }
            },
            circle: false,
            marker: false,
            circlemarker: false
        },
        edit: {
            featureGroup: drawnItems,
            remove: true
        }
    });

    map.addControl(drawControl);

    // Handle draw events
    map.on(L.Draw.Event.CREATED, function (event) {
        const layer = event.layer;

        // Remove previous polygon
        if (currentPolygon) {
            drawnItems.removeLayer(currentPolygon);
        }

        // Add new polygon
        drawnItems.addLayer(layer);
        currentPolygon = layer;

        // Get bounds
        const bounds = layer.getBounds();
        selectedBounds = {
            min_lat: bounds.getSouth(),
            max_lat: bounds.getNorth(),
            min_lon: bounds.getWest(),
            max_lon: bounds.getEast()
        };

        // Validate bounds are within satellite coverage
        if (window.satelliteBounds) {
            const satBounds = window.satelliteBounds;
            if (selectedBounds.min_lat < satBounds.min_lat ||
                selectedBounds.max_lat > satBounds.max_lat ||
                selectedBounds.min_lon < satBounds.min_lon ||
                selectedBounds.max_lon > satBounds.max_lon) {

                alert('⚠️ Warning: Your polygon extends outside the satellite coverage area!\n\n' +
                    'Please draw your polygon INSIDE the green dashed box.\n\n' +
                    'Analysis may fail if you continue.');
            }
        }

        // Enable analyze button
        document.getElementById('analyze-btn').disabled = false;

        console.log('Region selected:', selectedBounds);
    });

    map.on(L.Draw.Event.DELETED, function () {
        currentPolygon = null;
        selectedBounds = null;
        document.getElementById('analyze-btn').disabled = true;
    });

    // Add center marker
    L.marker(mapCenter)
        .addTo(map)
        .bindPopup('<b>Satellite Image Center</b><br>Draw polygons within the green box');
}

// Button event listeners
document.addEventListener('DOMContentLoaded', function () {
    // Draw polygon button
    document.getElementById('draw-polygon-btn').addEventListener('click', function () {
        if (map) {
            new L.Draw.Polygon(map, drawControl.options.draw.polygon).enable();
        }
    });

    // Clear polygon button
    document.getElementById('clear-polygon-btn').addEventListener('click', function () {
        if (currentPolygon) {
            drawnItems.removeLayer(currentPolygon);
            currentPolygon = null;
            selectedBounds = null;
            document.getElementById('analyze-btn').disabled = true;
            hideResults();
        }
    });

    // Analyze button
    document.getElementById('analyze-btn').addEventListener('click', analyzeForest);
});

// Analyze forest
async function analyzeForest() {
    if (!selectedBounds) {
        alert('Please select a region first');
        return;
    }

    // Show loading
    showLoading();
    hideResults();
    hideError();

    try {
        // Prepare request
        const requestData = {
            bounds: selectedBounds,
            date: new Date().toISOString().split('T')[0] // Current date
        };

        console.log('Sending analysis request:', requestData);

        // Call API
        const response = await fetch(`${API_BASE_URL}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Analysis failed');
        }

        const result = await response.json();
        console.log('Analysis result:', result);

        // Display results
        displayResults(result.data);

    } catch (error) {
        console.error('Analysis error:', error);
        showError(error.message);
    } finally {
        hideLoading();
    }
}

// Display results
function displayResults(data) {
    const { kpis, tree_locations, ndvi_heatmap } = data;

    // Update KPIs with circular progress
    updateCircularKPI('tree-count', kpis.tree_count.toLocaleString(), 'tree-count-circle', Math.min(kpis.tree_count / 1000 * 100, 100));
    updateCircularKPI('area', kpis.area_hectares.toFixed(2), 'area-circle', Math.min(kpis.area_hectares / 10 * 100, 100));
    updateCircularKPI('density', kpis.tree_density.toFixed(0), 'density-circle', Math.min(kpis.tree_density / 500 * 100, 100));
    updateCircularKPI('health-score', kpis.health_score, 'health-circle', kpis.health_score);

    // Update NDVI stats
    document.getElementById('ndvi-mean').textContent = kpis.ndvi.mean.toFixed(3);
    document.getElementById('ndvi-min').textContent = kpis.ndvi.min.toFixed(3);
    document.getElementById('ndvi-max').textContent = kpis.ndvi.max.toFixed(3);
    document.getElementById('health-status').textContent = kpis.health_status;

    // Display species distribution
    displaySpeciesChart(kpis.species_distribution, kpis.species_counts);

    // Display tree locations
    displayTreeLocations(tree_locations);

    // Add tree markers to map
    addTreeMarkersToMap(tree_locations);

    // Show results
    showResults();
}

// Update circular KPI with animation
function updateCircularKPI(valueId, value, circleId, percentage) {
    // Update value
    document.getElementById(valueId).textContent = value;
    
    // Calculate circle progress
    const circle = document.getElementById(circleId);
    const radius = 70;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (percentage / 100) * circumference;
    
    // Animate the circle
    setTimeout(() => {
        circle.style.strokeDashoffset = offset;
    }, 100);
}

// Display species chart
function displaySpeciesChart(distribution, counts) {
    const chartContainer = document.getElementById('species-chart');
    chartContainer.innerHTML = '';

    // Sort by percentage
    const sortedSpecies = Object.entries(distribution)
        .sort((a, b) => b[1] - a[1]);

    sortedSpecies.forEach(([species, percentage]) => {
        const count = counts[species];

        const barDiv = document.createElement('div');
        barDiv.className = 'species-bar';

        barDiv.innerHTML = `
            <div class="species-name">${species}</div>
            <div class="species-bar-container">
                <div class="species-bar-fill" style="width: ${percentage}%">
                    ${percentage}%
                </div>
            </div>
            <div class="species-count">${count} trees</div>
        `;

        chartContainer.appendChild(barDiv);
    });
}

// Display tree locations
function displayTreeLocations(trees) {
    const listContainer = document.getElementById('tree-list');
    listContainer.innerHTML = '';

    // Show first 50 trees
    const displayTrees = trees.slice(0, 50);

    displayTrees.forEach((tree, index) => {
        const treeDiv = document.createElement('div');
        treeDiv.className = 'tree-item';

        treeDiv.innerHTML = `
            <div>
                <span class="tree-species">${tree.species}</span>
                <span style="color: #999; margin-left: 0.5rem;">
                    (${tree.lat.toFixed(4)}, ${tree.lon.toFixed(4)})
                </span>
            </div>
            <div class="tree-confidence">${(tree.confidence * 100).toFixed(1)}%</div>
        `;

        listContainer.appendChild(treeDiv);
    });

    if (trees.length > 50) {
        const moreDiv = document.createElement('div');
        moreDiv.className = 'tree-item';
        moreDiv.style.textAlign = 'center';
        moreDiv.style.color = '#999';
        moreDiv.textContent = `... and ${trees.length - 50} more trees`;
        listContainer.appendChild(moreDiv);
    }
}

// Add tree markers to map
function addTreeMarkersToMap(trees) {
    // Remove existing tree markers
    map.eachLayer(function (layer) {
        if (layer instanceof L.CircleMarker && layer.options.className === 'tree-marker') {
            map.removeLayer(layer);
        }
    });

    // Species colors
    const speciesColors = {
        'Teak': '#8B4513',
        'Bamboo': '#90EE90',
        'Sal': '#228B22',
        'Mango': '#FFD700',
        'Neem': '#32CD32'
    };

    // Add markers for first 200 trees (for performance)
    const displayTrees = trees.slice(0, 200);

    displayTrees.forEach(tree => {
        const color = speciesColors[tree.species] || '#667eea';

        L.circleMarker([tree.lat, tree.lon], {
            radius: 4,
            fillColor: color,
            color: '#fff',
            weight: 1,
            opacity: 1,
            fillOpacity: 0.8,
            className: 'tree-marker'
        })
            .bindPopup(`
            <b>${tree.species}</b><br>
            Confidence: ${(tree.confidence * 100).toFixed(1)}%<br>
            Location: ${tree.lat.toFixed(4)}, ${tree.lon.toFixed(4)}
        `)
            .addTo(map);
    });
}

// UI helper functions
function showLoading() {
    document.getElementById('emptyState').style.display = 'none';
    document.getElementById('loading').style.display = 'block';
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

function showResults() {
    document.getElementById('emptyState').style.display = 'none';
    document.getElementById('results').style.display = 'block';
}

function hideResults() {
    document.getElementById('results').style.display = 'none';
    document.getElementById('emptyState').style.display = 'flex';
}

function showError(message) {
    document.getElementById('error-message').textContent = message;
    document.getElementById('error').style.display = 'block';
}

function hideError() {
    document.getElementById('error').style.display = 'none';
}

// Test API connection on load
async function testAPIConnection() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            console.log('✓ API connection successful');
        } else {
            console.warn('⚠ API health check failed');
        }
    } catch (error) {
        console.warn('⚠ Could not connect to API:', error.message);
    }
}

// Test connection when app loads
testAPIConnection();

// Make auth functions globally accessible IMMEDIATELY
window.openAuthModal = function () {
    console.log('Opening auth modal...');
    const modal = document.getElementById('authModal');
    if (modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
        console.log('Auth modal opened');
    } else {
        console.error('Auth modal not found!');
    }
};

window.closeAuthModal = function () {
    const modal = document.getElementById('authModal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
        clearAuthErrors();
    }
};

window.toggleAuthForms = toggleAuthForms;
window.authSignInWithGoogle = authSignInWithGoogle;

// Auth Modal Functions
let authIsSignInMode = true;

function openAuthModal() {
    console.log('Opening auth modal...');
    const modal = document.getElementById('authModal');
    if (modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
        authIsSignInMode = true;
        showAuthSignIn();
        console.log('Auth modal opened');
    } else {
        console.error('Auth modal not found!');
    }
}

function closeAuthModal() {
    document.getElementById('authModal').style.display = 'none';
    document.body.style.overflow = 'auto';
    clearAuthErrors();
}

function showAuthSignIn() {
    document.getElementById('authSignInForm').style.display = 'block';
    document.getElementById('authRegisterForm').style.display = 'none';
    document.getElementById('authFormTitle').textContent = 'Welcome Back';
    document.getElementById('authFormSubtitle').textContent = 'Sign in to access your forest monitoring dashboard';
    document.getElementById('authToggleText').textContent = "Don't have an account?";
    document.getElementById('authToggleLink').textContent = 'Register';
}

function showAuthRegister() {
    document.getElementById('authSignInForm').style.display = 'none';
    document.getElementById('authRegisterForm').style.display = 'block';
    document.getElementById('authFormTitle').textContent = 'Create Account';
    document.getElementById('authFormSubtitle').textContent = 'Join us to start monitoring forests';
    document.getElementById('authToggleText').textContent = 'Already have an account?';
    document.getElementById('authToggleLink').textContent = 'Sign In';
}

function toggleAuthForms(event) {
    event.preventDefault();
    authIsSignInMode = !authIsSignInMode;

    if (authIsSignInMode) {
        showAuthSignIn();
    } else {
        showAuthRegister();
    }

    clearAuthErrors();
}

function clearAuthErrors() {
    document.querySelectorAll('.auth-error-msg').forEach(el => el.textContent = '');
    document.querySelectorAll('.auth-form-group input').forEach(el => el.classList.remove('error'));
}

function validateAuthEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Sign In Form Handler
function handleAuthSignIn(e) {
    e.preventDefault();
    console.log('Sign-in form submitted');
    clearAuthErrors();

    const email = document.getElementById('authSignInEmail').value.trim();
    const password = document.getElementById('authSignInPassword').value;
    const remember = document.getElementById('authRememberMe').checked;

    let isValid = true;

    if (!email) {
        document.getElementById('authSignInEmailError').textContent = 'Email is required';
        document.getElementById('authSignInEmail').classList.add('error');
        isValid = false;
    } else if (!validateAuthEmail(email)) {
        document.getElementById('authSignInEmailError').textContent = 'Please enter a valid email';
        document.getElementById('authSignInEmail').classList.add('error');
        isValid = false;
    }

    if (!password) {
        document.getElementById('authSignInPasswordError').textContent = 'Password is required';
        document.getElementById('authSignInPassword').classList.add('error');
        isValid = false;
    } else if (password.length < 6) {
        document.getElementById('authSignInPasswordError').textContent = 'Password must be at least 6 characters';
        document.getElementById('authSignInPassword').classList.add('error');
        isValid = false;
    }

    if (!isValid) return;

    document.getElementById('authSignInBtnText').style.display = 'none';
    document.getElementById('authSignInLoader').style.display = 'flex';

    setTimeout(() => {
        console.log('Sign-in successful');
        if (remember) {
            localStorage.setItem('userEmail', email);
        }
        sessionStorage.setItem('isLoggedIn', 'true');
        sessionStorage.setItem('userName', email.split('@')[0]);

        document.getElementById('authSignInBtnText').style.display = 'block';
        document.getElementById('authSignInLoader').style.display = 'none';

        closeAuthModal();
        goToApp();
    }, 1500);
}

// Register Form Handler
function handleAuthRegister(e) {
    e.preventDefault();
    console.log('Register form submitted');
    clearAuthErrors();

    const name = document.getElementById('authRegisterName').value.trim();
    const email = document.getElementById('authRegisterEmail').value.trim();
    const password = document.getElementById('authRegisterPassword').value;
    const confirmPassword = document.getElementById('authConfirmPassword').value;

    let isValid = true;

    if (!name) {
        document.getElementById('authRegisterNameError').textContent = 'Name is required';
        document.getElementById('authRegisterName').classList.add('error');
        isValid = false;
    } else if (name.length < 2) {
        document.getElementById('authRegisterNameError').textContent = 'Name must be at least 2 characters';
        document.getElementById('authRegisterName').classList.add('error');
        isValid = false;
    }

    if (!email) {
        document.getElementById('authRegisterEmailError').textContent = 'Email is required';
        document.getElementById('authRegisterEmail').classList.add('error');
        isValid = false;
    } else if (!validateAuthEmail(email)) {
        document.getElementById('authRegisterEmailError').textContent = 'Please enter a valid email';
        document.getElementById('authRegisterEmail').classList.add('error');
        isValid = false;
    }

    if (!password) {
        document.getElementById('authRegisterPasswordError').textContent = 'Password is required';
        document.getElementById('authRegisterPassword').classList.add('error');
        isValid = false;
    } else if (password.length < 6) {
        document.getElementById('authRegisterPasswordError').textContent = 'Password must be at least 6 characters';
        document.getElementById('authRegisterPassword').classList.add('error');
        isValid = false;
    }

    if (!confirmPassword) {
        document.getElementById('authConfirmPasswordError').textContent = 'Please confirm your password';
        document.getElementById('authConfirmPassword').classList.add('error');
        isValid = false;
    } else if (password !== confirmPassword) {
        document.getElementById('authConfirmPasswordError').textContent = 'Passwords do not match';
        document.getElementById('authConfirmPassword').classList.add('error');
        isValid = false;
    }

    if (!isValid) return;

    document.getElementById('authRegisterBtnText').style.display = 'none';
    document.getElementById('authRegisterLoader').style.display = 'flex';

    setTimeout(() => {
        console.log('Registration successful');
        localStorage.setItem('userName', name);
        localStorage.setItem('userEmail', email);
        sessionStorage.setItem('isLoggedIn', 'true');

        document.getElementById('authRegisterBtnText').style.display = 'block';
        document.getElementById('authRegisterLoader').style.display = 'none';

        closeAuthModal();
        goToApp();
    }, 1500);
}

function authSignInWithGoogle() {
    sessionStorage.setItem('isLoggedIn', 'true');
    sessionStorage.setItem('userName', 'Google User');
    closeAuthModal();
    goToApp();
}

// Close modal when clicking outside
window.onclick = function (event) {
    const modal = document.getElementById('authModal');
    if (event.target === modal) {
        closeAuthModal();
    }
}

// Scroll Animation Observer - Simplified and working
document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM Content Loaded');

    const observerOptions = {
        threshold: 0.2,
        rootMargin: '0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);

    // Observe all content images and text
    const images = document.querySelectorAll('.content-image');
    const texts = document.querySelectorAll('.content-text');

    images.forEach(img => observer.observe(img));
    texts.forEach(text => observer.observe(text));

    // Make sure modal functions are available
    console.log('Functions available, openAuthModal:', typeof window.openAuthModal);

    // Add backup event listener to sign-in buttons
    const signInButtons = document.querySelectorAll('[onclick*="openAuthModal"]');
    console.log('Found sign-in buttons:', signInButtons.length);
    signInButtons.forEach(btn => {
        btn.addEventListener('click', function (e) {
            console.log('Button clicked via event listener');
            openAuthModal();
        });
    });

    // Form handlers
    const signInForm = document.getElementById('authSignInForm');
    const registerForm = document.getElementById('authRegisterForm');

    if (signInForm) {
        console.log('Sign-in form found, adding handler');
        signInForm.addEventListener('submit', handleAuthSignIn);
    }

    if (registerForm) {
        console.log('Register form found, adding handler');
        registerForm.addEventListener('submit', handleAuthRegister);
    }
});
