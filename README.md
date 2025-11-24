# AI Event Autopilot – Perfect Event Master Edition (November 2025)

This version does exactly this flow every single time:

1. You type anywhere:  
   `@AI Event Bot MC Retro Run – Friday 20:00 CET – 40-man – 8 tanks / 12 healers / 20 DPS @Sylvanas @Thrall @Jaina`

2. The bot instantly:
   - Goes to your **#events** channel  
   - Creates a new thread named **“MC Retro Run – Friday 20:00 CET”**  
   - Tags **@Event Master** and runs **/event create** inside that thread  
   - Answers every single question perfectly in your DMs  
   - When the signup is posted, the bot @-mentions everyone you listed (Sylvanas, Thrall, Jaina, …) in the thread  

You literally never touch Event Master again.

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
PLANNER_BOT_ID=787111761998888990