# Frontend - Forest Monitoring System

## Files

- `index.html` - Main HTML file with landing page and application
- `styles.css` - All CSS styling
- `app.js` - JavaScript logic and API integration
- `serve.py` - Simple Python HTTP server

## Running the Frontend

### Option 1: Using the Python server (Recommended)
```bash
python serve.py
```
Then open http://localhost:5500

### Option 2: Using the batch file
```bash
..\start_frontend.bat
```

### Option 3: Using any HTTP server
```bash
# Python 3
python -m http.server 5500

# Node.js
npx http-server -p 5500

# PHP
php -S localhost:5500
```

## Features

### Landing Page
- Hero section with call-to-action
- Features grid
- About section
- Responsive design
- Smooth animations

### Application Page
- Interactive map (Leaflet.js)
- Polygon drawing tool
- Region selection
- Real-time analysis
- Results visualization
- Tree markers on map

## Configuration

Edit `app.js` to change:

```javascript
// API endpoint
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Map center (Dang District)
const DANG_CENTER = [20.7489, 73.7294];
```

## Browser Compatibility

- Chrome/Edge: ✅ Fully supported
- Firefox: ✅ Fully supported
- Safari: ✅ Fully supported
- IE11: ❌ Not supported

## Dependencies (CDN)

- Leaflet.js 1.9.4
- Leaflet.Draw 1.0.4

All loaded from CDN, no installation needed.

## Troubleshooting

### Map doesn't load
- Check internet connection
- Verify Leaflet CDN is accessible
- Check browser console for errors

### API calls fail
- Ensure backend is running on port 8000
- Check CORS settings in backend
- Verify API_BASE_URL in app.js

### Polygon drawing doesn't work
- Ensure Leaflet.Draw is loaded
- Check browser console for errors
- Try refreshing the page

## Development

To modify the frontend:

1. Edit HTML in `index.html`
2. Edit styles in `styles.css`
3. Edit logic in `app.js`
4. Refresh browser to see changes

No build step required!
