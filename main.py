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
# CHECK ADMIN
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
        description=(
            "🚗 Car Parking Multiplayer RP\n\n"
            "🔥 Służby RP:\n"
            "🚒 OSP\n"
            "🚒 PSP\n"
            "🚓 POLICJA\n"
            "🚑 ZRM"
        ),
        color=discord.Color.red()
    )

    embed.set_thumbnail(url=bot.user.display_avatar.url)

    await ctx.send(embed=embed)


# =====================
# OGŁOSZENIA (ADMIN ONLY)
# =====================
@bot.command()
@is_admin()
async def ogloszenia(ctx):
    await ctx.message.delete()

    embed = discord.Embed(
        title="**CPM PL FIRE & RESCUE**",
        description=(
            "🚗 Car Parking Multiplayer RP\n"
            "(Car Parking Multiplayer – gra symulacyjna RP)\n\n"
            "🚒 OSP – Ochotnicza Straż Pożarna\n"
            "🚒 PSP – Państwowa Straż Pożarna\n"
            "🚓 POLICJA – jednostki porządkowe\n"
            "🚑 ZRM – Zespół Ratownictwa Medycznego\n\n"
            "👉 Wybierz role na <#1508527145658351730>\n"
            "👉 Dołącz do społeczności RP\n"
            "👉 Zacznij pisać na <#1508552147707498608>\n"
        ),
        color=discord.Color.orange()
    )

    embed.set_thumbnail(url=bot.user.display_avatar.url)

    await ctx.send(embed=embed)


# =====================
# CLEAR (ADMIN ONLY + ERROR FIX)
# =====================
@bot.command()
@is_admin()
async def clear(ctx, amount: int = None):

    if amount is None:
        embed = discord.Embed(
            title="❌ Błąd",
            description="Podaj liczbę wiadomości!\nPrzykład: `&clear 10`",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, delete_after=5)
        return

    await ctx.channel.purge(limit=amount + 1)

    msg = await ctx.send(f"🧹 Usunięto `{amount}` wiadomości")
    await msg.delete(delay=3)


# =====================
# KICK (ADMIN)
# =====================
@bot.command()
@is_admin()
async def kick(ctx, member: discord.Member, *, reason="Brak powodu"):
    await member.kick(reason=reason)
    await ctx.send(f"👢 Wyrzucono {member.mention} | {reason}")


# =====================
# BAN (ADMIN)
# =====================
@bot.command()
@is_admin()
async def ban(ctx, member: discord.Member, *, reason="Brak powodu"):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 Zbanowano {member.mention} | {reason}")


# =====================
# HELP (KATEGORIE)
# =====================
@bot.command(name="pomoc")
async def pomoc(ctx):
    await ctx.message.delete()

    embed = discord.Embed(
        title="📘 CPM PL FIRE & RESCUE • POMOC",
        description="Kategorie komend 🚒",
        color=discord.Color.green()
    )

    embed.set_thumbnail(url=bot.user.display_avatar.url)

    embed.add_field(
        name="👥 Dla wszystkich",
        value=(
            "`&ping` – sprawdź ping\n"
            "`&info` – info o RP"
        ),
        inline=False
    )

    embed.add_field(
        name="📢 Ogólne",
        value="`&ogloszenia` – ogłoszenie RP (admin)",
        inline=False
    )

    embed.add_field(
        name="🛠 Administracja",
        value=(
            "`&clear`\n"
            "`&kick`\n"
            "`&ban`"
        ),
        inline=False
    )

    await ctx.send(embed=embed)


# =====================
# ERROR HANDLER
# =====================
@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(
            title="❌ Nieznana komenda",
            description="Użyj `&pomoc`, aby zobaczyć dostępne komendy.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, delete_after=5)

    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="🔒 Brak uprawnień",
            description="Nie masz dostępu do tej komendy.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, delete_after=5)

    else:
        raise error


# =====================
# START BOT
# =====================
bot.run(os.getenv("TOKEN"))
