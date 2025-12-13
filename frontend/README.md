# Base Building Game - Frontend

Angular 17 frontend for the multiplayer base-building and tower defense game.

## Features

- 🏗️ **Base Building**: Place and manage buildings on a 10x10 grid
- 💰 **Resource Management**: Collect coins, wood, stone, and food
- ⚔️ **Tower Defense**: Build defensive towers to protect your base
- 👥 **Party System**: Play with friends in parties
- 🤝 **Trading**: Trade materials and items with other players
- 🔬 **Technology Research**: Unlock upgrades through research
- 🔨 **Crafting System**: Create items to enhance buildings
- 👷 **Worker Management**: Hire and assign workers for bonuses
- ⏱️ **Auto-Collection**: Resources automatically collect every minute

## Quick Start

### Prerequisites

- Node.js 18 or higher
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm start

# Open browser to http://localhost:4200
```

### Development

```bash
# Start dev server with hot reload
npm start

# Run tests
npm test

# Build for production
npm run build

# Build for development
npm run build:dev
```

## Environment Configuration

### Development

Edit `src/environments/environment.ts`:

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api'
};
```

### Production

Edit `src/environments/environment.prod.ts`:

```typescript
export const environment = {
  production: true,
  apiUrl: 'https://your-api-domain.com/api'
};
```

## Auto-Collection Feature

Resources are automatically collected every 60 seconds when viewing your base:

- ⏱️ Collects every minute in the background
- 🔄 Automatically starts when base component loads
- 🛑 Stops when you leave the base view
- 📊 Updates resources in real-time

To configure the interval, edit `src/app/services/api.service.ts`:

```typescript
// Change interval (in milliseconds)
interval(60000)  // 60 seconds (default)
interval(30000)  // 30 seconds
interval(120000) // 2 minutes
```

## Deployment

### Deploy to Netlify

See [NETLIFY_DEPLOYMENT.md](NETLIFY_DEPLOYMENT.md) for complete deployment guide.

Quick steps:

1. Update `src/environments/environment.prod.ts` with your API URL
2. Build: `npm run build`
3. Deploy to Netlify (auto-configured via `netlify.toml`)

## Project Structure

```
src/
├── app/
│   ├── components/
│   │   ├── base/           # Main game interface
│   │   ├── login/          # Authentication
│   │   ├── register/       # User registration
│   │   └── party/          # Party management
│   ├── services/
│   │   ├── api.service.ts  # API communication + auto-collection
│   │   └── auth.service.ts # Authentication
│   └── interceptors/
│       └── auth.interceptor.ts  # JWT token injection
├── environments/
│   ├── environment.ts      # Development config
│   └── environment.prod.ts # Production config
└── _redirects              # Netlify SPA routing
```

## API Integration

The frontend connects to a Django REST API backend:

- Authentication via JWT tokens
- Auto-refresh tokens
- Auto-collection every 60 seconds
- All endpoints documented in backend README

## Key Files

- `netlify.toml` - Netlify deployment config
- `src/_redirects` - SPA routing rules
- `angular.json` - Build configuration
- `src/environments/*` - Environment-specific settings

## Troubleshooting

### CORS Errors

Ensure Django backend allows requests from your frontend domain:

```python
# backend/settings.py
CORS_ALLOWED_ORIGINS = [
    'http://localhost:4200',  # Development
    'https://your-site.netlify.app',  # Production
]
```

### Auto-Collection Not Working

1. Check browser console for errors
2. Verify API endpoint `/api/profile/collect/` works
3. Ensure you're logged in
4. Check base component is loaded

### Build Errors

```bash
# Clear cache and rebuild
rm -rf node_modules package-lock.json dist
npm install
npm run build
```

## Documentation

- [Netlify Deployment Guide](./NETLIFY_DEPLOYMENT.md)
- [Backend Documentation](../README.md)
- [Material Management System](../MATERIAL_MANAGEMENT_SYSTEM.md)
- [Worker Hiring System](../WORKER_HIRING_SYSTEM.md)

## License

MIT
