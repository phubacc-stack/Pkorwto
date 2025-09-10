import re
import os
import asyncio
import random
import unicodedata
from discord.ext import commands, tasks
import discord
from flask import Flask
from threading import Thread

version = 'v3.2'

user_token = os.environ['user_token']
spam_id = os.environ['spam_id']

with open('pokemon', 'r', encoding='utf8') as file:
    pokemon_list = file.read()
with open('mythical', 'r') as file:
    mythical_list = file.read()

poketwo = 716390085896962058
p2assistant = 123456789012345678  # replace with actual p2assistant bot ID
client = commands.Bot(command_prefix="!")

intervals = [3.6, 2.8, 3.0, 3.2, 3.4]

# --- Flask keep-alive for Render ---
app = Flask('')

@app.route('/')
def home():
    return "I'm alive"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()


def sanitize_name(name: str) -> str:
    """Convert Pokémon names into safe Discord channel names."""
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("ascii")
    name = name.lower()
    name = name.replace("♀", "f").replace("♂", "m")
    safe = re.sub(r"[^a-z0-9]+", "-", name)
    return safe.strip("-")


def solve(message, file_name):
    """Extracts a hint from the message and finds matching solutions in the given file."""
    hint = [c for c in message[15:-1] if c != '\\']
    hint_string = ''.join(hint).replace('_', '.')
    with open(f"{file_name}", "r") as f:
        solutions = f.read()
    solution = re.findall(f'^{hint_string}$', solutions, re.MULTILINE)
    return solution if solution else None


@tasks.loop(seconds=random.choice(intervals))
async def spam():
    """Spam loop with rate-limit handling."""
    channel = client.get_channel(int(spam_id))
    if not channel:
        print("Channel not found.")
        return
    message_content = ''.join(random.sample('1234567890', 7) * 5)
    try:
        await channel.send(message_content)
    except discord.errors.HTTPException as e:
        if e.status == 429:
            retry_after = getattr(e, 'retry_after', 5)
            print(f"Rate limit exceeded. Retrying in {retry_after} seconds...")
            await asyncio.sleep(retry_after)
            await spam()
        else:
            print(f"HTTP error: {e}. Retrying in 60 seconds...")
            await asyncio.sleep(60)
            await spam()
    except discord.errors.DiscordServerError as e:
        print(f"Discord server error: {e}. Retrying in 60 seconds...")
        await asyncio.sleep(60)
        await spam()


@spam.before_loop
async def before_spam():
    await client.wait_until_ready()


@client.event
async def on_ready():
    print(f'Logged into account: {client.user.name}')
    spam.start()


