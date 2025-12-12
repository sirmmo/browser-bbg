# Worker Hiring System Guide

## Overview

The Worker Hiring System adds strategic depth by allowing players to hire NPCs that enhance buildings and towers. Workers are **fully templated**, making it easy to add new worker types with different effects and specializations.

## System Architecture

### Template-Based Design

```
WorkerType (Template) → Worker (Instance) → Assignment (Building/Tower)
```

1. **WorkerType** = Blueprint defining costs, effects, and compatibility
2. **Worker** = Individual hired employee with experience and morale
3. **Assignment** = Worker placed in a building or tower to provide bonuses

## Worker Categories

### Production Workers
Boost resource generation in buildings
- **Effects**: Production multiplier (1.5x = +50% resources)
- **Compatible with**: Resource buildings (mines, farms, etc.)
- **Examples**: Miner, Lumberjack, Farmer, Mason

### Defense Specialists
Enhance tower combat capabilities
- **Effects**: Damage bonus, range bonus, fire rate multiplier
- **Compatible with**: Towers only
- **Examples**: Archer, Guard, Marksman, Mage

### Support Staff
Provide utility bonuses
- **Effects**: Build speed, resource efficiency, mixed bonuses
- **Compatible with**: All or specific building types
- **Examples**: Engineer, Merchant, Apprentice

### Elite Workers
Powerful late-game specialists
- **Effects**: Multiple high-value bonuses
- **High Cost**: Expensive but game-changing
- **Examples**: Master Craftsman, General, Archmage

## Worker Types (14 Total)

### Production Category

| Worker | Level | Cost | Upkeep | Production Bonus | Icon |
|--------|-------|------|--------|-----------------|------|
| Farmer | 1 | 60💰 10🌾 | 1🌾 | +60% | 👨‍🌾 |
| Lumberjack | 2 | 80💰 15🌾 | 1🌾 | +40% | 🪓 |
| Miner | 3 | 100💰 20🌾 | 2🌾 | +50% | ⛏️ |
| Mason | 3 | 90💰 18🌾 | 2🌾 | +45% | 🧱 |

### Defense Category

| Worker | Level | Cost | Upkeep | Damage | Range | Fire Rate | Icon |
|--------|-------|------|--------|--------|-------|-----------|------|
| Guard | 3 | 120💰 20🌾 | 2🌾 | +10 | +0 | +30% | 🛡️ |
| Archer | 4 | 150💰 25🌾 | 3🌾 | +15 | +1 | +20% | 🏹 |
| Mage | 6 | 300💰 35🌾 | 3🌾 | +30 | +1 | +25% | 🧙 |
| Marksman | 7 | 250💰 40🌾 | 4🌾 | +25 | +2 | +15% | 🎯 |

### Support Category

| Worker | Level | Cost | Upkeep | Build Speed | Cost Reduction | Icon |
|--------|-------|------|--------|-------------|----------------|------|
| Apprentice | 1 | 50💰 8🌾 | 1🌾 | 1.0x | 0% | 👨‍🎓 |
| Engineer | 5 | 180💰 30🌾 | 2🌾 | 2.0x | 10% | 👷 |
| Merchant | 6 | 200💰 25🌾 | 2🌾 | 1.0x | 15% | 🤵 |

### Elite Category

| Worker | Level | Cost | Upkeep | Effects | Icon |
|--------|-------|------|--------|---------|------|
| Master Craftsman | 10 | 500💰 50🌾 | 5🌾 | 2x Prod, 1.5x Build, 20% Efficiency | 👨‍🔧 |
| General | 12 | 600💰 60🌾 | 6🌾 | +50 Dmg, +3 Range, 1.5x Fire | ⭐ |
| Archmage | 15 | 800💰 70🌾 | 7🌾 | +80 Dmg, +4 Range, 1.6x Fire | 🔮 |

## How Worker Effects Work

### Production Buildings

Workers multiply the base production rate:

