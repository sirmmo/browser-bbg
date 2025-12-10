from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Party(models.Model):
    """A group of players playing together"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Parties"

    def __str__(self):
        return self.name


class PlayerProfile(models.Model):
    """Extended user profile for game data"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    party = models.ForeignKey(Party, on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    coins = models.IntegerField(default=100)
    wood = models.IntegerField(default=50)
    stone = models.IntegerField(default=30)
    food = models.IntegerField(default=20)
    last_collection = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    def collect_resources(self):
        """Collect resources from buildings"""
        now = timezone.now()
        time_diff = (now - self.last_collection).total_seconds() / 60  # minutes

        for building in self.buildings.filter(is_built=True):
            production = building.building_type.calculate_production(time_diff)
            if building.building_type.resource_type == 'coins':
                self.coins += production
            elif building.building_type.resource_type == 'wood':
                self.wood += production
            elif building.building_type.resource_type == 'stone':
                self.stone += production
            elif building.building_type.resource_type == 'food':
                self.food += production

        self.last_collection = now
        self.save()
        return {
            'coins': self.coins,
            'wood': self.wood,
            'stone': self.stone,
            'food': self.food,
        }


class BuildingType(models.Model):
    """Template for different building types"""
    RESOURCE_CHOICES = [
        ('coins', 'Coins'),
        ('wood', 'Wood'),
        ('stone', 'Stone'),
        ('food', 'Food'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    resource_type = models.CharField(max_length=20, choices=RESOURCE_CHOICES)
    production_rate = models.IntegerField(help_text="Resources per minute")
    cost_coins = models.IntegerField(default=0)
    cost_wood = models.IntegerField(default=0)
    cost_stone = models.IntegerField(default=0)
    cost_food = models.IntegerField(default=0)
    build_time = models.IntegerField(help_text="Build time in seconds")
    width = models.IntegerField(default=1)
    height = models.IntegerField(default=1)
    icon = models.CharField(max_length=50, default='🏠')

    def __str__(self):
        return self.name

    def calculate_production(self, minutes):
        """Calculate production for given time period"""
        return int(self.production_rate * minutes)


class Building(models.Model):
    """A building placed on a player's base"""
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name='buildings')
    building_type = models.ForeignKey(BuildingType, on_delete=models.CASCADE)
    position_x = models.IntegerField()
    position_y = models.IntegerField()
    is_built = models.BooleanField(default=False)
    build_started = models.DateTimeField(auto_now_add=True)
    build_completed = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['player', 'position_x', 'position_y']

    def __str__(self):
        return f"{self.building_type.name} at ({self.position_x}, {self.position_y})"

    def check_completion(self):
        """Check if building construction is complete"""
        if not self.is_built and self.build_started:
            now = timezone.now()
            elapsed = (now - self.build_started).total_seconds()
            if elapsed >= self.building_type.build_time:
                self.is_built = True
                self.build_completed = now
                self.save()
                return True
        return False


class PartyMessage(models.Model):
    """Messages in party chat"""
    party = models.ForeignKey(Party, on_delete=models.CASCADE, related_name='messages')
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.player.user.username}: {self.message[:50]}"
