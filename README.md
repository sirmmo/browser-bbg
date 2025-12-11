# Base Builder Game with Tower Defense

A fun base-building game where players can construct buildings, gather resources, defend against enemy waves, and optionally play together in parties. Perfect for downtime between sessions!

## Features

### Base Building
- **Single Player**: Build your base, collect resources, and expand your empire
- **Resource Management**: Manage coins, wood, stone, and food
- **Building System**: Place various buildings that generate resources over time
- **Real-time Resource Generation**: Buildings produce resources automatically
- **Leveling System**: Gain experience and level up to unlock new content

### Tower Defense (NEW!)
- **Defensive Towers**: Build and upgrade towers to defend your base
- **Enemy Waves**: Fight off increasingly difficult waves of enemies
- **Tower Upgrades**: Evolve your towers through multiple tiers
  - Physical Path: Arrow → Crossbow → Ballista → Cannon
  - Magic Path: Magic → Wizard → Arcane
- **Enemy Variety**: Face Goblins, Orcs, Trolls, and Dragons
- **Progressive Difficulty**: Enemy waves scale with your progression
- **Rewards**: Earn coins and XP from defeating enemies
- **Strategic Gameplay**: Unlock at level 2, plan tower placement

### Multiplayer
- **Multiplayer Parties**: Create or join parties to play with friends
- **Party Chat**: Communicate with party members
- **Shared Progress Viewing**: See other players' levels and waves survived

## Tech Stack

- **Backend**: Django 4.2 + Django REST Framework
- **Frontend**: Angular 17
- **Database**: SQLite (default, can be configured to PostgreSQL)

## Prerequisites

- Python 3.8+
- Node.js 18+
- npm or yarn

## Installation

### Backend Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run database migrations:
```bash
python manage.py migrate
```

3. Initialize game data (building types):
```bash
python manage.py init_game_data
```

4. Initialize tower defense data (weapons and enemies):
```bash
python manage.py init_tower_defense
```

4. Create a superuser (optional, for admin access):
```bash
python manage.py createsuperuser
```

5. Start the Django development server:
```bash
python manage.py runserver
```

The backend will be available at http://localhost:8000

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the Angular development server:
```bash
npm start
```

The frontend will be available at http://localhost:4200

## How to Play

### Getting Started

1. **Register**: Create a new account at the register page
2. **Login**: Sign in with your credentials
3. **Build Your Base**: 
   - View your resources in the left sidebar
   - Select a building type to place
   - Click on the grid to place your building
   - Buildings take time to construct
4. **Collect Resources**: Click "Collect Resources" to gather what your buildings have produced

### Building Types

- **Gold Mine** 💰: Produces coins over time
- **Lumber Mill** 🪵: Produces wood
- **Stone Quarry** 🪨: Produces stone
- **Farm** 🌾: Produces food
- **Trading Post** 🏪: Advanced building with high coin production

### Tower Defense Mode

Tower defense unlocks at **Level 2** and provides an exciting combat dimension to the game.

#### Tower Types & Upgrades

**Physical Damage Path:**
1. **Arrow Tower** 🏹 (Level 2) - 10 damage, 3 range, 1.0 fire rate
2. **Crossbow Tower** 🏹 (Level 4) - 20 damage, 4 range, 1.2 fire rate
3. **Ballista Tower** 🏹 (Level 7) - 40 damage, 5 range, 0.8 fire rate
4. **Cannon Tower** 💣 (Level 10) - 80 damage, 6 range, 0.5 fire rate

**Magic Damage Path:**
1. **Magic Tower** ✨ (Level 3) - 15 damage, 4 range, 1.5 fire rate
2. **Wizard Tower** 🧙 (Level 6) - 35 damage, 5 range, 1.0 fire rate
3. **Arcane Tower** 🔮 (Level 9) - 70 damage, 7 range, 1.2 fire rate

#### Enemy Types

- **Goblin** 👺 (Wave 1+) - 30 HP, fast, 5 damage, rewards: 10 coins, 15 XP
- **Orc** 👹 (Wave 2+) - 60 HP, medium speed, 10 damage, rewards: 20 coins, 25 XP
- **Troll** 🧌 (Wave 4+) - 120 HP, slow, 20 damage, rewards: 40 coins, 50 XP
- **Dragon** 🐉 (Wave 7+) - 250 HP, boss, 50 damage, rewards: 100 coins, 150 XP

