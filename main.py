import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv

load_dotenv()

# =====================
# INTENTS + BOT
# =====================
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="&",
    intents=intents,
    help_command=None
)

# =====================
# LOG CHANNEL
# =====================
LOG_CHANNEL_ID = 1508590659672608778


async def send_log(embed):
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if channel:
        await channel.send(embed=embed)


# =====================
# STATUSY
# =====================
statuses = [
    "&pomoc | CPM PL FIRE & RESCUE 🚒",
    "Car Parking Multiplayer 🚗",
    "OSP • PSP • POLICJA • ZRM 🔥"
]

status_index = 0


@tasks.loop(seconds=15)
async def change_status():
    global status_index

    await bot.change_presence(
        activity=discord.Game(name=statuses[status_index])
    )

    status_index = (status_index + 1) % len(statuses)


@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}")
    change_status.start()


# =====================
# ADMIN CHECK
# =====================
def is_admin():
    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator
    return commands.check(predicate)


# =====================
# PING (ALL)
# =====================
@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong! `{round(bot.latency * 1000)}ms`")


# =====================
# INFO (ALL)
# =====================
@bot.command()
async def info(ctx):
    await ctx.message.delete()

    embed = discord.Embed(
        title="🚒 CPM PL FIRE & RESCUE",
        description="Car Parking Multiplayer RP 🚗",
        color=discord.Color.red()
    )

    embed.set_thumbnail(url=bot.user.display_avatar.url)

    await ctx.send(embed=embed)


# =====================
# OGŁOSZENIA (ADMIN)
# =====================
@bot.command()
@is_admin()
async def ogloszenia(ctx):
    await ctx.message.delete()

    embed = discord.Embed(
        title="**CPM PL FIRE & RESCUE**",
        description=(
            "🚗 Car Parking Multiplayer RP\n\n"
            "🚒 OSP – Ochotnicza Straż Pożarna\n"
            "🚒 PSP – Państwowa Straż Pożarna\n"
            "🚓 POLICJA\n"
            "🚑 ZRM\n\n"
            "👉 Wybierz role na <#1508527145658351730>\n"
            "👉 Zacznij pisać na <#1508552147707498608>\n"
        ),
        color=discord.Color.orange()
    )

    embed.set_thumbnail(url=bot.user.display_avatar.url)

    await ctx.send(embed=embed)

    await send_log(discord.Embed(
        title="📢 OGŁOSZENIE",
        description=f"Autor: {ctx.author}",
        color=discord.Color.orange()
    ))


# =====================
# CLEAR (ADMIN)
# =====================
@bot.command()
@is_admin()
async def clear(ctx, amount: int = None):

    if amount is None:
        await ctx.send("❌ Użycie: `&clear [ilość]`", delete_after=5)
        return

    deleted = await ctx.channel.purge(limit=amount + 1)

    msg = await ctx.send(f"🧹 Usunięto `{len(deleted)-1}` wiadomości")
    await msg.delete(delay=3)

    await send_log(discord.Embed(
        title="🧹 CLEAR",
        description=f"{ctx.author} usunął {len(deleted)-1} wiadomości",
        color=discord.Color.green()
    ))


# =====================
# KICK (ADMIN)
# =====================
@bot.command()
@is_admin()
async def kick(ctx, member: discord.Member, *, reason="Brak powodu"):

    await member.kick(reason=reason)

    await ctx.send(f"👢 {member.mention} został wyrzucony")

    await send_log(discord.Embed(
        title="👢 KICK",
        description=f"{member} | {reason} | {ctx.author}",
        color=discord.Color.orange()
    ))


# =====================
# BAN (ADMIN)
# =====================
@bot.command()
@is_admin()
async def ban(ctx, member: discord.Member, *, reason="Brak powodu"):

    await member.ban(reason=reason)

    await ctx.send(f"🔨 {member.mention} został zbanowany")

    await send_log(discord.Embed(
        title="🔨 BAN",
        description=f"{member} | {reason} | {ctx.author}",
        color=discord.Color.red()
    ))


# =====================
# HELP (KATEGORIE)
# =====================
@bot.command(name="pomoc")
async def pomoc(ctx):
    await ctx.message.delete()

    embed = discord.Embed(
        title="📘 CPM PL FIRE & RESCUE • HELP",
        description="Kategorie komend 🚒",
        color=discord.Color.green()
    )

    embed.set_thumbnail(url=bot.user.display_avatar.url)

    embed.add_field(
        name="👥 Dla wszystkich",
        value=(
            "`&ping`\n"
            "`&info`"
        ),
        inline=False
    )

    embed.add_field(
        name="📢 Ogólne",
        value="`&ogloszenia` (ADMIN)",
        inline=False
    )

    embed.add_field(
        name="🛠 Moderacja",
        value=(
            "`&clear [ilość]`\n"
            "`&kick @user [powód]`\n"
            "`&ban @user [powód]`\n"
            "`&embed`"
        ),
        inline=False
    )

    await ctx.send(embed=embed)


# =====================
# EMBED BUILDER (ADMIN ONLY - FIXED)
# =====================
@bot.command()
@is_admin()
async def embed(ctx, *, content=None):

    if content is None:
        await ctx.send("❌ Użycie: `&embed tytuł|opis|blue/red/green/orange/purple|av on/off|stopka on/off`", delete_after=35)
        return

    try:
        title, desc, color, avatar, footer = content.split("|")

        colors = {
            "blue": discord.Color.blue(),
            "red": discord.Color.red(),
            "green": discord.Color.green(),
            "orange": discord.Color.orange(),
            "purple": discord.Color.purple()
        }

        embed = discord.Embed(
            title=title.strip(),
            description=desc.strip(),
            color=colors.get(color.strip().lower(), discord.Color.blue())
        )

        if avatar.strip().lower() == "on":
            embed.set_thumbnail(url=bot.user.display_avatar.url)

        if footer.strip().lower() == "on":
            embed.set_footer(text="CPM PL FIRE & RESCUE • Custom Embed")

        await ctx.send(embed=embed)

        await send_log(discord.Embed(
            title="🎨 CUSTOM EMBED",
            description=f"Autor: {ctx.author}",
            color=discord.Color.purple()
        ))

    except ValueError:
        await ctx.send(
            "❌ Zły format!\n"
            "`&embed tytuł|opis|blue|on|on`",
            delete_after=5
        )


# =====================
# ERROR HANDLER
# =====================
@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Nieznana komenda → `&pomoc`", delete_after=5)

    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("🔒 Brak uprawnień", delete_after=5)

    else:
        raise error


# =====================
# START BOT
# =====================
bot.run(os.getenv("TOKEN"))
