from django.core.management.base import BaseCommand
from game.models import BuildingType


class Command(BaseCommand):
    help = 'Initialize warehouse building types'

    def handle(self, *args, **kwargs):
        self.stdout.write('Initializing warehouse buildings...')

        warehouses = [
            {
                'name': 'Small Warehouse',
                'description': 'Basic storage facility. Increases material storage by 500.',
                'category': 'special',
                'resource_type': 'none',
                'production_rate': 0,
                'cost_coins': 200,
                'cost_wood': 100,
                'cost_stone': 50,
                'cost_food': 0,
                'build_time': 180,  # 3 minutes
                'min_level': 2,
                'worker_capacity': 1,
                'storage_capacity': 500,
                'width': 2,
                'height': 2,
                'icon': '🏪',
            },
            {
                'name': 'Medium Warehouse',
                'description': 'Expanded storage facility. Increases material storage by 1500.',
                'category': 'special',
                'resource_type': 'none',
                'production_rate': 0,
                'cost_coins': 500,
                'cost_wood': 250,
                'cost_stone': 150,
                'cost_food': 0,
                'build_time': 360,  # 6 minutes
                'min_level': 4,
                'worker_capacity': 2,
                'storage_capacity': 1500,
                'width': 3,
                'height': 2,
                'icon': '🏬',
            },
            {
                'name': 'Large Warehouse',
                'description': 'Massive storage complex. Increases material storage by 3000.',
                'category': 'special',
                'resource_type': 'none',
                'production_rate': 0,
                'cost_coins': 1200,
                'cost_wood': 500,
                'cost_stone': 400,
                'cost_food': 0,
                'build_time': 720,  # 12 minutes
                'min_level': 7,
                'worker_capacity': 3,
                'storage_capacity': 3000,
                'width': 3,
                'height': 3,
                'icon': '🏭',
            },
        ]

        count = 0
        for warehouse_data in warehouses:
            _, created = BuildingType.objects.get_or_create(
                name=warehouse_data['name'],
                defaults=warehouse_data
            )
            if created:
                count += 1
                self.stdout.write(f"Created: {warehouse_data['name']}")
            else:
                self.stdout.write(f"Already exists: {warehouse_data['name']}")

        self.stdout.write(self.style.SUCCESS(f'Successfully initialized {count} warehouse building types'))
