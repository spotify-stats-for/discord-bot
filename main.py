import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="&", intents=intents, help_command=None)


# =====================
# STATUSY
# =====================
statuses = [
    "&pomoc | CPM PL FIRE & RESCUE 🚒",
    "Car Parking Multiplayer 🚗",
    "RP • OSP / PSP / POLICJA / ZRM 🔥"
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
# PING (dla wszystkich)
# =====================
@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong! `{round(bot.latency * 1000)}ms`")


# =====================
# INFO
# =====================
@bot.command()
async def info(ctx):
    await ctx.message.delete()

    embed = discord.Embed(
        title="🚒 CPM PL FIRE & RESCUE",
        description=(
            "🚗 **Car Parking Multiplayer RP**\n\n"
            "🔥 Społeczność RP:\n"
            "🚒 OSP (Ochotnicza Straż Pożarna)\n"
            "🚒 PSP (Państwowa Straż Pożarna)\n"
            "🚓 POLICJA\n"
            "🚑 ZRM (Zespół Ratownictwa Medycznego)\n"
        ),
        color=discord.Color.red()
    )

    embed.set_thumbnail(url=bot.user.display_avatar.url)

    await ctx.send(embed=embed)


# =====================
# OGŁOSZENIE (TWÓJ STYL)
# =====================
@bot.command()
async def ogloszenia(ctx):
    await ctx.message.delete()

    embed = discord.Embed(
        title="**CPM PL FIRE & RESCUE**",
        description=(
            "🚗 **Car Parking Multiplayer RP**\n"
            "(Car Parking Multiplayer – gra symulacyjna RP w otwartym świecie)\n\n"
            "🚒 OSP – Ochotnicza Straż Pożarna\n"
            "🚒 PSP – Państwowa Straż Pożarna\n"
            "🚓 POLICJA – służby porządkowe\n"
            "🚑 ZRM – Zespół Ratownictwa Medycznego\n\n"
            "👉 Wybierz role na <#1508527145658351730>\n"
            "👉 Dołącz do społeczności RP\n"
            "👉 Zacznij pisać na <#1508552147707498608>\n"
        ),
        color=discord.Color.orange()
    )

    # LOGO BOTA (bez zmian)
    embed.set_thumbnail(url=bot.user.display_avatar.url)

    await ctx.send(embed=embed)


# =====================
# HELP (ULEPSZONY)
# =====================
@bot.command(name="pomoc")
async def pomoc(ctx):
    await ctx.message.delete()

    embed = discord.Embed(
        title="📘 CPM PL FIRE & RESCUE • POMOC",
        description="Lista dostępnych komend bota RP 🚒",
        color=discord.Color.green()
    )

    embed.set_thumbnail(url=bot.user.display_avatar.url)

    # PUBLICZNE KOMENDY
    embed.add_field(
        name="👥 Komendy dla wszystkich",
        value=(
            "`&ping` – sprawdź opóźnienie bota\n"
            "`&info` – informacje o społeczności RP\n"
            "`&ogloszenia` – oficjalne ogłoszenie RP"
        ),
        inline=False
    )

    # ADMIN KOMENDY
    embed.add_field(
        name="🛠 Komendy administracyjne",
        value=(
            "`&clear [ilość]` – usuwa wiadomości (admin)\n"
        ),
        inline=False
    )

    embed.set_footer(text="CPM PL FIRE & RESCUE • RP Community")

    await ctx.send(embed=embed)


# =====================
# ADMIN CLEAR
# =====================
def is_admin():
    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator
    return commands.check(predicate)


@bot.command()
@is_admin()
async def clear(ctx, amount: int = 10):
    await ctx.channel.purge(limit=amount + 1)


bot.run(os.getenv("TOKEN"))
