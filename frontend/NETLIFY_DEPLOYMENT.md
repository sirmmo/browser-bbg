# Netlify Deployment Guide

Complete guide to deploying the Base Building Game frontend to Netlify.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Environment Configuration](#environment-configuration)
- [Deployment Steps](#deployment-steps)
- [Post-Deployment](#post-deployment)
- [Troubleshooting](#troubleshooting)
- [Local Testing](#local-testing)

---

## Prerequisites

Before deploying to Netlify, ensure you have:

1. **Netlify Account**: Sign up at [netlify.com](https://netlify.com)
2. **Git Repository**: Code pushed to GitHub, GitLab, or Bitbucket
3. **Backend API**: Your Django backend deployed and accessible via HTTPS
4. **Node.js**: Version 18 or higher (specified in `netlify.toml`)

---

## Quick Start

### Option 1: Deploy via Netlify UI

1. Log in to [Netlify](https://app.netlify.com)
2. Click **"Add new site"** → **"Import an existing project"**
3. Connect your Git repository
4. Configure build settings:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `dist/frontend/browser`
5. Add environment variable (see below)
6. Click **"Deploy site"**

### Option 2: Deploy via Netlify CLI

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Navigate to frontend directory
cd frontend

# Initialize Netlify site
netlify init

# Deploy
netlify deploy --prod
```

---

## Environment Configuration

### Required Environment Variable

Set the API URL for your backend in Netlify:

1. Go to **Site settings** → **Environment variables**
2. Add variable:
   - **Key**: `API_URL` (optional, for documentation)
   - **Value**: Your backend URL (e.g., `https://your-api.herokuapp.com/api`)

### Update Production Environment File

Edit `src/environments/environment.prod.ts`:

```typescript
export const environment = {
  production: true,
  apiUrl: 'https://your-backend-domain.com/api'  // Replace with your API URL
};
```

**Important**: Update this URL before deploying to point to your production Django backend.

---

## Deployment Steps

### Step 1: Prepare Your Code

```bash
cd frontend

# Install dependencies
npm install

# Test production build locally
npm run build

# Verify build output
ls -la dist/frontend/browser
```

### Step 2: Configure Backend CORS

Ensure your Django backend allows requests from your Netlify domain.

In `backend_project/settings.py`:

```python
CORS_ALLOWED_ORIGINS = [
    'https://your-site.netlify.app',
    'https://your-custom-domain.com',  # if using custom domain
]

# Or for development (not recommended for production)
CORS_ALLOW_ALL_ORIGINS = True
```

### Step 3: Deploy to Netlify

#### Via Git Integration (Recommended)

1. Push code to your repository:
```bash
git add .
git commit -m "Configure for Netlify deployment"
git push origin main
```

2. Netlify will automatically:
   - Detect changes
   - Run build command
   - Deploy to CDN
   - Provide deployment URL

#### Via CLI

```bash
# Deploy to production
netlify deploy --prod --dir=dist/frontend/browser

# Or with build
netlify deploy --prod --build
```

### Step 4: Verify Deployment

1. Visit your Netlify URL (e.g., `https://your-site.netlify.app`)
2. Test the following:
   - Registration/Login works
   - Resources load from API
   - Automatic resource collection (check console)
   - Building placement
   - Party features

---

## Post-Deployment

### Custom Domain Setup

1. Go to **Site settings** → **Domain management**
2. Click **"Add custom domain"**
3. Follow DNS configuration instructions
4. Wait for SSL certificate (automatic via Let's Encrypt)

### Enable HTTPS

- Netlify provides free HTTPS automatically
- Ensure **Force HTTPS** is enabled in Site settings

### Configure Redirects

The `netlify.toml` file already configures:
- SPA routing (all routes → `index.html`)
- Security headers
- Cache headers for static assets

### Monitor Deployment

1. **Deploy log**: Check build logs in Netlify dashboard
2. **Function logs**: N/A (no serverless functions)
3. **Analytics**: Enable Netlify Analytics (optional, paid feature)

---

## Troubleshooting

### Build Failures

**Error**: `Module not found`
```bash
# Solution: Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

**Error**: `Out of memory`
```toml
# Add to netlify.toml
[build.environment]
  NODE_OPTIONS = "--max-old-space-size=4096"
```

### API Connection Issues

**Error**: `CORS policy` error in browser console

**Solution**: Update Django CORS settings

```python
# backend/settings.py
CORS_ALLOWED_ORIGINS = [
    'https://your-netlify-site.netlify.app',
]
```

**Error**: API returns 404

**Solution**: Check `environment.prod.ts` has correct API URL

```typescript
apiUrl: 'https://your-api-domain.com/api'  // Must include /api
```

### Routing Issues

**Error**: 404 on page refresh

**Solution**: Ensure `_redirects` file is in build output

```bash
# Verify after build
ls dist/frontend/browser/_redirects

# Should output the redirects file
```

**Fix**: Already configured in `angular.json` assets

### Auto-Collection Not Working

**Issue**: Resources not collecting automatically

**Solution**: Check browser console for errors

1. Open DevTools (F12)
2. Go to Console tab
3. Look for "Auto-collected resources" logs every 60 seconds
4. If missing, check API service initialization

---

## Local Testing

### Test Production Build Locally

```bash
# Build for production
npm run build

# Serve production build (install http-server)
npm install -g http-server
http-server dist/frontend/browser -p 4200 -c-1

# Or use Angular CLI
npx ng serve --configuration=production
```

### Test with Production API

1. Temporarily update `environment.ts`:
```typescript
export const environment = {
  production: false,
  apiUrl: 'https://your-production-api.com/api'
};
```

2. Run development server:
```bash
npm start
```

3. Test all features work with production backend

### Simulate Netlify Environment

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Serve built site with Netlify's environment
netlify dev

# Or
netlify serve --dir=dist/frontend/browser
```

---

## Build Configuration

### `netlify.toml` Explained

```toml
[build]
  command = "npm run build"           # Runs production build
  publish = "dist/frontend/browser"   # Output directory

[build.environment]
  NODE_VERSION = "18"                 # Node.js version

[[redirects]]
  from = "/*"                         # All routes
  to = "/index.html"                  # Redirect to index
  status = 200                        # SPA routing (not 301/302)
```

### Environment Files

**Development** (`environment.ts`):
- Used during local development
- Points to `localhost:8000`
- Source maps enabled

**Production** (`environment.prod.ts`):
- Used in production build
- Points to production API
- Optimized and minified

---

## Auto-Collection Feature

### How It Works

The frontend automatically collects resources every 60 seconds:

1. **Initialization**: Starts in `BaseComponent.ngOnInit()`
2. **Interval**: RxJS `interval(60000)` - 60 seconds
3. **API Call**: `POST /api/profile/collect/`
4. **Auto-stop**: Stops when component destroyed

### Configuration

To change collection interval, edit `api.service.ts`:

```typescript
// Change from 60000 (1 minute) to desired milliseconds
interval(60000)  // 60 seconds
interval(30000)  // 30 seconds
interval(120000) // 2 minutes
```

### Monitoring

Check browser console for auto-collection logs:
```
Auto-collected resources: {coins: 150, wood: 75, ...}
```

---

## Performance Optimization

### Bundle Size

Current configuration limits:
- Initial bundle: 1MB max
- Component styles: 4KB max

To check bundle size:
```bash
npm run build
# Check dist/frontend/browser/*.js file sizes
```

### Caching Strategy

Static assets cached for 1 year:
- JavaScript files
- CSS files
- Images in `/assets/`

HTML files not cached (always fresh).

### CDN

Netlify automatically serves from global CDN:
- 100+ edge locations
- Automatic cache invalidation on deploy
- HTTPS everywhere

---

## Continuous Deployment

### Automatic Deploys

Netlify auto-deploys on:
- Push to `main` branch (production)
- Push to other branches (preview deploys)
- Pull requests (deploy previews)

### Deploy Contexts

Configure different settings per branch in `netlify.toml`:

```toml
[context.production.environment]
  API_URL = "https://prod-api.com/api"

[context.branch-deploy.environment]
  API_URL = "https://staging-api.com/api"
```

### Deploy Previews

Every PR gets a unique deploy preview URL:
- Test changes before merging
- Share with team for review
- Auto-deleted when PR closed

---

## Security

### Headers

Already configured in `netlify.toml`:

```toml
[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"              # Prevent clickjacking
    X-Content-Type-Options = "nosniff"    # Prevent MIME sniffing
    X-XSS-Protection = "1; mode=block"    # XSS protection
```

### HTTPS

- Automatic SSL certificate
- Force HTTPS redirect
- HSTS headers (optional, enable in Netlify UI)

### Environment Variables

- Never commit API keys to repository
- Use Netlify environment variables
- Access via build process

---

## Rollback

### Via Netlify UI

1. Go to **Deploys**
2. Find previous working deployment
3. Click **"Publish deploy"**
4. Site instantly rolls back

### Via CLI

```bash
# List deploys
netlify deploys:list

# Restore specific deploy
netlify deploy:restore <deploy-id>
```

---

## Cost

### Netlify Free Tier Includes:

- ✅ Unlimited sites
- ✅ 100GB bandwidth/month
- ✅ 300 build minutes/month
- ✅ Automatic HTTPS
- ✅ Global CDN
- ✅ Deploy previews
- ✅ Form submissions (limited)

### When to Upgrade:

- High traffic (>100GB/month)
- More build minutes needed
- Advanced features (Analytics, A/B testing)
- Team collaboration features

---

## Additional Resources

- [Netlify Documentation](https://docs.netlify.com/)
- [Angular Deployment Guide](https://angular.io/guide/deployment)
- [Netlify CLI Reference](https://cli.netlify.com/)
- [Netlify Support](https://answers.netlify.com/)

---

## Quick Reference

### Common Commands

```bash
# Local development
npm start

# Production build
npm run build

# Deploy to Netlify
netlify deploy --prod

# View deploy logs
netlify logs:deploy

# Open site in browser
netlify open:site
```

### Important Files

- `netlify.toml` - Netlify configuration
- `src/_redirects` - SPA routing rules
- `src/environments/environment.prod.ts` - Production API URL
- `angular.json` - Build configuration

### Support

For issues specific to this game:
1. Check browser console for errors
2. Verify API URL in environment.prod.ts
3. Ensure backend CORS configured
4. Test auto-collection feature

---

## Checklist

Before deploying to production:

- [ ] Update `environment.prod.ts` with production API URL
- [ ] Configure Django CORS to allow Netlify domain
- [ ] Test production build locally
- [ ] Verify auto-collection works
- [ ] Push code to Git repository
- [ ] Connect Netlify to repository
- [ ] Set build settings (if not using netlify.toml)
- [ ] Deploy and test live site
- [ ] Configure custom domain (optional)
- [ ] Enable Force HTTPS
- [ ] Set up monitoring/analytics (optional)

---

## Success!

Your Base Building Game frontend is now deployed on Netlify with:

✅ Automatic resource collection every minute
✅ Environment-based configuration
✅ SPA routing for Angular
✅ Global CDN delivery
✅ Automatic HTTPS
✅ Continuous deployment from Git

Users can now access your game at your Netlify URL and enjoy automatic resource collection while managing their bases!
