# AI Event Autopilot – Perfect Event Master Edition (November 2025)

This version does exactly this flow every single time:

1. You type anywhere:
    `@Stilzkin create MC Retro Run – Friday 20:00 CET – 40-man – 8 tanks / 12 healers / 20 DPS @Sylvanas @Thrall @Jaina`

2. The bot instantly:
    - Goes to your **#events** channel
    - Creates a new thread named **"MC Retro Run – Friday 20:00 CET"**
    - Posts an embed with the event details, date/time, size, roles, and buttons for Accept, Maybe, Decline
    - @-mentions everyone you listed (Sylvanas, Thrall, Jaina, …) in the thread
    - Users can click the buttons to sign up, and the embed updates with the current signups

The bot handles all signups directly without external dependencies.

### Files (copy-paste everything)

#### 1. `README.md` (this file)

#### 2. `.env`
```env
DISCORD_TOKEN=your_new_bot_token_here
ANTHROPIC_KEY=sk-ant-...          # ← Recommended – works 99.9 % perfectly
# OPENAI_KEY=sk-...               # also fine
# GROK_KEY=xai-...

# Channel where threads will be created (right-click channel → Copy Channel ID)
EVENTS_CHANNEL_ID=123456789012345678

# Event Master user ID – do NOT change
PLANNER_BOT_ID=787111761998888990# AI-events-autopilot
# AI-events-autopilot
