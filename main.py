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
class EmbedCreator(discord.ui.View):
    def __init__(self, author):
        super().__init__(timeout=600)

        self.author = author

        self.embed_title = "📢 Nowy Embed"
        self.embed_description = "Opis embeda"

        self.embed_color = discord.Color.blue()

        self.footer_mode = "default"
        self.image_mode = "thumbnail"

        self.custom_footer = None

        self.timestamp_enabled = False

        self.channel = None

    # =========================
    # BUDOWANIE EMBEDA
    # =========================

    def build_embed(self):

        embed = discord.Embed(
            title=self.embed_title,
            description=self.embed_description,
            color=self.embed_color
        )

        # MINIATURKA
        if self.image_mode == "thumbnail":
            embed.set_thumbnail(url=bot.user.display_avatar.url)

        elif self.image_mode == "author":
            embed.set_thumbnail(url=self.author.display_avatar.url)

        # STOPKA
        if self.footer_mode == "default":
            embed.set_footer(
                text="CPM PL FIRE & RESCUE • Custom Embed"
            )

        elif self.footer_mode == "bot":
            embed.set_footer(
                text="CPM PL FIRE & RESCUE • Custom Embed",
                icon_url=bot.user.display_avatar.url
            )

        elif self.footer_mode == "author":
            embed.set_footer(
                text=f"Autor: {self.author}",
                icon_url=self.author.display_avatar.url
            )

        elif self.footer_mode == "custom" and self.custom_footer:
            embed.set_footer(text=self.custom_footer)

        # DATA I GODZINA
        if self.timestamp_enabled:
            embed.timestamp = discord.utils.utcnow()

        return embed

    # =========================
    # EDYTUJ TEKST
    # =========================

    @discord.ui.button(
        label="✏️ Edytuj tekst",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def edit_text(self, interaction, button):

        class TextModal(discord.ui.Modal, title="Edycja embeda"):

            title_input = discord.ui.TextInput(
                label="Tytuł",
                default=self.embed_title,
                max_length=256
            )

            description_input = discord.ui.TextInput(
                label="Opis",
                style=discord.TextStyle.paragraph,
                default=self.embed_description,
                max_length=4000
            )

            async def on_submit(modal_self, interaction2):

                self.embed_title = str(modal_self.title_input)
                self.embed_description = str(modal_self.description_input)

                await interaction2.response.edit_message(
                    embed=self.build_embed(),
                    view=self
                )

        await interaction.response.send_modal(TextModal())

    # =========================
    # WYBÓR KOLORU
    # =========================

    @discord.ui.select(
        placeholder="🎨 Wybierz kolor...",
        options=[
            discord.SelectOption(label="Niebieski", emoji="🔵"),
            discord.SelectOption(label="Czerwony", emoji="🔴"),
            discord.SelectOption(label="Zielony", emoji="🟢"),
            discord.SelectOption(label="Pomarańczowy", emoji="🟠"),
            discord.SelectOption(label="Fioletowy", emoji="🟣"),
        ],
        row=1
    )
    async def select_color(self, interaction, select):

        colors = {
            "Niebieski": discord.Color.blue(),
            "Czerwony": discord.Color.red(),
            "Zielony": discord.Color.green(),
            "Pomarańczowy": discord.Color.orange(),
            "Fioletowy": discord.Color.purple()
        }

        self.embed_color = colors[select.values[0]]

        await interaction.response.edit_message(
            embed=self.build_embed(),
            view=self
        )

    # =========================
    # ZDJĘCIE
    # =========================

    @discord.ui.button(
        label="🖼 Zdjęcie",
        style=discord.ButtonStyle.secondary,
        row=2
    )
    async def image_button(self, interaction, button):

        if self.image_mode == "thumbnail":
            self.image_mode = "author"

        elif self.image_mode == "author":
            self.image_mode = "off"

        else:
            self.image_mode = "thumbnail"

        await interaction.response.edit_message(
            embed=self.build_embed(),
            view=self
        )

    # =========================
    # STOPKA
    # =========================

    @discord.ui.button(
        label="📄 Stopka",
        style=discord.ButtonStyle.secondary,
        row=2
    )
    async def footer_button(self, interaction, button):

        if self.footer_mode == "default":
            self.footer_mode = "bot"

        elif self.footer_mode == "bot":
            self.footer_mode = "author"

        elif self.footer_mode == "author":
            self.footer_mode = "off"

        else:
            self.footer_mode = "default"

        await interaction.response.edit_message(
            embed=self.build_embed(),
            view=self
        )

    # =========================
    # DATA I GODZINA
    # =========================

    @discord.ui.button(
        label="⏰ Data i godzina",
        style=discord.ButtonStyle.secondary,
        row=2
    )
    async def timestamp_button(self, interaction, button):

        self.timestamp_enabled = not self.timestamp_enabled

        await interaction.response.edit_message(
            embed=self.build_embed(),
            view=self
        )

    # =========================
    # GOTOWE SZABLONY
    # =========================

    @discord.ui.select(
        placeholder="🔥 Gotowe szablony...",
        options=[
            discord.SelectOption(label="Ogłoszenie", emoji="📢"),
            discord.SelectOption(label="Alarm", emoji="🚨"),
            discord.SelectOption(label="Rekrutacja", emoji="✅"),
            discord.SelectOption(label="Regulamin", emoji="⚠️"),
        ],
        row=3
    )
    async def templates(self, interaction, select):

        selected = select.values[0]

        if selected == "Ogłoszenie":
            self.embed_title = "📢 OGŁOSZENIE"
            self.embed_description = "Treść ogłoszenia..."
            self.embed_color = discord.Color.blue()

        elif selected == "Alarm":
            self.embed_title = "🚨 ALARM"
            self.embed_description = "Treść alarmu..."
            self.embed_color = discord.Color.red()

        elif selected == "Rekrutacja":
            self.embed_title = "✅ REKRUTACJA"
            self.embed_description = "Rekrutacja została otwarta."
            self.embed_color = discord.Color.green()

        elif selected == "Regulamin":
            self.embed_title = "⚠️ REGULAMIN"
            self.embed_description = "Zapoznaj się z regulaminem."
            self.embed_color = discord.Color.orange()

        await interaction.response.edit_message(
            embed=self.build_embed(),
            view=self
        )

    # =========================
    # WYCZYŚĆ
    # =========================

    @discord.ui.button(
        label="🧹 Wyczyść",
        style=discord.ButtonStyle.danger,
        row=4
    )
    async def clear_embed(self, interaction, button):

        self.embed_title = "📢 Nowy Embed"
        self.embed_description = "Opis embeda"

        self.embed_color = discord.Color.blue()

        await interaction.response.edit_message(
            embed=self.build_embed(),
            view=self
        )

    # =========================
    # WYŚLIJ
    # =========================

    @discord.ui.button(
        label="✅ Wyślij embed",
        style=discord.ButtonStyle.success,
        row=4
    )
    async def send_embed(self, interaction, button):

        await interaction.channel.send(
            embed=self.build_embed()
        )

        await interaction.response.send_message(
            "✅ Embed został wysłany.",
            ephemeral=True
        )

        await send_log(discord.Embed(
            title="🎨 CUSTOM EMBED",
            description=f"Autor: {interaction.user}",
            color=discord.Color.purple()
        ))

    # =========================
    # ZAMKNIJ
    # =========================

    @discord.ui.button(
        label="❌ Zamknij",
        style=discord.ButtonStyle.gray,
        row=4
    )
    async def close_creator(self, interaction, button):

        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(
            content="❌ Kreator został zamknięty.",
            embed=None,
            view=self
        )


# =========================
# KOMENDA
# =========================

@bot.command()
@is_admin()
async def embed(ctx):

    view = EmbedCreator(ctx.author)

    await ctx.send(
        embed=view.build_embed(),
        view=view
    )


# =====================
# ERROR HANDLER
# =====================
@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Nieznana komenda → `&pomoc`", delete_after=10)

    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("🔒 Brak uprawnień", delete_after=10)

    else:
        raise error


# =====================
# START BOT
# =====================
bot.run(os.getenv("TOKEN"))
