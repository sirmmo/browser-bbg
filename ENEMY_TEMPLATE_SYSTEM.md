# Enemy Template System Guide

## Overview

The enemy/monster system in the game is **fully templated**, making it incredibly easy to add new enemy types without modifying any code logic. The `EnemyType` model serves as a template that defines all the properties and behaviors of enemies.

## Enemy Template Model

```python
class EnemyType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    health = models.IntegerField()
    speed = models.FloatField(help_text="Grid units per second")
    damage = models.IntegerField(help_text="Damage to base if reaches end")
    reward_coins = models.IntegerField(default=5)
    reward_xp = models.IntegerField(default=10)
    icon = models.CharField(max_length=50, default='👾')
    min_wave = models.IntegerField(default=1, help_text="First wave this enemy appears")
```

## How It Works

1. **EnemyType** = Template (blueprint for enemy types)
2. **Enemy** = Instance (actual enemy spawned in a wave)

When a wave starts, the system:
- Queries `EnemyType` templates based on wave number
- Creates `Enemy` instances from those templates
- Each `Enemy` inherits stats from its `EnemyType` template

## Current Enemy Types (11 Total)

### Early Game (Wave 1-3)
- **Skeleton** 💀 - Fragile undead (25 HP, 1.8 speed)
- **Goblin** 👺 - Fast rusher (30 HP, 2.0 speed)
- **Orc** 👹 - Balanced warrior (60 HP, 1.5 speed)
- **Wolf** 🐺 - Pack hunter (40 HP, 2.5 speed)

### Mid Game (Wave 4-6)
- **Troll** 🧌 - Heavy tank (120 HP, 1.0 speed)
- **Dark Knight** ⚔️ - High damage (90 HP, 1.3 speed)
- **Wraith** 👻 - Fast spirit (70 HP, 2.2 speed)

### Late Game (Wave 7+)
- **Dragon** 🐉 - Flying boss (250 HP, 1.2 speed)
- **Demon** 😈 - Abyss creature (180 HP, 1.6 speed)
- **Giant** 🧟 - Devastating power (300 HP, 0.8 speed)
- **Ancient Dragon** 🐲 - Legendary boss (500 HP, 1.0 speed)

## Adding New Enemy Types

### Method 1: Via Management Command

Edit `game/management/commands/init_tower_defense.py` and add to the enemies list:

```python
{
    'name': 'Ice Elemental',
    'description': 'Frozen entity that slows towers',
    'health': 150,
    'speed': 1.4,
    'damage': 30,
    'reward_coins': 60,
    'reward_xp': 80,
    'icon': '❄️',
    'min_wave': 6,
},
```

Then run:
```bash
python manage.py init_tower_defense
```

### Method 2: Via Django Admin

1. Start server: `python manage.py runserver`
2. Go to http://localhost:8000/admin
3. Navigate to "Enemy types"
4. Click "Add enemy type"
5. Fill in the template fields:
   - **Name**: Enemy name (e.g., "Vampire")
   - **Description**: What makes this enemy unique
   - **Health**: Hit points (higher = tankier)
   - **Speed**: Movement speed (higher = faster)
   - **Damage**: Base damage if reaches the end
   - **Reward Coins**: Coins awarded on death
   - **Reward XP**: Experience points awarded
   - **Icon**: Emoji for visual representation
   - **Min Wave**: First wave where this enemy appears
6. Click "Save"

### Method 3: Via Python Code

```python
from game.models import EnemyType

EnemyType.objects.create(
    name='Vampire',
    description='Drains life from towers',
    health=200,
    speed=1.5,
    damage=35,
    reward_coins=75,
    reward_xp=100,
    icon='🧛',
    min_wave=8
)
```

## Design Guidelines

### Balancing Stats

**Speed vs Health Trade-off:**
- Fast enemies (2.0+): Lower health (25-50 HP)
- Medium enemies (1.3-1.9): Medium health (60-120 HP)
- Slow enemies (<1.3): High health (120-300 HP)

**Reward Scaling:**
- Coins: Roughly `health / 3` + bonus for difficulty
- XP: Roughly `health / 2` + bonus for difficulty

**Wave Unlocking:**
- Wave 1-3: Basic enemies (HP < 60)
- Wave 4-6: Medium enemies (HP 60-150)
- Wave 7-9: Hard enemies (HP 150-300)
- Wave 10+: Boss enemies (HP 300+)

### Strategic Variety

Create enemies with different roles:
- **Rushers**: High speed, low HP (challenge early defenses)
- **Tanks**: Low speed, high HP (soak up tower damage)
- **Balanced**: Medium speed/HP (all-around threat)
- **Bosses**: High HP/damage, appears rarely

### Example Enemy Concepts

```python
# Swarm enemy - many weak units
{
    'name': 'Rat',
    'description': 'Weak creature that comes in large swarms',
    'health': 15,
    'speed': 2.5,
    'damage': 2,
    'reward_coins': 5,
    'reward_xp': 8,
    'icon': '🐀',
    'min_wave': 1,
}

# Flying enemy - harder to hit
{
    'name': 'Harpy',
    'description': 'Flying creature that bypasses ground obstacles',
    'health': 80,
    'speed': 2.0,
    'damage': 15,
    'reward_coins': 45,
    'reward_xp': 60,
    'icon': '🦅',
    'min_wave': 5,
}

# Regenerating enemy
{
    'name': 'Hydra',
    'description': 'Multi-headed beast with high health',
    'health': 400,
    'speed': 0.9,
    'damage': 75,
    'reward_coins': 200,
    'reward_xp': 250,
    'icon': '🐍',
    'min_wave': 10,
}
```

## API Integration

Enemy templates are automatically available through the API:

```
GET /api/enemies/ - List all enemy instances
  ?wave_id=5 - Filter by wave

Enemy Response:
{
  "id": 42,
  "enemy_type": 3,
  "enemy_detail": {
    "name": "Goblin",
    "icon": "👺",
    "health": 30,
    "speed": 2.0,
    ...
  },
  "current_health": 20,
  "position_x": 4.5,
  "position_y": 2,
  "is_alive": true
}
```

## Wave Spawning Logic

The wave system automatically uses enemy templates:

```python
# From game/views.py - WaveViewSet.start()
enemy_types = EnemyType.objects.filter(min_wave__lte=wave_number)
num_enemies = 5 + (wave_number * 2)

for i in range(num_enemies):
    enemy_type = random.choice(enemy_types)
    Enemy.objects.create(
        wave=wave,
        enemy_type=enemy_type,
        current_health=enemy_type.health,  # Inherits from template
        ...
    )
```

## Future Expansion Ideas

The template system supports easy addition of:
- **Special Abilities**: Add fields like `has_shield`, `can_fly`, `poison_damage`
- **Resistances**: Add `physical_resistance`, `magic_resistance`
- **Size**: Add `size` field for larger enemies that occupy multiple grid cells
- **Loot Tables**: Add specific item drops
- **AI Behaviors**: Add `behavior` field (rush, patrol, boss)

## Summary

✅ **Already Implemented**: Fully templated enemy system
✅ **Easy to Extend**: Add via admin, command, or code
✅ **11 Enemy Types**: Diverse early to late game progression
✅ **Automatic Integration**: Waves use templates automatically
✅ **Strategic Variety**: Speed/health/damage variations

The enemy system requires **zero code changes** to add new types - just create new `EnemyType` templates and they'll automatically appear in waves!
