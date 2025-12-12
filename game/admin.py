from django.contrib import admin
from .models import (
    Party, PlayerProfile, BuildingType, Building, PartyMessage,
    WeaponType, Tower, EnemyType, Wave, Enemy, WorkerType, Worker,
    MaterialType, PlayerMaterial, TechnologyType, PlayerTechnology,
    CraftingRecipe, MaterialRequirement, TechnologyMaterialRequirement,
    PlayerItem, TradeOffer
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


@admin.register(MaterialType)
class MaterialTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'base_value', 'is_tradeable', 'produced_by_building', 'production_rate']
    list_filter = ['category', 'is_tradeable']
    search_fields = ['name', 'produced_by_building']
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'description', 'category', 'icon')
        }),
        ('Trading', {
            'fields': ('base_value', 'is_tradeable', 'stack_size')
        }),
        ('Production', {
            'fields': ('produced_by_building', 'production_rate')
        }),
    )


@admin.register(PlayerMaterial)
class PlayerMaterialAdmin(admin.ModelAdmin):
    list_display = ['player', 'material_type', 'quantity', 'last_updated']
    list_filter = ['material_type__category']
    search_fields = ['player__user__username', 'material_type__name']
    readonly_fields = ['last_updated']


class TechnologyMaterialRequirementInline(admin.TabularInline):
    model = TechnologyMaterialRequirement
    extra = 1


@admin.register(TechnologyType)
class TechnologyTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'research_time', 'cost_coins', 'min_level', 'prerequisite']
    list_filter = ['category', 'min_level']
    search_fields = ['name']
    inlines = [TechnologyMaterialRequirementInline]
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'description', 'category', 'icon', 'min_level')
        }),
        ('Research Requirements', {
            'fields': ('research_time', 'cost_coins', 'prerequisite')
        }),
        ('Effects', {
            'fields': ('production_bonus', 'building_cost_reduction', 'damage_bonus',
                      'unlock_building_type', 'unlock_worker_type')
        }),
    )


@admin.register(PlayerTechnology)
class PlayerTechnologyAdmin(admin.ModelAdmin):
    list_display = ['player', 'technology_type', 'is_completed', 'is_researching', 'research_started', 'research_completed']
    list_filter = ['is_completed', 'is_researching', 'technology_type__category']
    search_fields = ['player__user__username', 'technology_type__name']
    readonly_fields = ['research_started']


class MaterialRequirementInline(admin.TabularInline):
    model = MaterialRequirement
    extra = 1


@admin.register(CraftingRecipe)
class CraftingRecipeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'crafting_time', 'cost_coins', 'required_building',
                    'required_technology', 'min_level']
    list_filter = ['category', 'can_equip_to_building', 'is_consumable', 'tradeable']
    search_fields = ['name', 'required_building']
    inlines = [MaterialRequirementInline]
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'description', 'category', 'icon', 'min_level')
        }),
        ('Crafting Requirements', {
            'fields': ('crafting_time', 'cost_coins', 'required_building', 'required_technology')
        }),
        ('Effects', {
            'fields': ('production_bonus', 'worker_capacity_bonus', 'comfort_bonus')
        }),
        ('Properties', {
            'fields': ('can_equip_to_building', 'is_consumable', 'tradeable')
        }),
    )


@admin.register(MaterialRequirement)
class MaterialRequirementAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'material_type', 'quantity']
    list_filter = ['recipe__category', 'material_type__category']
    search_fields = ['recipe__name', 'material_type__name']


@admin.register(TechnologyMaterialRequirement)
class TechnologyMaterialRequirementAdmin(admin.ModelAdmin):
    list_display = ['technology', 'material_type', 'quantity']
    list_filter = ['technology__category', 'material_type__category']
    search_fields = ['technology__name', 'material_type__name']


@admin.register(PlayerItem)
class PlayerItemAdmin(admin.ModelAdmin):
    list_display = ['player', 'recipe', 'quantity', 'equipped_to_building', 'created_at']
    list_filter = ['recipe__category']
    search_fields = ['player__user__username', 'recipe__name']
    readonly_fields = ['created_at', 'last_updated']


@admin.register(TradeOffer)
class TradeOfferAdmin(admin.ModelAdmin):
    list_display = ['seller', 'buyer', 'trade_type', 'status', 'price_coins', 'created_at', 'expires_at']
    list_filter = ['status', 'trade_type', 'party_only']
    search_fields = ['seller__user__username', 'buyer__user__username']
    readonly_fields = ['created_at', 'completed_at']
    fieldsets = (
        ('Parties', {
            'fields': ('seller', 'buyer', 'party_only')
        }),
        ('Trade Details', {
            'fields': ('trade_type', 'material_offered', 'material_quantity',
                      'item_offered', 'item_quantity')
        }),
        ('Price', {
            'fields': ('price_coins', 'price_material', 'price_material_quantity')
        }),
        ('Status', {
            'fields': ('status', 'created_at', 'expires_at', 'completed_at')
        }),
    )
