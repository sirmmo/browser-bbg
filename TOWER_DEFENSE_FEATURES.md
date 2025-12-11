# Tower Defense Features

## Backend Implementation Complete ✅

### Models Added:
1. **PlayerProfile** - Enhanced with level, experience, waves_survived
2. **BuildingType** - Added category field (resource/defense/special) and min_level requirement
3. **WeaponType** - Tower templates with upgrade paths
4. **Tower** - Defense buildings that can be upgraded
5. **EnemyType** - Enemy templates
6. **Wave** - Wave management system
7. **Enemy** - Individual enemy instances

### API Endpoints:
- GET/POST `/api/weapon-types/` - List/create weapon types
- GET/POST `/api/towers/` - List/create towers
- POST `/api/towers/{id}/upgrade/` - Upgrade a tower
- GET/POST `/api/waves/` - List/create waves
- GET `/api/waves/current/` - Get active wave
- POST `/api/waves/start/` - Start new wave
- POST `/api/waves/{id}/complete/` - Complete a wave
- GET `/api/enemies/` - List enemies (filterable by wave)
- POST `/api/enemies/{id}/damage/` - Apply damage to enemy

### Tower Upgrade System:
**Physical Damage Path:**
- Arrow Tower (Lvl 2) → Crossbow Tower (Lvl 4) → Ballista Tower (Lvl 7) → Cannon Tower (Lvl 10)

**Magic Damage Path:**
- Magic Tower (Lvl 3) → Wizard Tower (Lvl 6) → Arcane Tower (Lvl 9)

### Enemy Types:
1. Goblin - Wave 1+ (30 HP, fast)
2. Orc - Wave 2+ (60 HP, medium)
3. Troll - Wave 4+ (120 HP, slow, tanky)
4. Dragon - Wave 7+ (250 HP, boss)

### Leveling System:
- Players earn XP from defeating enemies and completing waves
- Level = floor(XP / 100) + 1
- Higher levels unlock better towers and buildings

## Frontend Implementation Needed:

### 1. Update API Service (`frontend/src/app/services/api.service.ts`):
Add interfaces and methods for:
- WeaponType, Tower, EnemyType, Wave, Enemy
- Tower creation and upgrading
- Wave management
- Enemy tracking

### 2. Update Base Component:
- Display player level and XP bar
- Add tower placement mode (separate from buildings)
- Show tower range indicators
- Tower upgrade UI
- Wave start button
- Enemy display on grid

### 3. Create Defense Component (Optional):
Dedicated tower defense interface with:
- Tower arsenal
- Enemy wave information
- Statistics (kills, damage, waves survived)

### 4. Visual Enhancements:
- Different icons for towers vs buildings
- Enemy animations moving across grid
- Tower attack animations
- Health bars for enemies
- Level-up notifications

## Game Flow:
1. Player builds resource buildings
2. At level 2+, towers become available
3. Player places towers strategically
4. Start wave to spawn enemies
5. Towers automatically attack enemies in range
6. Defeat all enemies to complete wave
7. Earn coins and XP as rewards
8. Upgrade towers between waves
9. Higher waves = more/stronger enemies
10. Level up to unlock better towers

## Balance Notes:
- Resource buildings unlock defense gameplay
- Waves provide alternative resource income
- Tower upgrades are incremental improvements
- Enemy difficulty scales with wave number
- Party members can compare wave progress
