"""
Authentication views for Google OAuth and social login
"""
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from allauth.socialaccount.models import SocialAccount
import requests


def get_tokens_for_user(user):
    """Generate JWT tokens for a user"""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def google_login(request):
    """
    Handle Google OAuth login
    Expects: { "access_token": "..." } or { "code": "..." }
    """
    access_token = request.data.get('access_token')
    code = request.data.get('code')
    id_token = request.data.get('id_token')

    if not access_token and not code and not id_token:
        return Response(
            {'error': 'Access token, code, or id_token required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # If we have an access token, get user info from Google
        if access_token:
            # Get user info from Google
            response = requests.get(
                'https://www.googleapis.com/oauth2/v3/userinfo',
                headers={'Authorization': f'Bearer {access_token}'}
            )

            if response.status_code != 200:
                return Response(
                    {'error': 'Invalid access token'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user_data = response.json()

        elif id_token:
            # Verify ID token
            response = requests.get(
                f'https://oauth2.googleapis.com/tokeninfo?id_token={id_token}'
            )

            if response.status_code != 200:
                return Response(
                    {'error': 'Invalid ID token'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user_data = response.json()

        else:
            return Response(
                {'error': 'Access token or ID token required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Extract user information
        email = user_data.get('email')
        google_id = user_data.get('sub')
        name = user_data.get('name', '')
        given_name = user_data.get('given_name', '')
        family_name = user_data.get('family_name', '')
        picture = user_data.get('picture', '')

        if not email or not google_id:
            return Response(
                {'error': 'Could not retrieve user information from Google'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user exists with this Google account
        try:
            social_account = SocialAccount.objects.get(
                provider='google',
                uid=google_id
            )
            user = social_account.user

        except SocialAccount.DoesNotExist:
            # Check if user exists with this email
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                # Create new user
                username = email.split('@')[0]
                # Make username unique if needed
                base_username = username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=given_name,
                    last_name=family_name
                )

                # Create player profile
                from game.models import PlayerProfile
                PlayerProfile.objects.create(user=user)

            # Create social account
            social_account = SocialAccount.objects.create(
                user=user,
                provider='google',
                uid=google_id,
                extra_data={
                    'email': email,
                    'name': name,
                    'picture': picture,
                    'given_name': given_name,
                    'family_name': family_name
                }
            )

        # Generate JWT tokens
        tokens = get_tokens_for_user(user)

        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            },
            'tokens': tokens
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': f'Authentication failed: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def google_oauth_config(request):
    """
    Get Google OAuth configuration for frontend
    """
    google_config = settings.SOCIALACCOUNT_PROVIDERS.get('google', {})
    client_id = google_config.get('APP', {}).get('client_id', '')

    return Response({
        'client_id': client_id,
        'redirect_uri': request.build_absolute_uri('/api/auth/google/callback'),
        'scope': ' '.join(google_config.get('SCOPE', [])),
    })
