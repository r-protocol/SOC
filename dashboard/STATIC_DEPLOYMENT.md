# GitHub Pages Deployment - Static Data Workflow

## Overview

The dashboard is now configured to work as a **fully static website** on GitHub Pages, reading data directly from JSON files generated from the `threat_intel.db` database.

## How It Works

### 1. Data Export (Build Time)
- The `scripts/utilities/export_static_data.py` script reads from `threat_intel.db`
- Exports all dashboard data to JSON files in `dashboard/frontend/public/data/`
- Includes:
  - Pipeline overview stats
  - Recent threats list
  - Category distribution
  - IOC statistics
  - Individual article details
  - And much more...

### 2. Frontend (Runtime)
- React components use the `src/utils/api.js` utility
- In **production** (GitHub Pages): reads from `/SOC/data/*.json` files
- In **development** (localhost): can use live backend API at `localhost:5000`

### 3. GitHub Actions Workflow
Located at `.github/workflows/deploy-dashboard.yml`

**Workflow steps:**
1. Checkout code
2. Setup Python and install dependencies
3. **Export data from threat_intel.db to JSON files**
4. Setup Node.js and install dependencies
5. Build React app (with JSON files included)
6. Deploy to GitHub Pages

**Triggers:**
- Push to `main` branch (when dashboard files or database change)
- Manual trigger via GitHub Actions tab

## Usage

### Update the Dashboard

When you want to refresh the data on GitHub Pages:

```bash
# 1. Export fresh data locally (optional - to test)
python scripts/utilities/export_static_data.py

# 2. Commit and push your database
git add threat_intel.db
git commit -m "Update threat intelligence data"
git push origin main
```

The GitHub Actions workflow will automatically:
- Export the latest data from `threat_intel.db`
- Build the React app with fresh data
- Deploy to https://r-protocol.github.io/SOC/

### Local Development

```bash
# Terminal 1: Run the Python API (optional - for live data)
cd dashboard/backend
python app.py

# Terminal 2: Run the frontend
cd dashboard/frontend
npm run dev
```

In development mode, you can use the live API or static JSON files by toggling the mode in `src/utils/api.js`.

### Production Build (Test Locally)

```bash
# Export fresh data
python scripts/utilities/export_static_data.py

# Build for production
cd dashboard/frontend
npm run build

# Preview the production build
npm run preview
```

Visit http://localhost:4173 to test the production build locally.

## File Structure

```
PY/
├── threat_intel.db                    # SQLite database (source of truth)
├── dashboard/
│   ├── backend/
│   │   ├── database.py                # Database query methods
│   │   └── requirements.txt
│   └── frontend/
│       ├── public/
│       │   └── data/                  # Static JSON exports (git-ignored)
│       │       ├── pipeline-overview.json
│       │       ├── recent-threats.json
│       │       ├── articles/
│       │       │   ├── 1.json
│       │       │   ├── 2.json
│       │       │   └── ...
│       │       └── ...
│       ├── src/
│       │   ├── utils/
│       │   │   └── api.js             # API utility (smart routing)
│       │   └── components/
│       │       └── *.jsx              # Updated to use api utility
│       └── vite.config.js             # base: '/SOC/'
├── scripts/
│   └── utilities/
│       └── export_static_data.py      # Data export script
└── .github/
    └── workflows/
        └── deploy-dashboard.yml       # GitHub Actions workflow
```

## Key Features

✅ **No backend required** - Fully static website  
✅ **Fast loading** - Pre-generated JSON files  
✅ **Free hosting** - GitHub Pages  
✅ **Automatic updates** - Push database → workflow runs → site updates  
✅ **Local development** - Can still use live API  
✅ **Full functionality** - All dashboard features work with static data  

## Configuration

### API Base Path
The frontend automatically detects the environment:

```javascript
// In src/utils/api.js
const IS_PRODUCTION = import.meta.env.PROD;
const STATIC_DATA_BASE = '/SOC/data'; // GitHub Pages path
```

### Vite Config
```javascript
// vite.config.js
export default defineConfig({
  base: '/SOC/', // Must match GitHub repository name
  // ...
})
```

## Troubleshooting

### Issue: No data showing on GitHub Pages
**Solution:** Make sure the workflow ran successfully. Check:
1. GitHub Actions tab for workflow status
2. The `threat_intel.db` file is committed to the repo
3. Python dependencies are installed in the workflow

### Issue: 404 errors for JSON files
**Solution:** Ensure the `base` path in `vite.config.js` matches your repo name (`/SOC/`).

### Issue: Old data showing
**Solution:** Push an updated `threat_intel.db` and wait for the workflow to complete.

### Issue: Build fails in GitHub Actions
**Solution:** Check the logs:
1. Go to Actions tab
2. Click the failed workflow
3. Check the "Export static data" step

## Data Freshness

The dashboard data is updated whenever you:
1. Push an updated `threat_intel.db` to GitHub
2. Run the workflow manually via Actions tab

**Note:** This is not real-time data. It's a snapshot from when the workflow last ran.

## Next Steps

- ✅ Dashboard deployed as static site
- ✅ Data exports automatically from database
- ✅ All components updated to use static JSON
- ✅ GitHub Actions workflow configured
- 🎯 Monitor the first deployment!

## Monitoring

View deployment status:
- **GitHub Actions**: https://github.com/r-protocol/SOC/actions
- **Dashboard**: https://r-protocol.github.io/SOC/
- **Workflow Logs**: Check each workflow run for details

## Cost

- **GitHub Pages**: Free
- **GitHub Actions**: Free (for public repos)
- **Total**: $0 💰

---

**Last Updated:** October 2025  
**Maintained By:** r-protocol
