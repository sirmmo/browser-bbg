from django.contrib import admin
from .models import Party, PlayerProfile, BuildingType, Building, PartyMessage


@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'created_at', 'is_active']
    search_fields = ['name', 'code']


@admin.register(PlayerProfile)
class PlayerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'party', 'coins', 'wood', 'stone', 'food']
    list_filter = ['party']
    search_fields = ['user__username']


@admin.register(BuildingType)
class BuildingTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'resource_type', 'production_rate', 'build_time']
    list_filter = ['resource_type']


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ['player', 'building_type', 'position_x', 'position_y', 'is_built']
    list_filter = ['is_built', 'building_type']
    search_fields = ['player__user__username']


@admin.register(PartyMessage)
class PartyMessageAdmin(admin.ModelAdmin):
    list_display = ['party', 'player', 'message', 'created_at']
    list_filter = ['party', 'created_at']
