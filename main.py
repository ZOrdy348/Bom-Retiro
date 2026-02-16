import discord
from discord.ext import commands
from discord import app_commands

TOKEN = "SEU_TOKEN"
GUILD_ID = 1234567890
CATEGORY_TICKETS = 1234567890
ROLE_STAFF = 1234567890

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

tickets_ativos = True

# =========================
# SELECT
# =========================

class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Assuntos Internos", emoji="📂"),
            discord.SelectOption(label="Suporte Geral Bom Retiro", emoji="🛠️"),
            discord.SelectOption(label="Denúncias", emoji="🚨"),
            discord.SelectOption(label="Dúvidas", emoji="❓"),
        ]
        super().__init__(placeholder="Escolha o atendimento...", options=options)

    async def callback(self, interaction: discord.Interaction):

        if not tickets_ativos:
            await interaction.response.send_message("Os tickets estão desativados.", ephemeral=True)
            return

        guild = interaction.guild
        category = guild.get_channel(CATEGORY_TICKETS)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.get_role(ROLE_STAFF): discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }

        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(
            title="📌 Atendimento Bom Retiro",
            description="Descreva seu problema e aguarde a equipe.",
            color=discord.Color.red()
        )

        await channel.send(interaction.user.mention, embed=embed, view=TicketAdmin())
        await interaction.response.send_message(f"Ticket criado: {channel.mention}", ephemeral=True)

class TicketPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

# =========================
# ADMIN VIEW
# =========================

class TicketAdmin(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Assumir Atendimento", style=discord.ButtonStyle.primary)
    async def assumir(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"{interaction.user.mention} assumiu o ticket.")

    @discord.ui.button(label="Finalizar Ticket", style=discord.ButtonStyle.danger)
    async def fechar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Ticket encerrado.", ephemeral=True)
        await interaction.channel.delete()

# =========================
# SLASH COMMANDS
# =========================

@bot.tree.command(name="painel", description="Enviar painel de atendimento")
@app_commands.guilds(discord.Object(id=GUILD_ID))
async def painel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎫 ATENDIMENTO BOM RETIRO",
        description="Escolha o tipo de atendimento abaixo.",
        color=discord.Color.red()
    )
    await interaction.response.send_message(embed=embed, view=TicketPanel())

@bot.tree.command(name="ativar_tiquete", description="Ativar sistema de tickets")
@app_commands.checks.has_permissions(administrator=True)
async def ativar(interaction: discord.Interaction):
    global tickets_ativos
    tickets_ativos = True
    await interaction.response.send_message("Sistema de tickets ATIVADO ✅")

@bot.tree.command(name="desativar_tiquetes", description="Desativar sistema de tickets")
@app_commands.checks.has_permissions(administrator=True)
async def desativar(interaction: discord.Interaction):
    global tickets_ativos
    tickets_ativos = False
    await interaction.response.send_message("Sistema de tickets DESATIVADO ❌")

# =========================
# EVENTO READY
# =========================

@bot.event
async def on_ready():
    bot.add_view(TicketPanel())
    bot.add_view(TicketAdmin())
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"Bot online como {bot.user}")

bot.run(TOKEN)
