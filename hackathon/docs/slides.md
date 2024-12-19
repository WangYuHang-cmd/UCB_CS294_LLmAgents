---
title: "Prompt of Troy: A Competitive Prompt Hacking Game"
paginate: true
theme: gaia
_class: lead
marp: true
---

# Prompt of Troy  
**A Competitive Prompt Hacking Game**

Lucas Xu 
Team: Houkui

📧 xianminx@gmail.com

---

## Overview

Prompt of Troy is a prompt attack and defense game in Discord for LLM Agents course Hackathon on safety track 

![](./img/battles.png)
---

## Core Concept

- **Attack Prompts (Red):** Attempt to reveal a secret key.
- **Defense Prompts (Blue):** Safeguard the secret key while maintaining a helpful response.
- **Single-Turn Battles:** One-shot interaction between attack and defense prompts determines the winner.
- **ELO Rating:** Dynamic ranking system to measure prompt effectiveness.

---


## Battle Mechanics
**Flow:**
1. **Setup:** Defender prompt + secret key generated.
2. **Execution:** An execution agent runs Attacker prompt vs. Defender prompt in a single-turn conversation

    ~~~python
        messages = [
            {"role": "system", "content": get_defense_prompt(defense_prompt, secret)},
            {"role": "user", "content": attack_prompt},
        ]
    ~~~

3. **Evaluation:** An eval agent checks the response if the secret key is revealed.

---

## Battle Mechanics

**Outcome:**
- Attack wins if key is found in response.
- Defense wins if key remains hidden.
- Ratings are updated accordingly.

---

## Leaderboard & Rankings

**Leaderboard Categories:**
1. **Attack Rankings (Red)**: Effectiveness at extracting keys.
2. **Defense Rankings (Blue)**: Ability to protect the key.
3. **Player Rankings:** Sum of top attack & defense ratings.

**Key Metrics:**
- Rating (ELO-based)
- Win Rate
- Number of Battles

---


## ELO Rating System

**Rating Principles:**
- **Start:** 1200 rating
- **K-Factor:** 32 (64 for provisional)
- **Provisional:** First 10 battles
- **Bounds:** 100 to 3000

**Formula:**
```
New Rating = Old Rating + K * (Actual - Expected)
Expected = 1 / (1 + 10^((Opponent - Player)/400))
```

---

## Rating Dynamics

- **Stronger vs. Weaker:** Small gains for stronger winner.
- **Upsets:** Low-rated prompt beating a higher-rated prompt gains up to ~32 points.
- **Equal Match:** Winner/loser exchange ~16 points.

**Result:** Ratings evolve to reflect true skill level over time.

---

## Code Overview

**Battle Pseudocode:**
```python
def battle(defense_prompt, attack_prompt, secret):
    messages = [
        {"role": "system", "content": get_defense_prompt(defense_prompt, secret)},
        {"role": "user", "content": attack_prompt},
    ]
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    content = response.choices[0].message.content
    return secret.lower() in content.lower()
```

---

## Discord Integration
User action through Discord Channel "Prompt of Troy"

![](./img/discord.png)

---

## Discord Integration

**Prompt Management:**
- `/prompt create <type> <content>`
- `/prompt list`
- `/prompt delete <id>`

**Battle Management:**
- `/battle start <red> <blue>`
- `/battle status <id>`
- `/try` to test prompts privately


---

## Discord Integration
**Information:**
- `/leaderboard`
- `/stats @player`
- `/battle history`

---

## Web UI Features

- **Leaderboard Page:** Global rankings for players, attacks, defenses.
- **Battle History:** Browse past matches, outcomes, rating changes.
- **Player Profiles:** Detailed stats, win rates, rating evolution.
- **Documentation:** Rules, guidelines, prompt writing best practices.

---


## Leaderboard & Rankings

![](./img/players.png)

---


## Leaderboard by Prompts 

![](./img/prompts.png)

---


## Battle List 

![](./img/battles.png)

---

## Summary & Next Steps

**Summary:**
- **Prompt of Troy:** Gamifies prompt engineering.
- **ELO Ranking:** Reflects prompt skill.
- **Seamless Experience:** Discord + Web UI integration.

**Next Steps:**
- Refine your prompts.
- Challenge top-ranked players.
- Climb the leaderboard!

