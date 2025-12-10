from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
import random
import string

from .models import Party, PlayerProfile, BuildingType, Building, PartyMessage
from .serializers import (
    UserSerializer, RegisterSerializer, PartySerializer, PlayerProfileSerializer,
    BuildingTypeSerializer, BuildingSerializer, BuildingCreateSerializer,
    PartyMessageSerializer
)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlayerProfileViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PlayerProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PlayerProfile.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def me(self, request):
        profile, created = PlayerProfile.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def collect(self, request):
        profile = request.user.profile
        resources = profile.collect_resources()
        return Response({
            'message': 'Resources collected',
            'resources': resources
        })


class BuildingTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BuildingType.objects.all()
    serializer_class = BuildingTypeSerializer
    permission_classes = [IsAuthenticated]


class BuildingViewSet(viewsets.ModelViewSet):
    serializer_class = BuildingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Building.objects.filter(player=self.request.user.profile)

    def get_serializer_class(self):
        if self.action == 'create':
            return BuildingCreateSerializer
        return BuildingSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=True, methods=['post'])
    def check_completion(self, request, pk=None):
        building = self.get_object()
        completed = building.check_completion()
        serializer = self.get_serializer(building)
        return Response({
            'completed': completed,
            'building': serializer.data
        })


class PartyViewSet(viewsets.ModelViewSet):
    serializer_class = PartySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Party.objects.filter(is_active=True)

    def create(self, request):
        name = request.data.get('name')
        if not name:
            return Response({'error': 'Party name is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate unique code
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        while Party.objects.filter(code=code).exists():
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

        party = Party.objects.create(name=name, code=code)

        # Join the creator to the party
        profile = request.user.profile
        profile.party = party
        profile.save()

        serializer = self.get_serializer(party)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def join(self, request):
        code = request.data.get('code')
        if not code:
            return Response({'error': 'Party code is required'}, status=status.HTTP_400_BAD_REQUEST)

        party = get_object_or_404(Party, code=code, is_active=True)
        profile = request.user.profile
        profile.party = party
        profile.save()

        serializer = self.get_serializer(party)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def leave(self, request):
        profile = request.user.profile
        if not profile.party:
            return Response({'error': 'Not in a party'}, status=status.HTTP_400_BAD_REQUEST)

        profile.party = None
        profile.save()
        return Response({'message': 'Left party successfully'})

    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        party = self.get_object()
        members = party.members.all()
        serializer = PlayerProfileSerializer(members, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        party = self.get_object()
        messages = party.messages.all()[:50]  # Last 50 messages
        serializer = PartyMessageSerializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        party = self.get_object()
        profile = request.user.profile

        if profile.party != party:
            return Response({'error': 'You are not a member of this party'},
                            status=status.HTTP_403_FORBIDDEN)

        message_text = request.data.get('message')
        if not message_text:
            return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)

        message = PartyMessage.objects.create(
            party=party,
            player=profile,
            message=message_text
        )

        serializer = PartyMessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
