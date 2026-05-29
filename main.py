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
# PING (ALL)  
# =====================  
@bot.command()  
async def ping(ctx):  
    await ctx.send(f"🏓 Pong! `{round(bot.latency * 1000)}ms`")  
  
# =========================
# KONFIG
# =========================

ticket_config = {}
OWNER_ID = 975463222310219846


# =========================
# SETUP KOMENDA
# =========================

@bot.command()
async def ticket(ctx, channel_id: int):
    channel = bot.get_channel(channel_id)

    ticket_config[ctx.guild.id] = channel_id

    embed = discord.Embed(
        title="📩 System zgłoszeń",
        description="Kliknij przycisk poniżej aby otworzyć zgłoszenie.",
        color=discord.Color.blurple()
    )

    await channel.send(embed=embed, view=TicketViewPersistent())
    await ctx.send("✔ System ticketów ustawiony.")


# =========================
# PERSISTENT VIEW (NA START BOTA)
# =========================

class TicketViewPersistent(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🎫 Otwórz zgłoszenie",
        style=discord.ButtonStyle.green,
        custom_id="open_ticket_button"
    )
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):

        guild = interaction.guild
        user = interaction.user

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True),
        }

        for role in guild.roles:
            if role.permissions.administrator:
                overwrites[role] = discord.PermissionOverwrite(view_channel=True)

        channel = await guild.create_text_channel(
            name=f"ticket-{user.name}".lower(),
            overwrites=overwrites
        )

        await channel.send(
            f"Witaj {user.mention}, jestem asystentem i pomogę Ci z problemem.",
            view=TicketFormView(user.id)
        )

        await channel.send(
            "🔒 Aby zamknąć zgłoszenie kliknij przycisk poniżej.",
            view=CloseTicketView()
        )

        await interaction.response.send_message(
            f"✔ Utworzono zgłoszenie: {channel.mention}",
            ephemeral=True
        )


# =========================
# FORMULARZ W TICKECIE
# =========================

class TicketFormView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id

    @discord.ui.button(
        label="📝 Opisz problem",
        style=discord.ButtonStyle.primary,
        custom_id="ticket_form_button"
    )
    async def form(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TicketModal(self.user_id))


# =========================
# MODAL
# =========================

class TicketModal(discord.ui.Modal, title="Zgłoszenie"):

    category = discord.ui.TextInput(label="Kategoria")
    description = discord.ui.TextInput(label="Opis", style=discord.TextStyle.paragraph)

    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id

    async def on_submit(self, interaction: discord.Interaction):

        owner = await bot.fetch_user(OWNER_ID)

        embed = discord.Embed(
            title="📩 Nowe zgłoszenie",
            description=f"**User:** {interaction.user}\n"
                        f"**Kategoria:** {self.category}\n"
                        f"**Opis:** {self.description}",
            color=discord.Color.red()
        )

        await owner.send(embed=embed)

        await interaction.response.send_message(
            " ✅ Witaj! Przyjąłem Twoje zgłoszenie i już powiadomiłem support o Twojej sprawie 📩 \n \n 🛠️ Proszę o chwilę cierpliwości ktoś z zespołu wkrótce Ci pomoże 😊"
        )


# =========================
# ZAMYKANIE TICKETA
# =========================

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🔒 Zamknij ticket",
        style=discord.ButtonStyle.red,
        custom_id="close_ticket_button"
    )
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message(
            "🔒 Ticket zostanie zamknięty...",
            ephemeral=True
        )

        await interaction.channel.delete()

# =========================
# PERSISTENT VIEW REJESTRACJA
# =========================

@bot.event
async def on_ready():
    bot.add_view(TicketViewPersistent())
    bot.add_view(CloseTicketView())
    print("✔ Ticket system aktywny (persistent views loaded)")  


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
  
  
#========================
# PRZYPOMNIENIE ZMIANA NICKU
#========================
@bot.command()
async def przypomnienie(ctx, user: discord.Member):

    try:

        embed = discord.Embed(
            title="📌 Przypomnienie",
            description=(
                f"Cześć {user.mention} 👋\n\n"
                "Zauważyłem, że nie masz ustawionego nicku z gry na naszym serwerze ⚠️\n"
                "Proszę, zaktualizuj go jak najszybciej 🛠️\n\n"
                "Jeśli masz problem 😕, napisz do supportu na kanale "
                "<#1509566757378199742> 💬\n\n"
                "Dziękuję i życzę miłego dnia 😊"
            ),
            color=discord.Color.orange()
        )

        embed.set_footer(text="🤖 Wiadomość automatyczna od bota")

        await user.send(embed=embed)

        await ctx.send(f"✔ Przypomnienie wysłane do {user.mention} 📩")

    except discord.Forbidden:
        await ctx.send("❌ Nie mogę wysłać DM do tego użytkownika.")

    except Exception as e:
        await ctx.send(f"❌ Błąd: {e}")

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
   
