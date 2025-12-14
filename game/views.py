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
    WeaponType, Tower, EnemyType, Wave, Enemy, WorkerType, Worker,
    MaterialType, PlayerMaterial, TechnologyType, PlayerTechnology,
    CraftingRecipe, PlayerItem, TradeOffer, TerritorialExpansion, GameTick
)
from .serializers import (
    UserSerializer, RegisterSerializer, PartySerializer, PlayerProfileSerializer,
    BuildingTypeSerializer, BuildingSerializer, BuildingCreateSerializer,
    PartyMessageSerializer, WeaponTypeSerializer, TowerSerializer,
    TowerCreateSerializer, EnemySerializer, WaveSerializer,
    WorkerTypeSerializer, WorkerSerializer, WorkerHireSerializer,
    MaterialTypeSerializer, PlayerMaterialSerializer,
    TechnologyTypeSerializer, PlayerTechnologySerializer, ResearchStartSerializer,
    CraftingRecipeSerializer, PlayerItemSerializer, CraftItemSerializer,
    TradeOfferSerializer, CreateTradeOfferSerializer,
    TerritorialExpansionSerializer, PurchaseExpansionSerializer, GameTickSerializer
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


# Worker Management Views

class WorkerTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WorkerType.objects.all()
    serializer_class = WorkerTypeSerializer
    permission_classes = [IsAuthenticated]


class WorkerViewSet(viewsets.ModelViewSet):
    serializer_class = WorkerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Worker.objects.filter(player=self.request.user.profile)

    def get_serializer_class(self):
        if self.action == 'create':
            return WorkerHireSerializer
        return WorkerSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=True, methods=['post'])
    def assign_building(self, request, pk=None):
        """Assign worker to a building"""
        worker = self.get_object()
        building_id = request.data.get('building_id')
        
        if not building_id:
            return Response({'error': 'building_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            building = Building.objects.get(id=building_id, player=request.user.profile)
        except Building.DoesNotExist:
            return Response({'error': 'Building not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if worker.assign_to_building(building):
            serializer = self.get_serializer(worker)
            return Response(serializer.data)
        else:
            return Response({'error': 'Cannot assign worker to this building'}, 
                          status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def assign_tower(self, request, pk=None):
        """Assign worker to a tower"""
        worker = self.get_object()
        tower_id = request.data.get('tower_id')
        
        if not tower_id:
            return Response({'error': 'tower_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            tower = Tower.objects.get(id=tower_id, player=request.user.profile)
        except Tower.DoesNotExist:
            return Response({'error': 'Tower not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if worker.assign_to_tower(tower):
            serializer = self.get_serializer(worker)
            return Response(serializer.data)
        else:
            return Response({'error': 'Cannot assign worker to this tower'},
                          status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def unassign(self, request, pk=None):
        """Remove worker from current assignment"""
        worker = self.get_object()
        worker.unassign()
        serializer = self.get_serializer(worker)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_experience(self, request, pk=None):
        """Add experience to worker (for manual testing/admin)"""
        worker = self.get_object()
        amount = request.data.get('amount', 10)
        worker.add_experience(amount)
        serializer = self.get_serializer(worker)
        return Response(serializer.data)


# Material Management Views

class MaterialTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MaterialType.objects.all()
    serializer_class = MaterialTypeSerializer
    permission_classes = [IsAuthenticated]


class PlayerMaterialViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PlayerMaterialSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PlayerMaterial.objects.filter(player=self.request.user.profile)


# Technology System Views

class TechnologyTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TechnologyType.objects.all()
    serializer_class = TechnologyTypeSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get technologies available for research based on player level and prerequisites"""
        player = request.user.profile

        # Get technologies player can research (level requirement met)
        available_techs = TechnologyType.objects.filter(min_level__lte=player.level)

        # Filter out already researched
        researched_ids = PlayerTechnology.objects.filter(
            player=player,
            is_completed=True
        ).values_list('technology_type_id', flat=True)

        available_techs = available_techs.exclude(id__in=researched_ids)

        # Filter by prerequisites
        filtered_techs = []
        for tech in available_techs:
            if tech.prerequisite:
                # Check if prerequisite is researched
                if tech.prerequisite.id in researched_ids:
                    filtered_techs.append(tech)
            else:
                # No prerequisite required
                filtered_techs.append(tech)

        serializer = self.get_serializer(filtered_techs, many=True)
        return Response(serializer.data)


class PlayerTechnologyViewSet(viewsets.ModelViewSet):
    serializer_class = PlayerTechnologySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PlayerTechnology.objects.filter(player=self.request.user.profile)

    def get_serializer_class(self):
        if self.action == 'create':
            return ResearchStartSerializer
        return PlayerTechnologySerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get currently researching technology"""
        research = PlayerTechnology.objects.filter(
            player=request.user.profile,
            is_researching=True
        ).first()

        if research:
            serializer = self.get_serializer(research)
            return Response(serializer.data)
        return Response({'message': 'No active research'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def check_completion(self, request, pk=None):
        """Check if research is complete"""
        research = self.get_object()
        completed = research.check_completion()
        serializer = self.get_serializer(research)
        return Response({
            'completed': completed,
            'research': serializer.data
        })

    @action(detail=False, methods=['get'])
    def completed(self, request):
        """Get all completed technologies"""
        technologies = PlayerTechnology.objects.filter(
            player=request.user.profile,
            is_completed=True
        )
        serializer = self.get_serializer(technologies, many=True)
        return Response(serializer.data)


# Crafting System Views

class CraftingRecipeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CraftingRecipe.objects.all()
    serializer_class = CraftingRecipeSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get recipes available for crafting based on player level and unlocked technologies"""
        player = request.user.profile

        # Get recipes player can craft (level requirement met)
        available_recipes = CraftingRecipe.objects.filter(min_level__lte=player.level)

        # Filter by required technology
        researched_tech_ids = PlayerTechnology.objects.filter(
            player=player,
            is_completed=True
        ).values_list('technology_type_id', flat=True)

        filtered_recipes = []
        for recipe in available_recipes:
            if recipe.required_technology:
                # Check if technology is researched
                if recipe.required_technology.id in researched_tech_ids:
                    filtered_recipes.append(recipe)
            else:
                # No technology required
                filtered_recipes.append(recipe)

        serializer = self.get_serializer(filtered_recipes, many=True)
        return Response(serializer.data)


class PlayerItemViewSet(viewsets.ModelViewSet):
    serializer_class = PlayerItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PlayerItem.objects.filter(player=self.request.user.profile)

    def get_serializer_class(self):
        if self.action == 'create':
            return CraftItemSerializer
        return PlayerItemSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=True, methods=['post'])
    def equip(self, request, pk=None):
        """Equip item to a building"""
        item = self.get_object()
        building_id = request.data.get('building_id')

        if not building_id:
            return Response({'error': 'building_id required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            building = Building.objects.get(id=building_id, player=request.user.profile)
        except Building.DoesNotExist:
            return Response({'error': 'Building not found'}, status=status.HTTP_404_NOT_FOUND)

        if item.equip_to_building(building):
            serializer = self.get_serializer(item)
            return Response(serializer.data)
        else:
            return Response({'error': 'Cannot equip item to this building'},
                          status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def unequip(self, request, pk=None):
        """Unequip item from building"""
        item = self.get_object()
        if item.unequip():
            serializer = self.get_serializer(item)
            return Response(serializer.data)
        else:
            return Response({'error': 'Item is not equipped'},
                          status=status.HTTP_400_BAD_REQUEST)


# Trading System Views

class TradeOfferViewSet(viewsets.ModelViewSet):
    serializer_class = TradeOfferSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        player = self.request.user.profile

        # Show offers created by player or available to them
        if self.action == 'list':
            # Show public offers and party offers
            party_offers = TradeOffer.objects.filter(
                party_only=True,
                seller__party=player.party
            ) if player.party else TradeOffer.objects.none()

            public_offers = TradeOffer.objects.filter(party_only=False, buyer=None)
            direct_offers = TradeOffer.objects.filter(buyer=player)

            return (party_offers | public_offers | direct_offers).filter(
                status='pending'
            ).distinct().order_by('-created_at')

        # For other actions, only show player's own offers
        return TradeOffer.objects.filter(seller=player)

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateTradeOfferSerializer
        return TradeOfferSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=False, methods=['get'])
    def my_offers(self, request):
        """Get offers created by the player"""
        offers = TradeOffer.objects.filter(seller=request.user.profile)
        serializer = self.get_serializer(offers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def received_offers(self, request):
        """Get offers directed to the player"""
        offers = TradeOffer.objects.filter(
            buyer=request.user.profile,
            status='pending'
        )
        serializer = self.get_serializer(offers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept a trade offer"""
        offer = self.get_object()
        player = request.user.profile

        # Check if offer can be accepted
        if offer.seller == player:
            return Response({'error': 'Cannot accept your own offer'},
                          status=status.HTTP_400_BAD_REQUEST)

        if offer.buyer and offer.buyer != player:
            return Response({'error': 'This offer is for another player'},
                          status=status.HTTP_403_FORBIDDEN)

        success, message = offer.accept(player)

        if success:
            serializer = self.get_serializer(offer)
            return Response({'message': message, 'trade': serializer.data})
        else:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a trade offer"""
        offer = self.get_object()

        if offer.cancel():
            serializer = self.get_serializer(offer)
            return Response({'message': 'Trade cancelled', 'trade': serializer.data})
        else:
            return Response({'error': 'Cannot cancel this trade'},
                          status=status.HTTP_400_BAD_REQUEST)


# Territory and Time Progression Views

class TerritorialExpansionViewSet(viewsets.ReadOnlyModelViewSet):
    """View territorial expansion history"""
    serializer_class = TerritorialExpansionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TerritorialExpansion.objects.filter(player=self.request.user.profile)

    @action(detail=False, methods=['get'])
    def cost(self, request):
        """Get cost for next expansion"""
        player = request.user.profile
        expansion_type = request.query_params.get('type', 'both')

        if not player.can_expand_territory():
            return Response({'error': 'Maximum territory size reached'},
                          status=status.HTTP_400_BAD_REQUEST)

        current_size = max(player.grid_size_x, player.grid_size_y)
        cost = TerritorialExpansion.get_expansion_cost(current_size)

        return Response({
            'expansion_type': expansion_type,
            'current_size': {'x': player.grid_size_x, 'y': player.grid_size_y},
            'max_size': 20,
            'cost': cost
        })

    @action(detail=False, methods=['post'])
    def purchase(self, request):
        """Purchase a territorial expansion"""
        serializer = PurchaseExpansionSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            player = request.user.profile
            expansion_type = serializer.validated_data['expansion_type']

            # Get cost
            current_size = max(player.grid_size_x, player.grid_size_y)
            cost = TerritorialExpansion.get_expansion_cost(current_size)

            # Deduct resources
            player.coins -= cost['coins']
            player.wood -= cost['wood']
            player.stone -= cost['stone']
            player.save()

            # Create expansion record
            expansion = TerritorialExpansion.objects.create(
                player=player,
                expansion_type=expansion_type,
                cost_coins=cost['coins'],
                cost_wood=cost['wood'],
                cost_stone=cost['stone']
            )

            # Apply expansion
            expansion.apply_expansion()

            # Reload player
            player.refresh_from_db()

            return Response({
                'message': f'{expansion_type.capitalize()} expansion purchased successfully',
                'expansion': TerritorialExpansionSerializer(expansion).data,
                'new_size': {'x': player.grid_size_x, 'y': player.grid_size_y},
                'resources': {
                    'coins': player.coins,
                    'wood': player.wood,
                    'stone': player.stone
                }
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GameTickViewSet(viewsets.ReadOnlyModelViewSet):
    """View game tick history (read-only)"""
    queryset = GameTick.objects.all()
    serializer_class = GameTickSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current tick number"""
        tick_number = GameTick.get_current_tick()
        return Response({'tick_number': tick_number})

    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get latest tick details"""
        tick = GameTick.objects.first()
        if tick:
            serializer = self.get_serializer(tick)
            return Response(serializer.data)
        return Response({'message': 'No ticks processed yet'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def health(self, request):
        """Check tick service health"""
        from django.utils import timezone
        from datetime import timedelta

        latest_tick = GameTick.objects.first()

        if not latest_tick:
            return Response({
                'status': 'warning',
                'message': 'No ticks have been processed yet',
                'healthy': False
            })

        # Check if last tick was within expected interval (2 minutes threshold)
        time_since_last = timezone.now() - latest_tick.processed_at
        threshold = timedelta(minutes=2)

        is_healthy = time_since_last < threshold

        return Response({
            'status': 'healthy' if is_healthy else 'unhealthy',
            'healthy': is_healthy,
            'last_tick_number': latest_tick.tick_number,
            'last_tick_time': latest_tick.processed_at,
            'seconds_since_last_tick': int(time_since_last.total_seconds()),
            'threshold_seconds': int(threshold.total_seconds()),
            'message': 'Tick service is running normally' if is_healthy else 'Tick service may be down or stalled'
        })
