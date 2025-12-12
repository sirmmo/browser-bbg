# Material Management System

Comprehensive guide to the material management, technology research, crafting, and trading systems in the base-building game.

## Table of Contents
- [Overview](#overview)
- [Material System](#material-system)
- [Technology System](#technology-system)
- [Crafting System](#crafting-system)
- [Trading System](#trading-system)
- [API Endpoints](#api-endpoints)
- [Game Progression](#game-progression)

---

## Overview

The material management system extends the base-building game with advanced resource management:

- **Materials**: Advanced resources produced by buildings (farms, mines) beyond basic resources (coins, wood, stone, food)
- **Technologies**: Research tree with prerequisites, unlocking bonuses and new content
- **Crafting**: Create items and equipment to enhance buildings and workers
- **Trading**: Player-to-player marketplace for materials and crafted items

### Key Features

✨ **Templated Design**: All systems use template models for easy expansion
📈 **Progressive Unlocking**: Content unlocks based on player level and research
🔄 **Automated Production**: Materials produce automatically over time
⚡ **Effect Stacking**: Multiple bonuses combine for powerful synergies
🤝 **Player Economy**: Full trading system with public and party-only markets

---

## Material System

### Material Categories

#### Raw Materials (Produced by Buildings)
| Material | Building | Rate/min | Value | Icon |
|----------|----------|----------|-------|------|
| Wheat | Farm | 2.0 | 5 | 🌾 |
| Vegetables | Farm | 1.5 | 8 | 🥕 |
| Iron Ore | Mine | 1.0 | 15 | ⛏️ |
| Copper Ore | Mine | 1.2 | 12 | 🟠 |
| Coal | Mine | 1.5 | 10 | ⚫ |
| Gold Ore | Mine | 0.2 | 100 | 💰 |
| Crystal | Mine | 0.1 | 150 | 💎 |

#### Processed Materials (Crafted)
| Material | Description | Value | Used For |
|----------|-------------|-------|----------|
| Iron Bar | Refined iron | 50 | Tools, equipment, construction |
| Copper Bar | Refined copper | 40 | Advanced items, decorations |
| Lumber | Processed wood | 20 | Furniture, tools |
| Cloth | Woven fabric | 30 | Furniture, decorations |

#### Luxury Items
| Material | Description | Value | Usage |
|----------|-------------|-------|-------|
| Fine Wine | Premium beverage | 200 | Trading, high-value commerce |
| Jewelry | Crafted accessories | 300 | Trading, decorations |

### Material Production

Materials are produced automatically by buildings:

```python
# Buildings produce materials based on their type
# Farm produces: Wheat, Vegetables
# Mine produces: Iron Ore, Copper Ore, Coal, Gold Ore, Crystal

# Production calculation
production = base_rate * time_minutes * worker_multiplier * (1 + item_bonus)
```

#### Production Bonuses
- **Workers**: Production workers (Farmer, Miner) provide 40-60% multipliers
- **Items**: Equipped tools (Hoe, Pickaxe) add 15% bonus
- **Technologies**: Research bonuses add 10-25% global multipliers

#### Collection
Materials are collected automatically when players collect resources:

```http
POST /api/profile/collect/
```

Response includes both basic resources and materials:
```json
{
  "coins": 150,
  "wood": 75,
  "stone": 50,
  "food": 30,
  "materials": {
    "Wheat": 45,
    "Iron Ore": 12,
    "Coal": 8
  }
}
```

### PlayerMaterial Model

Player material inventory with automatic stacking:

```python
class PlayerMaterial(models.Model):
    player = ForeignKey(PlayerProfile)
    material_type = ForeignKey(MaterialType)
    quantity = IntegerField(default=0)
    last_updated = DateTimeField(auto_now=True)

    # Maximum stack size from MaterialType.stack_size (default: 1000)
```

---

## Technology System

### Technology Tree

Technologies form a research tree with prerequisites:

```
Basic Farming → Advanced Farming
Mining Techniques → Deep Mining
Efficient Building → Master Architecture
Weapon Training → Advanced Tactics
Trade Routes → Banking System
```

### Technology Categories

#### Agriculture (🚜 🌱)
- **Basic Farming**: +10% farm production | 60s | 100 coins | Level 1
- **Advanced Farming**: +20% farm production | 300s | 500 coins | Level 3
  - Requires: Basic Farming + 50 Wheat

#### Mining (⛏️ 🏔️)
- **Mining Techniques**: +15% mine production | 120s | 200 coins | Level 2
- **Deep Mining**: +25% mine production | 600s | 800 coins | Level 5
  - Requires: Mining Techniques + 30 Iron Ore + 20 Coal

#### Construction (🏗️ 🏛️)
- **Efficient Building**: -10% building costs | 180s | 300 coins | Level 2
- **Master Architecture**: -20% building costs | 900s | 1000 coins | Level 7
  - Requires: Efficient Building + 100 Lumber + 20 Iron Bar

#### Military (⚔️ 🛡️)
- **Weapon Training**: +5 tower damage | 120s | 250 coins | Level 2
- **Advanced Tactics**: +15 tower damage | 480s | 750 coins | Level 5
  - Requires: Weapon Training + 30 Iron Bar

#### Economy (💹 🏦)
- **Trade Routes**: Better trading | 240s | 400 coins | Level 3
- **Banking System**: Wealth management | 600s | 1200 coins | Level 6
  - Requires: Trade Routes

#### Advanced (🔥 🔨)
- **Metallurgy**: Unlocks bar refining | 300s | 500 coins | Level 4
  - Requires: 50 Iron Ore + 50 Coal
- **Craftsmanship**: Unlocks furniture crafting | 360s | 600 coins | Level 4
  - Requires: 50 Lumber

### Research Process

1. **Check Prerequisites**:
   - Player level requirement
   - Previous technology researched (if any)
   - Sufficient coins and materials

2. **Start Research**:
```http
POST /api/technologies/
{
  "technology_type": 5
}
```

3. **Monitor Progress**:
```http
GET /api/technologies/current/
```

Response includes progress percentage:
```json
{
  "id": 12,
  "technology_type": 5,
  "technology_detail": {...},
  "progress": 45,
  "is_researching": true,
  "is_completed": false
}
```

4. **Check Completion**:
```http
POST /api/technologies/{id}/check_completion/
```

### Technology Effects

Technologies provide passive bonuses:

| Effect Type | Field | Example |
|-------------|-------|---------|
| Production Bonus | `production_bonus` | 0.15 = +15% production |
| Cost Reduction | `building_cost_reduction` | 0.1 = -10% costs |
| Damage Bonus | `damage_bonus` | 10 = +10 damage |
| Content Unlock | `unlock_building_type` | "Advanced Farm" |
| Worker Unlock | `unlock_worker_type` | "Engineer" |

---

## Crafting System

### Crafting Recipes

#### Furniture (Comfort Bonus)
| Item | Cost | Time | Materials | Effect | Level |
|------|------|------|-----------|--------|-------|
| Wooden Chair | 20 | 60s | 5 Lumber | +5 morale | 1 |
| Wooden Table | 40 | 120s | 10 Lumber | +10 morale | 2 |
| Comfortable Bed | 80 | 180s | 15 Lumber, 10 Cloth | +20 morale | 3 |

#### Equipment (Production Bonus)
| Item | Cost | Time | Materials | Effect | Level |
|------|------|------|-----------|--------|-------|
| Work Tools | 50 | 120s | 5 Iron Bar, 5 Lumber | +10% production | 2 |
| Advanced Tools | 150 | 300s | 15 Iron Bar, 10 Copper Bar | +25% production | 5 |
| Worker Barracks Extension | 200 | 240s | 30 Lumber, 10 Iron Bar | +1 worker capacity | 4 |

#### Tools (Specific Building Bonus)
| Item | Cost | Time | Materials | Effect | Building | Level |
|------|------|------|-----------|--------|----------|-------|
| Hoe | 60 | 120s | 6 Iron Bar, 4 Lumber | +15% production | Farm | 2 |
| Pickaxe | 80 | 150s | 8 Iron Bar, 5 Lumber | +15% production | Mine | 3 |

#### Decorations (Combined Bonuses)
| Item | Cost | Time | Materials | Effect | Level |
|------|------|------|-----------|--------|-------|
| Painting | 60 | 90s | 5 Cloth | +8 morale | 3 |
| Chandelier | 120 | 180s | 10 Iron Bar, 3 Crystal | +15 morale, +5% production | 5 |

### Crafting Process

1. **Check Requirements**:
   - Player level
   - Required technology researched
   - Required building built (for some items)
   - Sufficient coins and materials

2. **Craft Item**:
```http
POST /api/items/
{
  "recipe": 3
}
```

3. **Equip to Building**:
```http
POST /api/items/{id}/equip/
{
  "building_id": 15
}
```

4. **Unequip**:
```http
POST /api/items/{id}/unequip/
```

### Item Effects

Items equipped to buildings provide bonuses:

```python
# Production bonus from items
def get_item_bonus(building):
    total_bonus = 0.0
    for item in building.equipped_items.all():
        total_bonus += item.recipe.production_bonus
    return total_bonus

# Worker capacity bonus
def get_effective_worker_capacity(building):
    base = building.building_type.worker_capacity
    item_bonus = sum(item.recipe.worker_capacity_bonus
                     for item in building.equipped_items.all())
    return base + item_bonus

# Morale bonus for workers
comfort_bonus = sum(item.recipe.comfort_bonus
                    for item in building.equipped_items.all())
worker_morale += comfort_bonus
```

---

## Trading System

### Trade Offer Types

#### Material Trade
Sell raw or processed materials to other players:
```json
{
  "trade_type": "material",
  "material_offered": 3,
  "material_quantity": 100,
  "price_coins": 1500
}
```

#### Item Trade
Sell crafted items:
```json
{
  "trade_type": "item",
  "item_offered": 5,
  "item_quantity": 2,
  "price_coins": 300
}
```

#### Barter Trade
Trade materials for materials:
```json
{
  "trade_type": "material",
  "material_offered": 3,
  "material_quantity": 50,
  "price_material": 10,
  "price_material_quantity": 5
}
```

### Trading Visibility

1. **Public Offers** (`party_only=false`, `buyer=null`):
   - Visible to all players
   - First come, first served

2. **Party Offers** (`party_only=true`):
   - Only visible to party members
   - Exclusive trading within group

3. **Direct Offers** (`buyer=<player_id>`):
   - Targeted to specific player
   - Private negotiation

### Trading Workflow

#### Create Offer
```http
POST /api/trades/
{
  "trade_type": "material",
  "material_offered": 3,
  "material_quantity": 100,
  "price_coins": 1500,
  "party_only": false
}
```

#### Browse Offers
```http
GET /api/trades/
```

Returns pending offers visible to player:
- Public offers
- Party offers (if in party)
- Direct offers sent to player

#### Accept Trade
```http
POST /api/trades/{id}/accept/
```

Transaction process:
1. Verify buyer has payment (coins/materials)
2. Verify seller still has items
3. Transfer payment to seller
4. Transfer items to buyer
5. Mark trade as `accepted`

#### Cancel Offer
```http
POST /api/trades/{id}/cancel/
```

### Trade Expiration

Trades automatically expire after 7 days:
- Status changes to `expired`
- Items returned to seller
- Removed from marketplace

---

## API Endpoints

### Material Endpoints

```http
# List all material types
GET /api/material-types/

# Get player's material inventory
GET /api/materials/
```

### Technology Endpoints

```http
# List all technologies
GET /api/technology-types/

# Get available technologies for research
GET /api/technology-types/available/

# List player's researched technologies
GET /api/technologies/

# Get completed technologies
GET /api/technologies/completed/

# Get current research
GET /api/technologies/current/

# Start research
POST /api/technologies/
{
  "technology_type": 5
}

# Check if research completed
POST /api/technologies/{id}/check_completion/
```

### Crafting Endpoints

```http
# List all recipes
GET /api/recipes/

# Get available recipes (unlocked)
GET /api/recipes/available/

# List player's items
GET /api/items/

# Craft item
POST /api/items/
{
  "recipe": 3
}

# Equip item to building
POST /api/items/{id}/equip/
{
  "building_id": 15
}

# Unequip item
POST /api/items/{id}/unequip/
```

### Trading Endpoints

```http
# List available trades
GET /api/trades/

# Get player's offers
GET /api/trades/my_offers/

# Get offers sent to player
GET /api/trades/received_offers/

# Create trade offer
POST /api/trades/
{
  "trade_type": "material",
  "material_offered": 3,
  "material_quantity": 100,
  "price_coins": 1500
}

# Accept trade
POST /api/trades/{id}/accept/

# Cancel trade
POST /api/trades/{id}/cancel/
```

---

## Game Progression

### Early Game (Levels 1-3)

**Goals**:
- Build Farm and Mine
- Start material production
- Research Basic Farming or Mining Techniques
- Craft basic furniture for worker morale

**Key Technologies**:
1. Basic Farming (Level 1) - +10% farm production
2. Mining Techniques (Level 2) - +15% mine production
3. Efficient Building (Level 2) - -10% building costs

**Crafting Focus**:
- Wooden Chair (+5 morale)
- Wooden Table (+10 morale)
- Hoe or Pickaxe (+15% production)

### Mid Game (Levels 4-6)

**Goals**:
- Research advanced technologies
- Unlock metallurgy and crafting
- Start trading with other players
- Equip buildings with advanced items

**Key Technologies**:
1. Metallurgy (Level 4) - Unlock bar refining
2. Craftsmanship (Level 4) - Unlock furniture
3. Advanced Farming/Deep Mining (Level 3/5) - Major production boosts
4. Trade Routes (Level 3) - Better trading

**Crafting Focus**:
- Work Tools (+10% production)
- Comfortable Bed (+20 morale)
- Worker Barracks Extension (+1 worker slot)

**Trading Strategy**:
- Sell excess raw materials (Wheat, Iron Ore)
- Buy rare materials (Crystal, Gold Ore)
- Trade processed materials (Iron Bar, Copper Bar)

### Late Game (Levels 7+)

**Goals**:
- Complete technology tree
- Max out building efficiency
- Dominate player market
- Create luxury item economy

**Key Technologies**:
1. Master Architecture (Level 7) - -20% building costs
2. Advanced Tactics (Level 5) - +15 tower damage
3. Banking System (Level 6) - Advanced economy

**Crafting Focus**:
- Advanced Tools (+25% production)
- Chandelier (+15 morale, +5% production)
- Luxury items for high-value trading

**Trading Strategy**:
- Control rare material markets
- Sell high-end crafted items
- Create party-exclusive trading networks
- Bulk trading for maximum profit

---

## Admin Management

### Adding New Materials

```python
# Via Django Admin
MaterialType.objects.create(
    name='Mythril Ore',
    description='Rare magical metal',
    category='rare',
    icon='✨',
    base_value=500,
    produced_by_building='Deep Mine',
    production_rate=0.05,
    is_tradeable=True,
    stack_size=100
)
```

### Adding New Technologies

```python
# Via Django Admin
tech = TechnologyType.objects.create(
    name='Advanced Metallurgy',
    description='Master metal refining',
    category='advanced',
    icon='🔥',
    research_time=1200,
    cost_coins=2000,
    min_level=8,
    prerequisite=TechnologyType.objects.get(name='Metallurgy'),
    production_bonus=0.30
)

# Add material requirements
TechnologyMaterialRequirement.objects.create(
    technology=tech,
    material_type=MaterialType.objects.get(name='Crystal'),
    quantity=10
)
```

### Adding New Recipes

```python
# Via Django Admin
recipe = CraftingRecipe.objects.create(
    name='Master Workbench',
    description='Ultimate crafting station',
    category='equipment',
    icon='🛠️',
    crafting_time=600,
    cost_coins=500,
    required_technology=TechnologyType.objects.get(name='Craftsmanship'),
    min_level=7,
    production_bonus=0.40,
    worker_capacity_bonus=2
)

# Add material requirements
MaterialRequirement.objects.create(
    recipe=recipe,
    material_type=MaterialType.objects.get(name='Iron Bar'),
    quantity=50
)
MaterialRequirement.objects.create(
    recipe=recipe,
    material_type=MaterialType.objects.get(name='Crystal'),
    quantity=5
)
```

---

## Database Schema

### Key Relationships

```
MaterialType (template)
  ├── PlayerMaterial (inventory)
  ├── MaterialRequirement (recipe costs)
  └── TechnologyMaterialRequirement (research costs)

TechnologyType (template)
  ├── PlayerTechnology (research progress)
  ├── prerequisite → TechnologyType (tech tree)
  ├── TechnologyMaterialRequirement (costs)
  └── CraftingRecipe.required_technology (unlocks)

CraftingRecipe (template)
  ├── MaterialRequirement (crafting costs)
  ├── PlayerItem (crafted instances)
  └── required_technology → TechnologyType

PlayerItem (inventory)
  ├── recipe → CraftingRecipe
  └── equipped_to_building → Building

TradeOffer (marketplace)
  ├── seller → PlayerProfile
  ├── buyer → PlayerProfile (nullable)
  ├── material_offered → MaterialType
  ├── item_offered → CraftingRecipe
  └── price_material → MaterialType
```

---

## Performance Considerations

### Material Production

Materials are calculated on collection, not stored per tick:
```python
# Efficient time-based calculation
time_diff_minutes = (now - last_collection).total_seconds() / 60
production = rate * time_diff_minutes * multipliers
```

### Query Optimization

Use `select_related` and `prefetch_related` for complex queries:
```python
# Efficient technology loading
technologies = PlayerTechnology.objects.select_related(
    'technology_type',
    'technology_type__prerequisite'
).prefetch_related(
    'technology_type__material_requirements__material_type'
)

# Efficient crafting query
recipes = CraftingRecipe.objects.select_related(
    'required_technology'
).prefetch_related(
    'material_requirements__material_type'
)
```

### Trade Filtering

Trades are filtered efficiently using Q objects:
```python
from django.db.models import Q

# Efficient marketplace query
visible_trades = TradeOffer.objects.filter(
    Q(party_only=False) |
    Q(party_only=True, seller__party=player.party) |
    Q(buyer=player),
    status='pending'
).select_related('seller', 'buyer', 'material_offered', 'item_offered')
```

---

## Testing

### Initialize Test Data

```bash
python manage.py init_materials
```

Creates:
- 13 material types
- 12 technologies
- 10 crafting recipes

### Test Material Production

```python
# Create test player with buildings
player = PlayerProfile.objects.first()
farm = Building.objects.create(
    player=player,
    building_type=BuildingType.objects.get(name='Farm'),
    is_built=True
)

# Wait 1 minute and collect
time.sleep(60)
resources = player.collect_resources()
# Should include Wheat and Vegetables in materials dict
```

### Test Technology Research

```python
# Start research
tech = TechnologyType.objects.get(name='Basic Farming')
research = PlayerTechnology.objects.create(
    player=player,
    technology_type=tech
)

# Wait for completion
time.sleep(tech.research_time + 1)
completed = research.check_completion()
assert completed == True
```

---

## Future Enhancements

### Potential Additions

1. **Material Conversion**: Convert materials into other materials (e.g., 10 Wheat → 1 Flour)
2. **Quality Tiers**: Common/Rare/Epic materials with different effects
3. **Auction House**: Timed bidding system for rare items
4. **Material Storage**: Warehouse buildings with capacity limits
5. **Recipe Discovery**: Find recipes through exploration or experimentation
6. **Technology Specialization**: Choose tech paths for different bonuses
7. **Crafting Queues**: Queue multiple items for automated crafting
8. **Market Analytics**: Price history and demand tracking
9. **Bulk Trading**: Package deals with multiple items
10. **Guild Trading**: Party-wide material pools and shared inventories

---

## Conclusion

The material management system provides deep economic gameplay with:
- ✅ Automated material production from buildings
- ✅ Progressive technology research tree
- ✅ Meaningful crafting with building enhancements
- ✅ Player-driven economy through trading
- ✅ Full template-based expansion system

All systems are production-ready with complete API endpoints, admin interfaces, and initialization commands. The design supports easy expansion through Django admin or management commands without code changes.
