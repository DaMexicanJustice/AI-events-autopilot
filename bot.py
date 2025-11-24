import discord
import os
from dotenv import load_dotenv
from anthropic import Anthropic
import re

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
ANTHROPIC_KEY = os.getenv('ANTHROPIC_KEY')
EVENTS_CHANNEL_ID = int(os.getenv('EVENTS_CHANNEL_ID'))
PLANNER_BOT_ID = int(os.getenv('PLANNER_BOT_ID'))

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = discord.Client(intents=intents)
anthropic = Anthropic(api_key=ANTHROPIC_KEY)

current_events = {}  # thread_id: {'mentions': [], 'user_id': }

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Check if message mentions the bot and starts with "@AI Event Bot"
    if bot.user in message.mentions and message.content.startswith(f'<@{bot.user.id}> AI Event Bot'):
        await handle_event_creation(message)

    # Handle DMs from Event Master
    if message.author.id == PLANNER_BOT_ID and isinstance(message.channel, discord.DMChannel):
        await handle_dm_response(message)

    # Check if message is in a thread and from Event Master, and contains signup
    if message.author.id == PLANNER_BOT_ID and hasattr(message.channel, 'parent') and message.channel.parent.id == EVENTS_CHANNEL_ID:
        if 'signup' in message.content.lower() or 'sign up' in message.content.lower():
            # Mention users
            if message.channel.id in current_events:
                mentions_str = ' '.join(current_events[message.channel.id]['mentions'])
                await message.channel.send(mentions_str)

async def handle_event_creation(message):
    content = message.content.replace(f'<@{bot.user.id}> AI Event Bot', '').strip()
    # Parse content: "MC Retro Run – Friday 20:00 CET – 40-man – 8 tanks / 12 healers / 20 DPS @Sylvanas @Thrall @Jaina"
    parts = content.split(' – ')
    if len(parts) < 4:
        await message.reply("Invalid format. Please use: @AI Event Bot <event name> – <time> – <size> – <roles> <mentions>")
        return

    event_name = parts[0].strip()
    event_time = parts[1].strip()
    event_size = parts[2].strip()
    roles_and_mentions = ' – '.join(parts[3:])

    # Extract mentions at the end
    mention_pattern = r'(@\w+)'
    mentions = re.findall(mention_pattern, roles_and_mentions)
    roles = re.sub(mention_pattern, '', roles_and_mentions).strip()

    # Create thread
    events_channel = bot.get_channel(EVENTS_CHANNEL_ID)
    if not events_channel:
        await message.reply("Events channel not found.")
        return

    thread_name = f"{event_name} – {event_time}"
    thread = await events_channel.create_thread(name=thread_name, message=message, type=discord.ChannelType.public_thread)

    # Mention Event Master and send /event create
    planner_mention = f'<@{PLANNER_BOT_ID}>'
    await thread.send(f'{planner_mention} /event create')

    # Store context
    current_events[thread.id] = {
        'mentions': mentions,
        'user_id': message.author.id
    }

async def handle_dm_response(message):
    # Use AI to respond
    response = await get_ai_response(message.content)
    await message.channel.send(response)

async def get_ai_response(question):
    # Use Anthropic to answer
    prompt = f"You are an event planner bot. Answer this question perfectly: {question}"
    response = anthropic.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

bot.run(DISCORD_TOKEN)