```python
# Without worker
Gold Mine: 5 coins/min

# With Miner (1.5x multiplier)
Gold Mine: 5 * 1.5 = 7.5 coins/min (+50%)

# With Master Craftsman (2.0x multiplier)
Gold Mine: 5 * 2.0 = 10 coins/min (+100%)

# With 2 workers stacking
Gold Mine: 5 * (1.0 + 0.5 + 0.4) = 9.5 coins/min
```

### Defense Towers

Workers add flat bonuses and multipliers:

```python
# Arrow Tower base stats
Damage: 10, Range: 3, Fire Rate: 1.0

# With Archer assigned
Damage: 10 + 15 = 25 (+150%)
Range: 3 + 1 = 4 (+33%)
Fire Rate: 1.0 * 1.2 = 1.2 (+20%)

# With General assigned (elite)
Damage: 10 + 50 = 60 (+500%)
Range: 3 + 3 = 6 (+100%)
Fire Rate: 1.0 * 1.5 = 1.5 (+50%)
```

### Worker Experience & Efficiency

Workers improve over time through a progression system:

```python
# Base efficiency
New Worker: 1.0x effectiveness

# With experience
Worker with 500 XP: 1.25x effectiveness
Worker with 1000+ XP: 1.5x effectiveness (max)

# Morale affects performance
High Morale (100): 1.0x multiplier
Low Morale (50): 0.5x multiplier

# Combined effective multiplier
Effective = Efficiency * (Morale / 100)
Example: 1.5 * (100/100) = 1.5x final boost
```

## Building Capacity

Buildings have worker slots:

```python
# BuildingType.worker_capacity (default: 2)
Gold Mine: 2 workers max
  Worker 1 (Miner): +50% production
  Worker 2 (Merchant): +20% production, -15% costs
  Total Bonus: +70% production

# Towers: 1 worker max
Arrow Tower: 1 worker
  Worker (Archer): +15 dmg, +1 range, +20% fire rate
```

## API Endpoints

### Worker Types

```
GET /api/worker-types/
```

Response:
```json
{
  "id": 1,
  "name": "Miner",
  "category": "production",
  "description": "Experienced miner...",
  "cost_coins": 100,
  "cost_food": 20,
  "upkeep_food": 2,
  "production_multiplier": 1.5,
  "damage_bonus": 0,
  "range_bonus": 0,
  "fire_rate_multiplier": 1.0,
  "compatible_building_category": "resource",
  "min_level": 3,
  "icon": "⛏️"
}
```

### Hire Worker

```
POST /api/workers/
Body: { "worker_type": 1 }
```

### List Workers

```
GET /api/workers/
```

Response includes effective multiplier and assignment:
```json
{
  "id": 42,
  "worker_type": 1,
  "worker_detail": { ...worker_type_data... },
  "assignment": {
    "type": "building",
    "id": 5,
    "name": "Gold Mine"
  },
  "experience": 250,
  "efficiency": 1.25,
  "morale": 100,
  "effective_multiplier": 1.25
}
```

### Assign Worker to Building

```
POST /api/workers/{id}/assign_building/
Body: { "building_id": 5 }
```

### Assign Worker to Tower

```
POST /api/workers/{id}/assign_tower/
Body: { "tower_id": 3 }
```

### Unassign Worker

```
POST /api/workers/{id}/unassign/
```

### Add Experience (Testing/Admin)

```
POST /api/workers/{id}/add_experience/
Body: { "amount": 50 }
```

## Strategic Considerations

### Early Game (Level 1-5)
- **Hire**: Farmer, Apprentice, Lumberjack
- **Focus**: Basic production boosts
- **Strategy**: Low-cost workers to jumpstart economy

### Mid Game (Level 6-10)
- **Hire**: Miner, Guard, Merchant, Engineer
- **Focus**: Specialized production + basic defense
- **Strategy**: Balance resource generation and tower defense

### Late Game (Level 11+)
- **Hire**: Marksman, Master Craftsman, General
- **Focus**: Elite specialists
- **Strategy**: Maximum efficiency, prepare for Ancient Dragons

### Endgame (Level 15+)
- **Hire**: Archmage (ultimate power)
- **Focus**: Overwhelming force
- **Strategy**: Dominate high waves with elite workers

