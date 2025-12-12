from django.core.management.base import BaseCommand
from game.models import WorkerType


class Command(BaseCommand):
    help = 'Initialize worker types with diverse templates'

    def handle(self, *args, **options):
        worker_types = [
            # Production Workers - Boost resource buildings
            {
                'name': 'Miner',
                'description': 'Experienced miner who increases coin production',
                'category': 'production',
                'cost_coins': 100,
                'cost_food': 20,
                'upkeep_food': 2,
                'production_multiplier': 1.5,  # +50% production
                'compatible_building_category': 'resource',
                'min_level': 3,
                'icon': '⛏️',
            },
            {
                'name': 'Lumberjack',
                'description': 'Skilled woodcutter who boosts wood production',
                'category': 'production',
                'cost_coins': 80,
                'cost_food': 15,
                'upkeep_food': 1,
                'production_multiplier': 1.4,
                'compatible_building_category': 'resource',
                'min_level': 2,
                'icon': '🪓',
            },
            {
                'name': 'Farmer',
                'description': 'Experienced farmer who improves food production',
                'category': 'production',
                'cost_coins': 60,
                'cost_food': 10,
                'upkeep_food': 1,
                'production_multiplier': 1.6,  # +60% production for farms
                'compatible_building_category': 'resource',
                'min_level': 1,
                'icon': '👨‍🌾',
            },
            {
                'name': 'Mason',
                'description': 'Expert stoneworker who increases stone production',
                'category': 'production',
                'cost_coins': 90,
                'cost_food': 18,
                'upkeep_food': 2,
                'production_multiplier': 1.45,
                'compatible_building_category': 'resource',
                'min_level': 3,
                'icon': '🧱',
            },

            # Defense Specialists - Boost towers
            {
                'name': 'Archer',
                'description': 'Skilled archer who mans your tower',
                'category': 'defense',
                'cost_coins': 150,
                'cost_food': 25,
                'upkeep_food': 3,
                'damage_bonus': 15,
                'range_bonus': 1,
                'fire_rate_multiplier': 1.2,
                'compatible_building_category': 'defense',
                'min_level': 4,
                'icon': '🏹',
            },
            {
                'name': 'Guard',
                'description': 'Professional soldier who defends your towers',
                'category': 'defense',
                'cost_coins': 120,
                'cost_food': 20,
                'upkeep_food': 2,
                'damage_bonus': 10,
                'range_bonus': 0,
                'fire_rate_multiplier': 1.3,
                'min_level': 3,
                'icon': '🛡️',
            },
            {
                'name': 'Marksman',
                'description': 'Elite sniper with exceptional accuracy and range',
                'category': 'defense',
                'cost_coins': 250,
                'cost_food': 40,
                'upkeep_food': 4,
                'damage_bonus': 25,
                'range_bonus': 2,
                'fire_rate_multiplier': 1.15,
                'min_level': 7,
                'icon': '🎯',
            },
            {
                'name': 'Mage',
                'description': 'Powerful mage who enhances magical towers',
                'category': 'defense',
                'cost_coins': 300,
                'cost_food': 35,
                'upkeep_food': 3,
                'damage_bonus': 30,
                'range_bonus': 1,
                'fire_rate_multiplier': 1.25,
                'min_level': 6,
                'icon': '🧙',
            },

            # Support Staff - Mixed benefits
            {
                'name': 'Engineer',
                'description': 'Skilled engineer who speeds up construction',
                'category': 'support',
                'cost_coins': 180,
                'cost_food': 30,
                'upkeep_food': 2,
                'build_speed_multiplier': 2.0,  # 2x build speed
                'resource_efficiency': 0.9,  # 10% less resource costs
                'compatible_building_category': '',  # Works everywhere
                'min_level': 5,
                'icon': '👷',
            },
            {
                'name': 'Merchant',
                'description': 'Savvy trader who reduces operational costs',
                'category': 'support',
                'cost_coins': 200,
                'cost_food': 25,
                'upkeep_food': 2,
                'production_multiplier': 1.2,
                'resource_efficiency': 0.85,  # 15% less costs
                'compatible_building_category': 'resource',
                'min_level': 6,
                'icon': '🤵',
            },
            {
                'name': 'Apprentice',
                'description': 'Young helper with basic skills',
                'category': 'support',
                'cost_coins': 50,
                'cost_food': 8,
                'upkeep_food': 1,
                'production_multiplier': 1.15,
                'compatible_building_category': '',
                'min_level': 1,
                'icon': '👨‍🎓',
            },

            # Elite Workers - Best of the best
            {
                'name': 'Master Craftsman',
                'description': 'Legendary artisan who excels at production',
                'category': 'elite',
                'cost_coins': 500,
                'cost_food': 50,
                'upkeep_food': 5,
                'production_multiplier': 2.0,  # Double production!
                'build_speed_multiplier': 1.5,
                'resource_efficiency': 0.8,
                'compatible_building_category': 'resource',
                'min_level': 10,
                'icon': '👨‍🔧',
            },
            {
                'name': 'General',
                'description': 'Military genius who commands your defenses',
                'category': 'elite',
                'cost_coins': 600,
                'cost_food': 60,
                'upkeep_food': 6,
                'damage_bonus': 50,
                'range_bonus': 3,
                'fire_rate_multiplier': 1.5,
                'compatible_building_category': 'defense',
                'min_level': 12,
                'icon': '⭐',
            },
            {
                'name': 'Archmage',
                'description': 'Supreme magic user with overwhelming power',
                'category': 'elite',
                'cost_coins': 800,
                'cost_food': 70,
                'upkeep_food': 7,
                'damage_bonus': 80,
                'range_bonus': 4,
                'fire_rate_multiplier': 1.6,
                'compatible_building_category': 'defense',
                'min_level': 15,
                'icon': '🔮',
            },
        ]

        for worker_data in worker_types:
            WorkerType.objects.get_or_create(
                name=worker_data['name'],
                defaults=worker_data
            )

        self.stdout.write(self.style.SUCCESS(f'Successfully initialized {len(worker_types)} worker types'))
