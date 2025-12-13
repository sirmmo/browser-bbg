# Warehouse, Territorial Expansion & Tick System

This document describes the warehouse storage, territorial expansion, and tick-based time progression systems added to the base-building game.

## Table of Contents

1. [Warehouse System](#warehouse-system)
2. [Territorial Expansion System](#territorial-expansion-system)
3. [Tick-Based Time Progression](#tick-based-time-progression)
4. [API Endpoints](#api-endpoints)
5. [Management Commands](#management-commands)

---

## Warehouse System

### Overview

Warehouses are special buildings that increase your material storage capacity. Without warehouses, players are limited to the base storage capacity (1000 materials). Building warehouses allows you to store more materials for crafting and trading.

### Warehouse Types

Three warehouse types are available, unlocked at different player levels:

| Warehouse Type | Storage Bonus | Size | Cost (Coins/Wood/Stone) | Min Level | Build Time |
|---------------|---------------|------|-------------------------|-----------|------------|
| Small Warehouse | +500 | 2x2 | 200/100/50 | 2 | 3 minutes |
| Medium Warehouse | +1500 | 3x2 | 500/300/200 | 4 | 5 minutes |
| Large Warehouse | +3000 | 3x3 | 1000/600/400 | 7 | 8 minutes |

### Storage Capacity Calculation

Total storage capacity is calculated as:
```
Total Capacity = Base Capacity (1000) + Sum of all built warehouse bonuses
```

Example:
- Base capacity: 1000
- 1x Small Warehouse: +500
- 2x Medium Warehouse: +3000
- **Total: 4500 materials**

### Model Changes

#### BuildingType Model
```python
storage_capacity = models.IntegerField(default=0, help_text="Material storage capacity bonus")
```

#### PlayerProfile Model
```python
material_storage_capacity = models.IntegerField(default=1000, help_text="Total material storage")

def get_total_storage_capacity(self):
    """Calculate total storage capacity including bonuses from buildings"""
    base_capacity = self.material_storage_capacity
    warehouse_bonus = 0
    for building in self.buildings.filter(building_type__name__icontains='Warehouse', is_built=True):
        warehouse_bonus += building.building_type.storage_capacity
    return base_capacity + warehouse_bonus
```

### Usage

1. **Check available warehouse types:**
   ```
   GET /api/building-types/
   ```

2. **Build a warehouse:**
   ```
   POST /api/buildings/
   {
     "building_type": 15,  // Warehouse type ID
     "position_x": 5,
     "position_y": 5
   }
   ```

3. **View total storage capacity:**
   ```
   GET /api/profile/me/
   ```
   Response includes:
   ```json
   {
     "material_storage_capacity": 1000,
     "total_storage_capacity": 2500  // Includes warehouse bonuses
   }
   ```

---

## Territorial Expansion System

### Overview

Players start with a 10x10 base grid. As you progress, you can purchase territorial expansions to increase your building area. Maximum territory size is 20x20.

### Expansion Types

- **Horizontal Expansion**: Increases grid width (grid_size_x) by 2
- **Vertical Expansion**: Increases grid height (grid_size_y) by 2
- **Full Expansion**: Increases both width and height by 2

### Expansion Cost

Costs scale exponentially based on current territory size:

```python
base_cost = 500
multiplier = (current_size - 10) / 2 + 1

expansion_cost = {
    'coins': int(base_cost * multiplier),
    'wood': int(200 * multiplier),
    'stone': int(200 * multiplier)
}
```

**Example Costs:**

| Current Size | Multiplier | Cost (Coins/Wood/Stone) |
|-------------|------------|-------------------------|
| 10x10 | 1.0 | 500/200/200 |
| 12x12 | 2.0 | 1000/400/400 |
| 14x14 | 3.0 | 1500/600/600 |
| 16x16 | 4.0 | 2000/800/800 |
| 18x18 | 5.0 | 2500/1000/1000 |
| 20x20 | — | Max size reached |

### Model: TerritorialExpansion

Tracks all territorial expansion purchases:

```python
class TerritorialExpansion(models.Model):
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name='expansions')
    expansion_type = models.CharField(max_length=20, choices=[
        ('horizontal', 'Horizontal Expansion'),
        ('vertical', 'Vertical Expansion'),
        ('both', 'Full Expansion')
    ])
    cost_coins = models.IntegerField()
    cost_wood = models.IntegerField(default=0)
    cost_stone = models.IntegerField(default=0)
    size_increase = models.IntegerField(default=2, help_text="Grid size increase")
    purchased_at = models.DateTimeField(auto_now_add=True)
```

### Usage

1. **Check current territory size:**
   ```
   GET /api/profile/me/
   ```
   Response includes:
   ```json
   {
     "grid_size_x": 10,
     "grid_size_y": 10,
     "territory_size": {
       "width": 10,
       "height": 10,
       "total": 100
     },
     "can_expand": true
   }
   ```

2. **Get expansion cost:**
   ```
   GET /api/expansions/cost/?type=both
   ```
   Response:
   ```json
   {
     "expansion_type": "both",
     "current_size": {"x": 10, "y": 10},
     "max_size": 20,
     "cost": {
       "coins": 500,
       "wood": 200,
       "stone": 200
     }
   }
   ```

3. **Purchase expansion:**
   ```
   POST /api/expansions/purchase/
   {
     "expansion_type": "both"
   }
   ```
   Response:
   ```json
   {
     "message": "Both expansion purchased successfully",
     "expansion": { ... },
     "new_size": {"x": 12, "y": 12},
     "resources": {
       "coins": 1500,
       "wood": 800,
       "stone": 300
     }
   }
   ```

4. **View expansion history:**
   ```
   GET /api/expansions/
   ```

---

## Tick-Based Time Progression

### Overview

The tick system provides server-side time progression for all time-based events in the game. A "tick" represents a discrete time step where the game processes:

- Building completion checks
- Research completion checks
- Resource collection
- Player progression

### How It Works

1. A cron job or scheduled task runs the `process_tick` management command periodically (e.g., every 1 minute)
2. Each tick creates a new `GameTick` record with an incremented tick number
3. The tick processor iterates through all players and processes time-based events
4. Statistics are recorded for monitoring

### Model: GameTick

```python
class GameTick(models.Model):
    tick_number = models.IntegerField(unique=True)
    processed_at = models.DateTimeField(auto_now_add=True)
    players_processed = models.IntegerField(default=0)
    buildings_completed = models.IntegerField(default=0)
    researches_completed = models.IntegerField(default=0)
    resources_collected = models.IntegerField(default=0)

    @staticmethod
    def get_current_tick():
        """Get the latest tick number"""
        latest = GameTick.objects.first()
        return latest.tick_number if latest else 0

    @staticmethod
    def create_tick():
        """Create a new game tick"""
        current = GameTick.get_current_tick()
        return GameTick.objects.create(tick_number=current + 1)

    def process_tick(self):
        """Process all time-based game events for this tick"""
        # Processes buildings, research, etc.
        # Returns statistics
```

### PlayerProfile Changes

```python
last_tick = models.DateTimeField(default=timezone.now, help_text="Last game tick processed")
```

This tracks when the player was last processed by a tick, useful for determining resource accumulation and other time-based calculations.

### Tick Processing

The tick processor:

1. **Building Completion**: Checks if any buildings have finished construction
2. **Research Completion**: Checks if any technologies have been researched
3. **Resource Collection**: Could be extended to auto-collect resources based on production rates
4. **Player Updates**: Updates each player's `last_tick` timestamp

### Usage

Ticks are typically processed automatically by a cron job, but can also be triggered manually:

1. **Get current tick number:**
   ```
   GET /api/ticks/current/
   ```
   Response:
   ```json
   {
     "tick_number": 1542
   }
   ```

2. **Get latest tick details:**
   ```
   GET /api/ticks/latest/
   ```
   Response:
   ```json
   {
     "id": 1542,
     "tick_number": 1542,
     "processed_at": "2025-12-13T10:30:00Z",
     "players_processed": 15,
     "buildings_completed": 3,
     "researches_completed": 2,
     "resources_collected": 0
   }
   ```

3. **View tick history:**
   ```
   GET /api/ticks/
   ```

---

## API Endpoints

### Warehouse Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/building-types/` | List all building types (includes warehouses) |
| GET | `/api/buildings/` | List player's buildings |
| POST | `/api/buildings/` | Build a new warehouse |
| DELETE | `/api/buildings/{id}/` | Remove a warehouse |

### Territorial Expansion Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/profile/me/` | Get player profile with territory info |
| GET | `/api/expansions/` | List player's expansion history |
| GET | `/api/expansions/cost/?type={type}` | Get cost for next expansion |
| POST | `/api/expansions/purchase/` | Purchase territorial expansion |

**Purchase Request Body:**
```json
{
  "expansion_type": "horizontal" | "vertical" | "both"
}
```

### Game Tick Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/ticks/` | List tick history (paginated) |
| GET | `/api/ticks/{id}/` | Get specific tick details |
| GET | `/api/ticks/current/` | Get current tick number |
| GET | `/api/ticks/latest/` | Get latest tick details |

---

## Management Commands

### Initialize Warehouses

Creates the three warehouse building types in the database:

```bash
python manage.py init_warehouses
```

This should be run once during initial setup or after migrations.

### Process Game Tick

Manually trigger a game tick:

```bash
python manage.py process_tick
```

Output:
```
Processing game tick...
Tick #1543 processed successfully!
  Players processed: 15
  Buildings completed: 3
  Researches completed: 2
  Resources collected: 0
```

For continuous/scheduled processing:

```bash
python manage.py process_tick --continuous
```

### Setting Up Automated Tick Processing

#### Using Cron (Linux/Mac)

Edit crontab:
```bash
crontab -e
```

Add entry to run every minute:
```
* * * * * cd /path/to/browser-bbg && /path/to/venv/bin/python manage.py process_tick
```

Or every 5 minutes:
```
*/5 * * * * cd /path/to/browser-bbg && /path/to/venv/bin/python manage.py process_tick
```

#### Using Django Celery (Recommended for Production)

Install dependencies:
```bash
pip install celery redis
```

Create periodic task in `celery.py`:
```python
from celery import Celery
from celery.schedules import crontab

app = Celery('browser_bbg')

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Run every minute
    sender.add_periodic_task(60.0, process_game_tick.s(), name='process tick every minute')

@app.task
def process_game_tick():
    from game.models import GameTick
    tick = GameTick.create_tick()
    tick.process_tick()
```

---

## Database Schema Changes

### New Fields

**PlayerProfile:**
- `grid_size_x` (IntegerField, default=10)
- `grid_size_y` (IntegerField, default=10)
- `material_storage_capacity` (IntegerField, default=1000)
- `last_tick` (DateTimeField, default=timezone.now)

**BuildingType:**
- `storage_capacity` (IntegerField, default=0)

### New Models

**TerritorialExpansion:**
- `player` (ForeignKey → PlayerProfile)
- `expansion_type` (CharField: horizontal/vertical/both)
- `cost_coins` (IntegerField)
- `cost_wood` (IntegerField)
- `cost_stone` (IntegerField)
- `size_increase` (IntegerField, default=2)
- `purchased_at` (DateTimeField)

**GameTick:**
- `tick_number` (IntegerField, unique)
- `processed_at` (DateTimeField)
- `players_processed` (IntegerField)
- `buildings_completed` (IntegerField)
- `researches_completed` (IntegerField)
- `resources_collected` (IntegerField)

### Migration

Apply migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Frontend Integration

### Displaying Territory Size

Update the base component to show current territory:

```typescript
// In base.component.ts
gridSizeX: number = 10;
gridSizeY: number = 10;

loadProfile() {
  this.apiService.getProfile().subscribe(profile => {
    this.profile = profile;
    this.gridSizeX = profile.grid_size_x;
    this.gridSizeY = profile.grid_size_y;
    // Update grid rendering...
  });
}
```

### Displaying Storage Capacity

```typescript
// In base.component.html or resource display
<div class="storage-info">
  Materials: {{ getTotalMaterials() }} / {{ profile.total_storage_capacity }}
  <div class="progress-bar">
    <div class="progress" [style.width.%]="getStoragePercentage()"></div>
  </div>
</div>
```

### Expansion Purchase UI

```typescript
// In api.service.ts
getExpansionCost(type: string): Observable<any> {
  return this.http.get(`${this.apiUrl}/expansions/cost/?type=${type}`);
}

purchaseExpansion(type: string): Observable<any> {
  return this.http.post(`${this.apiUrl}/expansions/purchase/`, { expansion_type: type });
}

// In component
purchaseExpansion(type: string) {
  this.apiService.getExpansionCost(type).subscribe(costInfo => {
    if (confirm(`Purchase ${type} expansion for ${costInfo.cost.coins} coins?`)) {
      this.apiService.purchaseExpansion(type).subscribe(
        result => {
          alert(result.message);
          this.loadProfile(); // Refresh to show new grid size
        },
        error => alert(error.error.error)
      );
    }
  });
}
```

---

## Testing

### Test Warehouse System

1. Create a player and verify base storage is 1000
2. Build a small warehouse
3. Wait for completion (or use tick system)
4. Verify total storage increases to 1500
5. Build multiple warehouses and verify cumulative bonuses

### Test Territorial Expansion

1. Create a player with 10x10 grid
2. Get expansion cost (should be 500/200/200 for first expansion)
3. Give player enough resources
4. Purchase "both" expansion
5. Verify grid size increases to 12x12
6. Verify costs increase for next expansion
7. Continue until 20x20 max size
8. Verify cannot expand beyond 20x20

### Test Tick System

1. Start a building with 3 minute build time
2. Run `python manage.py process_tick`
3. Verify building is still not complete
4. Wait 3 minutes
5. Run `python manage.py process_tick`
6. Verify building is now complete
7. Check tick statistics are recorded correctly

---

## Future Enhancements

### Warehouse System
- Specialized warehouses for specific material types
- Warehouse upgrades to increase capacity
- Warehouse workers to boost efficiency
- Refrigerated storage for food preservation

### Territorial Expansion
- Different terrain types with varying costs
- Special expansion events or discounts
- Territory quality/fertility ratings
- Shared territory for parties

### Tick System
- Tick-based resource generation
- Tick-based worker production bonuses
- Energy/stamina system that regenerates per tick
- Event system triggered by specific tick numbers
- Seasonal changes based on tick count
- Tick speed modifiers for VIP players

---

## Troubleshooting

### Storage Capacity Not Updating

**Issue:** Built warehouse but storage capacity doesn't increase

**Solutions:**
1. Verify warehouse is marked as `is_built=True`
2. Check `building_type.storage_capacity` is set correctly
3. Refresh player profile from API
4. Run process_tick to complete the building

### Expansion Purchase Fails

**Issue:** Expansion purchase returns validation error

**Common Causes:**
1. Insufficient resources (coins, wood, stone)
2. Already at maximum size (20x20)
3. Invalid expansion type

**Debug:**
```bash
# Check player resources
GET /api/profile/me/

# Check expansion cost
GET /api/expansions/cost/?type=both
```

### Ticks Not Processing

**Issue:** Buildings never complete, research stalls

**Solutions:**
1. Verify cron job is running: `crontab -l`
2. Check cron logs for errors
3. Manually run `python manage.py process_tick`
4. Check Django logs for exceptions
5. Verify database connectivity

---

## Conclusion

The warehouse, territorial expansion, and tick systems add strategic depth to the base-building game:

- **Warehouses** solve the storage limitation problem and encourage building optimization
- **Territorial Expansion** provides a resource sink and progression path
- **Tick System** enables server-side time progression and ensures fair gameplay

These systems work together to create a more engaging and balanced gameplay experience.
