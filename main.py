import re, os, asyncio, random, string
from threading import Thread
from flask import Flask
from discord.ext import commands, tasks
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
    # use 0.0.0.0 so external services can ping it
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

num_pokemon = 0
shiny = 0
legendary = 0
mythical = 0

poketwo = 716390085896962058
client = commands.Bot(command_prefix='*')  # prefix changed
intervals = [2.2, 2.4, 2.6, 2.8]

def solve(message, file_name):
    hint = []
    for i in range(15, len(message) - 1):
        if message[i] != '\\':
            hint.append(message[i])
    hint_string = ''.join(hint)
    hint_replaced = hint_string.replace('_', '.')
    with open(f"{file_name}", "r") as f:
        solutions = f.read()
    solution = re.findall('^'+hint_replaced+'$', solutions, re.MULTILINE)
    if len(solution) == 0:
        return None
    return solution

@tasks.loop(seconds=random.choice(intervals))
async def spam():
    channel = client.get_channel(int(spam_id))
    await channel.send(''.join(random.sample(['1','2','3','4','5','6','7','8','9','0'],7)*5))

@spam.before_loop
async def before_spam():
    await client.wait_until_ready()

# start the spam task
spam.start()

@client.event
async def on_ready():
    print(f'Logged into account: {client.user.name}')

