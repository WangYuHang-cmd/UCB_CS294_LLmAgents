# Technical Documentation

## System Architecture

### Core Components

```
hackathon/
├── src/
│   ├── battle.py          # Battle execution and evaluation
│   ├── arena.py           # Game coordination
│   ├── models.py          # Data models
│   ├── repositories.py    # Database access
│   ├── discord_bot.py     # Discord interface
│   └── secret_key_generator.py
├── config/
│   ├── battle_config.yaml # Battle rules
│   └── llm_config.yaml    # LLM settings
├── schema/
│   └── database.sql       # Database structure
└── docs/
    ├── Technical.md       # Implementation details
    └── Design.md          # Game design and rules
```

### Component Interactions

1. **Discord Bot** → **Arena** → **Battle System**
   * Commands received through Discord
   * Arena manages game state
   * Battle system handles execution

2. **Battle System** → **LLM** → **Evaluation**
   * Manages conversation flow
   * Handles LLM interactions
   * Evaluates battle outcomes

3. **Database** ← **Repositories** ← **All Components**
   * Centralized data storage
   * Async database access
   * Transaction management

## Development Setup

### Prerequisites

* PostgreSQL 13+
* Python 3.9+
* Discord.py 2.0+
* OpenAI API access

### Environment Setup

```bash
# Required environment variables
POSTGRES_URL=postgresql://user:pass@localhost:5432/hackathon
OPENAI_API_KEY=sk-...
DISCORD_TOKEN=...

# Installation
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
psql -f schema/database.sql
pytest tests/
```

## Security Implementation

### Rate Limiting

* Redis-based rate limiting implementation
* Rolling window counter per user
* Separate limits for battles and commands

### Authentication & Authorization

* Discord OAuth2 integration
* JWT tokens for API access
* Role-based access control matrix

## Monitoring & Observability

* Battle success/failure rates
* System performance metrics
* User activity patterns
* Rating distribution
* Common attack/defense patterns

### Logging

* Structured JSON logging
* Log levels: INFO, WARNING, ERROR
* Battle audit trails
* Security events

## Database Schema

### Key Tables

* users
* prompts
* battles

### Rating Calculation

The rating system uses an ELO-based algorithm:

```python
def calculate_new_ratings(red_rating, blue_rating, winner):
    K = 32  # Rating adjustment factor
    
    # Calculate expected scores
    exp_red = 1 / (1 + 10 ** ((blue_rating - red_rating) / 400))
    exp_blue = 1 - exp_red
    
    # Actual scores based on winner
    if winner == 'red':
        act_red, act_blue = 1, 0
    elif winner == 'blue':
        act_red, act_blue = 0, 1
    else:  # draw
        act_red = act_blue = 0.5
        
    # Calculate new ratings
    new_red = red_rating + K * (act_red - exp_red)
    new_blue = blue_rating + K * (act_blue - exp_blue)
    
    return round(new_red), round(new_blue)
```

### Leaderboard Queries

```sql
-- Attack leaderboard
SELECT * FROM prompts WHERE type = 'attack' ORDER BY rating DESC;

-- Defense leaderboard
SELECT * FROM prompts WHERE type = 'defense' ORDER BY rating DESC;
```

Player leaderboard is calculated by sorting the `users` table by `rating` in descending order.

```sql
SELECT * FROM users ORDER BY rating DESC;
```

## API Implementation

### REST Endpoints

```sh
GET    /api/v1/battles/{battle_id}
POST   /api/v1/battles/start
POST   /api/v1/battles/dryrun
GET    /api/v1/prompts/{prompt_id}
POST   /api/v1/prompts
GET    /api/v1/leaderboard
```

### Error Handling

* Standard error response format
* HTTP status codes mapping
* Error logging and monitoring
* Rate limit headers

For game design, rules, and user-facing features, please refer to Design.md.
