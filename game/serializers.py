from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import (
    Party, PlayerProfile, BuildingType, Building, PartyMessage,
    WeaponType, Tower, EnemyType, Wave, Enemy, WorkerType, Worker,
    MaterialType, PlayerMaterial, TechnologyType, PlayerTechnology,
    CraftingRecipe, MaterialRequirement, TechnologyMaterialRequirement,
    PlayerItem, TradeOffer, TerritorialExpansion, GameTick
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        PlayerProfile.objects.create(user=user)
        return user


class CustomRegisterSerializer(serializers.Serializer):
    """Custom registration serializer for dj-rest-auth"""
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    username = serializers.CharField(required=False, allow_blank=True)

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return email

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def get_cleaned_data(self):
        return {
            'email': self.validated_data.get('email', ''),
            'password1': self.validated_data.get('password1', ''),
            'username': self.validated_data.get('username', '') or self.validated_data.get('email', '').split('@')[0],
        }

    def save(self, request):
        cleaned_data = self.get_cleaned_data()
        user = User.objects.create_user(
            username=cleaned_data['username'],
            email=cleaned_data['email'],
            password=cleaned_data['password1']
        )
        # Create player profile
        PlayerProfile.objects.create(user=user)
        return user


class PartySerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Party
        fields = ['id', 'name', 'code', 'created_at', 'is_active', 'member_count']

    def get_member_count(self, obj):
        return obj.members.count()


class PlayerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    party = PartySerializer(read_only=True)
    next_level_xp = serializers.SerializerMethodField()
    total_storage_capacity = serializers.SerializerMethodField()
    territory_size = serializers.SerializerMethodField()
    can_expand = serializers.SerializerMethodField()

    class Meta:
        model = PlayerProfile
        fields = ['id', 'user', 'party', 'coins', 'wood', 'stone', 'food', 'level', 'experience',
                  'next_level_xp', 'waves_survived', 'last_collection', 'created_at',
                  'grid_size_x', 'grid_size_y', 'material_storage_capacity',
                  'total_storage_capacity', 'territory_size', 'can_expand', 'last_tick']

    def get_next_level_xp(self, obj):
        return obj.get_next_level_xp()

    def get_total_storage_capacity(self, obj):
        return obj.get_total_storage_capacity()

    def get_territory_size(self, obj):
        return obj.get_territory_size()

    def get_can_expand(self, obj):
        return obj.can_expand_territory()


class BuildingTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuildingType
        fields = '__all__'


class BuildingSerializer(serializers.ModelSerializer):
    building_type_detail = BuildingTypeSerializer(source='building_type', read_only=True)
    time_remaining = serializers.SerializerMethodField()
    completion_percentage = serializers.SerializerMethodField()
    estimated_completion = serializers.SerializerMethodField()

    class Meta:
        model = Building
        fields = ['id', 'building_type', 'building_type_detail', 'position_x', 'position_y',
                  'is_built', 'build_started', 'build_completed', 'created_at',
                  'time_remaining', 'completion_percentage', 'estimated_completion']
        read_only_fields = ['is_built', 'build_started', 'build_completed']

    def get_time_remaining(self, obj):
        """Get seconds remaining until construction is complete"""
        return obj.get_time_remaining()

    def get_completion_percentage(self, obj):
        """Get construction progress percentage (0-100)"""
        return obj.get_completion_percentage()

    def get_estimated_completion(self, obj):
        """Get estimated completion datetime"""
        return obj.get_estimated_completion()


class BuildingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = ['building_type', 'position_x', 'position_y']

    def validate(self, data):
        request = self.context.get('request')
        player = request.user.profile

        building_type = data['building_type']
        position_x = data['position_x']
        position_y = data['position_y']

        # Check player level requirement
        if player.level < building_type.min_level:
            raise serializers.ValidationError(
                f"Player level {building_type.min_level} required (current: {player.level})"
            )

        # Check if building fits within grid boundaries
        if position_x < 0 or position_y < 0:
            raise serializers.ValidationError("Building position cannot be negative")

        if position_x + building_type.width > player.grid_size_x:
            raise serializers.ValidationError(
                f"Building extends beyond grid width (position: {position_x}, "
                f"building width: {building_type.width}, grid width: {player.grid_size_x})"
            )

        if position_y + building_type.height > player.grid_size_y:
            raise serializers.ValidationError(
                f"Building extends beyond grid height (position: {position_y}, "
                f"building height: {building_type.height}, grid height: {player.grid_size_y})"
            )

        # Check if player has enough resources
        if player.coins < building_type.cost_coins:
            raise serializers.ValidationError("Not enough coins")
        if player.wood < building_type.cost_wood:
            raise serializers.ValidationError("Not enough wood")
        if player.stone < building_type.cost_stone:
            raise serializers.ValidationError("Not enough stone")
        if player.food < building_type.cost_food:
            raise serializers.ValidationError("Not enough food")

        # Check if position is already occupied by checking for overlaps
        existing_buildings = Building.objects.filter(player=player)
        for existing in existing_buildings:
            # Check if the new building overlaps with existing building
            if not (position_x + building_type.width <= existing.position_x or
                    position_x >= existing.position_x + existing.building_type.width or
                    position_y + building_type.height <= existing.position_y or
                    position_y >= existing.position_y + existing.building_type.height):
                raise serializers.ValidationError(
                    f"Building overlaps with existing {existing.building_type.name} "
                    f"at position ({existing.position_x}, {existing.position_y})"
                )

        return data

    def create(self, validated_data):
        request = self.context.get('request')
        player = request.user.profile
        building_type = validated_data['building_type']

        # Deduct resources
        player.coins -= building_type.cost_coins
        player.wood -= building_type.cost_wood
        player.stone -= building_type.cost_stone
        player.food -= building_type.cost_food
        player.save()

        # Create building
        building = Building.objects.create(
            player=player,
            **validated_data
        )
        return building


class PartyMessageSerializer(serializers.ModelSerializer):
    player_name = serializers.CharField(source='player.user.username', read_only=True)

    class Meta:
        model = PartyMessage
        fields = ['id', 'party', 'player', 'player_name', 'message', 'created_at']
        read_only_fields = ['party', 'player']


class WeaponTypeSerializer(serializers.ModelSerializer):
    upgrade_path_name = serializers.CharField(source='upgrade_path.name', read_only=True)
    can_upgrade = serializers.SerializerMethodField()

    class Meta:
        model = WeaponType
        fields = ['id', 'name', 'description', 'base_damage', 'base_range', 'base_fire_rate',
                  'cost_coins', 'cost_wood', 'cost_stone', 'min_level', 'icon',
                  'upgrade_path', 'upgrade_path_name', 'can_upgrade']

    def get_can_upgrade(self, obj):
        return obj.upgrade_path is not None


class TowerSerializer(serializers.ModelSerializer):
    weapon_detail = WeaponTypeSerializer(source='weapon_type', read_only=True)
    can_upgrade = serializers.SerializerMethodField()
    upgrade_cost = serializers.SerializerMethodField()

    class Meta:
        model = Tower
        fields = ['id', 'weapon_type', 'weapon_detail', 'position_x', 'position_y',
                  'kills', 'damage_dealt', 'can_upgrade', 'upgrade_cost', 'created_at']

    def get_can_upgrade(self, obj):
        return obj.can_upgrade()

    def get_upgrade_cost(self, obj):
        if obj.can_upgrade():
            return obj.weapon_type.get_upgrade_cost()
        return None


class TowerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tower
        fields = ['weapon_type', 'position_x', 'position_y']

    def validate(self, data):
        request = self.context.get('request')
        player = request.user.profile

        weapon_type = data['weapon_type']

        # Check level requirement
        if player.level < weapon_type.min_level:
            raise serializers.ValidationError(f"Level {weapon_type.min_level} required")

        # Check if player has enough resources
        if player.coins < weapon_type.cost_coins:
            raise serializers.ValidationError("Not enough coins")
        if player.wood < weapon_type.cost_wood:
            raise serializers.ValidationError("Not enough wood")
        if player.stone < weapon_type.cost_stone:
            raise serializers.ValidationError("Not enough stone")

        # Check if position is already occupied
        from .models import Building
        if Building.objects.filter(
            player=player,
            position_x=data['position_x'],
            position_y=data['position_y']
        ).exists() or Tower.objects.filter(
            player=player,
            position_x=data['position_x'],
            position_y=data['position_y']
        ).exists():
            raise serializers.ValidationError("Position already occupied")

        return data

    def create(self, validated_data):
        request = self.context.get('request')
        player = request.user.profile
        weapon_type = validated_data['weapon_type']

        # Deduct resources
        player.coins -= weapon_type.cost_coins
        player.wood -= weapon_type.cost_wood
        player.stone -= weapon_type.cost_stone
        player.save()

        # Create tower
        tower = Tower.objects.create(
            player=player,
            **validated_data
        )
        return tower


class EnemyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnemyType
        fields = '__all__'


class EnemySerializer(serializers.ModelSerializer):
    enemy_detail = EnemyTypeSerializer(source='enemy_type', read_only=True)

    class Meta:
        model = Enemy
        fields = ['id', 'enemy_type', 'enemy_detail', 'current_health', 'position_x', 'position_y',
                  'is_alive', 'spawn_time']


class WaveSerializer(serializers.ModelSerializer):
    enemies = EnemySerializer(many=True, read_only=True)

    class Meta:
        model = Wave
        fields = ['id', 'wave_number', 'started_at', 'completed_at', 'is_active',
                  'enemies_defeated', 'total_enemies', 'damage_taken', 'enemies']


class WorkerTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkerType
        fields = '__all__'


class WorkerSerializer(serializers.ModelSerializer):
    worker_detail = WorkerTypeSerializer(source='worker_type', read_only=True)
    assignment = serializers.SerializerMethodField()
    effective_multiplier = serializers.SerializerMethodField()

    class Meta:
        model = Worker
        fields = ['id', 'worker_type', 'worker_detail', 'assigned_building', 'assigned_tower',
                  'assignment', 'experience', 'efficiency', 'morale', 'effective_multiplier',
                  'hired_at', 'last_paid']
        read_only_fields = ['efficiency', 'hired_at', 'last_paid']

    def get_assignment(self, obj):
        if obj.assigned_building:
            return {'type': 'building', 'id': obj.assigned_building.id, 
                    'name': obj.assigned_building.building_type.name}
        elif obj.assigned_tower:
            return {'type': 'tower', 'id': obj.assigned_tower.id,
                    'name': obj.assigned_tower.weapon_type.name}
        return None

    def get_effective_multiplier(self, obj):
        return obj.get_effective_multiplier()


class WorkerHireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields = ['worker_type']

    def validate(self, data):
        request = self.context.get('request')
        player = request.user.profile
        worker_type = data['worker_type']

        # Check level requirement
        if player.level < worker_type.min_level:
            raise serializers.ValidationError(f"Level {worker_type.min_level} required")

        # Check if player has enough resources
        if player.coins < worker_type.cost_coins:
            raise serializers.ValidationError("Not enough coins")
        if player.food < worker_type.cost_food:
            raise serializers.ValidationError("Not enough food")

        return data

    def create(self, validated_data):
        request = self.context.get('request')
        player = request.user.profile
        worker_type = validated_data['worker_type']

        # Deduct resources
        player.coins -= worker_type.cost_coins
        player.food -= worker_type.cost_food
        player.save()

        # Create worker
        worker = Worker.objects.create(
            player=player,
            worker_type=worker_type
        )
        return worker


# Material System Serializers

class MaterialTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialType
        fields = '__all__'


class PlayerMaterialSerializer(serializers.ModelSerializer):
    material_detail = MaterialTypeSerializer(source='material_type', read_only=True)

    class Meta:
        model = PlayerMaterial
        fields = ['id', 'material_type', 'material_detail', 'quantity', 'last_updated']
        read_only_fields = ['last_updated']


# Technology System Serializers

class TechnologyMaterialRequirementSerializer(serializers.ModelSerializer):
    material_detail = MaterialTypeSerializer(source='material_type', read_only=True)

    class Meta:
        model = TechnologyMaterialRequirement
        fields = ['id', 'material_type', 'material_detail', 'quantity']


class TechnologyTypeSerializer(serializers.ModelSerializer):
    material_requirements = TechnologyMaterialRequirementSerializer(many=True, read_only=True)
    prerequisite_name = serializers.CharField(source='prerequisite.name', read_only=True)

    class Meta:
        model = TechnologyType
        fields = '__all__'


class PlayerTechnologySerializer(serializers.ModelSerializer):
    technology_detail = TechnologyTypeSerializer(source='technology_type', read_only=True)
    progress = serializers.SerializerMethodField()

    class Meta:
        model = PlayerTechnology
        fields = ['id', 'technology_type', 'technology_detail', 'research_started',
                  'research_completed', 'is_researching', 'is_completed', 'progress']
        read_only_fields = ['research_started', 'research_completed', 'is_researching', 'is_completed']

    def get_progress(self, obj):
        if obj.is_completed:
            return 100
        if obj.is_researching:
            elapsed = (timezone.now() - obj.research_started).total_seconds()
            total = obj.technology_type.research_time
            return min(100, int((elapsed / total) * 100))
        return 0


class ResearchStartSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerTechnology
        fields = ['technology_type']

    def validate(self, data):
        request = self.context.get('request')
        player = request.user.profile
        technology_type = data['technology_type']

        # Check level requirement
        if player.level < technology_type.min_level:
            raise serializers.ValidationError(f"Level {technology_type.min_level} required")

        # Check if already researched
        if PlayerTechnology.objects.filter(
            player=player,
            technology_type=technology_type,
            is_completed=True
        ).exists():
            raise serializers.ValidationError("Already researched")

        # Check if already researching
        if PlayerTechnology.objects.filter(
            player=player,
            technology_type=technology_type,
            is_researching=True
        ).exists():
            raise serializers.ValidationError("Already researching")

        # Check prerequisite
        if technology_type.prerequisite:
            if not PlayerTechnology.objects.filter(
                player=player,
                technology_type=technology_type.prerequisite,
                is_completed=True
            ).exists():
                raise serializers.ValidationError(
                    f"Prerequisite technology '{technology_type.prerequisite.name}' required"
                )

        # Check coins
        if player.coins < technology_type.cost_coins:
            raise serializers.ValidationError("Not enough coins")

        # Check material requirements
        for req in technology_type.material_requirements.all():
            player_mat = PlayerMaterial.objects.filter(
                player=player,
                material_type=req.material_type
            ).first()
            if not player_mat or player_mat.quantity < req.quantity:
                raise serializers.ValidationError(
                    f"Not enough {req.material_type.name} (need {req.quantity})"
                )

        return data

    def create(self, validated_data):
        request = self.context.get('request')
        player = request.user.profile
        technology_type = validated_data['technology_type']

        # Deduct costs
        player.coins -= technology_type.cost_coins
        player.save()

        # Deduct materials
        for req in technology_type.material_requirements.all():
            player_mat = PlayerMaterial.objects.get(
                player=player,
                material_type=req.material_type
            )
            player_mat.remove_quantity(req.quantity)

        # Start research
        research = PlayerTechnology.objects.create(
            player=player,
            technology_type=technology_type
        )
        return research


# Crafting System Serializers

class MaterialRequirementSerializer(serializers.ModelSerializer):
    material_detail = MaterialTypeSerializer(source='material_type', read_only=True)

    class Meta:
        model = MaterialRequirement
        fields = ['id', 'material_type', 'material_detail', 'quantity']


class CraftingRecipeSerializer(serializers.ModelSerializer):
    material_requirements = MaterialRequirementSerializer(many=True, read_only=True)
    required_technology_name = serializers.CharField(source='required_technology.name', read_only=True)

    class Meta:
        model = CraftingRecipe
        fields = '__all__'


class PlayerItemSerializer(serializers.ModelSerializer):
    recipe_detail = CraftingRecipeSerializer(source='recipe', read_only=True)
    equipped_to = serializers.SerializerMethodField()

    class Meta:
        model = PlayerItem
        fields = ['id', 'recipe', 'recipe_detail', 'quantity', 'equipped_to_building',
                  'equipped_to', 'created_at', 'last_updated']
        read_only_fields = ['created_at', 'last_updated']

    def get_equipped_to(self, obj):
        if obj.equipped_to_building:
            return {
                'building_id': obj.equipped_to_building.id,
                'building_type': obj.equipped_to_building.building_type.name,
                'position': f"({obj.equipped_to_building.position_x}, {obj.equipped_to_building.position_y})"
            }
        return None


class CraftItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerItem
        fields = ['recipe']

    def validate(self, data):
        request = self.context.get('request')
        player = request.user.profile
        recipe = data['recipe']

        # Check level requirement
        if player.level < recipe.min_level:
            raise serializers.ValidationError(f"Level {recipe.min_level} required")

        # Check if required technology is researched
        if recipe.required_technology:
            if not PlayerTechnology.objects.filter(
                player=player,
                technology_type=recipe.required_technology,
                is_completed=True
            ).exists():
                raise serializers.ValidationError(
                    f"Technology '{recipe.required_technology.name}' required"
                )

        # Check if required building exists
        if recipe.required_building:
            if not Building.objects.filter(
                player=player,
                building_type__name=recipe.required_building,
                is_built=True
            ).exists():
                raise serializers.ValidationError(
                    f"Building '{recipe.required_building}' required"
                )

        # Check coins
        if player.coins < recipe.cost_coins:
            raise serializers.ValidationError("Not enough coins")

        # Check material requirements
        for req in recipe.material_requirements.all():
            player_mat = PlayerMaterial.objects.filter(
                player=player,
                material_type=req.material_type
            ).first()
            if not player_mat or player_mat.quantity < req.quantity:
                raise serializers.ValidationError(
                    f"Not enough {req.material_type.name} (need {req.quantity})"
                )

        return data

    def create(self, validated_data):
        request = self.context.get('request')
        player = request.user.profile
        recipe = validated_data['recipe']

        # Deduct costs
        player.coins -= recipe.cost_coins
        player.save()

        # Deduct materials
        for req in recipe.material_requirements.all():
            player_mat = PlayerMaterial.objects.get(
                player=player,
                material_type=req.material_type
            )
            player_mat.remove_quantity(req.quantity)

        # Create or update item
        item, created = PlayerItem.objects.get_or_create(
            player=player,
            recipe=recipe,
            defaults={'quantity': 1}
        )
        if not created:
            item.quantity += 1
            item.save()

        return item


# Trading System Serializers

class TradeOfferSerializer(serializers.ModelSerializer):
    seller_name = serializers.CharField(source='seller.user.username', read_only=True)
    buyer_name = serializers.CharField(source='buyer.user.username', read_only=True)
    material_offered_detail = MaterialTypeSerializer(source='material_offered', read_only=True)
    item_offered_detail = CraftingRecipeSerializer(source='item_offered', read_only=True)
    price_material_detail = MaterialTypeSerializer(source='price_material', read_only=True)
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = TradeOffer
        fields = ['id', 'seller', 'seller_name', 'buyer', 'buyer_name', 'party_only',
                  'trade_type', 'material_offered', 'material_offered_detail', 'material_quantity',
                  'item_offered', 'item_offered_detail', 'item_quantity',
                  'price_coins', 'price_material', 'price_material_detail', 'price_material_quantity',
                  'status', 'created_at', 'expires_at', 'completed_at', 'is_expired']
        read_only_fields = ['seller', 'status', 'created_at', 'completed_at']

    def get_is_expired(self, obj):
        return obj.status == 'pending' and timezone.now() > obj.expires_at


class CreateTradeOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = TradeOffer
        fields = ['trade_type', 'material_offered', 'material_quantity',
                  'item_offered', 'item_quantity', 'price_coins',
                  'price_material', 'price_material_quantity', 'buyer', 'party_only']

    def validate(self, data):
        request = self.context.get('request')
        player = request.user.profile
        trade_type = data['trade_type']

        # Validate trade type consistency
        if trade_type == 'material':
            if not data.get('material_offered') or data.get('material_quantity', 0) <= 0:
                raise serializers.ValidationError("Material and quantity required for material trade")
            # Check if seller has the materials
            player_mat = PlayerMaterial.objects.filter(
                player=player,
                material_type=data['material_offered']
            ).first()
            if not player_mat or player_mat.quantity < data['material_quantity']:
                raise serializers.ValidationError("Not enough materials to offer")

        elif trade_type == 'item':
            if not data.get('item_offered') or data.get('item_quantity', 0) <= 0:
                raise serializers.ValidationError("Item and quantity required for item trade")
            # Check if seller has the items
            player_item = PlayerItem.objects.filter(
                player=player,
                recipe=data['item_offered']
            ).first()
            if not player_item or player_item.quantity < data['item_quantity']:
                raise serializers.ValidationError("Not enough items to offer")

        # Validate price
        if data.get('price_coins', 0) <= 0 and (
            not data.get('price_material') or data.get('price_material_quantity', 0) <= 0
        ):
            raise serializers.ValidationError("Must specify either coin price or material price")

        return data

    def create(self, validated_data):
        request = self.context.get('request')
        player = request.user.profile

        # Set expiration (7 days from now)
        expires_at = timezone.now() + timedelta(days=7)

        trade_offer = TradeOffer.objects.create(
            seller=player,
            expires_at=expires_at,
            **validated_data
        )
        return trade_offer


# Territorial Expansion Serializers

class TerritorialExpansionSerializer(serializers.ModelSerializer):
    player_name = serializers.CharField(source='player.user.username', read_only=True)

    class Meta:
        model = TerritorialExpansion
        fields = ['id', 'player', 'player_name', 'expansion_type', 'cost_coins',
                  'cost_wood', 'cost_stone', 'size_increase', 'purchased_at']
        read_only_fields = ['player', 'purchased_at']


class PurchaseExpansionSerializer(serializers.Serializer):
    expansion_type = serializers.ChoiceField(choices=['horizontal', 'vertical', 'both'])

    def validate(self, data):
        request = self.context.get('request')
        player = request.user.profile
        expansion_type = data['expansion_type']

        # Check if player can expand
        if not player.can_expand_territory():
            raise serializers.ValidationError("Maximum territory size reached")

        # Get expansion cost
        current_size = max(player.grid_size_x, player.grid_size_y)
        cost = TerritorialExpansion.get_expansion_cost(current_size)

        # Check if player has enough resources
        if player.coins < cost['coins']:
            raise serializers.ValidationError(f"Not enough coins (need {cost['coins']})")
        if player.wood < cost['wood']:
            raise serializers.ValidationError(f"Not enough wood (need {cost['wood']})")
        if player.stone < cost['stone']:
            raise serializers.ValidationError(f"Not enough stone (need {cost['stone']})")

        data['cost'] = cost
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        player = request.user.profile
        expansion_type = validated_data['expansion_type']
        cost = validated_data['cost']

        # Deduct costs
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
            cost_stone=cost['stone'],
            size_increase=2
        )

        # Apply expansion
        expansion.apply_expansion()

        return expansion


# Game Tick Serializers

class GameTickSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameTick
        fields = ['id', 'tick_number', 'processed_at', 'players_processed',
                  'buildings_completed', 'researches_completed', 'resources_collected']
        read_only_fields = '__all__'
