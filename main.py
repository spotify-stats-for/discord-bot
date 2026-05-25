import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="&", intents=intents)


# =====================
# STATUSY
# =====================
statuses = [
    "&help | CPM PL FIRE & RESCUE 🚒",
    "Car Parking Multiplayer 🚗",
    "RP Community Start 🔥",
    "Porucznik gotowy do działania 👨‍🚒"
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


# =====================
# CHECK ADMIN
# =====================
def is_admin():
    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator
    return commands.check(predicate)


# =====================
# HELP MENU (SELECT)
# =====================
class HelpSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="📢 Informacje", description="Info o serwerze RP"),
            discord.SelectOption(label="🎮 RP Start", description="Jak zacząć RP"),
            discord.SelectOption(label="🛠 Komendy Admina", description="Tylko dla administracji"),
        ]

        super().__init__(
            placeholder="Wybierz kategorię komend...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        embed = discord.Embed(color=discord.Color.blue())

        if self.values[0] == "📢 Informacje":
            embed.title = "📢 Informacje"
            embed.description = (
                "🚒 **CPM PL FIRE & RESCUE**\n\n"
                "Nowa społeczność RP w Car Parking Multiplayer 🚗\n"
                "Tworzymy role i realistyczne RP."
            )

        elif self.values[0] == "🎮 RP Start":
            embed.title = "🎮 Jak zacząć RP"
            embed.description = (
                "1️⃣ Wybierz role na selfrole\n"
                "2️⃣ Dołącz do aktywności na czacie\n"
                "3️⃣ Graj RP w Car Parking Multiplayer 🚗\n"
                "4️⃣ Twórz akcje i scenariusze 🚒"
            )

        elif self.values[0] == "🛠 Komendy Admina":
            embed.title = "🛠 Komendy Admina"

            embed.description = (
                "🔒 Dostęp tylko dla administracji\n\n"
                "`&clear` – usuń wiadomości\n"
                "`&kick` – wyrzuć użytkownika\n"
                "`&ban` – zbanuj użytkownika"
            )

        await interaction.response.edit_message(embed=embed)


class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(HelpSelect())


# =====================
# HELP COMMAND
# =====================
@bot.command(name="help")
async def help_cmd(ctx):
    await ctx.message.delete()

    embed = discord.Embed(
        title="📘 CPM PL FIRE & RESCUE HELP",
        description="Wybierz kategorię komend z menu poniżej 👇",
        color=discord.Color.green()
    )

    embed.set_thumbnail(url=bot.user.display_avatar.url)

    await ctx.send(embed=embed, view=HelpView())


# =====================
# INFO
# =====================
@bot.command()
async def info(ctx):
    await ctx.message.delete()

    embed = discord.Embed(
        title="🚒 CPM PL FIRE & RESCUE",
        description="Start społeczności RP w Car Parking Multiplayer 🚗",
        color=discord.Color.red()
    )

    embed.set_thumbnail(url=bot.user.display_avatar.url)

    await ctx.send(embed=embed)


# =====================
# ADMIN COMMAND EXAMPLE
# =====================
@bot.command()
@is_admin()
async def clear(ctx, amount: int = 10):
    await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f"🧹 Usunięto {amount} wiadomości")
    await msg.delete(delay=3)


# =====================
# OGŁOSZENIA
# =====================
@bot.command()
async def ogloszenia(ctx):
    await ctx.message.delete()

    embed = discord.Embed(
        title="🚒🔥 START RP COMMUNITY",
        description=(
            "**CPM PL FIRE & RESCUE**\n\n"
            "🚗 Car Parking Multiplayer RP\n"
            "🚒 Straż Pożarna\n"
            "🚓 Policja\n\n"
            "👉 Wybierz role na selfrole\n"
            "👉 Dołącz do społeczności RP\n"
        ),
        color=discord.Color.orange()
    )

    embed.set_thumbnail(url=bot.user.display_avatar.url)

    await ctx.send(embed=embed)


bot.run(os.getenv("TOKEN"))