@client.event
async def on_message(message):
    if message.author.id == client.user.id:
        return

    if message.author.id == poketwo and message.channel.category:
        # --- Spawn embed ---
        if message.embeds:
            embed_title = message.embeds[0].title
            if 'wild pokémon has appeared!' in embed_title:
                print("[poketwo] Wild Pokémon appeared! Waiting for p2assistant…")

                def check(m):
                    return m.author.id == p2assistant and m.channel == message.channel

                try:
                    p2_msg = await client.wait_for('message', timeout=55.0, check=check)
                    name = p2_msg.content.split(":")[0].strip()
                    print(f"[p2assistant] Got name '{name}'")

                    solution = None
                    with open("collection", "r", encoding="utf8") as f:
                        if re.search(fr'^{name}$', f.read(), re.MULTILINE):
                            solution = name
                            cloned_channel = await message.channel.clone(reason="Cloning for backup")
                            await cloned_channel.send("Pokémon spawn has been backed up here.")
                            await move_to_category(message.channel, name, "🎉Friends Col", message.guild)
                            await cloned_channel.send(
                                "<@716390085896962058> redirect " + " ".join(str(i) for i in range(1, 51))
                            )
                    if not solution:
                        with open("mythical", "r", encoding="utf8") as f:
                            if re.search(fr'^{name}$', f.read(), re.MULTILINE):
                                solution = name
                                cloned_channel = await message.channel.clone(reason="Cloning for backup")
                                await cloned_channel.send("Pokémon spawn has been backed up here.")
                                await move_to_category(message.channel, name, "😈Collection", message.guild)
                                await cloned_channel.send(
                                    "<@716390085896962058> redirect " + " ".join(str(i) for i in range(1, 51))
                                )

                except asyncio.TimeoutError:
                    print("[backup] No p2assistant, sending @Pokétwo h…")
                    await message.channel.send('<@716390085896962058> h')

        # --- Pokétwo hints ---
        else:
            content = message.content
            if 'The pokémon is ' in content:
                print("[hint] Processing Pokétwo hint…")
                solution = solve(content, 'collection')
                if solution:
                    print(f"[hint] Solved: {solution[0]} (Collection)")
                    cloned_channel = await message.channel.clone(reason="Cloning for backup")
                    await cloned_channel.send("Pokémon spawn has been backed up here.")
                    await move_to_category(message.channel, solution[0], "🎉Friends Col", message.guild)
                    await cloned_channel.send(
                        "<@716390085896962058> redirect " + " ".join(str(i) for i in range(1, 51))
                    )
                else:
                    solution = solve(content, 'mythical')
                    if solution:
                        print(f"[hint] Solved: {solution[0]} (Mythical)")
                        cloned_channel = await message.channel.clone(reason="Cloning for backup")
                        await cloned_channel.send("Pokémon spawn has been backed up here.")
                        await move_to_category(message.channel, solution[0], "😈Collection", message.guild)
                        await cloned_channel.send(
                            "<@716390085896962058> redirect " + " ".join(str(i) for i in range(1, 51))
                        )

    # --- Pokétwo congratulations ---
    if message.author.id == poketwo and message.content.startswith("Congratulations"):
        if "colors seem unusual...✨" not in message.content:
            if message.channel.category and message.channel.category.name.startswith("Spawns"):
                print("[poketwo] Congrats (non-shiny) in spawns → keeping channel")
            else:
                print("[poketwo] Congrats (non-shiny) → deleting channel in 15s")
                await asyncio.sleep(15)
                await message.channel.delete()
        else:
            print("[poketwo] Congrats (shiny) → keeping channel")

    await client.process_commands(message)


async def move_to_category(channel, solution, base_category_name, guild, max_channels=48, max_categories=5):
    """Moves the channel to the appropriate category, creating categories if needed."""
    for i in range(1, max_categories + 1):
        category_name = f"{base_category_name} {i}" if i > 1 else base_category_name
        category = discord.utils.get(guild.categories, name=category_name)
        if category is None:
            print(f"[move] Creating new category: {category_name}")
            category = await guild.create_category(category_name)
        if len(category.channels) < max_channels:
            print(f"[move] Moving channel to {category_name} as {solution}")
            await channel.edit(
                name=sanitize_name(solution),
                category=category,
                sync_permissions=True,
            )
            return
    print(f"[move] All {base_category_name} categories are full.")


@client.command()
async def setup(ctx):
    """Sets up Friends Col 1–5, Collection 1–5, and Spawns 1–50 categories."""
    guild = ctx.guild

    for i in range(1, 6):
        name = f"🎉Friends Col {i}" if i > 1 else "🎉Friends Col"
        if not discord.utils.get(guild.categories, name=name):
            await guild.create_category(name)
            print(f"[setup] Created category {name}")

    for i in range(1, 6):
        name = f"😈Collection {i}" if i > 1 else "😈Collection"
        if not discord.utils.get(guild.categories, name=name):
            await guild.create_category(name)
            print(f"[setup] Created category {name}")

    for i in range(1, 51):
        name = f"Spawns {i}"
        if not discord.utils.get(guild.categories, name=name):
            cat = await guild.create_category(name)
            await guild.create_text_channel(f"spawn-{i}", category=cat)
            print(f"[setup] Created category {name} with channel spawn-{i}")

    await ctx.send("✅ Setup complete!")


@client.command()
async def report(ctx, *, args):
    await ctx.send(args)


@client.command()
async def reboot(ctx):
    if spam.is_running():
        spam.cancel()
        await ctx.send("Spam loop has been stopped.")
    spam.start()
    await ctx.send("Spam loop has been restarted.")


@client.command()
async def pause(ctx):
    spam.cancel()
    await ctx.send("Spam loop paused.")


# --- Start keep-alive + bot ---
keep_alive()
client.run(user_token)
