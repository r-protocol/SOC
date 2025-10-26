# Threat Intelligence Dashboard

Web-based dashboard for visualizing and monitoring threat intelligence data from your RSS feed pipeline.

## 🏗️ Architecture

- **Backend**: Flask REST API (Python)
- **Frontend**: React + Vite (JavaScript)
- **Database**: SQLite (threat_intel.db)
- **Charts**: Recharts
- **Styling**: Custom CSS with dark theme + Google color palette

## 📦 Installation

### Backend Setup

```powershell
# Navigate to backend directory
cd dashboard\backend

# Install Python dependencies
pip install flask flask-cors python-dateutil

# Run the Flask API server
python app.py
```

Backend will run on: **http://localhost:5000**

### Frontend Setup

```powershell
# Navigate to frontend directory (in a NEW terminal)
cd dashboard\frontend

# Install Node.js dependencies
npm install

# Run the development server
npm run dev
```

Frontend will run on: **http://localhost:5173**

## 🚀 Quick Start

1. **Start Backend** (Terminal 1):
```powershell
cd c:\Users\PC\Documents\WORK\ThreatIntelligence\PY\dashboard\backend
python app.py
```

2. **Start Frontend** (Terminal 2):
```powershell
cd c:\Users\PC\Documents\WORK\ThreatIntelligence\PY\dashboard\frontend
npm run dev
```

3. **Open Browser**: http://localhost:5173

## 📊 Dashboard Features

### KPI Cards
- 🔴 **Critical Threats**: Count of HIGH risk articles
- 📊 **Articles Processed**: Total articles in database
- 🎯 **IOCs Extracted**: Total indicators of compromise
- 📈 **Recent (7 days)**: Articles from last week

### Charts & Visualizations
- **Threat Timeline**: 7-day trend of threats by risk level
- **Category Distribution**: Pie chart of threat categories
- **IOC Breakdown**: Bar chart of IOC types (domains, IPs, hashes, CVEs)
- **Threat Families**: Word cloud of common threat actors/malware

### Interactive Elements
- **Recent Threats Feed**: Click any threat to see full details
- **Article Modal**: View summary, IOCs, and KQL queries
- **RSS Feed Stats**: Monitor your 5 RSS sources

### Auto-Refresh
Dashboard automatically refreshes every 60 seconds to show latest data.

## 🗄️ API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/pipeline-overview` | GET | Get KPI statistics |
| `/api/risk-distribution` | GET | Get risk level counts |
| `/api/category-distribution` | GET | Get category breakdown |
| `/api/threat-timeline?days=7` | GET | Get timeline data |
| `/api/recent-threats?limit=20` | GET | Get recent articles |
| `/api/ioc-stats` | GET | Get IOC type counts |
| `/api/rss-feed-stats` | GET | Get RSS source stats |
| `/api/threat-families` | GET | Get threat actor names |
| `/api/article/<id>` | GET | Get article details |

## 🎨 Design Specifications

### Color Palette
```css
--bg-primary: #1e1e2e        /* Main dark background */
--bg-secondary: #2a2a3e      /* Cards/panels */
--google-blue: #4285f4       /* Primary actions */
--google-red: #ea4335        /* HIGH risk */
--google-yellow: #fbbc04     /* MEDIUM risk */
--google-green: #34a853      /* LOW risk */
```

### Risk Badges
- 🔴 **HIGH**: Red background (#ea4335)
- 🟠 **MEDIUM**: Yellow background (#fbbc04)
- 🟢 **LOW**: Green background (#34a853)

## 🔧 Configuration

### Backend Configuration
Edit `dashboard/backend/database.py` to change database path:
```python
DATABASE_PATH = "../../threat_intel.db"  # Adjust as needed
```

### Frontend Configuration
Edit `dashboard/frontend/src/components/*.jsx` to change API URL:
```javascript
const API_BASE = 'http://localhost:5000/api';
```

### Auto-Refresh Interval
Edit `dashboard/frontend/src/App.jsx`:
```javascript
const [refreshInterval, setRefreshInterval] = useState(60000); // milliseconds
```

## 🐛 Troubleshooting

### Backend Issues

**Database not found**
```powershell
# Check if threat_intel.db exists
ls ..\..\threat_intel.db

# Run your RSS pipeline first to populate data
cd ..\..
python main.py -n 5
```

**Port already in use**
```powershell
# Change port in app.py:
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Frontend Issues

**CORS errors**
- Ensure Flask-CORS is installed: `pip install flask-cors`
- Backend must be running before frontend

**Charts not rendering**
```powershell
# Reinstall chart library
npm install recharts
```

**Blank dashboard**
- Check browser console (F12) for errors
- Verify backend is running: http://localhost:5000/health
- Check if database has data: See Backend Issues above

## 📁 Project Structure

```
dashboard/
├── backend/
│   ├── app.py              # Flask application
│   ├── routes.py           # API endpoints
│   ├── database.py         # Database queries
│   └── requirements.txt    # Python dependencies
│
└── frontend/
    ├── public/
    │   └── index.html
    ├── src/
    │   ├── components/     # React components
    │   │   ├── PipelineOverview.jsx
    │   │   ├── ThreatTimeline.jsx
    │   │   ├── CategoryDistribution.jsx
    │   │   ├── RecentThreats.jsx
    │   │   ├── IOCStats.jsx
    │   │   ├── RSSFeedStats.jsx
    │   │   └── ThreatFamilies.jsx
    │   ├── styles/
    │   │   └── index.css   # Global styles
    │   ├── App.jsx         # Main app component
    │   └── main.jsx        # Entry point
    ├── package.json
    └── vite.config.js
```

## 🔄 Development Workflow

1. **Collect Threat Data** (parent directory):
```powershell
python main.py --kql
```

2. **View in Dashboard**:
- Backend auto-connects to `threat_intel.db`
- Frontend auto-refreshes every 60s
- Click threats for details

3. **Iterate**:
- Add more feeds in `config.py`
- Run pipeline again
- Dashboard updates automatically

## 📈 Next Steps

### Enhancements to Consider
- [ ] Add search/filter functionality
- [ ] Export data to CSV
- [ ] MITRE ATT&CK heatmap
- [ ] Historical trend analysis
- [ ] Email alerts for HIGH risk threats
- [ ] Docker deployment
- [ ] Authentication/multi-user support

## 🆘 Support

If you encounter issues:
1. Check both terminal outputs for errors
2. Verify database exists and has data
3. Test API endpoints directly: `curl http://localhost:5000/api/pipeline-overview`
4. Check browser console (F12) for frontend errors

## 📝 License

Part of the Threat Intelligence Pipeline project.
