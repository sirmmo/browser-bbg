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

        # Create enemy types - fully templated for easy expansion!
        # You can add new enemy types by simply adding to this list or via Django admin
        enemies = [
            # Early game enemies (Wave 1-3)
            {
                'name': 'Goblin',
                'description': 'Weak but fast enemy - rushes your defenses',
                'health': 30,
                'speed': 2.0,
                'damage': 5,
                'reward_coins': 10,
                'reward_xp': 15,
                'icon': '👺',
                'min_wave': 1,
            },
            {
                'name': 'Skeleton',
                'description': 'Fragile undead warrior',
                'health': 25,
                'speed': 1.8,
                'damage': 4,
                'reward_coins': 8,
                'reward_xp': 12,
                'icon': '💀',
                'min_wave': 1,
            },
            {
                'name': 'Orc',
                'description': 'Tough warrior with balanced stats',
                'health': 60,
                'speed': 1.5,
                'damage': 10,
                'reward_coins': 20,
                'reward_xp': 25,
                'icon': '👹',
                'min_wave': 2,
            },
            {
                'name': 'Wolf',
                'description': 'Fast predator that hunts in packs',
                'health': 40,
                'speed': 2.5,
                'damage': 8,
                'reward_coins': 15,
                'reward_xp': 20,
                'icon': '🐺',
                'min_wave': 3,
            },

            # Mid game enemies (Wave 4-6)
            {
                'name': 'Troll',
                'description': 'Heavily armored tank - slow but durable',
                'health': 120,
                'speed': 1.0,
                'damage': 20,
                'reward_coins': 40,
                'reward_xp': 50,
                'icon': '🧌',
                'min_wave': 4,
            },
            {
                'name': 'Dark Knight',
                'description': 'Armored knight with high damage',
                'health': 90,
                'speed': 1.3,
                'damage': 25,
                'reward_coins': 35,
                'reward_xp': 45,
                'icon': '⚔️',
                'min_wave': 5,
            },
            {
                'name': 'Wraith',
                'description': 'Ethereal spirit - fast and elusive',
                'health': 70,
                'speed': 2.2,
                'damage': 15,
                'reward_coins': 30,
                'reward_xp': 40,
                'icon': '👻',
                'min_wave': 6,
            },

            # Late game enemies (Wave 7+)
            {
                'name': 'Dragon',
                'description': 'Flying boss - high HP and damage',
                'health': 250,
                'speed': 1.2,
                'damage': 50,
                'reward_coins': 100,
                'reward_xp': 150,
                'icon': '🐉',
                'min_wave': 7,
            },
            {
                'name': 'Demon',
                'description': 'Powerful demon from the abyss',
                'health': 180,
                'speed': 1.6,
                'damage': 40,
                'reward_coins': 80,
                'reward_xp': 120,
                'icon': '😈',
                'min_wave': 8,
            },
            {
                'name': 'Giant',
                'description': 'Massive creature with devastating power',
                'health': 300,
                'speed': 0.8,
                'damage': 60,
                'reward_coins': 120,
                'reward_xp': 180,
                'icon': '🧟',
                'min_wave': 9,
            },
            {
                'name': 'Ancient Dragon',
                'description': 'Legendary boss - ultimate challenge',
                'health': 500,
                'speed': 1.0,
                'damage': 100,
                'reward_coins': 250,
                'reward_xp': 300,
                'icon': '🐲',
                'min_wave': 12,
            },
        ]

        for enemy_data in enemies:
            EnemyType.objects.get_or_create(
                name=enemy_data['name'],
                defaults=enemy_data
            )

        self.stdout.write(self.style.SUCCESS('Successfully initialized tower defense data'))
