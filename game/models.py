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

    # Basic resources
    coins = models.IntegerField(default=100)
    wood = models.IntegerField(default=50)
    stone = models.IntegerField(default=30)
    food = models.IntegerField(default=20)

    # Player progression
    level = models.IntegerField(default=1)
    experience = models.IntegerField(default=0)
    waves_survived = models.IntegerField(default=0)

    # Territory and storage
    grid_size_x = models.IntegerField(default=10, help_text="Territory width")
    grid_size_y = models.IntegerField(default=10, help_text="Territory height")
    material_storage_capacity = models.IntegerField(default=1000, help_text="Total material storage")

    # Timestamps
    last_collection = models.DateTimeField(auto_now_add=True)
    last_wave = models.DateTimeField(null=True, blank=True)
    last_tick = models.DateTimeField(default=timezone.now, help_text="Last game tick processed")
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

    def get_total_storage_capacity(self):
        """Calculate total storage capacity including bonuses from buildings"""
        base_capacity = self.material_storage_capacity

        # Add capacity from warehouse buildings
        warehouse_bonus = 0
        for building in self.buildings.filter(building_type__name__icontains='Warehouse', is_built=True):
            # Each warehouse adds capacity based on its type
            warehouse_bonus += building.building_type.storage_capacity if hasattr(building.building_type, 'storage_capacity') else 500

        return base_capacity + warehouse_bonus

    def get_territory_size(self):
        """Get current territory dimensions"""
        return {'width': self.grid_size_x, 'height': self.grid_size_y, 'total': self.grid_size_x * self.grid_size_y}

    def can_expand_territory(self):
        """Check if player can purchase territory expansion"""
        # Max territory size
        max_size = 20
        return self.grid_size_x < max_size or self.grid_size_y < max_size

    def collect_resources(self):
        """Collect resources from buildings (with worker bonuses)"""
        now = timezone.now()
        time_diff = (now - self.last_collection).total_seconds() / 60  # minutes

        materials_collected = {}

        for building in self.buildings.filter(is_built=True):
            # Calculate production with worker multiplier
            worker_multiplier = building.get_worker_multiplier()

            # Handle basic resources (coins, wood, stone, food)
            production = building.building_type.calculate_production(time_diff, worker_multiplier)

            if building.building_type.resource_type == 'coins':
                self.coins += production
            elif building.building_type.resource_type == 'wood':
                self.wood += production
            elif building.building_type.resource_type == 'stone':
                self.stone += production
            elif building.building_type.resource_type == 'food':
                self.food += production

            # Handle advanced materials production
            material_production = building.collect_materials(time_diff, worker_multiplier)
            for material_name, quantity in material_production.items():
                materials_collected[material_name] = materials_collected.get(material_name, 0) + quantity

        self.last_collection = now
        self.save()

        return {
            'coins': self.coins,
            'wood': self.wood,
            'stone': self.stone,
            'food': self.food,
            'materials': materials_collected,
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
    worker_capacity = models.IntegerField(default=2, help_text="Maximum workers that can be assigned")
    storage_capacity = models.IntegerField(default=0, help_text="Material storage capacity bonus")
    width = models.IntegerField(default=1)
    height = models.IntegerField(default=1)
    icon = models.CharField(max_length=50, default='🏠')

    def __str__(self):
        return self.name

    def calculate_production(self, minutes, worker_multiplier=1.0):
        """Calculate production for given time period with optional worker bonus"""
        return int(self.production_rate * minutes * worker_multiplier)


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

    def get_worker_multiplier(self):
        """Calculate total production multiplier from assigned workers"""
        total_multiplier = 1.0
        for worker in self.workers.all():
            worker_bonus = (worker.worker_type.production_multiplier - 1.0) * worker.get_effective_multiplier()
            total_multiplier += worker_bonus
        return total_multiplier

    def get_item_bonus(self):
        """Calculate production bonus from equipped items"""
        bonus = 0.0
        for item in self.equipped_items.all():
            bonus += item.recipe.production_bonus
        return bonus

    def get_effective_worker_capacity(self):
        """Get worker capacity including bonuses from equipped items"""
        base_capacity = self.building_type.worker_capacity
        item_bonus = sum(item.recipe.worker_capacity_bonus for item in self.equipped_items.all())
        return base_capacity + item_bonus

    def collect_materials(self, time_diff_minutes, worker_multiplier=1.0):
        """Collect advanced materials produced by this building"""
        from game.models import MaterialType, PlayerMaterial

        materials_collected = {}

        # Find all materials that this building type can produce
        material_types = MaterialType.objects.filter(produced_by_building=self.building_type.name)

        for material_type in material_types:
            if material_type.production_rate > 0:
                # Calculate production with worker and item bonuses
                item_bonus = self.get_item_bonus()
                total_multiplier = worker_multiplier * (1.0 + item_bonus)

                production = int(material_type.production_rate * time_diff_minutes * total_multiplier)

                if production > 0:
                    # Add to player's material inventory
                    player_material, created = PlayerMaterial.objects.get_or_create(
                        player=self.player,
                        material_type=material_type
                    )
                    player_material.add_quantity(production)
                    materials_collected[material_type.name] = production

        return materials_collected

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

    def get_effective_damage(self):
        """Calculate total damage with worker bonuses"""
        base_damage = self.weapon_type.base_damage
        bonus_damage = 0
        for worker in self.workers.all():
            bonus_damage += worker.worker_type.damage_bonus * worker.get_effective_multiplier()
        return int(base_damage + bonus_damage)

    def get_effective_range(self):
        """Calculate total range with worker bonuses"""
        base_range = self.weapon_type.base_range
        bonus_range = 0
        for worker in self.workers.all():
            bonus_range += worker.worker_type.range_bonus * worker.get_effective_multiplier()
        return int(base_range + bonus_range)

    def get_effective_fire_rate(self):
        """Calculate fire rate with worker multipliers"""
        base_fire_rate = self.weapon_type.base_fire_rate
        multiplier = 1.0
        for worker in self.workers.all():
            worker_bonus = (worker.worker_type.fire_rate_multiplier - 1.0) * worker.get_effective_multiplier()
            multiplier += worker_bonus
        return round(base_fire_rate * multiplier, 2)

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


class WorkerType(models.Model):
    """Template for worker/staff types that can be hired"""
    WORKER_CATEGORY_CHOICES = [
        ('production', 'Production Worker'),
        ('defense', 'Defense Specialist'),
        ('support', 'Support Staff'),
        ('elite', 'Elite Worker'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=WORKER_CATEGORY_CHOICES)
    
    # Hiring costs
    cost_coins = models.IntegerField(default=50)
    cost_food = models.IntegerField(default=10, help_text="Food cost per hire")
    upkeep_food = models.IntegerField(default=1, help_text="Food consumed per day")
    
    # Effect modifiers (multipliers and bonuses)
    production_multiplier = models.FloatField(default=1.0, help_text="Production boost (1.0 = no boost, 1.5 = +50%)")
    damage_bonus = models.IntegerField(default=0, help_text="Extra damage for towers")
    range_bonus = models.IntegerField(default=0, help_text="Extra range for towers")
    fire_rate_multiplier = models.FloatField(default=1.0, help_text="Fire rate boost for towers")
    build_speed_multiplier = models.FloatField(default=1.0, help_text="Build speed boost (2.0 = 2x faster)")
    resource_efficiency = models.FloatField(default=1.0, help_text="Resource usage efficiency (0.9 = -10% costs)")
    
    # Compatibility
    compatible_building_category = models.CharField(max_length=20, blank=True, 
                                                     help_text="Leave blank for all, or specify: resource/defense/special")
    min_level = models.IntegerField(default=1)
    icon = models.CharField(max_length=50, default='👷')
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def is_compatible_with_building(self, building_type):
        """Check if this worker type can work in the given building type"""
        if not self.compatible_building_category:
            return True  # Works in all buildings
        return building_type.category == self.compatible_building_category


class Worker(models.Model):
    """An individual worker hired by a player"""
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name='workers')
    worker_type = models.ForeignKey(WorkerType, on_delete=models.CASCADE)
    
    # Assignment
    assigned_building = models.ForeignKey('Building', on_delete=models.SET_NULL, 
                                         null=True, blank=True, related_name='workers')
    assigned_tower = models.ForeignKey('Tower', on_delete=models.SET_NULL,
                                       null=True, blank=True, related_name='workers')
    
    # Worker progression
    experience = models.IntegerField(default=0)
    efficiency = models.FloatField(default=1.0, help_text="Worker efficiency multiplier (improves with experience)")
    morale = models.IntegerField(default=100, help_text="Worker morale (0-100)")
    
    hired_at = models.DateTimeField(auto_now_add=True)
    last_paid = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        location = "Unassigned"
        if self.assigned_building:
            location = f"at {self.assigned_building.building_type.name}"
        elif self.assigned_tower:
            location = f"at {self.assigned_tower.weapon_type.name}"
        return f"{self.worker_type.name} {location}"

    def assign_to_building(self, building):
        """Assign worker to a building"""
        if building.player != self.player:
            return False
        
        # Check compatibility
        if not self.worker_type.is_compatible_with_building(building.building_type):
            return False
        
        # Check capacity
        if building.workers.count() >= building.building_type.worker_capacity:
            return False
        
        self.assigned_building = building
        self.assigned_tower = None
        self.save()
        return True

    def assign_to_tower(self, tower):
        """Assign worker to a tower"""
        if tower.player != self.player:
            return False
        
        # Check if worker is defense category
        if self.worker_type.category != 'defense' and self.worker_type.category != 'elite':
            return False
        
        # Check capacity (towers can have 1 worker by default)
        if tower.workers.count() >= 1:
            return False
        
        self.assigned_tower = tower
        self.assigned_building = None
        self.save()
        return True

    def unassign(self):
        """Remove worker from current assignment"""
        self.assigned_building = None
        self.assigned_tower = None
        self.save()

    def get_effective_multiplier(self):
        """Get the worker's effective multiplier including efficiency"""
        return self.efficiency * (self.morale / 100.0)

    def add_experience(self, amount):
        """Add experience to worker and improve efficiency"""
        self.experience += amount
        # Efficiency improves slightly with experience (caps at 1.5x)
        new_efficiency = 1.0 + min(0.5, self.experience / 1000.0)
        self.efficiency = new_efficiency
        self.save()


class MaterialType(models.Model):
    """Template for materials that can be produced, traded, and used in crafting"""
    MATERIAL_CATEGORY_CHOICES = [
        ('raw', 'Raw Material'),
        ('processed', 'Processed Material'),
        ('rare', 'Rare Material'),
        ('luxury', 'Luxury Item'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=MATERIAL_CATEGORY_CHOICES)
    icon = models.CharField(max_length=50, default='📦')
    base_value = models.IntegerField(default=10, help_text="Base market value in coins")
    is_tradeable = models.BooleanField(default=True)
    stack_size = models.IntegerField(default=1000, help_text="Maximum stack size")

    # Production info
    produced_by_building = models.CharField(max_length=100, blank=True,
                                            help_text="Building type name that produces this")
    production_rate = models.FloatField(default=0, help_text="Base production per minute")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['category', 'name']


class PlayerMaterial(models.Model):
    """Player's material inventory"""
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name='materials')
    material_type = models.ForeignKey(MaterialType, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['player', 'material_type']
        ordering = ['material_type__category', 'material_type__name']

    def __str__(self):
        return f"{self.player.user.username}: {self.quantity}x {self.material_type.name}"

    def add_quantity(self, amount):
        """Add materials to inventory"""
        self.quantity = min(self.quantity + amount, self.material_type.stack_size)
        self.save()
        return self.quantity

    def remove_quantity(self, amount):
        """Remove materials from inventory, returns True if successful"""
        if self.quantity >= amount:
            self.quantity -= amount
            self.save()
            return True
        return False


class TechnologyType(models.Model):
    """Template for technologies that can be researched"""
    TECH_CATEGORY_CHOICES = [
        ('agriculture', 'Agriculture'),
        ('mining', 'Mining & Extraction'),
        ('construction', 'Construction'),
        ('military', 'Military'),
        ('economy', 'Economy'),
        ('advanced', 'Advanced Technology'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=TECH_CATEGORY_CHOICES)
    icon = models.CharField(max_length=50, default='🔬')

    # Research requirements
    research_time = models.IntegerField(help_text="Research time in seconds")
    cost_coins = models.IntegerField(default=0)
    min_level = models.IntegerField(default=1)
    prerequisite = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='unlocks', help_text="Required technology")

    # Effects (bonuses granted when researched)
    production_bonus = models.FloatField(default=0, help_text="Global production multiplier bonus")
    building_cost_reduction = models.FloatField(default=0, help_text="Building cost reduction (0.1 = -10%)")
    damage_bonus = models.IntegerField(default=0, help_text="Global tower damage bonus")
    unlock_building_type = models.CharField(max_length=100, blank=True,
                                            help_text="Building type name to unlock")
    unlock_worker_type = models.CharField(max_length=100, blank=True,
                                          help_text="Worker type name to unlock")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Technologies"
        ordering = ['category', 'min_level']


class PlayerTechnology(models.Model):
    """Technologies researched by a player"""
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name='technologies')
    technology_type = models.ForeignKey(TechnologyType, on_delete=models.CASCADE)
    research_started = models.DateTimeField(auto_now_add=True)
    research_completed = models.DateTimeField(null=True, blank=True)
    is_researching = models.BooleanField(default=True)
    is_completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ['player', 'technology_type']
        verbose_name_plural = "Player Technologies"
        ordering = ['-research_started']

    def __str__(self):
        status = "Completed" if self.is_completed else "Researching"
        return f"{self.player.user.username}: {self.technology_type.name} ({status})"

    def check_completion(self):
        """Check if research is complete"""
        if not self.is_completed and self.is_researching:
            now = timezone.now()
            elapsed = (now - self.research_started).total_seconds()
            if elapsed >= self.technology_type.research_time:
                self.is_completed = True
                self.is_researching = False
                self.research_completed = now
                self.save()
                return True
        return False


class CraftingRecipe(models.Model):
    """Template for items/objects that can be crafted"""
    ITEM_CATEGORY_CHOICES = [
        ('furniture', 'Furniture'),
        ('decoration', 'Decoration'),
        ('equipment', 'Equipment'),
        ('tool', 'Tool'),
        ('consumable', 'Consumable'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=ITEM_CATEGORY_CHOICES)
    icon = models.CharField(max_length=50, default='🔨')

    # Crafting requirements
    crafting_time = models.IntegerField(help_text="Crafting time in seconds")
    cost_coins = models.IntegerField(default=0)
    required_building = models.CharField(max_length=100, blank=True,
                                        help_text="Building type name required for crafting")
    required_technology = models.ForeignKey(TechnologyType, on_delete=models.SET_NULL,
                                           null=True, blank=True,
                                           help_text="Technology required to unlock recipe")
    min_level = models.IntegerField(default=1)

    # Effects when equipped to a building
    production_bonus = models.FloatField(default=0, help_text="Production boost for building")
    worker_capacity_bonus = models.IntegerField(default=0, help_text="Extra worker slots")
    comfort_bonus = models.IntegerField(default=0, help_text="Worker morale boost")

    # Item properties
    can_equip_to_building = models.BooleanField(default=True)
    is_consumable = models.BooleanField(default=False)
    tradeable = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['category', 'name']


class MaterialRequirement(models.Model):
    """Materials required for a crafting recipe"""
    recipe = models.ForeignKey(CraftingRecipe, on_delete=models.CASCADE, related_name='material_requirements')
    material_type = models.ForeignKey(MaterialType, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    class Meta:
        unique_together = ['recipe', 'material_type']

    def __str__(self):
        return f"{self.recipe.name}: {self.quantity}x {self.material_type.name}"


class TechnologyMaterialRequirement(models.Model):
    """Materials required for a technology research"""
    technology = models.ForeignKey(TechnologyType, on_delete=models.CASCADE, related_name='material_requirements')
    material_type = models.ForeignKey(MaterialType, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    class Meta:
        unique_together = ['technology', 'material_type']

    def __str__(self):
        return f"{self.technology.name}: {self.quantity}x {self.material_type.name}"


class PlayerItem(models.Model):
    """Crafted items in player's inventory"""
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name='items')
    recipe = models.ForeignKey(CraftingRecipe, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    # Equipment status
    equipped_to_building = models.ForeignKey('Building', on_delete=models.SET_NULL,
                                            null=True, blank=True, related_name='equipped_items')

    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['player', 'recipe']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.player.user.username}: {self.quantity}x {self.recipe.name}"

    def equip_to_building(self, building):
        """Equip item to a building"""
        if not self.recipe.can_equip_to_building:
            return False
        if building.player != self.player:
            return False
        if self.quantity < 1:
            return False

        self.equipped_to_building = building
        self.quantity -= 1
        self.save()
        return True

    def unequip(self):
        """Unequip item from building"""
        if self.equipped_to_building:
            self.equipped_to_building = None
            self.quantity += 1
            self.save()
            return True
        return False


class TradeOffer(models.Model):
    """Player-to-player trading of materials and items"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]

    TRADE_TYPE_CHOICES = [
        ('material', 'Material Trade'),
        ('item', 'Item Trade'),
        ('mixed', 'Mixed Trade'),
    ]

    # Parties involved
    seller = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name='trade_offers_sent')
    buyer = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name='trade_offers_received',
                              null=True, blank=True, help_text="Leave blank for public listing")
    party_only = models.BooleanField(default=False, help_text="Only visible to party members")

    # Trade details
    trade_type = models.CharField(max_length=20, choices=TRADE_TYPE_CHOICES)

    # Material trade
    material_offered = models.ForeignKey(MaterialType, on_delete=models.CASCADE,
                                        null=True, blank=True, related_name='offered_in_trades')
    material_quantity = models.IntegerField(default=0)

    # Item trade
    item_offered = models.ForeignKey(CraftingRecipe, on_delete=models.CASCADE,
                                     null=True, blank=True, related_name='offered_in_trades')
    item_quantity = models.IntegerField(default=0)

    # Price
    price_coins = models.IntegerField(default=0)
    price_material = models.ForeignKey(MaterialType, on_delete=models.CASCADE,
                                       null=True, blank=True, related_name='used_as_currency')
    price_material_quantity = models.IntegerField(default=0)

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(help_text="Trade offer expiration")
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        item_desc = f"{self.material_quantity}x {self.material_offered.name}" if self.material_offered else f"{self.item_quantity}x {self.item_offered.name}"
        return f"{self.seller.user.username} offers {item_desc} for {self.price_coins} coins"

    def check_expiration(self):
        """Check if trade offer has expired"""
        if self.status == 'pending' and timezone.now() > self.expires_at:
            self.status = 'expired'
            self.save()
            return True
        return False

    def accept(self, buyer_profile):
        """Accept and execute the trade"""
        if self.status != 'pending':
            return False, "Trade is no longer available"

        if self.check_expiration():
            return False, "Trade has expired"

        # Check if buyer has enough coins
        if buyer_profile.coins < self.price_coins:
            return False, "Insufficient coins"

        # Check if buyer has enough materials for price
        if self.price_material and self.price_material_quantity > 0:
            buyer_mat = PlayerMaterial.objects.filter(
                player=buyer_profile,
                material_type=self.price_material
            ).first()
            if not buyer_mat or buyer_mat.quantity < self.price_material_quantity:
                return False, f"Insufficient {self.price_material.name}"

        # Check if seller still has the items
        if self.material_offered:
            seller_mat = PlayerMaterial.objects.filter(
                player=self.seller,
                material_type=self.material_offered
            ).first()
            if not seller_mat or seller_mat.quantity < self.material_quantity:
                return False, "Seller no longer has the materials"

        if self.item_offered:
            seller_item = PlayerItem.objects.filter(
                player=self.seller,
                recipe=self.item_offered
            ).first()
            if not seller_item or seller_item.quantity < self.item_quantity:
                return False, "Seller no longer has the items"

        # Execute the trade
        # Transfer payment to seller
        buyer_profile.coins -= self.price_coins
        self.seller.coins += self.price_coins

        if self.price_material and self.price_material_quantity > 0:
            buyer_mat.remove_quantity(self.price_material_quantity)
            seller_mat_price, _ = PlayerMaterial.objects.get_or_create(
                player=self.seller,
                material_type=self.price_material
            )
            seller_mat_price.add_quantity(self.price_material_quantity)

        # Transfer items to buyer
        if self.material_offered:
            seller_mat.remove_quantity(self.material_quantity)
            buyer_mat_recv, _ = PlayerMaterial.objects.get_or_create(
                player=buyer_profile,
                material_type=self.material_offered
            )
            buyer_mat_recv.add_quantity(self.material_quantity)

        if self.item_offered:
            seller_item.quantity -= self.item_quantity
            seller_item.save()
            buyer_item_recv, _ = PlayerItem.objects.get_or_create(
                player=buyer_profile,
                recipe=self.item_offered
            )
            buyer_item_recv.quantity += self.item_quantity
            buyer_item_recv.save()

        # Update status
        self.buyer = buyer_profile
        self.status = 'accepted'
        self.completed_at = timezone.now()

        buyer_profile.save()
        self.seller.save()
        self.save()

        return True, "Trade completed successfully"

    def cancel(self):
        """Cancel the trade offer"""
        if self.status == 'pending':
            self.status = 'cancelled'
            self.save()
            return True
        return False


class TerritorialExpansion(models.Model):
    """Player territorial expansion purchases"""
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name='expansions')
    expansion_type = models.CharField(max_length=20, choices=[
        ('horizontal', 'Horizontal Expansion'),
        ('vertical', 'Vertical Expansion'),
        ('both', 'Full Expansion')
    ])
    cost_coins = models.IntegerField()
    cost_wood = models.IntegerField(default=0)
    cost_stone = models.IntegerField(default=0)
    size_increase = models.IntegerField(default=2, help_text="Grid size increase")
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-purchased_at']

    def __str__(self):
        return f"{self.player.user.username}: {self.expansion_type} expansion"

    @staticmethod
    def get_expansion_cost(current_size):
        """Calculate cost for next expansion based on current size"""
        # Cost increases exponentially with size
        base_cost = 500
        multiplier = (current_size - 10) / 2 + 1
        return {
            'coins': int(base_cost * multiplier),
            'wood': int(200 * multiplier),
            'stone': int(200 * multiplier),
        }

    def apply_expansion(self):
        """Apply the expansion to the player's territory"""
        player = self.player

        if self.expansion_type == 'horizontal':
            player.grid_size_x += self.size_increase
        elif self.expansion_type == 'vertical':
            player.grid_size_y += self.size_increase
        elif self.expansion_type == 'both':
            player.grid_size_x += self.size_increase
            player.grid_size_y += self.size_increase

        player.save()


class GameTick(models.Model):
    """Global game tick for time-based progression"""
    tick_number = models.IntegerField(unique=True)
    processed_at = models.DateTimeField(auto_now_add=True)
    players_processed = models.IntegerField(default=0)
    buildings_completed = models.IntegerField(default=0)
    researches_completed = models.IntegerField(default=0)
    resources_collected = models.IntegerField(default=0)

    class Meta:
        ordering = ['-tick_number']

    def __str__(self):
        return f"Tick #{self.tick_number} - {self.processed_at}"

    @staticmethod
    def get_current_tick():
        """Get the latest tick number"""
        latest = GameTick.objects.first()
        return latest.tick_number if latest else 0

    @staticmethod
    def create_tick():
        """Create a new game tick"""
        current = GameTick.get_current_tick()
        return GameTick.objects.create(tick_number=current + 1)

    def process_tick(self):
        """Process all time-based game events for this tick"""
        from game.models import PlayerProfile, Building, PlayerTechnology

        stats = {
            'players_processed': 0,
            'buildings_completed': 0,
            'researches_completed': 0,
            'resources_collected': 0,
        }

        # Process all players
        for player in PlayerProfile.objects.all():
            # Process building completions
            for building in player.buildings.filter(is_built=False):
                if building.check_completion():
                    stats['buildings_completed'] += 1

            # Process research completions
            for research in player.technologies.filter(is_completed=False, is_researching=True):
                if research.check_completion():
                    stats['researches_completed'] += 1

            # Auto-collect resources (optional, can be disabled if frontend handles it)
            # player.collect_resources()
            # stats['resources_collected'] += 1

            # Update last tick timestamp
            player.last_tick = timezone.now()
            player.save()

            stats['players_processed'] += 1

        # Update tick statistics
        self.players_processed = stats['players_processed']
        self.buildings_completed = stats['buildings_completed']
        self.researches_completed = stats['researches_completed']
        self.resources_collected = stats['resources_collected']
        self.save()

        return stats
