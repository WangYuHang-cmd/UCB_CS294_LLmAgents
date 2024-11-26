# **Prompt of Troy** Technical Design

## Overview

**Prompt of Troy** is a competitive prompt hacking game where players craft prompts to either attack or defend a secret key. It uses an [ELO rating system](https://en.wikipedia.org/wiki/Elo_rating_system) that reflects your skill in prompt engineering.

## Leaderboard System

The leaderboard shows rankings in three categories:

### Prompt Rankings

#### Attack Prompts (RED)

| Rank | Rating | Prompt ID | Battles | Win Rate |
|------|---------|-----------|----------|-----------|
| 1 | 2100 | @Alice/attack/Trojan_Horse | 45 | 72% |
| 2 | 1950 | @Bob/attack/Mind_Control | 38 | 65% |

#### Defense Prompts (BLUE)

| Rank | Rating | Prompt ID | Battles | Win Rate |
|------|---------|-----------|----------|-----------|
| 1 | 2050 | @Bob/defense/Firewall | 52 | 75% |
| 2 | 1920 | @Alice/defense/Zero_Trust | 41 | 68% |

### Player Rankings

A player's rating is the sum of their highest-rated attack and defense prompts. If a player has no attack or defense prompt, the corresponding rating will be set to the base score of 1200.

| Rank | Player | Overall Rating | Attack Rating | Defense Rating | Battles | Win Rate |
|------|--------|----------------|---------------|----------------|----------|-----------|
| 1 | @Alice | 3700 | 1920 | 1780 | 152 | 68% |
| 2 | @Bob | 3520 | 1690 | 1830 | 98 | 62% |
| 3 | @Charlie | 3360 | 1750 | 1610 | 73 | 55% |

### Rating System

* **Starting Rating**: 1200 for new players and prompts
* **K-factor**: 32 (64 for provisional)
* **Provisional period**: First 10 battles
* **Rating bounds**: 100-3000

Rating changes follow standard ELO formula:

```sh
New Rating = Old Rating + K * (Actual - Expected)
where:
- Actual = 1 for win, 0 for loss
- Expected = 1 / (1 + 10^((Opponent Rating - Player Rating)/400))
- K = 32 (or 64 if provisional)
```

The rating change will range from 0 to 32 points. If a higher-rated player defeats a lower-rated player, they will earn only a small number of points (close to 0). On the other hand, when a lower-rated player defeats a higher-rated player, they will earn the maximum points (close to 32). If two players of equal rating compete, each will gain around 16 points.

## Game Record

Battle history shows matches between attack (red) and defense (blue) prompts.
Each record includes:

| Field | Description |
|-------|-------------|
| Battle ID | Unique identifier for the battle |
| Time | When the battle occurred |
| Red | Attacking prompt ID |
| Blue | Defending prompt ID |
| Outcome | Winner (attack/defense) |
| Rating Change | ELO points gained/lost |

### Battle List

| Battle ID | Time | Red | Blue | Outcome | Rating Change |
|-----------|-----------|-----|------|---------|---------------|
| #1842 | 2024-01-15 13:45 | @Alice/attack/Trojan_Horse | @Bob/defense/ Firewall | Attack | +16/-16 |
| #1841 | 2024-01-15 14:20 | @Bob/attack/Mind_Control | @Charlie/defense/ Zero_Trust | Defense | -24/+24 |
| #1840 | 2024-01-15 15:05 | @Charlie/attack/Data_Leak | @Alice/defense/ Runtime_Guard | Defense | -18/+18 |

## Game Mechanics

### Core Concepts

* **Attack Prompt (Red)**: Try to extract a hidden secret key
* **Defense Prompt (Blue)**: Try to protect the secret key while maintaining functional conversation
* **Battle**: One-on-one matches between attack and defense prompts
* **Rating**: Dynamic ELO-based ratings that reflect prompt effectiveness

### Battle Flow

1. **Setup Phase**
   * Defender submits their defense prompt
   * System generates a random secret key and prepends to defense prompt

2. **Execution Phase**
   * Attacker submits their attack prompt
   * System initiates conversation with LLM
   * Single-turn interaction between attack and defense prompts

3. **Evaluation Phase**
   * System scans response for secret key (case-insensitive)
   * Victory conditions:
     * **Attack** wins if response contains the secret key
     * **Defense** wins if secret key remains protected
   * Ratings updated based on battle outcome

The code flow is as follows:

```python
def battle(defense_prompt, attack_prompt, secret):
    messages = [
        {"role": "system", "content": get_defense_prompt(defense_prompt, secret)},
        {"role": "user", "content": attack_prompt},
    ]
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    content = response.choices[0].message.content
    return secret.lower() in content.lower()
```

### Battle Rules

* Battles are single-turn interactions
* No multi-step conversations allowed
* Maximum prompt length: 2000 characters
* 60-second timeout per battle
* Cooldown: 3 minutes between battles

## Discord Commands

### Prompt Management

```sh
/prompt list [@player]/[type]     # List prompts for a player
/prompt create <type> <content>      # Create new prompt. 
/prompt delete <id>               # Delete a prompt
```

An `id` in the form `@[User]/[type]/[code_name]` will be automatically generated for each prompt. For example:  `@Alice/attack/Mind_Control`,  `@Bob/defense/Firewall`.

### Battle Management

```sh
/battle start <red> <blue>        # Start a battle
/battle status <battle_id>        # Check battle status
```

#### Dry run

Players can dry run to test their prompts before submitting to the system for others to play against.

```sh
/try @Alice/attack/Trojan_Horse [defense prompt]
/try @Alice/defense/Trojan_Horse [attack prompt]
```

If your prompt has been tested successfully over several attacks, you can submit it to the system to make it available for others to challenge:

```sh
/prompt create <type> <content>  # 1. create the prompt
/battle start <red> <blue>   # 2. run the battle

```

### Information

```sh
/leaderboard [player / attack / defense]           # View rankings 
/stats [@player]                                   # View player statistics
/battle history [filter]                           # View battle history
```

### Web UI

A web interface is provided with the following pages:

* Leaderboard - View global rankings and statistics
* Battle History - Browse and replay past battles
* Player Profiles - View detailed stats for individual players
* Documentation - System rules and prompt writing guidelines