## Adding New Worker Types

### Method 1: Via Django Admin

1. Go to http://localhost:8000/admin
2. Click "Worker types" → "Add worker type"
3. Fill in fields:
   - **Name**: Worker name
   - **Category**: production/defense/support/elite
   - **Costs**: Hiring cost (coins/food) and upkeep
   - **Effects**: Multipliers and bonuses
   - **Compatibility**: Which building categories (blank = all)
   - **Min Level**: Required player level
4. Save

### Method 2: Via Management Command

Edit `init_workers.py`, add to worker_types list:

```python
{
    'name': 'Alchemist',
    'description': 'Transforms resources efficiently',
    'category': 'support',
    'cost_coins': 220,
    'cost_food': 30,
    'upkeep_food': 3,
    'production_multiplier': 1.3,
    'resource_efficiency': 0.7,  # 30% cost reduction!
    'compatible_building_category': 'special',
    'min_level': 8,
    'icon': '⚗️',
},
```

Then run:
```bash
python manage.py init_workers
```

### Method 3: Via Python Code

```python
from game.models import WorkerType

WorkerType.objects.create(
    name='Blacksmith',
    description='Forges superior equipment',
    category='support',
    cost_coins=180,
    cost_food=25,
    upkeep_food=2,
    build_speed_multiplier=1.8,
    resource_efficiency=0.85,
    min_level=7,
    icon='🔨'
)
```

## Design Guidelines

### Effect Balancing

**Production Multipliers:**
- Basic: 1.2x - 1.4x (+20-40%)
- Advanced: 1.5x - 1.7x (+50-70%)
- Elite: 2.0x+ (+100%+)

**Defense Bonuses:**
- Basic: +5-10 damage, +0-1 range
- Advanced: +15-30 damage, +1-2 range
- Elite: +50-80 damage, +3-4 range

**Cost Scaling:**
```
Cost Formula: BaselineRelevant File: /home/user/browser-bbg/WORKER_HIRING_SYSTEM.md
 * (EffectPower ^ 1.5)
Upkeep: ~2-5% of hire cost per day
```

**Level Requirements:**
- Levels 1-3: Basic workers
- Levels 4-7: Specialized workers
- Levels 8-12: Advanced workers
- Levels 13+: Elite workers

### Worker Variety Ideas

```python
# Specialized niches
{
    'name': 'Night Watch',
    'description': 'Bonus defense during night waves',
    'category': 'defense',
    'damage_bonus': 20,
    'fire_rate_multiplier': 1.4,
    # Special: Could add time-based bonuses
},

{
    'name': 'Beast Tamer',
    'description': 'Extra effective vs animal enemies',
    'category': 'defense',
    'damage_bonus': 15,
    # Special: Could add enemy-type bonuses
},

{
    'name': 'Quartermaster',
    'description': 'Reduces all resource consumption',
    'category': 'support',
    'upkeep_food': 1,  # Low upkeep
    'resource_efficiency': 0.75,  # 25% reduction
},
```

## Future Enhancements

The template system supports:
- **Personality traits**: Happy, grumpy, efficient
- **Specializations**: Anti-air, anti-armor bonuses
- **Skills/Abilities**: Active or passive special powers
- **Training**: Upgrade workers to higher tiers
- **Synergies**: Bonuses when certain workers work together

## Summary

✅ **Fully Templated**: 14 diverse worker types, easily expandable
✅ **Strategic Depth**: Production vs Defense vs Support choices
✅ **Progressive Unlock**: Level-gated content keeps game fresh
✅ **Stacking Effects**: Multiple workers compound benefits
✅ **Experience System**: Workers improve over time
✅ **Assignment Flexibility**: Move workers between buildings
✅ **Building Synergy**: Right worker in right building = powerful combos
✅ **Elite Options**: Late-game power spikes

Workers transform static buildings into dynamic, customizable systems. A Gold Mine with a Master Craftsman produces 2x resources. An Arrow Tower with a General becomes a devastating defense. Strategic worker placement is key to success!
