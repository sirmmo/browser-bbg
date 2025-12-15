# Google OAuth Integration - Angular Frontend

This document describes the Google OAuth authentication implementation in the Angular frontend.

## Overview

The login component now supports two authentication methods:
1. **Google Sign-In** - One-click authentication using Google accounts
2. **Traditional Login** - Username/password authentication

## Implementation Details

### Files Modified

1. **src/index.html**
   - Added Google Identity Services (GIS) script tag
   - Script: `https://accounts.google.com/gsi/client`

2. **src/app/services/auth.service.ts**
   - Added `loginWithGoogle()` method for Google authentication
   - Added `loadGoogleConfig()` to fetch client ID from backend
   - Added `getGoogleClientId()` to provide client ID to components
   - Stores JWT tokens from backend in localStorage

3. **src/app/components/login/login.component.ts**
   - Implements `OnInit` and `AfterViewInit` lifecycle hooks
   - Added `initializeGoogleSignIn()` to initialize Google library
   - Added `renderGoogleButton()` to render the Google Sign-In button
   - Added `handleGoogleSignIn()` to process Google authentication callback
   - Added loading state management

4. **src/app/components/login/login.component.html**
   - Added Google Sign-In button container
   - Added visual divider between Google and traditional login
   - Added loading state to form inputs and submit button

5. **src/app/components/login/login.component.css**
   - Styled Google Sign-In section with centered layout
   - Added divider styling with "OR" separator
   - Maintained consistent visual design with existing styles

## Authentication Flow

### Google Sign-In Flow

1. User loads login page
2. Component initializes Google Sign-In library
3. Auth service fetches Google Client ID from backend (`GET /api/google/config/`)
4. Google Sign-In button is rendered
5. User clicks "Sign in with Google"
6. Google OAuth popup appears
7. User selects Google account and authorizes
8. Google returns ID token to callback
9. Frontend sends ID token to backend (`POST /api/google/login/`)
10. Backend validates token and returns JWT tokens
11. Frontend stores JWT tokens in localStorage
12. User is redirected to `/base`

### Traditional Login Flow

1. User enters username and password
2. Frontend sends credentials to backend (`POST /api/login/`)
3. Backend validates credentials and returns JWT tokens
4. Frontend stores JWT tokens in localStorage
5. User is redirected to `/base`

## API Endpoints Used

- `GET /api/google/config/` - Fetch Google OAuth configuration (client ID)
- `POST /api/google/login/` - Authenticate with Google ID token
- `POST /api/login/` - Traditional username/password authentication

## Configuration

The frontend automatically fetches the Google Client ID from the backend. No frontend-specific configuration is needed.

To configure the backend, see `GOOGLE_AUTH_SETUP.md` in the project root.

## User Experience

### Login Page Features

- **Prominent Google Sign-In button** at the top for easy access
- **Visual separator** ("OR") between authentication methods
- **Loading states** prevent duplicate submissions
- **Error messages** for failed authentication attempts
- **Disabled inputs** during authentication process
- **Consistent styling** with existing application design

### Error Handling

- Google authentication errors display: "Google authentication failed. Please try again."
- Traditional login errors display: "Invalid username or password"
- Network errors are logged to console for debugging

## Security Considerations

1. **ID Token Validation**: The backend validates Google ID tokens before issuing JWT tokens
2. **HTTPS Required**: Google OAuth requires HTTPS in production
3. **CORS Configuration**: Backend must allow frontend origin
4. **Token Storage**: JWT tokens are stored in localStorage (consider httpOnly cookies for enhanced security)

## Testing

### Local Development

1. Ensure backend is running with Google OAuth configured
2. Start Angular dev server: `npm start`
3. Navigate to login page
4. Click "Sign in with Google" button
5. Authenticate with a Google account
6. Verify redirection to base building game

### Troubleshooting

**Google button doesn't appear:**
- Check browser console for errors
- Verify Google Client ID is configured in backend
- Ensure Google library loaded (`https://accounts.google.com/gsi/client`)

**Authentication fails:**
- Check network tab for API response errors
- Verify backend Google OAuth configuration
- Check CORS settings allow frontend origin

**Infinite redirect loop:**
- Clear localStorage
- Check auth guard implementation
- Verify token validation logic

## Future Enhancements

Potential improvements:
- Add "One Tap" sign-in for returning users
- Implement token refresh logic
- Add account linking for existing users
- Support additional OAuth providers (Facebook, GitHub, etc.)
- Add session management and timeout handling
- Migrate to httpOnly cookies for enhanced security
