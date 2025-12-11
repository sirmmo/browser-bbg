from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
import random
import string

from .models import (
    Party, PlayerProfile, BuildingType, Building, PartyMessage,
    WeaponType, Tower, EnemyType, Wave, Enemy
)
from .serializers import (
    UserSerializer, RegisterSerializer, PartySerializer, PlayerProfileSerializer,
    BuildingTypeSerializer, BuildingSerializer, BuildingCreateSerializer,
    PartyMessageSerializer, WeaponTypeSerializer, TowerSerializer,
    TowerCreateSerializer, EnemySerializer, WaveSerializer
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


# Tower Defense Views

class WeaponTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WeaponType.objects.all()
    serializer_class = WeaponTypeSerializer
    permission_classes = [IsAuthenticated]


class TowerViewSet(viewsets.ModelViewSet):
    serializer_class = TowerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Tower.objects.filter(player=self.request.user.profile)

    def get_serializer_class(self):
        if self.action == 'create':
            return TowerCreateSerializer
        return TowerSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=True, methods=['post'])
    def upgrade(self, request, pk=None):
        tower = self.get_object()
        if tower.upgrade():
            serializer = self.get_serializer(tower)
            return Response({'success': True, 'tower': serializer.data})
        return Response({'error': 'Cannot upgrade tower'}, status=status.HTTP_400_BAD_REQUEST)


class WaveViewSet(viewsets.ModelViewSet):
    serializer_class = WaveSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wave.objects.filter(player=self.request.user.profile)

    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current active wave"""
        wave = Wave.objects.filter(player=request.user.profile, is_active=True).first()
        if wave:
            serializer = self.get_serializer(wave)
            return Response(serializer.data)
        return Response({'message': 'No active wave'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def start(self, request):
        """Start a new wave"""
        from .models import Enemy, EnemyType
        import random

        player = request.user.profile

        # Check if player has active wave
        if Wave.objects.filter(player=player, is_active=True).exists():
            return Response({'error': 'Wave already active'}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate wave number
        last_wave = Wave.objects.filter(player=player).first()
        wave_number = (last_wave.wave_number + 1) if last_wave else 1

        # Create wave
        wave = Wave.objects.create(player=player, wave_number=wave_number)

        # Spawn enemies based on wave number
        enemy_types = list(EnemyType.objects.filter(min_wave__lte=wave_number))
        num_enemies = 5 + (wave_number * 2)  # Scaling difficulty

        for i in range(num_enemies):
            enemy_type = random.choice(enemy_types)
            Enemy.objects.create(
                wave=wave,
                enemy_type=enemy_type,
                current_health=enemy_type.health,
                position_x=0,
                position_y=random.randint(0, 9)
            )

        wave.total_enemies = num_enemies
        wave.save()

        serializer = self.get_serializer(wave)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark wave as complete"""
        wave = self.get_object()
        success = request.data.get('success', True)
        wave.complete(success=success)
        return Response({'message': 'Wave completed'})


class EnemyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EnemySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        wave_id = self.request.query_params.get('wave_id')
        if wave_id:
            return Enemy.objects.filter(wave_id=wave_id)
        return Enemy.objects.filter(wave__player=self.request.user.profile, is_alive=True)

    @action(detail=True, methods=['post'])
    def damage(self, request, pk=None):
        """Apply damage to an enemy"""
        enemy = self.get_object()
        damage_amount = request.data.get('damage', 0)

        if enemy.take_damage(damage_amount):
            # Enemy died
            return Response({'killed': True, 'rewards': {
                'coins': enemy.enemy_type.reward_coins,
                'xp': enemy.enemy_type.reward_xp
            }})
        return Response({'killed': False, 'current_health': enemy.current_health})
