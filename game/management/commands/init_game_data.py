from django.core.management.base import BaseCommand
from game.models import BuildingType


class Command(BaseCommand):
    help = 'Initialize game data with building types'

    def handle(self, *args, **options):
        building_types = [
            {
                'name': 'Gold Mine',
                'description': 'Produces coins over time',
                'resource_type': 'coins',
                'production_rate': 5,
                'cost_coins': 0,
                'cost_wood': 10,
                'cost_stone': 5,
                'cost_food': 0,
                'build_time': 10,
                'width': 2,
                'height': 2,
                'icon': '💰'
            },
            {
                'name': 'Lumber Mill',
                'description': 'Produces wood over time',
                'resource_type': 'wood',
                'production_rate': 3,
                'cost_coins': 20,
                'cost_wood': 0,
                'cost_stone': 5,
                'cost_food': 5,
                'build_time': 15,
                'width': 2,
                'height': 2,
                'icon': '🪵'
            },
            {
                'name': 'Stone Quarry',
                'description': 'Produces stone over time',
                'resource_type': 'stone',
                'production_rate': 2,
                'cost_coins': 30,
                'cost_wood': 10,
                'cost_stone': 0,
                'cost_food': 5,
                'build_time': 20,
                'width': 2,
                'height': 2,
                'icon': '🪨'
            },
            {
                'name': 'Farm',
                'description': 'Produces food over time',
                'resource_type': 'food',
                'production_rate': 4,
                'cost_coins': 15,
                'cost_wood': 5,
                'cost_stone': 0,
                'cost_food': 0,
                'build_time': 12,
                'width': 2,
                'height': 2,
                'icon': '🌾'
            },
            {
                'name': 'Trading Post',
                'description': 'Advanced building that produces lots of coins',
                'resource_type': 'coins',
                'production_rate': 15,
                'cost_coins': 50,
                'cost_wood': 30,
                'cost_stone': 20,
                'cost_food': 10,
                'build_time': 30,
                'width': 3,
                'height': 3,
                'icon': '🏪'
            },
        ]

        for building_data in building_types:
            BuildingType.objects.get_or_create(
                name=building_data['name'],
                defaults=building_data
            )

        self.stdout.write(self.style.SUCCESS('Successfully initialized game data'))
