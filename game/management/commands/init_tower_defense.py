from django.core.management.base import BaseCommand
from game.models import BuildingType, WeaponType, EnemyType


class Command(BaseCommand):
    help = 'Initialize tower defense data with weapons and enemies'

    def handle(self, *args, **options):
        # Update existing buildings to have category
        BuildingType.objects.filter(resource_type='coins').update(category='resource')
        BuildingType.objects.filter(resource_type='wood').update(category='resource')
        BuildingType.objects.filter(resource_type='stone').update(category='resource')
        BuildingType.objects.filter(resource_type='food').update(category='resource')

        # Create weapon types with upgrade paths
        arrow_tower, _ = WeaponType.objects.get_or_create(
            name='Arrow Tower',
            defaults={
                'description': 'Basic defensive tower',
                'base_damage': 10,
                'base_range': 3,
                'base_fire_rate': 1.0,
                'cost_coins': 50,
                'cost_wood': 20,
                'cost_stone': 10,
                'min_level': 2,
                'icon': '🏹',
            }
        )

        crossbow_tower, _ = WeaponType.objects.get_or_create(
            name='Crossbow Tower',
            defaults={
                'description': 'Upgraded arrow tower with more damage',
                'base_damage': 20,
                'base_range': 4,
                'base_fire_rate': 1.2,
                'cost_coins': 100,
                'cost_wood': 40,
                'cost_stone': 30,
                'min_level': 4,
                'icon': '🏹',
            }
        )

        ballista_tower, _ = WeaponType.objects.get_or_create(
            name='Ballista Tower',
            defaults={
                'description': 'Heavy siege weapon',
                'base_damage': 40,
                'base_range': 5,
                'base_fire_rate': 0.8,
                'cost_coins': 200,
                'cost_wood': 80,
                'cost_stone': 60,
                'min_level': 7,
                'icon': '🏹',
            }
        )

        cannon_tower, _ = WeaponType.objects.get_or_create(
            name='Cannon Tower',
            defaults={
                'description': 'Explosive cannon dealing massive damage',
                'base_damage': 80,
                'base_range': 6,
                'base_fire_rate': 0.5,
                'cost_coins': 400,
                'cost_wood': 100,
                'cost_stone': 150,
                'min_level': 10,
                'icon': '💣',
            }
        )

        # Set up upgrade paths
        arrow_tower.upgrade_path = crossbow_tower
        arrow_tower.save()

        crossbow_tower.upgrade_path = ballista_tower
        crossbow_tower.save()

        ballista_tower.upgrade_path = cannon_tower
        ballista_tower.save()

        # Create magic towers (alternative path)
        magic_tower, _ = WeaponType.objects.get_or_create(
            name='Magic Tower',
            defaults={
                'description': 'Mystical tower that shoots magic bolts',
                'base_damage': 15,
                'base_range': 4,
                'base_fire_rate': 1.5,
                'cost_coins': 80,
                'cost_wood': 10,
                'cost_stone': 50,
                'min_level': 3,
                'icon': '✨',
            }
        )

        wizard_tower, _ = WeaponType.objects.get_or_create(
            name='Wizard Tower',
            defaults={
                'description': 'Powerful wizard tower with area effect',
                'base_damage': 35,
                'base_range': 5,
                'base_fire_rate': 1.0,
                'cost_coins': 180,
                'cost_wood': 30,
                'cost_stone': 120,
                'min_level': 6,
                'icon': '🧙',
            }
        )

        arcane_tower, _ = WeaponType.objects.get_or_create(
            name='Arcane Tower',
            defaults={
                'description': 'Ultimate magical defense',
                'base_damage': 70,
                'base_range': 7,
                'base_fire_rate': 1.2,
                'cost_coins': 350,
                'cost_wood': 50,
                'cost_stone': 250,
                'min_level': 9,
                'icon': '🔮',
            }
        )

        magic_tower.upgrade_path = wizard_tower
        magic_tower.save()

        wizard_tower.upgrade_path = arcane_tower
        wizard_tower.save()

        # Create enemy types
        enemies = [
            {
                'name': 'Goblin',
                'description': 'Weak but fast enemy',
                'health': 30,
                'speed': 2.0,
                'damage': 5,
                'reward_coins': 10,
                'reward_xp': 15,
                'icon': '👺',
                'min_wave': 1,
            },
            {
                'name': 'Orc',
                'description': 'Tough warrior',
                'health': 60,
                'speed': 1.5,
                'damage': 10,
                'reward_coins': 20,
                'reward_xp': 25,
                'icon': '👹',
                'min_wave': 2,
            },
            {
                'name': 'Troll',
                'description': 'Heavily armored',
                'health': 120,
                'speed': 1.0,
                'damage': 20,
                'reward_coins': 40,
                'reward_xp': 50,
                'icon': '🧌',
                'min_wave': 4,
            },
            {
                'name': 'Dragon',
                'description': 'Flying boss enemy',
                'health': 250,
                'speed': 1.2,
                'damage': 50,
                'reward_coins': 100,
                'reward_xp': 150,
                'icon': '🐉',
                'min_wave': 7,
            },
        ]

        for enemy_data in enemies:
            EnemyType.objects.get_or_create(
                name=enemy_data['name'],
                defaults=enemy_data
            )

        self.stdout.write(self.style.SUCCESS('Successfully initialized tower defense data'))
