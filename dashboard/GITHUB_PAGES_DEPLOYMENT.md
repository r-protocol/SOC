# GitHub Pages Deployment Guide

## Prerequisites
- Node.js 18+ installed
- GitHub account with repo access
- GitHub Pages enabled in repository settings

## Quick Start

### 1. Enable GitHub Pages
1. Go to your repository on GitHub: `https://github.com/r-protocol/SOC`
2. Click **Settings** → **Pages**
3. Under **Source**, select **GitHub Actions**
4. Save

### 2. Install Dependencies
```bash
cd dashboard/frontend
npm install
```

### 3. Build Locally (Test)
```bash
npm run build
npm run preview
```
Visit `http://localhost:4173` to test the production build locally.

### 4. Deploy
Simply push to the main branch:
```bash
git add .
git commit -m "Configure GitHub Pages deployment"
git push origin main
```

The GitHub Actions workflow will automatically:
- Build the React app
- Deploy to GitHub Pages
- Make it available at: `https://r-protocol.github.io/SOC/`

## Configuration

### Vite Config (`vite.config.js`)
```javascript
base: '/SOC/'  // Must match your repository name
```

### Environment Variables
Create `.env` file in `dashboard/frontend/`:
```env
VITE_API_URL=https://your-backend-api.com/api
```

For local development, it defaults to `http://localhost:5000`.

## Backend Deployment Options

Since GitHub Pages only hosts static files, you need to deploy the backend separately:

### Option 1: Railway (Recommended)
1. Go to [railway.app](https://railway.app)
2. Connect your GitHub repo
3. Select the `dashboard/backend` directory
4. Add environment variables
5. Deploy

### Option 2: Render
1. Go to [render.com](https://render.com)
2. New Web Service → Connect GitHub
3. Root directory: `dashboard/backend`
4. Build command: `pip install -r requirements.txt`
5. Start command: `python app.py`

### Option 3: Heroku
```bash
cd dashboard/backend
heroku create your-app-name
git subtree push --prefix dashboard/backend heroku main
```

### Option 4: PythonAnywhere
1. Upload backend files
2. Configure WSGI
3. Enable CORS for your GitHub Pages domain

## GitHub Actions Workflow

The workflow (`.github/workflows/deploy-dashboard.yml`) runs on:
- Push to main branch (when frontend files change)
- Manual trigger via Actions tab

### Workflow Steps:
1. ✅ Checkout code
2. ✅ Setup Node.js
3. ✅ Install dependencies
4. ✅ Build React app
5. ✅ Deploy to GitHub Pages

## URLs

After deployment:
- **Dashboard**: `https://r-protocol.github.io/SOC/`
- **Backend**: Deploy separately (see options above)

## Troubleshooting

### Issue: 404 on GitHub Pages
**Solution**: Make sure GitHub Pages is set to **GitHub Actions** source in Settings → Pages.

### Issue: Blank page after deployment
**Solution**: Check `vite.config.js` base path matches your repo name (`/SOC/`).

### Issue: API calls failing
**Solution**: 
1. Deploy backend separately
2. Update `VITE_API_URL` in `.env`
3. Enable CORS on backend for your GitHub Pages domain

### Issue: Build fails in Actions
**Solution**: Check Node version in workflow matches your local (18+).

## Local Development vs Production

### Development
```bash
npm run dev
# Uses proxy to localhost:5000
```

### Production Build
```bash
npm run build
# Uses VITE_API_URL from .env
```

### Preview Production Build
```bash
npm run preview
# Test production build locally
```

## Manual Deployment (Alternative)

If you prefer not to use GitHub Actions:

```bash
cd dashboard/frontend
npm run build
npx gh-pages -d dist
```

This pushes the `dist` folder to the `gh-pages` branch.

## Security Notes

1. **Never commit `.env` files** - use `.env.example` as template
2. **Enable CORS** on backend for GitHub Pages domain only
3. **Use environment variables** for sensitive data
4. **Consider authentication** if dashboard contains sensitive data

## Next Steps

After deployment:
1. ✅ Test dashboard at GitHub Pages URL
2. ✅ Deploy backend (choose option above)
3. ✅ Update API URL in environment variables
4. ✅ Test API connectivity
5. ✅ Monitor GitHub Actions for successful deployments

## Monitoring

View deployment status:
- Go to **Actions** tab in GitHub
- Click on latest workflow run
- Check build and deploy steps

## Rollback

To rollback to previous version:
```bash
git revert HEAD
git push origin main
```

The workflow will automatically redeploy the previous version.

## Custom Domain (Optional)

1. Add `CNAME` file to `dashboard/frontend/public/`:
   ```
   yourdomain.com
   ```

2. Update DNS records:
   ```
   A     @     185.199.108.153
   A     @     185.199.109.153
   A     @     185.199.110.153
   A     @     185.199.111.153
   ```

3. Update `base: '/'` in `vite.config.js`

## Cost

- **GitHub Pages**: Free for public repos
- **Backend hosting**: Free tier available on Railway, Render, PythonAnywhere
- **Total**: $0 for small projects

## Support

If you encounter issues:
1. Check GitHub Actions logs
2. Test build locally first
3. Verify backend is accessible
4. Check browser console for errors
