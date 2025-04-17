# Game Architecture

## Component Overview

![Overview](https://kroki.io/mermaid/svg/eNptkk1PwzAMhv_KKaeB1K0wKJN22mGH3ZB23QlVIXWzCFK7KkmL-O_YabcWxnqJ_Tx-_TpJHQrLDRQO9w4bHDHwoKHxHIQUGNBH36LghvANl_oVJSEXgo7pGBuyQhF5KNOjI-vRBoFiQAtdlvkaXxizTxOtOzMkWJpA5YkUgRhrnVTYQXq5YDPBmUFa9Df0K9ZnzK_qVj7mWdgTXobO3wgU9iPf5YVryLJ42YWuR-usRteVSONpr2n8RXXGBg8VlM48ORznZICypu2yR0ohHTKe46sR_9V8uJbLlbDVbAd_iwupSzXDb_BCge0Dvl8Y3lECbZWuZdwKxWCZRIRQELDZ7CEvYuwcgeCp4E5DBQcL_dRrhi8wvuLJfuoMpRncz_nwCLZlblPipzO-cZNq71iBnWV5WZHVdp5di1o05hSz2_XqdfmGTuPp0_VdZK_1ivn0h_mJ3yQ5wHE=)

```mermaid
graph TD
    Game[Game Logic] --> |controls| Player[Player]
    Game --> |manages| GameRecord[Game Record]
    Player --> |calls| LLM[LLM Client]
    Player --> |generates| Payload[JSON Payload]
    GameRecord --> |stores| Payload
    GameRecord --> |provides context| Player
    Payload --> |includes| Talk[Talk Content]
    Payload --> |includes| Behavior[Behavior]
    Payload --> |includes| Cards[Played Cards]
    GameRecord --> |formats| Performance[Player Performance]
    Performance --> |influences| Challenge[Challenge Decisions]
```

## Data Flow

### Play Cards Flow

![Play Flow](https://kroki.io/mermaid/svg/eNqNkstOwzAQRX_F8qogtW0KRUJq2WWXXVR0zQoFubEnqUXiRH5A1fDvOA-aoKoIshp77pw7M7InyVxwBonHjcMGO_TcKGg8ByE5evTRtyiYjfAVV-oFBSHjnA7oEBuynMceitToQFv0gaNY0kKXab7CF0rs00TmzkwJVsZReSS5j461SiocQTq7YDNBmUFa9Df0K9ZnzH_VrXxIs3AnWI7O3wgU9j3dxYVLSLJ42YWuR-usRteVSMNpL2j4RXXCBg8VlM48Ohyn5BLKmrbLHimFtMhYjq9G_Ffz_lpul9xWsx38LS4kL9UMv8EL-W0f8O3C8JYSaKt0LcNWKAbLJCKEgoDNZoeyIsbOEQiWCu40VLAz0E-9ZvgM_TUe7YfOYJrB_ZwP92BbZjclfjrjGzepdocV2FmWlxVZbc_ZhahFY04xu12uX5Yv6DSePl3fhfZar6lPf5jf-A0fytU-)

```mermaid
sequenceDiagram
    participant G as Game
    participant P as Player
    participant L as LLM
    participant R as GameRecord
    
    G->>P: choose_cards_to_play(context)
    P->>L: Send prompt template
    L-->>P: Generate JSON response
    Note over P: Validates payload:<br/>- played_cards<br/>- behavior<br/>- talk<br/>- play_reason
    P-->>G: Return play_result
    G->>R: record_play()
    Note over R: PlayAction Object:<br/>- player_name<br/>- played_cards<br/>- behavior<br/>- talk<br/>- play_reason<br/>- remaining_cards
```

### Challenge Flow

![Challenge Flow](https://kroki.io/mermaid/svg/eNqNkstOAjEUhl-l6UoTmAFFDSRGF-5cuBBds1FDO50zHUjbSXsRw-TdKXcFoolupv3P5fvP6SSJz9YQO1w7rLHFDg0Fab0VQjJMElTEJd6RRGkVJGgDD4buVJK2VuPR4abBbugxbYQ0kLpuHKdKOa1pnVnHHadVJiU0IwmIkGiFeweHWXhE7qR1WJChwjpn5YHMTEPVBG0RuWwJ-iNMPcV-kPUfqQthG5JwuH2ISXUVLqwiW7-kNgTxnfum4TdyFwBFAqfJBgwbf7BIrD3cKyR4Bsn4lmGi-zHrcX6hIvGnOkunmFKcSWQtb6rR_u0YViLTaFRqJeYQxyTWC3UZGqjatjr-pd1M7c-SuXgRO8WpawdwNfdU1Cvy3oF8lXdzIeAQ5V7uMpOZThib6-ueaJsgxNT0oaArLGkuC26my3uWWXB7lNwYLrh8Y6vXQ9tmEoeEzl58vdXPZu9EjA==)

```mermaid
sequenceDiagram
    participant G as Game
    participant R as GameRecord
    participant P as Player
    participant L as LLM
    
    G->>R: get_latest_play_behavior()
    R-->>G: Formatted performance text<br/>(includes talk & behavior)
    G->>P: decide_challenge(performance)
    P->>L: Send challenge prompt
    L-->>P: Generate decision
    Note over P: Validates payload:<br/>- was_challenged<br/>- challenge_reason
    P-->>G: Return challenge_result
    G->>R: record_challenge()
    Note over R: Updates PlayAction:<br/>- challenge result<br/>- challenge reason
```

## Key Components

### Game Logic (game.py)
- Manages game flow and rules
- Coordinates between players
- Controls round progression
- Handles system challenges
- Delegates record keeping to GameRecord

### Player (player.py)
- Interfaces with LLM
- Generates decisions through prompts
- Validates LLM responses
- Manages player state (hand, opinions)
- Makes play and challenge decisions

### Game Record (game_record.py)
- Stores game state and history
- Tracks player actions and results
- Provides context for decisions
- Formats action summaries
- Maintains persistent record

### Payloads

#### Play Card Payload
```json
{
    "played_cards": ["K", "K"],
    "behavior": "nervously shuffles cards",
    "talk": "I'm confident these are the right cards",
    "play_reason": "strategic decision explanation"
}
```

#### Challenge Payload
```json
{
    "was_challenged": true,
    "challenge_reason": "explanation for challenge decision"
}
```

## Context Generation

### For Play Decisions
1. Game provides:
   - Round base info (current round, target card)
   - Round action history
   - Play decision context
2. Record formats:
   - Previous plays
   - Player behaviors
   - Player dialogue
   - Challenge outcomes

### For Challenge Decisions
1. Game provides:
   - Round base info
   - Action history
   - Challenge decision context
   - Previous player's performance
2. Record formats:
   - Player actions
   - Behaviors
   - Dialogue
   - Current game state

## Information Flow
1. Game initiates action
2. Player receives context
3. Player generates decision
4. Game validates action
5. Record stores result
6. Record provides context for next decision

This architecture ensures:
- Clean separation of concerns
- Persistent game state
- Rich context for decisions
- Traceable player actions
- Structured data flow
