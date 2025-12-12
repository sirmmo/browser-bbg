from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Party, PlayerProfile, BuildingType, Building, PartyMessage,
    WeaponType, Tower, EnemyType, Wave, Enemy, WorkerType, Worker
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

    class Meta:
        model = PlayerProfile
        fields = ['id', 'user', 'party', 'coins', 'wood', 'stone', 'food', 'level', 'experience',
                  'next_level_xp', 'waves_survived', 'last_collection', 'created_at']

    def get_next_level_xp(self, obj):
        return obj.get_next_level_xp()


class BuildingTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuildingType
        fields = '__all__'


class BuildingSerializer(serializers.ModelSerializer):
    building_type_detail = BuildingTypeSerializer(source='building_type', read_only=True)

    class Meta:
        model = Building
        fields = ['id', 'building_type', 'building_type_detail', 'position_x', 'position_y',
                  'is_built', 'build_started', 'build_completed', 'created_at']
        read_only_fields = ['is_built', 'build_started', 'build_completed']


class BuildingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = ['building_type', 'position_x', 'position_y']

    def validate(self, data):
        request = self.context.get('request')
        player = request.user.profile

        building_type = data['building_type']

        # Check if player has enough resources
        if player.coins < building_type.cost_coins:
            raise serializers.ValidationError("Not enough coins")
        if player.wood < building_type.cost_wood:
            raise serializers.ValidationError("Not enough wood")
        if player.stone < building_type.cost_stone:
            raise serializers.ValidationError("Not enough stone")
        if player.food < building_type.cost_food:
            raise serializers.ValidationError("Not enough food")

        # Check if position is already occupied
        if Building.objects.filter(
            player=player,
            position_x=data['position_x'],
            position_y=data['position_y']
        ).exists():
            raise serializers.ValidationError("Position already occupied")

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
