from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Party, PlayerProfile, BuildingType, Building, PartyMessage


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

    class Meta:
        model = PlayerProfile
        fields = ['id', 'user', 'party', 'coins', 'wood', 'stone', 'food', 'last_collection', 'created_at']


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
