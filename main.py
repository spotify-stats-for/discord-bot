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
# KOMENDY DLA WSZYSTKICH
# =====================
@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong! `{round(bot.latency * 1000)}ms`")


@bot.command()
async def info(ctx):
    await ctx.message.delete()

    embed = discord.Embed(
        title="🚒 CPM PL FIRE & RESCUE",
        description=(
            "🚗 **Car Parking Multiplayer RP**\n\n"
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
# OGŁOSZENIA (TYLKO ADMIN)
# =====================
@bot.command()
@is_admin()
async def ogloszenia(ctx):
    await ctx.message.delete()

    embed = discord.Embed(
        title="**CPM PL FIRE & RESCUE**",
        description=(
            "🚗 Car Parking Multiplayer RP\n"
            "(Car Parking Multiplayer – gra RP)\n\n"
            "🚒 OSP – Ochotnicza Straż Pożarna\n"
            "🚒 PSP – Państwowa Straż Pożarna\n"
            "🚓 POLICJA – jednostki porządkowe\n"
            "🚑 ZRM – ratownictwo medyczne\n\n"
            "👉 Wybierz role na <#1508527145658351730>\n"
            "👉 Dołącz do społeczności RP\n"
            "👉 Zacznij pisać na <#1508552147707498608>\n"
        ),
        color=discord.Color.orange()
    )

    embed.set_thumbnail(url=bot.user.display_avatar.url)

    await ctx.send(embed=embed)


# =====================
# KICK (ADMIN)
# =====================
@bot.command()
@is_admin()
async def kick(ctx, member: discord.Member, *, reason="Brak powodu"):
    await member.kick(reason=reason)
    await ctx.send(f"👢 Wyrzucono {member.mention} | Powód: {reason}")


# =====================
# BAN (ADMIN)
# =====================
@bot.command()
@is_admin()
async def ban(ctx, member: discord.Member, *, reason="Brak powodu"):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 Zbanowano {member.mention} | Powód: {reason}")


# =====================
# HELP (KATEGORIE ZOSTAJĄ)
# =====================
@bot.command(name="pomoc")
async def pomoc(ctx):
    await ctx.message.delete()

    embed = discord.Embed(
        title="📘 CPM PL FIRE & RESCUE • POMOC",
        description="Kategorie komend bota 🚒",
        color=discord.Color.green()
    )

    embed.set_thumbnail(url=bot.user.display_avatar.url)

    embed.add_field(
        name="👥 Dla wszystkich",
        value=(
            "`&ping` – sprawdź ping bota\n"
            "`&info` – informacje o RP"
        ),
        inline=False
    )

    embed.add_field(
        name="📢 Ogólne RP",
        value=(
            "`&ogloszenia` – ogłoszenie serwera RP"
        ),
        inline=False
    )

    embed.add_field(
        name="🛠 Administracja",
        value=(
            "`&kick @user [powód]`\n"
            "`&ban @user [powód]`\n"
        ),
        inline=False
    )

    embed.set_footer(text="CPM PL FIRE & RESCUE • RP System")

    await ctx.send(embed=embed)


bot.run(os.getenv("TOKEN"))
