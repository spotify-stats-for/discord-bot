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
# FIX: KOMENDY MUSZĄ DZIAŁAĆ (to był kluczowy bug u Ciebie)
# =====================
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await bot.process_commands(message)


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
# PING / INFO / OGŁOSZENIA / CLEAR / KICK / BAN
# (tu NIC nie zmieniam funkcjonalnie)
# =====================

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong! `{round(bot.latency * 1000)}ms`")


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


@bot.command()
@is_admin()
async def ogloszenia(ctx):
    await ctx.message.delete()

    embed = discord.Embed(
        title="CPM PL FIRE & RESCUE",
        description="Ogłoszenie administracji",
        color=discord.Color.orange()
    )

    await ctx.send(embed=embed)

    await send_log(discord.Embed(
        title="📢 OGŁOSZENIE",
        description=f"Autor: {ctx.author}",
        color=discord.Color.orange()
    ))


@bot.command()
@is_admin()
async def clear(ctx, amount: int):
    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 Usunięto `{len(deleted)-1}`", delete_after=3)


@bot.command()
@is_admin()
async def kick(ctx, member: discord.Member, *, reason="Brak"):
    await member.kick(reason=reason)
    await ctx.send("Wyrzucono")

@bot.command()
@is_admin()
async def ban(ctx, member: discord.Member, *, reason="Brak"):
    await member.ban(reason=reason)
    await ctx.send("Zbanowano")


# =====================
# HELP (bez zmian logiki)
# =====================
class HelpMenu(discord.ui.Select):
    def __init__(self):
        super().__init__(
            placeholder="Wybierz kategorię",
            options=[
                discord.SelectOption(label="Strona główna"),
                discord.SelectOption(label="Dla wszystkich"),
                discord.SelectOption(label="Ogólne"),
                discord.SelectOption(label="Moderacja"),
            ]
        )

    async def callback(self, interaction: discord.Interaction):

        choice = self.values[0]

        if choice == "Strona główna":
            embed = discord.Embed(title="HELP", description="Menu")

        elif choice == "Dla wszystkich":
            embed = discord.Embed(title="User")

        elif choice == "Ogólne":
            embed = discord.Embed(title="Info")

        else:
            embed = discord.Embed(title="Moderacja")

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
        description="Wybierz kategorię"
    )

    await ctx.send(embed=embed, view=HelpView())


# =====================
# EMBED CREATOR (NAPRAWIONY CORE)
# =====================

class EmbedCreator(discord.ui.View):

    active_sessions = set()

    def __init__(self, author):
        super().__init__(timeout=600)

        # 🔥 FIX: blokada multi panel
        if author.id in self.active_sessions:
            raise Exception("Masz już aktywny panel!")

        self.active_sessions.add(author.id)

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

        self._lock = False  # 🔥 dodatkowa ochrona

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

        elif self.image_mode == "custom" and self.image_url:
            embed.set_image(url=self.image_url)

        if self.footer_mode == "default":
            embed.set_footer(text="CPM PL FIRE & RESCUE")

        elif self.footer_mode == "custom" and self.custom_footer:
            embed.set_footer(text=self.custom_footer)

        if self.timestamp_enabled:
            embed.timestamp = discord.utils.utcnow()

        return embed


    # =====================
    # WYŚLIJ (FIX DUPLIKATÓW)
    # =====================
    @discord.ui.button(label="Wyślij", style=discord.ButtonStyle.success)
    async def send(self, interaction, button):

        if self.used or self._lock:
            return

        self.used = True
        self._lock = True

        channel = self.send_channel or interaction.channel

        await channel.send(embed=self.build_embed())

        self.active_sessions.discard(self.author.id)

        await interaction.response.edit_message(
            content="Wysłano embed",
            embed=None,
            view=None
        )

        self.stop()


    # =====================
    # ZAMKNIJ (CLEAN)
    # =====================
    @discord.ui.button(label="Zamknij", style=discord.ButtonStyle.danger)
    async def close(self, interaction, button):

        self.active_sessions.discard(self.author.id)

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