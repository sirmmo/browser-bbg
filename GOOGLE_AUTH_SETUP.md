# Google Authentication Setup Guide

This document explains how to set up Google OAuth authentication for the Browser BBG base-building game.

## Table of Contents

1. [Overview](#overview)
2. [Google OAuth Configuration](#google-oauth-configuration)
3. [Backend Configuration](#backend-configuration)
4. [API Endpoints](#api-endpoints)
5. [Frontend Integration](#frontend-integration)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)

---

## Overview

The application uses **django-allauth** for social authentication with Google. Users can:
- Sign in with their Google account
- Automatically create a player profile
- Receive JWT tokens for API authentication

### Authentication Flow

```
1. Frontend redirects user to Google login
2. User authenticates with Google
3. Google returns access_token/id_token
4. Frontend sends token to backend API
5. Backend verifies token with Google
6. Backend creates/retrieves user account
7. Backend creates PlayerProfile if new user
8. Backend returns JWT tokens
9. Frontend stores JWT for API calls
```

---

## Google OAuth Configuration

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API:
   - Go to **APIs & Services** → **Library**
   - Search for "Google+ API"
   - Click **Enable**

### Step 2: Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. Configure the OAuth consent screen if prompted:
   - User Type: **External** (or Internal for Google Workspace)
   - App name: `Browser BBG` (or your app name)
   - User support email: Your email
   - Developer contact: Your email
   - Add scopes: `email`, `profile`
   - Add test users if needed

4. Create OAuth Client ID:
   - Application type: **Web application**
   - Name: `Browser BBG Web Client`
   - Authorized JavaScript origins:
     ```
     http://localhost:4200
     http://localhost:8000
     https://your-production-domain.com
     ```
   - Authorized redirect URIs:
     ```
     http://localhost:4200
     http://localhost:4200/auth/google/callback
     https://your-production-domain.com
     https://your-production-domain.com/auth/google/callback
     ```

5. Click **Create**
6. **Copy the Client ID and Client Secret** - you'll need these!

### Step 3: Configure Backend Settings

Update `basebuilder/settings.py` with your Google OAuth credentials:

```python
# Google OAuth Configuration
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'APP': {
            'client_id': 'YOUR_GOOGLE_CLIENT_ID_HERE',
            'secret': 'YOUR_GOOGLE_CLIENT_SECRET_HERE',
            'key': ''
        }
    }
}
```

**Using Environment Variables** (Recommended for production):

```python
import os

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'APP': {
            'client_id': os.getenv('GOOGLE_CLIENT_ID', ''),
            'secret': os.getenv('GOOGLE_CLIENT_SECRET', ''),
            'key': ''
        }
    }
}
```

Then set environment variables:
```bash
export GOOGLE_CLIENT_ID="your-client-id"
export GOOGLE_CLIENT_SECRET="your-client-secret"
```

### Step 4: Create Social App in Django Admin

1. Run the development server:
   ```bash
   python manage.py runserver
   ```

2. Go to [http://localhost:8000/admin/](http://localhost:8000/admin/)
3. Log in with your superuser account
4. Navigate to **Social applications** → **Add**
5. Fill in the form:
   - Provider: **Google**
   - Name: `Google OAuth`
   - Client ID: Your Google Client ID
   - Secret key: Your Google Client Secret
   - Sites: Select `example.com` (or your site)
6. Click **Save**

---

## Backend Configuration

### Installed Packages

The following package is installed:
- `django-allauth==0.57.0` - Social authentication

### Settings Configuration

**INSTALLED_APPS**:
```python
INSTALLED_APPS = [
    ...
    "django.contrib.sites",  # Required
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    ...
]

SITE_ID = 1
```

**MIDDLEWARE**:
```python
MIDDLEWARE = [
    ...
    "allauth.account.middleware.AccountMiddleware",
]
```

**AUTHENTICATION_BACKENDS**:
```python
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]
```

**ALLAUTH_SETTINGS**:
```python
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_UNIQUE_EMAIL = True
SOCIALACCOUNT_AUTO_SIGNUP = True
```

---

## API Endpoints

### 1. Get Google OAuth Config

Get the configuration needed for frontend Google login.

**Endpoint**: `GET /api/google/config/`

**Response**:
```json
{
  "client_id": "your-google-client-id",
  "redirect_uri": "http://localhost:4200/auth/google/callback",
  "scope": "profile email"
}
```

### 2. Google Login

Authenticate with Google access token or ID token.

**Endpoint**: `POST /api/google/login/`

**Request Body** (Option 1 - Access Token):
```json
{
  "access_token": "ya29.a0AfH6SMBxxx..."
}
```

**Request Body** (Option 2 - ID Token):
```json
{
  "id_token": "eyJhbGciOiJSUzI1NiIs..."
}
```

**Success Response** (200 OK):
```json
{
  "user": {
    "id": 1,
    "username": "john.doe",
    "email": "john.doe@gmail.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

**Error Response** (400 Bad Request):
```json
{
  "error": "Invalid access token"
}
```

### 3. Standard JWT Endpoints

**Login (Username/Password)**:
- `POST /api/login/` - Get JWT tokens
- Request: `{"username": "...", "password": "..."}`

**Token Refresh**:
- `POST /api/token/refresh/` - Refresh access token
- Request: `{"refresh": "..."}`

**Registration**:
- `POST /api/register/` - Create new account
- Request: `{"username": "...", "email": "...", "password": "..."}`

---

## Frontend Integration

### Using @angular/fire (Angular)

**1. Install Google OAuth Library**:
```bash
npm install @codetrix-studio/capacitor-google-auth
# or
npm install @react-oauth/google  # For React
```

**2. Configure Google Client ID**:

```typescript
// src/app/auth/auth.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private apiUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) {}

  getGoogleConfig() {
    return this.http.get(`${this.apiUrl}/google/config/`);
  }

  loginWithGoogle(accessToken: string) {
    return this.http.post(`${this.apiUrl}/google/login/`, {
      access_token: accessToken
    });
  }

  saveTokens(tokens: any) {
    localStorage.setItem('access_token', tokens.access);
    localStorage.setItem('refresh_token', tokens.refresh);
  }
}
```

**3. Google Sign-In Button**:

```typescript
// auth.component.ts
import { Component, OnInit } from '@angular/core';
import { AuthService } from './auth.service';

declare const google: any;

@Component({
  selector: 'app-auth',
  template: `
    <div id="g_id_onload"
         [attr.data-client_id]="googleClientId"
         data-callback="handleCredentialResponse">
    </div>
    <div class="g_id_signin" data-type="standard"></div>
  `
})
export class AuthComponent implements OnInit {
  googleClientId: string = '';

  constructor(private authService: AuthService) {}

  ngOnInit() {
    // Get Google client ID from backend
    this.authService.getGoogleConfig().subscribe((config: any) => {
      this.googleClientId = config.client_id;
      this.initializeGoogleSignIn();
    });

    // Make callback available globally
    (window as any).handleCredentialResponse = this.handleCredentialResponse.bind(this);
  }

  initializeGoogleSignIn() {
    // Load Google Sign-In script
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    document.head.appendChild(script);
  }

  handleCredentialResponse(response: any) {
    // Send ID token to backend
    this.authService.loginWithGoogle(response.credential).subscribe(
      (result: any) => {
        this.authService.saveTokens(result.tokens);
        console.log('Logged in:', result.user);
        // Redirect to game
        window.location.href = '/base';
      },
      error => {
        console.error('Login failed:', error);
      }
    );
  }
}
```

**4. Add Google Script to index.html**:

```html
<!-- src/index.html -->
<!doctype html>
<html lang="en">
<head>
  ...
  <script src="https://accounts.google.com/gsi/client" async defer></script>
</head>
<body>
  <app-root></app-root>
</body>
</html>
```

### Alternative: Using Popup Flow

```typescript
// Google Sign-In with Popup
signInWithGoogle() {
  const oauth2Endpoint = 'https://accounts.google.com/o/oauth2/v2/auth';
  const params = {
    client_id: this.googleClientId,
    redirect_uri: window.location.origin + '/auth/google/callback',
    response_type: 'token',
    scope: 'https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile',
  };

  const url = oauth2Endpoint + '?' + new URLSearchParams(params as any).toString();

  const popup = window.open(url, 'Google Sign In', 'width=500,height=600');

  // Listen for callback
  window.addEventListener('message', (event) => {
    if (event.data.type === 'google-auth') {
      this.authService.loginWithGoogle(event.data.access_token).subscribe(...);
    }
  });
}
```

---

## Testing

### Manual Testing

1. **Get Google Config**:
   ```bash
   curl http://localhost:8000/api/google/config/
   ```

2. **Test with Access Token**:
   ```bash
   curl -X POST http://localhost:8000/api/google/login/ \
     -H "Content-Type: application/json" \
     -d '{"access_token": "YOUR_GOOGLE_ACCESS_TOKEN"}'
   ```

3. **Verify User Created**:
   - Check Django admin: http://localhost:8000/admin/auth/user/
   - Check player profile: http://localhost:8000/admin/game/playerprofile/

### Testing Flow

1. Open frontend application
2. Click "Sign in with Google"
3. Authenticate with Google account
4. Verify JWT tokens received
5. Check player profile created in database
6. Test API calls with JWT token

---

## Troubleshooting

### Common Issues

**1. "Invalid access token" error**
- **Cause**: Token expired or invalid
- **Solution**: Get a fresh token from Google

**2. "Client ID not configured" error**
- **Cause**: Google client ID not set in settings
- **Solution**: Add client ID to `settings.py` or environment variables

**3. "Redirect URI mismatch" error**
- **Cause**: Redirect URI not whitelisted in Google Console
- **Solution**: Add the exact URI to Google Cloud Console

**4. "User already exists" for new Google user**
- **Cause**: Email already registered with standard auth
- **Solution**: App links Google account to existing user automatically

**5. Player profile not created**
- **Cause**: Signal or creation logic issue
- **Solution**: Check that `PlayerProfile.objects.create(user=user)` runs

### Debug Mode

Enable debug logging:
```python
# settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'allauth': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

### Verify Setup

Check configuration:
```python
# Django shell
python manage.py shell

>>> from django.conf import settings
>>> settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['client_id']
'your-client-id'

>>> from allauth.socialaccount.models import SocialApp
>>> SocialApp.objects.filter(provider='google')
<QuerySet [<SocialApp: Google OAuth>]>
```

---

## Production Deployment

### Environment Variables

```bash
# .env file
GOOGLE_CLIENT_ID=your-production-client-id
GOOGLE_CLIENT_SECRET=your-production-client-secret
```

### Security Considerations

1. **Never commit credentials** to version control
2. **Use HTTPS** in production
3. **Whitelist specific redirect URIs**
4. **Enable CSRF protection** (already enabled)
5. **Set secure cookie flags**:
   ```python
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   ```

### CORS Configuration

```python
# settings.py (production)
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend-domain.com",
]
CORS_ALLOW_CREDENTIALS = True
```

---

## API Authentication Flow Diagram

```
┌─────────┐            ┌─────────┐          ┌──────────┐
│ Frontend│            │ Backend │          │  Google  │
└────┬────┘            └────┬────┘          └────┬─────┘
     │                      │                    │
     │ 1. Get Config        │                    │
     ├─────────────────────>│                    │
     │                      │                    │
     │ 2. Return client_id  │                    │
     │<─────────────────────┤                    │
     │                      │                    │
     │ 3. Redirect to Google OAuth               │
     ├───────────────────────────────────────────>│
     │                      │                    │
     │ 4. User authenticates│                    │
     │                      │                    │
     │ 5. Return tokens     │                    │
     │<───────────────────────────────────────────┤
     │                      │                    │
     │ 6. POST /google/login/                   │
     │    {access_token}    │                    │
     ├─────────────────────>│                    │
     │                      │ 7. Verify token    │
     │                      ├───────────────────>│
     │                      │                    │
     │                      │ 8. User info       │
     │                      │<───────────────────┤
     │                      │                    │
     │                      │ 9. Create/get user │
     │                      │                    │
     │ 10. Return JWT tokens│                    │
     │<─────────────────────┤                    │
     │                      │                    │
     │ 11. API calls with JWT                   │
     ├─────────────────────>│                    │
     │                      │                    │
```

---

## Summary

✅ Google OAuth configured with django-allauth
✅ Custom REST API endpoints for Google login
✅ Automatic user and player profile creation
✅ JWT token generation for API authentication
✅ Frontend integration examples provided
✅ Production deployment guide included

For questions or issues, check the troubleshooting section or review the Django admin for social app configuration.
