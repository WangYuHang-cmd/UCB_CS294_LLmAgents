-- Users table
CREATE TABLE users (
    user_id VARCHAR(50) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    attack_rating INTEGER DEFAULT 1200,
    defense_rating INTEGER DEFAULT 1200,
    battles_count INTEGER DEFAULT 0,
    last_active TIMESTAMP
);

-- Prompts table
CREATE TABLE prompts (
    prompt_id VARCHAR(100) PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES users(user_id),
    type ENUM('attack', 'defense') NOT NULL,
    code_name VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    rating INTEGER DEFAULT 1200,
    battles_count INTEGER DEFAULT 0,
    wins_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_battle_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    UNIQUE(user_id, type, code_name)
);

-- Battles table
CREATE TABLE battles (
    battle_id SERIAL PRIMARY KEY,
    red_prompt_id VARCHAR(100) REFERENCES prompts(prompt_id),
    blue_prompt_id VARCHAR(100) REFERENCES prompts(prompt_id),
    secret_key VARCHAR(50) NOT NULL,
    state battle_state NOT NULL DEFAULT 'initialized',
    winner ENUM('attack', 'defense') NULL,
    rating_change INTEGER NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    transcript JSONB NULL
);

-- Battle turns table
CREATE TABLE battle_turns (
    turn_id SERIAL PRIMARY KEY,
    battle_id INTEGER REFERENCES battles(battle_id),
    turn_number INTEGER NOT NULL,
    role ENUM('attack', 'defense') NOT NULL,
    content TEXT NOT NULL,
    tokens_used INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_prompts_user ON prompts(user_id);
CREATE INDEX idx_prompts_rating ON prompts(rating DESC);
CREATE INDEX idx_battles_time ON battles(started_at DESC);
CREATE INDEX idx_battles_state ON battles(state);

-- Views
CREATE VIEW leaderboard_players AS
SELECT 
    u.username,
    u.attack_rating,
    u.defense_rating,
    (u.attack_rating + u.defense_rating)/2 as overall_rating,
    u.battles_count,
    COUNT(CASE WHEN b.winner = 'attack' THEN 1 END)::FLOAT / 
        NULLIF(COUNT(*), 0) as win_rate
FROM users u
LEFT JOIN battles b ON b.red_prompt_id LIKE CONCAT(u.user_id, '%')
GROUP BY u.user_id;

CREATE VIEW leaderboard_prompts AS
SELECT 
    p.prompt_id,
    p.type,
    p.rating,
    p.battles_count,
    p.wins_count::FLOAT / NULLIF(p.battles_count, 0) as win_rate,
    p.last_battle_at
FROM prompts p
WHERE p.battles_count >= 10;

-- Triggers
CREATE TRIGGER update_user_ratings
AFTER UPDATE ON battles
FOR EACH ROW
EXECUTE FUNCTION update_user_ratings();

CREATE TRIGGER check_rate_limits
BEFORE INSERT ON battles
FOR EACH ROW
EXECUTE FUNCTION check_rate_limits(); 