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
    level = models.IntegerField(default=1)
    experience = models.IntegerField(default=0)
    last_collection = models.DateTimeField(auto_now_add=True)
    last_wave = models.DateTimeField(null=True, blank=True)
    waves_survived = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    def add_experience(self, amount):
        """Add experience and level up if needed"""
        self.experience += amount
        # Simple level formula: level = floor(xp / 100) + 1
        new_level = (self.experience // 100) + 1
        if new_level > self.level:
            self.level = new_level
            self.save()
            return True  # Leveled up
        self.save()
        return False

    def get_next_level_xp(self):
        """Get XP needed for next level"""
        return (self.level * 100) - self.experience

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
    CATEGORY_CHOICES = [
        ('resource', 'Resource Production'),
        ('defense', 'Defense Tower'),
        ('special', 'Special Building'),
    ]

    RESOURCE_CHOICES = [
        ('coins', 'Coins'),
        ('wood', 'Wood'),
        ('stone', 'Stone'),
        ('food', 'Food'),
        ('none', 'None'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='resource')
    resource_type = models.CharField(max_length=20, choices=RESOURCE_CHOICES, default='none')
    production_rate = models.IntegerField(default=0, help_text="Resources per minute")
    cost_coins = models.IntegerField(default=0)
    cost_wood = models.IntegerField(default=0)
    cost_stone = models.IntegerField(default=0)
    cost_food = models.IntegerField(default=0)
    build_time = models.IntegerField(help_text="Build time in seconds")
    min_level = models.IntegerField(default=1, help_text="Minimum level required")
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


class WeaponType(models.Model):
    """Template for tower/weapon types that can be upgraded"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    base_damage = models.IntegerField(help_text="Base damage per shot")
    base_range = models.IntegerField(help_text="Range in grid units")
    base_fire_rate = models.FloatField(help_text="Shots per second")
    cost_coins = models.IntegerField(default=0)
    cost_wood = models.IntegerField(default=0)
    cost_stone = models.IntegerField(default=0)
    min_level = models.IntegerField(default=1, help_text="Minimum player level")
    icon = models.CharField(max_length=50, default='🗼')
    upgrade_path = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='upgrades_from', help_text="What this upgrades to")

    def __str__(self):
        return self.name

    def get_upgrade_cost(self):
        """Get the cost to upgrade to the next level"""
        if self.upgrade_path:
            return {
                'coins': self.upgrade_path.cost_coins - self.cost_coins,
                'wood': self.upgrade_path.cost_wood - self.cost_wood,
                'stone': self.upgrade_path.cost_stone - self.cost_stone,
            }
        return None


class Tower(models.Model):
    """A defensive tower placed on a player's base"""
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name='towers')
    weapon_type = models.ForeignKey(WeaponType, on_delete=models.CASCADE)
    position_x = models.IntegerField()
    position_y = models.IntegerField()
    kills = models.IntegerField(default=0)
    damage_dealt = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['player', 'position_x', 'position_y']

    def __str__(self):
        return f"{self.weapon_type.name} at ({self.position_x}, {self.position_y})"

    def can_upgrade(self):
        """Check if tower can be upgraded"""
        return self.weapon_type.upgrade_path is not None

    def upgrade(self):
        """Upgrade tower to next weapon type"""
        if self.can_upgrade():
            upgrade_cost = self.weapon_type.get_upgrade_cost()
            player = self.player

            # Check if player can afford upgrade
            if (player.coins >= upgrade_cost['coins'] and
                player.wood >= upgrade_cost['wood'] and
                player.stone >= upgrade_cost['stone']):

                # Deduct resources
                player.coins -= upgrade_cost['coins']
                player.wood -= upgrade_cost['wood']
                player.stone -= upgrade_cost['stone']
                player.save()

                # Upgrade weapon
                self.weapon_type = self.weapon_type.upgrade_path
                self.save()
                return True
        return False


class EnemyType(models.Model):
    """Template for enemy types"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    health = models.IntegerField()
    speed = models.FloatField(help_text="Grid units per second")
    damage = models.IntegerField(help_text="Damage to base if reaches end")
    reward_coins = models.IntegerField(default=5)
    reward_xp = models.IntegerField(default=10)
    icon = models.CharField(max_length=50, default='👾')
    min_wave = models.IntegerField(default=1, help_text="First wave this enemy appears")

    def __str__(self):
        return self.name


class Wave(models.Model):
    """A wave of enemies attacking a player's base"""
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name='waves')
    wave_number = models.IntegerField()
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    enemies_defeated = models.IntegerField(default=0)
    total_enemies = models.IntegerField(default=0)
    damage_taken = models.IntegerField(default=0)

    class Meta:
        ordering = ['-wave_number']

    def __str__(self):
        return f"Wave {self.wave_number} for {self.player.user.username}"

    def complete(self, success=True):
        """Mark wave as complete"""
        self.completed_at = timezone.now()
        self.is_active = False
        self.save()

        if success:
            self.player.waves_survived += 1
            # Reward XP based on wave number
            xp_reward = 20 * self.wave_number
            self.player.add_experience(xp_reward)
            self.player.last_wave = timezone.now()
            self.player.save()


class Enemy(models.Model):
    """An enemy instance in a wave"""
    wave = models.ForeignKey(Wave, on_delete=models.CASCADE, related_name='enemies')
    enemy_type = models.ForeignKey(EnemyType, on_delete=models.CASCADE)
    current_health = models.IntegerField()
    position_x = models.FloatField(default=0)
    position_y = models.FloatField(default=0)
    is_alive = models.BooleanField(default=True)
    spawn_time = models.DateTimeField(auto_now_add=True)
    death_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.enemy_type.name} in {self.wave}"

    def take_damage(self, damage):
        """Apply damage to enemy"""
        self.current_health -= damage
        if self.current_health <= 0:
            self.is_alive = False
            self.death_time = timezone.now()
            self.wave.enemies_defeated += 1
            self.wave.save()

            # Award rewards to player
            player = self.wave.player
            player.coins += self.enemy_type.reward_coins
            player.add_experience(self.enemy_type.reward_xp)
        self.save()
        return not self.is_alive
