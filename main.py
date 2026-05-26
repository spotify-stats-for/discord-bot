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
# FIX: KOMENDY MUSZĄ DZIAŁAĆ Z ON_MESSAGE
# =====================
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await bot.process_commands(message)


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
# PING
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
        description="Car Parking Multiplayer RP 🚗",
        color=discord.Color.red()
    )

    embed.set_thumbnail(url=bot.user.display_avatar.url)

    await ctx.send(embed=embed)


# =====================
# OGŁOSZENIA
# =====================
@bot.command()
@is_admin()
async def ogloszenia(ctx):
    await ctx.message.delete()

    embed = discord.Embed(
        title="CPM PL FIRE & RESCUE",
        description="Ogłoszenie administracji...",
        color=discord.Color.orange()
    )

    embed.set_footer(
        text="CMP PL FIRE & RESCUE",
        icon_url=bot.user.display_avatar.url
    )

    await ctx.send(embed=embed)

    await send_log(discord.Embed(
        title="📢 OGŁOSZENIE",
        description=f"Autor: {ctx.author}",
        color=discord.Color.orange()
    ))


# =====================
# CLEAR
# =====================
@bot.command()
@is_admin()
async def clear(ctx, amount: int):

    deleted = await ctx.channel.purge(limit=amount + 1)

    msg = await ctx.send(f"🧹 Usunięto `{len(deleted)-1}` wiadomości")
    await msg.delete(delay=3)


# =====================
# HELP (bez zmian logiki)
# =====================
class HelpMenu(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Strona główna", emoji="🏠"),
            discord.SelectOption(label="Dla wszystkich", emoji="👥"),
            discord.SelectOption(label="Ogólne", emoji="📢"),
            discord.SelectOption(label="Moderacja", emoji="🛠"),
        ]

        super().__init__(
            placeholder="📂 Wybierz kategorię...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        choice = self.values[0]

        if choice == "Strona główna":
            embed = discord.Embed(
                title="HELP",
                description="Wybierz kategorię",
                color=discord.Color.green()
            )

        elif choice == "Dla wszystkich":
            embed = discord.Embed(title="Dla wszystkich", color=discord.Color.green())
            embed.add_field(name="&ping", value="Ping bota", inline=False)
            embed.add_field(name="&info", value="Info", inline=False)

        elif choice == "Ogólne":
            embed = discord.Embed(title="Ogólne", color=discord.Color.blue())
            embed.add_field(name="&ogloszenia", value="Ogłoszenia", inline=False)

        else:
            embed = discord.Embed(title="Moderacja", color=discord.Color.red())
            embed.add_field(name="&clear", value="Czyszczenie", inline=False)
            embed.add_field(name="&kick", value="Wyrzucanie", inline=False)
            embed.add_field(name="&ban", value="Ban", inline=False)

        await interaction.response.edit_message(embed=embed, view=self.view)


class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(HelpMenu())


@bot.command()
async def pomoc(ctx):
    await ctx.message.delete()

    embed = discord.Embed(
        title="HELP",
        description="Wybierz kategorię",
        color=discord.Color.green()
    )

    await ctx.send(embed=embed, view=HelpView())


# =====================
# EMBED CREATOR FIX
# =====================

class EmbedCreator(discord.ui.View):

    _active_sessions = set()

    def __init__(self, author):
        super().__init__(timeout=600)

        if author.id in self._active_sessions:
            raise Exception("Masz już aktywny panel!")

        self._active_sessions.add(author.id)

        self.author = author

        self.embed_title = "Nowy Embed"
        self.embed_description = "Opis"

        self.embed_color = discord.Color.blue()

        self.footer_mode = "default"
        self.custom_footer = None

        self.image_mode = "bot"
        self.image_url = None

        self.timestamp_enabled = False

        self.send_channel = None

        self.used = False

        self.add_item(ChannelSelect())

    def build_embed(self):

        embed = discord.Embed(
            title=self.embed_title,
            description=self.embed_description,
            color=self.embed_color
        )

        if self.image_mode == "bot":
            embed.set_thumbnail(url=bot.user.display_avatar.url)

        elif self.image_mode == "author":
            embed.set_thumbnail(url=self.author.display_avatar.url)

        elif self.image_mode == "custom":
            embed.set_image(url=self.image_url)

        if self.footer_mode == "default":
            embed.set_footer(text="CPM PL FIRE & RESCUE")

        elif self.footer_mode == "custom":
            embed.set_footer(text=self.custom_footer)

        if self.timestamp_enabled:
            embed.timestamp = discord.utils.utcnow()

        return embed

    # =====================
    # WYŚLIJ
    # =====================
    @discord.ui.button(label="Wyślij", style=discord.ButtonStyle.success)
    async def send(self, interaction, button):

        if self.used:
            return

        self.used = True

        channel = self.send_channel or interaction.channel

        await channel.send(embed=self.build_embed())

        self._active_sessions.discard(self.author.id)

        await interaction.response.edit_message(
            content="Wysłano embed",
            embed=None,
            view=None
        )

        self.stop()

    # =====================
    # ZAMKNIJ
    # =====================
    @discord.ui.button(label="Zamknij", style=discord.ButtonStyle.danger)
    async def close(self, interaction, button):

        self._active_sessions.discard(self.author.id)

        await interaction.response.edit_message(
            content="Zamknięto",
            embed=None,
            view=None
        )

        self.stop()


# =====================
# KOMENDA EMBED
# =====================
@bot.command()
@is_admin()
async def embed(ctx):

    await ctx.message.delete()

    view = EmbedCreator(ctx.author)

    await ctx.send(embed=view.build_embed(), view=view)


# =====================
# START
# =====================
bot.run(os.getenv("TOKEN"))