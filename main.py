import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="&", intents=intents)

# ===== STATUSY =====
statuses = [
    "*Gra w* Car Parking Multiplayer",
    "Porucznik gotowy do działania 🚒"
]

status_index = 0


@tasks.loop(seconds=15)
async def change_status():
    global status_index

    activity = discord.Game(name=statuses[status_index])
    await bot.change_presence(activity=activity)

    status_index = (status_index + 1) % len(statuses)


@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}")
    change_status.start()


# ===== KOMENDA OGŁOSZENIA =====
@bot.command(name="ogloszenia")
async def ogloszenia(ctx):

    # usuwa wiadomość z komendą
    await ctx.message.delete()

    embed = discord.Embed(
        title="📢 OGŁOSZENIE",
        description=(
            "**CPM PL FIRE & RESCUE**\n\n"
            "Właśnie doszło do **otwarcia serwera/społeczności RP** w grze "
            "**Car Parking Multiplayer**.\n\n"
            "🔴 Zachęcamy wszystkich do dalszej aktywności i budowy społeczności.\n\n"
            "👉 Wybierz swoje role na kanale: <#SELFROLE_ID>\n"
            "👉 Pisz na czacie i bądź aktywny!\n\n"
            "🚒 CPM PL FIRE & RESCUE nadal działa i szuka nowych członków!"
        ),
        color=discord.Color.red()
    )

    embed.set_footer(text="CPM PL FIRE & RESCUE • RP Community")

    await ctx.send(embed=embed)


bot.run(os.getenv("TOKEN"))
