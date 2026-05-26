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
        title="CPM PL FIRE & RESCUE",
        description=(
            "Drodzy gracze oraz pasjonaci roleplay! 👋\n\n"
            "Z ogromną przyjemnością ogłaszamy otwarcie nowej społeczności RP w grze Car Parking Multiplayer 🎮, "
            "stworzonej z myślą o realistycznych scenariuszach służb ratunkowych.\n\n"
            "🚓🚑🚒 CMP PL FIRE & RESCUE to miejsce łączące Policję, Pogotowie i Straż Pożarną.\n\n"
            "Naszym celem jest aktywna i zorganizowana społeczność 🤝, gdzie każdy może wcielić się w rolę i brać udział w akcjach.\n\n"
            "🔥 Co oferujemy:\n"
            "• Realistyczne RP służb 🚓🚑🚒\n"
            "• Aktywną administrację 👮‍♂️\n"
            "• Patrole i eventy 📢\n"
            "• Awans i rozwój 📈\n\n"
            "💬 Szukamy osób zaangażowanych i chętnych do współpracy.\n\n"
            "🌟 Zapraszamy do dołączenia!"
        ),
        color=discord.Color.orange()
    )

    embed.set_footer(
        text="CMP PL FIRE & RESCUE",
        icon_url=bot.user.display_avatar.url
    )

    await ctx.send(embed=embed)

    # LOG SYSTEM (to co usunąłem przypadkiem)
    await send_log(
        discord.Embed(
            title="📢 OGŁOSZENIE",
            description=f"Autor: {ctx.author}",
            color=discord.Color.orange()
        )
    )


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
class HelpMenu(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Strona główna",
                description="Powrót do menu głównego",
                emoji="🏠"
            ),

            discord.SelectOption(
                label="Dla wszystkich",
                description="Komendy użytkowników",
                emoji="👥"
            ),

            discord.SelectOption(
                label="Ogólne",
                description="Ogólne komendy serwera",
                emoji="📢"
            ),

            discord.SelectOption(
                label="Moderacja",
                description="Komendy administracyjne",
                emoji="🛠"
            ),
        ]

        super().__init__(
            placeholder="📂 Wybierz kategorię komend...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        # =========================
        # STRONA GŁÓWNA
        # =========================
        if self.values[0] == "Strona główna":

            embed = discord.Embed(
                title="📘 CPM PL FIRE & RESCUE • HELP",
                description=(
                    "Wybierz kategorię komend z menu poniżej.\n\n"
                    "👥 Komendy użytkowników\n"
                    "📢 Komendy ogólne\n"
                    "🛠 Komendy moderacyjne"
                ),
                color=discord.Color.green()
            )

        # =========================
        # DLA WSZYSTKICH
        # =========================
        elif self.values[0] == "Dla wszystkich":

            embed = discord.Embed(
                title="👥 Dla wszystkich",
                color=discord.Color.green()
            )

            embed.add_field(
                name="`&ping`",
                value="Sprawdza opóźnienie bota.",
                inline=False
            )

            embed.add_field(
                name="`&info`",
                value="Pokazuje informacje o serwerze lub bocie.",
                inline=False
            )

        # =========================
        # OGÓLNE
        # =========================
        elif self.values[0] == "Ogólne":

            embed = discord.Embed(
                title="📢 Ogólne",
                color=discord.Color.blue()
            )

            embed.add_field(
                name="`&ogloszenia`",
                value="Wysyła oficjalne ogłoszenie administracji.",
                inline=False
            )

        # =========================
        # MODERACJA
        # =========================
        elif self.values[0] == "Moderacja":

            embed = discord.Embed(
                title="🛠 Moderacja",
                color=discord.Color.red()
            )

            embed.add_field(
                name="`&clear [ilość]`",
                value="Usuwa wybraną liczbę wiadomości.",
                inline=False
            )

            embed.add_field(
                name="`&kick @user [powód]`",
                value="Wyrzuca użytkownika z serwera.",
                inline=False
            )

            embed.add_field(
                name="`&ban @user [powód]`",
                value="Banuje użytkownika na serwerze.",
                inline=False
            )

            embed.add_field(
                name="`&embed`",
                value="Wysyła własny embed.",
                inline=False
            )

        embed.set_thumbnail(url=interaction.client.user.display_avatar.url)

        embed.set_footer(
            text=f"Wybrane przez: {interaction.user}",
            icon_url=interaction.user.display_avatar.url
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self.view
        )


class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(HelpMenu())


@bot.command(name="pomoc")
async def pomoc(ctx):
    await ctx.message.delete()

    embed = discord.Embed(
        title="📘 CPM PL FIRE & RESCUE • HELP",
        description=(
            "Wybierz kategorię komend z menu poniżej.\n\n"
            "👥 Komendy użytkowników\n"
            "📢 Komendy ogólne\n"
            "🛠 Komendy moderacyjne"
        ),
        color=discord.Color.green()
    )

    embed.set_thumbnail(url=bot.user.display_avatar.url)

    embed.set_footer(
        text=f"Wywołane przez: {ctx.author}",
        icon_url=ctx.author.display_avatar.url
    )

    await ctx.send(
        embed=embed,
        view=HelpView()
    )


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
