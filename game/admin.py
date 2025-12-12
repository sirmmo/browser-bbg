from django.contrib import admin
from .models import (
    Party, PlayerProfile, BuildingType, Building, PartyMessage,
    WeaponType, Tower, EnemyType, Wave, Enemy, WorkerType, Worker
)


@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'created_at', 'is_active']
    search_fields = ['name', 'code']


@admin.register(PlayerProfile)
class PlayerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'party', 'level', 'experience', 'coins', 'wood', 'stone', 'food', 'waves_survived']
    list_filter = ['party', 'level']
    search_fields = ['user__username']


@admin.register(BuildingType)
class BuildingTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'resource_type', 'production_rate', 'min_level', 'build_time']
    list_filter = ['category', 'resource_type', 'min_level']


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ['player', 'building_type', 'position_x', 'position_y', 'is_built']
    list_filter = ['is_built', 'building_type']
    search_fields = ['player__user__username']


@admin.register(PartyMessage)
class PartyMessageAdmin(admin.ModelAdmin):
    list_display = ['party', 'player', 'message', 'created_at']
    list_filter = ['party', 'created_at']


@admin.register(WeaponType)
class WeaponTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_damage', 'base_range', 'base_fire_rate', 'min_level', 'upgrade_path']
    list_filter = ['min_level']


@admin.register(Tower)
class TowerAdmin(admin.ModelAdmin):
    list_display = ['player', 'weapon_type', 'position_x', 'position_y', 'kills', 'damage_dealt']
    list_filter = ['weapon_type']
    search_fields = ['player__user__username']


@admin.register(EnemyType)
class EnemyTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'health', 'speed', 'damage', 'reward_coins', 'reward_xp', 'min_wave']
    list_filter = ['min_wave']


@admin.register(Wave)
class WaveAdmin(admin.ModelAdmin):
    list_display = ['player', 'wave_number', 'is_active', 'enemies_defeated', 'total_enemies', 'started_at']
    list_filter = ['is_active', 'wave_number']
    search_fields = ['player__user__username']


@admin.register(Enemy)
class EnemyAdmin(admin.ModelAdmin):
    list_display = ['enemy_type', 'wave', 'current_health', 'is_alive', 'spawn_time']
    list_filter = ['is_alive', 'enemy_type']


@admin.register(WorkerType)
class WorkerTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'cost_coins', 'cost_food', 'production_multiplier', 
                    'damage_bonus', 'min_level']
    list_filter = ['category', 'min_level']
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'description', 'category', 'icon', 'min_level')
        }),
        ('Costs', {
            'fields': ('cost_coins', 'cost_food', 'upkeep_food')
        }),
        ('Production Effects', {
            'fields': ('production_multiplier', 'build_speed_multiplier', 'resource_efficiency')
        }),
        ('Defense Effects', {
            'fields': ('damage_bonus', 'range_bonus', 'fire_rate_multiplier')
        }),
        ('Compatibility', {
            'fields': ('compatible_building_category',)
        }),
    )


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ['worker_type', 'player', 'get_assignment', 'efficiency', 'morale', 'experience']
    list_filter = ['worker_type__category', 'morale']
    search_fields = ['player__user__username']
    readonly_fields = ['efficiency', 'hired_at']
    
    def get_assignment(self, obj):
        if obj.assigned_building:
            return f"Building: {obj.assigned_building.building_type.name}"
        elif obj.assigned_tower:
            return f"Tower: {obj.assigned_tower.weapon_type.name}"
        return "Unassigned"
    get_assignment.short_description = 'Assignment'
