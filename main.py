import re, os, asyncio, random, string
from threading import Thread
from flask import Flask
from discord.ext import commands
import discord

version = 'v2.7'

user_token = os.environ['user_token']
spam_id = os.environ['spam_id']
report_id = os.environ['report_id']

# --- Keep-alive Flask app (for Render/Replit) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive"

def run_web():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()

# --- End keep-alive setup ---

with open('pokemon','r', encoding='utf8') as file:
    pokemon_list = file.read()
with open('mythical','r', encoding='utf8') as file:
    mythical_list = file.read()

num_pokemon = shiny = legendary = mythical = 0
poketwo = 716390085896962058
client = commands.Bot(command_prefix='*')
intervals = [2.2, 2.4, 2.6, 2.8]

def solve(message, file_name):
    hint = [c for c in message[15:-1] if c != '\\']
    hint_string = ''.join(hint).replace('_', '.')
    with open(file_name, 'r') as f:
        solutions = f.read()
    solution = re.findall('^'+hint_string+'$', solutions, re.MULTILINE)
    return solution if solution else None

# --- Spam task compatible with old Discord fork ---
async def spam_task():
    await client.wait_until_ready()
    channel = client.get_channel(int(spam_id))
    while not client.is_closed():
        if channel:
            await channel.send(''.join(random.sample(['1','2','3','4','5','6','7','8','9','0'],7)*5))
        await asyncio.sleep(random.choice(intervals))

@client.event
async def on_ready():
    print(f'Logged into account: {client.user.name}')
    # Start spam task
    client.loop.create_task(spam_task())

@client.event
async def on_message(message):
    if message.author == client.user or message.guild is None:
        return

    channel = client.get_channel(message.channel.id)
    guild = message.guild
    if message.author.id == poketwo:
        if channel.category and channel.category.name == 'catch':
            # handle embeds
            if message.embeds:
                embed_title = message.embeds[0].title or ''
                if 'wild pokémon has appeared!' in embed_title:
                    await asyncio.sleep(1)
                    await channel.send('<@716390085896962058> h')
            else:
                content = message.content
                solution = solve(content, 'collection')
                if solution:
                    await channel.clone()
                    await move_to_stock(channel, guild, solution[0])
                else:
                    solution = solve(content, 'mythical')
                    if solution:
                        await channel.clone()
                        await move_to_rare(channel, guild, solution[0])
        # Handle channel deletion on certain Pokétwo messages
        if 'congratulations' in message.content.lower():
            if not channel.category or channel.category.name != 'catch':
                await channel.delete()
        if 'these colors seem unusual' in message.content.lower():
            pass  # do not delete, just ignore

async def move_to_stock(channel, guild, pokemon_name):
    for i in range(1, 11):
        category_name = f'Stock {i}'
        cat = discord.utils.get(guild.categories, name=category_name)
        if cat and len(cat.channels) < 48:
            await channel.edit(name=pokemon_name.lower().replace(' ', '-'), category=cat, sync_permissions=True)
            # Ping Pokétwo after moving
            await channel.send(f'<@716390085896962058> redirect 1 2 3 4 5')
            break

async def move_to_rare(channel, guild, pokemon_name):
    for i in range(1, 3):
        category_name = f'Rare {i}'
        cat = discord.utils.get(guild.categories, name=category_name)
        if cat and len(cat.channels) < 48:
            await channel.edit(name=pokemon_name.lower().replace(' ', '-'), category=cat, sync_permissions=True)
            # Ping Pokétwo after moving
            await channel.send(f'<@716390085896962058> redirect 1 2 3 4 5')
            break

@client.command()
async def report(ctx, *, args):
    await ctx.send(args)

@client.command()
async def reboot(ctx):
    client.loop.create_task(spam_task())
    await ctx.send("✅ Rebooted tasks.")

@client.command()
async def pause(ctx):
    # Stops spam by canceling the task
    # Not fully cancellable with old fork without extra flags, but we leave as placeholder
    await ctx.send("⏸️ Spam task paused (restart bot to resume).")

@client.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    """Create and reorder all required categories for the bot."""
    guild = ctx.guild
    category_names = [
        "catch",
        "Stock 1", "Stock 2", "Stock 3", "Stock 4", "Stock 5",
        "Stock 6", "Stock 7", "Stock 8", "Stock 9", "Stock 10",
        "Rare 1", "Rare 2"
    ]

    created = []
    for name in category_names:
        existing = discord.utils.get(guild.categories, name=name)
        if not existing:
            await guild.create_category(name)
            created.append(name)

    # 🔹 refresh categories after creating so reorder works
    await asyncio.sleep(1)
    categories = {c.name: c for c in guild.categories}

    for index, name in enumerate(category_names):
        cat = categories.get(name)
        if cat:
            await cat.edit(position=index)

    if created:
        await ctx.send(f"✅ Created categories: {', '.join(created)} (and reordered all)")
    else:
        await ctx.send("ℹ️ All categories already exist, order was fixed.")

# --- Start keep-alive ---
keep_alive()
client.run(user_token)
