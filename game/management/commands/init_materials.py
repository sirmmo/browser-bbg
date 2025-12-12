from django.core.management.base import BaseCommand
from game.models import (
    MaterialType, TechnologyType, TechnologyMaterialRequirement,
    CraftingRecipe, MaterialRequirement
)


class Command(BaseCommand):
    help = 'Initialize material types, technologies, and crafting recipes'

    def handle(self, *args, **kwargs):
        self.stdout.write('Initializing materials, technologies, and recipes...')

        # Create Materials
        materials_created = self.create_materials()
        self.stdout.write(f'Created {materials_created} material types')

        # Create Technologies
        techs_created = self.create_technologies()
        self.stdout.write(f'Created {techs_created} technologies')

        # Create Crafting Recipes
        recipes_created = self.create_recipes()
        self.stdout.write(f'Created {recipes_created} crafting recipes')

        self.stdout.write(self.style.SUCCESS('Successfully initialized material management system'))

    def create_materials(self):
        """Create material types"""
        materials = [
            # Raw Materials (from Farm)
            {
                'name': 'Wheat',
                'description': 'Basic grain crop used for food and crafting',
                'category': 'raw',
                'icon': '🌾',
                'base_value': 5,
                'produced_by_building': 'Farm',
                'production_rate': 2.0,  # per minute
            },
            {
                'name': 'Vegetables',
                'description': 'Fresh vegetables from the farm',
                'category': 'raw',
                'icon': '🥕',
                'base_value': 8,
                'produced_by_building': 'Farm',
                'production_rate': 1.5,
            },
            # Raw Materials (from Mine)
            {
                'name': 'Iron Ore',
                'description': 'Raw iron extracted from the mine',
                'category': 'raw',
                'icon': '⛏️',
                'base_value': 15,
                'produced_by_building': 'Mine',
                'production_rate': 1.0,
            },
            {
                'name': 'Copper Ore',
                'description': 'Copper ore for tools and crafting',
                'category': 'raw',
                'icon': '🟠',
                'base_value': 12,
                'produced_by_building': 'Mine',
                'production_rate': 1.2,
            },
            {
                'name': 'Coal',
                'description': 'Fuel for forges and industry',
                'category': 'raw',
                'icon': '⚫',
                'base_value': 10,
                'produced_by_building': 'Mine',
                'production_rate': 1.5,
            },
            # Processed Materials
            {
                'name': 'Iron Bar',
                'description': 'Refined iron ready for crafting',
                'category': 'processed',
                'icon': '⚙️',
                'base_value': 50,
                'is_tradeable': True,
            },
            {
                'name': 'Copper Bar',
                'description': 'Refined copper for advanced items',
                'category': 'processed',
                'icon': '🔩',
                'base_value': 40,
                'is_tradeable': True,
            },
            {
                'name': 'Lumber',
                'description': 'Processed wood planks',
                'category': 'processed',
                'icon': '🪵',
                'base_value': 20,
                'is_tradeable': True,
            },
            {
                'name': 'Cloth',
                'description': 'Woven fabric for furniture',
                'category': 'processed',
                'icon': '🧵',
                'base_value': 30,
                'is_tradeable': True,
            },
            # Rare Materials
            {
                'name': 'Gold Ore',
                'description': 'Precious gold ore',
                'category': 'rare',
                'icon': '💰',
                'base_value': 100,
                'produced_by_building': 'Mine',
                'production_rate': 0.2,
            },
            {
                'name': 'Crystal',
                'description': 'Magical crystals with special properties',
                'category': 'rare',
                'icon': '💎',
                'base_value': 150,
                'produced_by_building': 'Mine',
                'production_rate': 0.1,
            },
            # Luxury Items
            {
                'name': 'Fine Wine',
                'description': 'Premium wine for luxury',
                'category': 'luxury',
                'icon': '🍷',
                'base_value': 200,
                'is_tradeable': True,
            },
            {
                'name': 'Jewelry',
                'description': 'Crafted decorative items',
                'category': 'luxury',
                'icon': '📿',
                'base_value': 300,
                'is_tradeable': True,
            },
        ]

        count = 0
        for mat_data in materials:
            _, created = MaterialType.objects.get_or_create(
                name=mat_data['name'],
                defaults=mat_data
            )
            if created:
                count += 1

        return count

    def create_technologies(self):
        """Create technology types"""
        technologies = [
            # Agriculture Technologies
            {
                'name': 'Basic Farming',
                'description': 'Learn efficient farming techniques. +10% production in farms.',
                'category': 'agriculture',
                'icon': '🚜',
                'research_time': 60,  # 1 minute for testing
                'cost_coins': 100,
                'min_level': 1,
                'production_bonus': 0.1,
            },
            {
                'name': 'Advanced Farming',
                'description': 'Master advanced crop rotation and irrigation. +20% production in farms.',
                'category': 'agriculture',
                'icon': '🌱',
                'research_time': 300,
                'cost_coins': 500,
                'min_level': 3,
                'production_bonus': 0.2,
                'prerequisite_name': 'Basic Farming',
            },
            # Mining Technologies
            {
                'name': 'Mining Techniques',
                'description': 'Improve mining efficiency. +15% production in mines.',
                'category': 'mining',
                'icon': '⛏️',
                'research_time': 120,
                'cost_coins': 200,
                'min_level': 2,
                'production_bonus': 0.15,
            },
            {
                'name': 'Deep Mining',
                'description': 'Access deeper ore veins. +25% production in mines.',
                'category': 'mining',
                'icon': '🏔️',
                'research_time': 600,
                'cost_coins': 800,
                'min_level': 5,
                'production_bonus': 0.25,
                'prerequisite_name': 'Mining Techniques',
            },
            # Construction Technologies
            {
                'name': 'Efficient Building',
                'description': 'Reduce building costs by 10%.',
                'category': 'construction',
                'icon': '🏗️',
                'research_time': 180,
                'cost_coins': 300,
                'min_level': 2,
                'building_cost_reduction': 0.1,
            },
            {
                'name': 'Master Architecture',
                'description': 'Advanced building techniques. Reduce costs by 20%.',
                'category': 'construction',
                'icon': '🏛️',
                'research_time': 900,
                'cost_coins': 1000,
                'min_level': 7,
                'building_cost_reduction': 0.2,
                'prerequisite_name': 'Efficient Building',
            },
            # Military Technologies
            {
                'name': 'Weapon Training',
                'description': 'Basic weapon training. +5 damage to all towers.',
                'category': 'military',
                'icon': '⚔️',
                'research_time': 120,
                'cost_coins': 250,
                'min_level': 2,
                'damage_bonus': 5,
            },
            {
                'name': 'Advanced Tactics',
                'description': 'Master combat strategies. +15 damage to all towers.',
                'category': 'military',
                'icon': '🛡️',
                'research_time': 480,
                'cost_coins': 750,
                'min_level': 5,
                'damage_bonus': 15,
                'prerequisite_name': 'Weapon Training',
            },
            # Economy Technologies
            {
                'name': 'Trade Routes',
                'description': 'Establish trade networks for better prices.',
                'category': 'economy',
                'icon': '💹',
                'research_time': 240,
                'cost_coins': 400,
                'min_level': 3,
            },
            {
                'name': 'Banking System',
                'description': 'Create a banking system for wealth management.',
                'category': 'economy',
                'icon': '🏦',
                'research_time': 600,
                'cost_coins': 1200,
                'min_level': 6,
                'prerequisite_name': 'Trade Routes',
            },
            # Advanced Technologies
            {
                'name': 'Metallurgy',
                'description': 'Learn to refine ores into bars. Unlocks advanced crafting.',
                'category': 'advanced',
                'icon': '🔥',
                'research_time': 300,
                'cost_coins': 500,
                'min_level': 4,
            },
            {
                'name': 'Craftsmanship',
                'description': 'Master crafting techniques. Unlocks furniture and tools.',
                'category': 'advanced',
                'icon': '🔨',
                'research_time': 360,
                'cost_coins': 600,
                'min_level': 4,
            },
        ]

        count = 0
        # First pass: create all technologies without prerequisites
        for tech_data in technologies:
            prereq_name = tech_data.pop('prerequisite_name', None)
            tech, created = TechnologyType.objects.get_or_create(
                name=tech_data['name'],
                defaults=tech_data
            )
            if created:
                count += 1

        # Second pass: set prerequisites
        for tech_data in technologies:
            if 'prerequisite_name' in tech_data:
                tech = TechnologyType.objects.get(name=tech_data['name'])
                prereq = TechnologyType.objects.get(name=tech_data['prerequisite_name'])
                tech.prerequisite = prereq
                tech.save()

        # Add material requirements for some technologies
        self.add_tech_material_requirements()

        return count

    def add_tech_material_requirements(self):
        """Add material requirements to technologies"""
        requirements = [
            ('Advanced Farming', 'Wheat', 50),
            ('Deep Mining', 'Iron Ore', 30),
            ('Deep Mining', 'Coal', 20),
            ('Master Architecture', 'Lumber', 100),
            ('Master Architecture', 'Iron Bar', 20),
            ('Advanced Tactics', 'Iron Bar', 30),
            ('Metallurgy', 'Iron Ore', 50),
            ('Metallurgy', 'Coal', 50),
            ('Craftsmanship', 'Lumber', 50),
        ]

        for tech_name, mat_name, quantity in requirements:
            try:
                tech = TechnologyType.objects.get(name=tech_name)
                material = MaterialType.objects.get(name=mat_name)
                TechnologyMaterialRequirement.objects.get_or_create(
                    technology=tech,
                    material_type=material,
                    defaults={'quantity': quantity}
                )
            except (TechnologyType.DoesNotExist, MaterialType.DoesNotExist):
                pass

    def create_recipes(self):
        """Create crafting recipes"""
        recipes = [
            # Furniture
            {
                'name': 'Wooden Chair',
                'description': 'A simple wooden chair. +5 worker morale.',
                'category': 'furniture',
                'icon': '🪑',
                'crafting_time': 60,
                'cost_coins': 20,
                'comfort_bonus': 5,
                'min_level': 1,
                'required_technology_name': 'Craftsmanship',
                'materials': [('Lumber', 5)],
            },
            {
                'name': 'Wooden Table',
                'description': 'A sturdy table. +10 worker morale.',
                'category': 'furniture',
                'icon': '🪑',
                'crafting_time': 120,
                'cost_coins': 40,
                'comfort_bonus': 10,
                'min_level': 2,
                'required_technology_name': 'Craftsmanship',
                'materials': [('Lumber', 10)],
            },
            {
                'name': 'Comfortable Bed',
                'description': 'A comfortable bed for workers. +20 morale.',
                'category': 'furniture',
                'icon': '🛏️',
                'crafting_time': 180,
                'cost_coins': 80,
                'comfort_bonus': 20,
                'min_level': 3,
                'required_technology_name': 'Craftsmanship',
                'materials': [('Lumber', 15), ('Cloth', 10)],
            },
            # Equipment
            {
                'name': 'Work Tools',
                'description': 'Basic tools. +10% production for building.',
                'category': 'equipment',
                'icon': '🔧',
                'crafting_time': 120,
                'cost_coins': 50,
                'production_bonus': 0.1,
                'min_level': 2,
                'required_technology_name': 'Metallurgy',
                'materials': [('Iron Bar', 5), ('Lumber', 5)],
            },
            {
                'name': 'Advanced Tools',
                'description': 'High-quality tools. +25% production.',
                'category': 'equipment',
                'icon': '⚒️',
                'crafting_time': 300,
                'cost_coins': 150,
                'production_bonus': 0.25,
                'min_level': 5,
                'required_technology_name': 'Metallurgy',
                'materials': [('Iron Bar', 15), ('Copper Bar', 10)],
            },
            {
                'name': 'Worker Barracks Extension',
                'description': 'Adds space for 1 more worker in building.',
                'category': 'equipment',
                'icon': '🏠',
                'crafting_time': 240,
                'cost_coins': 200,
                'worker_capacity_bonus': 1,
                'min_level': 4,
                'required_technology_name': 'Master Architecture',
                'materials': [('Lumber', 30), ('Iron Bar', 10)],
            },
            # Decoration
            {
                'name': 'Painting',
                'description': 'A beautiful painting. +8 morale.',
                'category': 'decoration',
                'icon': '🖼️',
                'crafting_time': 90,
                'cost_coins': 60,
                'comfort_bonus': 8,
                'min_level': 3,
                'materials': [('Cloth', 5)],
            },
            {
                'name': 'Chandelier',
                'description': 'Elegant lighting. +15 morale, +5% production.',
                'category': 'decoration',
                'icon': '💡',
                'crafting_time': 180,
                'cost_coins': 120,
                'comfort_bonus': 15,
                'production_bonus': 0.05,
                'min_level': 5,
                'required_technology_name': 'Craftsmanship',
                'materials': [('Iron Bar', 10), ('Crystal', 3)],
            },
            # Tools
            {
                'name': 'Pickaxe',
                'description': 'Mining pickaxe. +15% production for mines.',
                'category': 'tool',
                'icon': '⛏️',
                'crafting_time': 150,
                'cost_coins': 80,
                'production_bonus': 0.15,
                'min_level': 3,
                'required_building': 'Mine',
                'required_technology_name': 'Metallurgy',
                'materials': [('Iron Bar', 8), ('Lumber', 5)],
            },
            {
                'name': 'Hoe',
                'description': 'Farming tool. +15% production for farms.',
                'category': 'tool',
                'icon': '🧑‍🌾',
                'crafting_time': 120,
                'cost_coins': 60,
                'production_bonus': 0.15,
                'min_level': 2,
                'required_building': 'Farm',
                'required_technology_name': 'Metallurgy',
                'materials': [('Iron Bar', 6), ('Lumber', 4)],
            },
        ]

        count = 0
        for recipe_data in recipes:
            materials = recipe_data.pop('materials', [])
            tech_name = recipe_data.pop('required_technology_name', None)

            # Get technology if specified
            tech = None
            if tech_name:
                try:
                    tech = TechnologyType.objects.get(name=tech_name)
                    recipe_data['required_technology'] = tech
                except TechnologyType.DoesNotExist:
                    pass

            recipe, created = CraftingRecipe.objects.get_or_create(
                name=recipe_data['name'],
                defaults=recipe_data
            )
            if created:
                count += 1

                # Add material requirements
                for mat_name, quantity in materials:
                    try:
                        material = MaterialType.objects.get(name=mat_name)
                        MaterialRequirement.objects.get_or_create(
                            recipe=recipe,
                            material_type=material,
                            defaults={'quantity': quantity}
                        )
                    except MaterialType.DoesNotExist:
                        pass

        return count
