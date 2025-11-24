import discord
import os
from dotenv import load_dotenv
import re
import json
import anthropic
import random

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
EVENTS_CHANNEL_ID = int(os.getenv('EVENTS_CHANNEL_ID'))
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

print(f"DISCORD_TOKEN loaded: {'Yes' if DISCORD_TOKEN else 'No'}")
print(f"EVENTS_CHANNEL_ID: {EVENTS_CHANNEL_ID}")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = discord.Client(intents=intents)

current_events = {}  # thread_id: {'title':, 'time':, 'size':, 'roles':, 'signups': {'accept':[], 'maybe':[], 'decline':[]}, 'message_id':, 'mentions':[], 'user_id':}

def create_embed(event_data):
    accept_list = ', '.join([u.display_name for u in event_data['signups']['accept']]) or 'None'
    maybe_list = ', '.join([u.display_name for u in event_data['signups']['maybe']]) or 'None'
    decline_list = ', '.join([u.display_name for u in event_data['signups']['decline']]) or 'None'
    desc = event_data.get('description', '')
    embed = discord.Embed(
        title=f"📅 {event_data['title']}",
        description=desc if desc else None,
        color=0x3498db  # Nice blue color
    )
    embed.add_field(name="🕒 Date/Time", value=event_data['time'], inline=True)
    embed.add_field(name="✅ Accept", value=accept_list, inline=False)
    embed.add_field(name="🤔 Maybe", value=maybe_list, inline=False)
    embed.add_field(name="❌ Decline", value=decline_list, inline=False)
    embed.set_footer(text="Event Management Bot", icon_url=bot.user.avatar.url if bot.user.avatar else None)
    return embed

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    print(f"Received message from {message.author}: {message.content}")

    content = message.content
    if content.lower().startswith('create '):
        print("Create condition met, handling event creation")
        await handle_event_creation(message, content)

@bot.event
async def on_interaction(interaction):
    if interaction.type == discord.InteractionType.component:
        custom_id = interaction.data['custom_id']
        thread_id = interaction.channel.id
        if thread_id in current_events:
            signups = current_events[thread_id]['signups']
            user = interaction.user
            # Remove from all lists
            for status in signups:
                if user in signups[status]:
                    signups[status].remove(user)
            # Add to the clicked one
            if custom_id in signups:
                signups[custom_id].append(user)
            # Update embed
            embed = create_embed(current_events[thread_id])
            message = await interaction.channel.fetch_message(current_events[thread_id]['message_id'])
            await message.edit(embed=embed)
            await interaction.response.defer()

async def extract_event_data(text):
    prompt = f"""Extract the event details from the following text. The text may be in Danish. Parse dates and times accordingly. If the date is partial (e.g., "Lørdag d. 29"), assume the current or next occurrence and format as dd/mm/yyyy. Return date in dd/mm/yyyy format. Return only a valid JSON object with the keys: title, description, time, date, size, roles. Use empty strings for missing information. Do not include any other text or explanations.

Text: {text}"""
    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.content[0].text.strip()
        data = json.loads(content)
        return data
    except Exception as e:
        print(f"Error extracting event data: {e}")
        return None

async def handle_event_creation(message, content):
    print(f"Content to extract: '{content}'")
    # Remove 'create ' prefix
    content = content[7:].strip()
    # Extract mentions from content
    mentions = re.findall(r'<@\d+>', content)
    # Send confirmation response
    responses = ["Sending your letter to Mog Central", "Working on it", "Kupo...", "Now, don't you worry. I'll write", "Thanks, buddy. I'll sell you stuff again"]
    await message.channel.send(random.choice(responses))
    # Delete the original message to avoid double notifications
    try:
        await message.delete()
    except discord.errors.Forbidden:
        pass  # Bot lacks permission to delete messages
    data = await extract_event_data(content)
    if not data:
        await message.channel.send("Failed to process the event details. Please try again.")
        return
    if not data.get('title') or not data.get('time'):
        await message.channel.send("Failed to extract event details. Please ensure your message includes a clear title and time.")
        return

    event_name = data.get('title', 'Untitled Event')
    event_time = data.get('time', 'TBD')
    if data.get('date'):
        event_time = f"{data['date']} {event_time}".strip()
    event_size = data.get('size') or 'Unknown'
    roles = data.get('roles') or 'Not specified'
    description = data.get('description', '')

    # Get events channel
    events_channel = bot.get_channel(EVENTS_CHANNEL_ID)
    if not events_channel:
        await message.reply("Events channel not found.")
        return

    thread_name = f"{event_name} – {event_time}"

    # Create starter message in events_channel
    starter_msg = await events_channel.send("Creating event thread...")

    # Create thread from starter message
    thread = await events_channel.create_thread(name=thread_name, message=starter_msg, type=discord.ChannelType.private_thread)

    # Add mentioned users to the private thread
    for mention in mentions:
        user_id = int(mention.strip('<@>'))
        user = bot.get_user(user_id)
        if user:
            await thread.add_user(user)

    # Create embed and buttons
    event_data = {
        'title': event_name,
        'time': event_time,
        'size': event_size,
        'roles': roles,
        'description': description,
        'signups': {'accept': [], 'maybe': [], 'decline': []},
        'mentions': mentions,
        'user_id': message.author.id
    }
    embed = create_embed(event_data)
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="✅ Accept", style=discord.ButtonStyle.green, custom_id="accept"))
    view.add_item(discord.ui.Button(label="🤔 Maybe", style=discord.ButtonStyle.secondary, custom_id="maybe"))
    view.add_item(discord.ui.Button(label="❌ Decline", style=discord.ButtonStyle.red, custom_id="decline"))
    msg = await thread.send(embed=embed, view=view)
    event_data['message_id'] = msg.id

    # Delete starter message
    await starter_msg.delete()

    # Store context
    current_events[thread.id] = event_data

    # Mention users
    if mentions:
        await thread.send(' '.join(mentions))

try:
    bot.run(DISCORD_TOKEN)
except Exception as e:
    print(f"Error during bot login: {e}")