# =========================
# WYBÓR KANAŁU
# =========================

class ChannelSelect(discord.ui.ChannelSelect):
    def __init__(self):
        super().__init__(
            placeholder="📢 Wybierz kanał wysyłki...",
            channel_types=[discord.ChannelType.text],
            min_values=1,
            max_values=1
        )

    async def callback(self, interaction: discord.Interaction):

        # zapisuje poprawny kanał
        self.view.send_channel = interaction.guild.get_channel(
            self.values[0].id
        )

        await interaction.response.send_message(
            f"✅ Kanał ustawiony: {self.view.send_channel.mention}",
            ephemeral=True
        )
  
  
# =========================  
# KREATOR EMBEDÓW  
# =========================  
  
class EmbedCreator(discord.ui.View):  
    def __init__(self, author):  
        super().__init__(timeout=600)  
  
        self.author = author  
  
        self.embed_title = "📢 Nowy Embed"  
        self.embed_description = "Opis embeda"  
  
        self.embed_color = discord.Color.blue()  
  
        self.footer_mode = "default"  
        self.custom_footer = None  
  
        self.image_mode = "bot"  
        self.image_url = None  
  
        self.timestamp_enabled = False  
  
        self.send_channel = None  
  
        self.used = False  # 🔒 blokada duplikatu  
  
        self.add_item(ChannelSelect())  
  
    # =========================  
    # EMBED BUILDER  
    # =========================  
  
    def build_embed(self):  
  
        embed = discord.Embed(  
            title=self.embed_title,  
            description=self.embed_description,  
            color=self.embed_color  
        )  
  
        # OBRAZEK  
        if self.image_mode == "bot":  
            embed.set_thumbnail(url=bot.user.display_avatar.url)  
  
        elif self.image_mode == "author":  
            embed.set_thumbnail(url=self.author.display_avatar.url)  
  
        elif self.image_mode == "custom" and self.image_url:  
            embed.set_image(url=self.image_url)  
  
        # STOPKA  
        if self.footer_mode == "default":  
            embed.set_footer(text="CPM PL FIRE & RESCUE • Custom Embed")  
  
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
  
        # TIMESTAMP  
        if self.timestamp_enabled:  
            embed.timestamp = discord.utils.utcnow()  
  
        return embed  
  
    # =========================  
    # EDYCJA TEKSTU  
    # =========================  
  
    @discord.ui.button(label="✏️ Edytuj tekst", style=discord.ButtonStyle.primary)  
    async def edit_text(self, interaction, button):  
  
        class TextModal(discord.ui.Modal, title="Edycja embeda"):  
  
            title_input = discord.ui.TextInput(  
                label="Tytuł",  
                default=self.embed_title,  
                max_length=256  
            )  
  
            desc_input = discord.ui.TextInput(  
                label="Opis",  
                style=discord.TextStyle.paragraph,  
                default=self.embed_description,  
                max_length=4000  
            )  
  
            async def on_submit(modal_self, interaction2):  
  
                self.embed_title = str(modal_self.title_input)  
                self.embed_description = str(modal_self.desc_input)  
  
                await interaction2.response.edit_message(  
                    embed=self.build_embed(),  
                    view=self  
                )  
  
        await interaction.response.send_modal(TextModal())  
  
    # =========================  
    # KOLOR  
    # =========================  
  
    @discord.ui.select(  
        placeholder="🎨 Wybierz kolor...",  
        options=[  
            discord.SelectOption(label="Niebieski", emoji="🔵"),  
            discord.SelectOption(label="Czerwony", emoji="🔴"),  
            discord.SelectOption(label="Zielony", emoji="🟢"),  
            discord.SelectOption(label="Pomarańczowy", emoji="🟠"),  
            discord.SelectOption(label="Fioletowy", emoji="🟣"),  
        ]  
    )  
    async def color_select(self, interaction, select):  
  
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
    # OBRAZ  
    # =========================  
  
    @discord.ui.select(  
        placeholder="🖼 Ustaw obraz...",  
        options=[  
            discord.SelectOption(label="Avatar bota", emoji="🤖"),  
            discord.SelectOption(label="Avatar autora", emoji="👤"),  
            discord.SelectOption(label="Własny obraz", emoji="🌆"),  
            discord.SelectOption(label="Wyłącz obraz", emoji="❌"),  
        ]  
    )  
    async def image_select(self, interaction, select):  
  
        choice = select.values[0]  
  
        if choice == "Avatar bota":  
            self.image_mode = "bot"  
  
        elif choice == "Avatar autora":  
            self.image_mode = "author"  
  
        elif choice == "Wyłącz obraz":  
            self.image_mode = "off"  
  
        elif choice == "Własny obraz":  
  
            class ImageModal(discord.ui.Modal, title="Własny obraz"):  
  
                url = discord.ui.TextInput(label="URL obrazka")  
  
                async def on_submit(modal_self, interaction2):  
                    self.image_mode = "custom"  
                    self.image_url = str(modal_self.url)  
  
                    await interaction2.response.edit_message(  
                        embed=self.build_embed(),  
                        view=self  
                    )  
  
            await interaction.response.send_modal(ImageModal())  
            return  
  
        await interaction.response.edit_message(  
            embed=self.build_embed(),  
            view=self  
        )  
  
    # =========================  
    # STOPKA  
    # =========================  
  
    @discord.ui.select(  
        placeholder="📄 Stopka...",  
        options=[  
            discord.SelectOption(label="Domyślna", emoji="📄"),  
            discord.SelectOption(label="Ikona bota", emoji="🤖"),  
            discord.SelectOption(label="Autor", emoji="👤"),  
            discord.SelectOption(label="Własna stopka", emoji="✏️"),  
            discord.SelectOption(label="Wyłącz stopkę", emoji="❌"),  
        ]  
    )  
    async def footer_select(self, interaction, select):  
  
        choice = select.values[0]  
  
        if choice == "Domyślna":  
            self.footer_mode = "default"  
  
        elif choice == "Ikona bota":  
            self.footer_mode = "bot"  
  
        elif choice == "Autor":  
            self.footer_mode = "author"  
  
        elif choice == "Wyłącz stopkę":  
            self.footer_mode = "off"  
  
        elif choice == "Własna stopka":  
  
            class FooterModal(discord.ui.Modal, title="Własna stopka"):  
  
                text = discord.ui.TextInput(label="Tekst stopki")  
  
                async def on_submit(modal_self, interaction2):  
                    self.footer_mode = "custom"  
                    self.custom_footer = str(modal_self.text)  
  
                    await interaction2.response.edit_message(  
                        embed=self.build_embed(),  
                        view=self  
                    )  
  
            await interaction.response.send_modal(FooterModal())  
            return  
  
        await interaction.response.edit_message(  
            embed=self.build_embed(),  
            view=self  
        )  
  
    # =========================  
    # TIMESTAMP  
    # =========================  
  
    @discord.ui.button(label="⏰ Data i godzina", style=discord.ButtonStyle.secondary)  
    async def timestamp_btn(self, interaction, button):  
  
        self.timestamp_enabled = not self.timestamp_enabled  
  
        await interaction.response.edit_message(  
            embed=self.build_embed(),  
            view=self  
        )  
  
    # =========================  
    # WYŚLIJ  
    # =========================  

    @discord.ui.button(label="✅ Wyślij",
style=discord.ButtonStyle.success
    )
    async def send(self, interaction: discord.Interaction, button):

        if self.used:
            return

        self.used = True

        channel = self.send_channel

        # fallback jeśli nie wybrano kanału
        if channel is None:
            channel = interaction.channel

        try:
            await channel.send(embed=self.build_embed())

            await interaction.response.edit_message(
                content="✅ Wysłano embed!",
                embed=None,
                view=None
            )

        except Exception as e:

            self.used = False

            await interaction.response.send_message(
                f"❌ Błąd podczas wysyłania:\n```python\n{e}\n```",
                ephemeral=True
            )

        self.stop()
 
  
    # =========================  
    # ZAMKNIJ  
    # =========================  
  
    @discord.ui.button(label="❌ Zamknij", style=discord.ButtonStyle.danger)  
    async def close(self, interaction, button):  
  
        await interaction.response.edit_message(  
            content="❌ Kreator zamknięty",  
            embed=None,  
            view=None  
        )  
  
        self.stop()  
  
# =========================  
# KOMENDA  
# =========================  
  
@bot.command()  
@commands.has_permissions(administrator=True)  
async def embed(ctx):  
  
    view = EmbedCreator(ctx.author)  
  
    await ctx.send(embed=view.build_embed(), view=view)  
  
  
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