#### How to Play

1. Build resource buildings to gather materials
2. Reach **Level 2** to unlock tower defense
3. Place towers strategically on your grid
4. Click "Start Wave" to spawn enemies
5. Towers automatically attack enemies in range
6. Defeat all enemies to complete the wave
7. Earn coins and XP as rewards
8. Upgrade towers between waves for better performance
9. Higher waves spawn more and stronger enemies
10. Level up to unlock advanced towers

#### Leveling System

- **Level Formula**: Level = floor(XP / 100) + 1
- Defeat enemies to gain XP
- Complete waves for bonus XP (20 * wave number)
- Higher levels unlock better towers and buildings
- Buildings and towers have minimum level requirements

### Multiplayer (Party Mode)

1. Navigate to the **Party** page
2. **Create a Party**: Enter a party name and create
3. **Share the Code**: Share the generated party code with friends
4. **Join a Party**: Enter a party code to join an existing party
5. **Chat**: Use the party chat to communicate
6. **See Progress**: View other members' resource counts

## Game Mechanics

- Buildings cost resources to construct
- Once built, buildings generate resources passively over time
- Resources accumulate until you collect them
- Plan your base layout strategically
- Work together in parties to build complementary economies

## API Endpoints

### Authentication
- `POST /api/register/` - Register new user
- `POST /api/login/` - Login and get JWT token
- `POST /api/token/refresh/` - Refresh JWT token

### Profile
- `GET /api/profile/me/` - Get current player profile
- `POST /api/profile/collect/` - Collect resources from buildings

### Buildings
- `GET /api/building-types/` - List all building types
- `GET /api/buildings/` - List player's buildings
- `POST /api/buildings/` - Create a new building
- `DELETE /api/buildings/{id}/` - Delete a building
- `POST /api/buildings/{id}/check_completion/` - Check if building is complete

### Parties
- `GET /api/parties/` - List active parties
- `POST /api/parties/` - Create a new party
- `POST /api/parties/join/` - Join a party by code
- `POST /api/parties/leave/` - Leave current party
- `GET /api/parties/{id}/members/` - List party members
- `GET /api/parties/{id}/messages/` - Get party messages
- `POST /api/parties/{id}/send_message/` - Send a message to party

### Tower Defense
- `GET /api/weapon-types/` - List all weapon/tower types
- `GET /api/towers/` - List player's towers
- `POST /api/towers/` - Create a new tower
- `POST /api/towers/{id}/upgrade/` - Upgrade a tower
- `DELETE /api/towers/{id}/` - Delete a tower
- `GET /api/waves/` - List player's waves
- `GET /api/waves/current/` - Get current active wave
- `POST /api/waves/start/` - Start a new enemy wave
- `POST /api/waves/{id}/complete/` - Mark wave as complete
- `GET /api/enemies/` - List enemies (filter by wave_id)
- `POST /api/enemies/{id}/damage/` - Apply damage to an enemy

## Development

### Django Admin

Access the Django admin at http://localhost:8000/admin to:
- Manage users and profiles
- Create/edit building types
- View parties and messages
- Monitor game state

### Adding New Buildings

1. Go to Django admin
2. Navigate to "Building types"
3. Add a new building type with:
   - Name and description
   - Resource type it produces
   - Production rate (per minute)
   - Construction costs
   - Build time
   - Icon (emoji)

## Architecture

### Backend
- `game/models.py` - Database models (PlayerProfile, Building, Party, etc.)
- `game/views.py` - API views and business logic
- `game/serializers.py` - DRF serializers for API
- `game/admin.py` - Django admin configuration

### Frontend
- `src/app/services/` - API and authentication services
- `src/app/components/` - Angular components (login, base, party)
- `src/app/interceptors/` - HTTP interceptors for JWT

## Future Enhancements

- Real-time updates using WebSockets
- Building upgrades
- Trade system between players
- Quests and achievements
- Mobile-responsive design improvements
- Player leaderboards
- Defense mechanisms and raids

## License

MIT

## Contributing

Contributions are welcome! Feel free to submit issues and pull requests.