@client.event
async def on_message(message):
    # ignore messages from ourselves
    if message.author == client.user:
        return

    # safe-guard for DM messages (no guild)
    if message.guild is None:
        return

    channel = client.get_channel(message.channel.id)
    guild = message.guild
    category = channel.category
    if message.author.id == poketwo:
        # guard in case channel.category is None
        if channel.category and channel.category.name == 'catch':
            if message.embeds:
                embed_title = message.embeds[0].title or ''
                if 'wild pokémon has appeared!' in embed_title:
                    await asyncio.sleep(1)
                    await channel.send('<@716390085896962058> h')
            else:
                content = message.content
                solution = None
                if 'The pokémon is ' in content:
                    solution = solve(content, 'collection')
                    if solution:
                        await channel.clone()
                        category_name = 'Stock 1'
                        guild = message.guild
                        # find the target category (assumes it exists)
                        new_category = [c for c in guild.categories if c.name == category_name][0]
                        num_channels = len(new_category.channels)
                        print(f"There are {num_channels} channels in the {category_name} category.")
                        if len(new_category.channels) <= 48:
                            await channel.edit(name=solution[0].lower().replace(' ', '-'), category=new_category, sync_permissions=True)
                        if len(new_category.channels) >= 48:
                            category_name = 'Stock 2'
                            new_category = [c for c in guild.categories if c.name == category_name][0]
                            num_channels = len(new_category.channels)
                            print(f"There are {num_channels} channels in the {category_name} category.")
                            if len(new_category.channels) <= 48:
                                await channel.edit(name=solution[0].lower().replace(' ', '-'), category=new_category, sync_permissions=True)
                            if len(new_category.channels) >= 48:
                                category_name = 'Stock 3'
                                new_category = [c for c in guild.categories if c.name == category_name][0]
                                num_channels = len(new_category.channels)
                                print(f"There are {num_channels} channels in the {category_name} category.")
                                if len(new_category.channels) <= 48:
                                    await channel.edit(name=solution[0].lower().replace(' ', '-'), category=new_category, sync_permissions=True)
                                if len(new_category.channels) >= 48:
                                    category_name = 'Stock 4'
                                    new_category = [c for c in guild.categories if c.name == category_name][0]
                                    num_channels = len(new_category.channels)
                                    print(f"There are {num_channels} channels in the {category_name} category.")
                                    if len(new_category.channels) <= 48:
                                        await channel.edit(name=solution[0].lower().replace(' ', '-'), category=new_category, sync_permissions=True)
                                    if len(new_category.channels) >= 48:
                                        category_name = 'Stock 5'
                                        new_category = [c for c in guild.categories if c.name == category_name][0]
                                        num_channels = len(new_category.channels)
                                        print(f"There are {num_channels} channels in the {category_name} category.")
                                        if len(new_category.channels) <= 48:
                                            await channel.edit(name=solution[0].lower().replace(' ', '-'), category=new_category, sync_permissions=True)
                                        if len(new_category.channels) >= 48:
                                            category_name = 'Stock 6'
                                            new_category = [c for c in guild.categories if c.name == category_name][0]
                                            num_channels = len(new_category.channels)
                                            print(f"There are {num_channels} channels in the {category_name} category.")
                                            if len(new_category.channels) <= 48:
                                                await channel.edit(name=solution[0].lower().replace(' ', '-'), category=new_category, sync_permissions=True)
                                            if len(new_category.channels) >= 48:
                                                category_name = 'Stock 7'
                                                new_category = [c for c in guild.categories if c.name == category_name][0]
                                                num_channels = len(new_category.channels)
                                                print(f"There are {num_channels} channels in the {category_name} category.")
                                                if len(new_category.channels) <= 48:
                                                    await channel.edit(name=solution[0].lower().replace(' ', '-'), category=new_category, sync_permissions=True)
                                                if len(new_category.channels) >= 48:
                                                    category_name = 'Stock 8'
                                                    new_category = [c for c in guild.categories if c.name == category_name][0]
                                                    num_channels = len(new_category.channels)
                                                    print(f"There are {num_channels} channels in the {category_name} category.")
                                                    if len(new_category.channels) <= 48:
                                                        await channel.edit(name=solution[0].lower().replace(' ', '-'), category=new_category, sync_permissions=True)
                                                    if len(new_category.channels) >= 48:
                                                        category_name = 'Stock 9'
                                                        new_category = [c for c in guild.categories if c.name == category_name][0]
                                                        num_channels = len(new_category.channels)
                                                        print(f"There are {num_channels} channels in the {category_name} category.")
                                                        if len(new_category.channels) <= 48:
                                                            await channel.edit(name=solution[0].lower().replace(' ', '-'), category=new_category, sync_permissions=True)
                                                        if len(new_category.channels) >= 48:
                                                            category_name = 'Stock 10'
                                                            new_category = [c for c in guild.categories if c.name == category_name][0]
                                                            num_channels = len(new_category.channels)
                                                            print(f"There are {num_channels} channels in the {category_name} category.")
                                                            if len(new_category.channels) <= 48:
                                                                await channel.edit(name=solution[0].lower().replace(' ', '-'), category=new_category, sync_permissions=True)
                        await channel.send(f'<@716390085896962058> redirect 1 2 3 4 5 6 7 ')
                    if not solution:
                        solution = solve(content, 'mythical')
                        if solution:
                            await channel.clone()
                            category_name = 'Rare 1'
                            guild = message.guild
                            new_category = [c for c in guild.categories if c.name == category_name][0]
                            num_channels = len(new_category.channels)
                            print(f"There are {num_channels} channels in the {category_name} category.")
                            if len(new_category.channels) <= 48:
                                await channel.edit(name=solution[0].lower().replace(' ', '-'), category=new_category, sync_permissions=True)
                            if len(new_category.channels) >= 48:
                                category_name = 'Rare 2'
                                new_category = [c for c in guild.categories if c.name == category_name][0]
                                num_channels = len(new_category.channels)
                                print(f"There are {num_channels} channels in the {category_name} category.")
                                if len(new_category.channels) <= 48:
                                    await channel.edit(name=solution[0].lower().replace(' ', '-'), category=new_category, sync_permissions=True)

@client.command()
async def report(ctx, *, args):
    await ctx.send(args)

@client.command()
async def reboot(ctx):
    # restart spam task if it's not running
    if not spam.is_running():
        spam.start()
    await ctx.send("✅ Rebooted tasks.")

@client.command()
async def pause(ctx):
    if spam.is_running():
        spam.cancel()
        await ctx.send("⏸️ Spam task paused.")
    else:
        await ctx.send("ℹ️ Spam task was not running.")

# NEW: setup command with reordering
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

    # reorder categories in desired order
    categories = {c.name: c for c in guild.categories}
    for index, name in enumerate(category_names):
        cat = categories.get(name)
        if cat:
            # move category to desired position
            await cat.edit(position=index)

    if created:
        await ctx.send(f"✅ Created categories: {', '.join(created)} (and reordered all)")
    else:
        await ctx.send("ℹ️ All categories already exist, order was fixed.")

# start the keep-alive webserver, then run the bot
keep_alive()
client.run(f"{user_token}")
            
