import discord
from discord.ext import commands, tasks
from discord import ButtonStyle
import os
import sys
import json
import asyncio
from datetime import datetime, timedelta
import random
import threading

# ==========================================
# SERVEUR WEB POUR RENDER (GRATUIT)
# ==========================================
try:
    from flask import Flask
    app = Flask(__name__)

    @app.route('/')
    def home():
        return "🤖 Bot Discord en ligne ! | owner = 2030.m"

    @app.route('/health')
    def health():
        return "OK", 200

    def run_web():
        app.run(host='0.0.0.0', port=10000)

    # Démarrer le serveur web dans un thread séparé
    threading.Thread(target=run_web, daemon=True).start()
    print("🌐 Serveur web démarré sur le port 10000")
except ImportError:
    print("⚠️ Flask non installé, le serveur web ne sera pas démarré")

# ==========================================
# BOT
# ==========================================
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help')

OWNER_IDS = [1012286584613257246]

# ==========================================
# FONCTIONS
# ==========================================
def load_json(f):
    try:
        if os.path.exists(f):
            with open(f, 'r') as file:
                return json.load(file)
        return {}
    except:
        return {}

def save_json(f, data):
    with open(f, 'w') as file:
        json.dump(data, file, indent=4)

def load_stock():
    stock = load_json("stock.json")
    if not stock:
        stock = {
            # === Steal à Brainrot ===
            "garama_regu": 26,
            "garama_gold": 5,
            "garama_diamant": 6,

            # === Monde 1 ===
            "star_fruit_seed": 48,
            "mega_seed": 47,
            "hypno_bloom_seed": 11,
            "moon_bloom_seed": 2,
            "sun_bloom_seed": 1,
            "dragon_breath_seed": 5,
            "big_deer": 1,
            "raccoon": 1,
            "super_watering_can": 100,
            "super_sprinkler_can": 84,

            # === Monde 2 ===
            "mega squirrel": 1,
            "mega hedgehog": 1,
            "mega turkey ": 2,
            "atlantic giant pumkin seed": 34,
            "super_syrup_sprinkler": 4,
            "super_syrup_can": 23,
            "bamboo_seed": 854,
            "mushroom_seed": 137,
            "fox": 19,
            "wolf": 21
        }
        save_json("stock.json", stock)
    return stock

def get_emoji(item):
    emojis = {
        # === Steal à Brainrot ===
        "garama_regu": "⭐",
        "garama_gold": "✨",
        "garama_diamant": "💎",

        # === Monde 1 ===
        "star_fruit_seed": "🌟",
        "mega_seed": "🌰",
        "hypno_bloom_seed": "🌙",
        "moon_bloom_seed": "🌚",
        "sun_bloom_seed": "☀️",
        "dragon_breath_seed": "🐉",
        "big_deer": "🦌",
        "raccoon": "🦝",
        "super_watering_can": "💧",
        "super_sprinkler_can": "🌧️",

        # === Monde 2 ===
        "atlantic giant pumkin seed": "🎃",
        "super_syrup_sprinkler": "🧪",
        "super_syrup_can": "🥫",
        "bamboo_seed": "🎋",
        "mushroom_seed": "🍄",
        "fox": "🦊",
        "wolf": "🐺"

    }
    return emojis.get(item, "📦")

PRICES = {
    # === Steal à Brainrot ===
    "garama_regu": {"price": 1.00, "info": "", "category": "steal"},
    "garama_gold": {"price": 1.20, "info": "", "category": "steal"},
    "garama_diamant": {"price": 1.40, "info": "", "category": "steal"},

    # === Monde 1 ===
    "star_fruit_seed": {"price": 0.10, "info": "", "category": "monde1"},
    "mega_seed": {"price": 0.01, "info": "", "category": "monde1"},
    "hypno_bloom_seed": {"price": 0.01, "info": "", "category": "monde1"},
    "moon_bloom_seed": {"price": 0.01, "info": "", "category": "monde1"},
    "sun_bloom_seed": {"price": 0.01, "info": "", "category": "monde1"},
    "dragon_breath_seed": {"price": 0.03, "info": "", "category": "monde1"},
    "big_deer": {"price": 0.23, "info": "", "category": "monde1"},
    "raccoon": {"price": 0.45, "info": "", "category": "monde1"},
    "super_watering_can": {"price": 0.01, "info": "", "category": "monde1"},
    "super_sprinkler_can": {"price": 0.01, "info": "", "category": "monde1"},

    # === Monde 2 ===
    "atlantic giant pumkin seed": {"price": 0.04, "info": "","category":"monde2"},     
    "super_syrup_sprinkler": {"price": 0.01, "info": "", "category": "monde2"},
    "super_syrup_can": {"price": 0.01, "info": "", "category": "monde2"},
    "bamboo_seed": {"price": 0.01, "info": "les 10", "category": "monde2"},
    "mushroom_seed": {"price": 0.01, "info": "les 5", "category": "monde2"},
    "fox": {"price": 0.01, "info": "", "category": "monde2"},
    "wolf": {"price": 0.01, "info": "", "category": "monde2"}
}

# ==========================================
# TICKETS
# ==========================================
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫 Créer un ticket", style=ButtonStyle.primary, custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        tickets = load_json("tickets.json")
        for data in tickets.values():
            if (data.get('guild_id') == interaction.guild.id and 
                data.get('user_id') == interaction.user.id and 
                data.get('status') == 'open' and
                data.get('type') != 'middleman'):
                return await interaction.response.send_message("❌ Tu as déjà un ticket classique ouvert !", ephemeral=True)

        category = discord.utils.get(interaction.guild.categories, name="TICKETS")
        if not category:
            category = await interaction.guild.create_category("TICKETS")

        channel = await interaction.guild.create_text_channel(f"ticket-{interaction.user.name}", category=category)
        await channel.set_permissions(interaction.guild.default_role, view_channel=False)
        await channel.set_permissions(interaction.user, view_channel=True, send_messages=True, read_message_history=True)
        await channel.set_permissions(interaction.guild.me, view_channel=True, send_messages=True)

        staff_role = discord.utils.get(interaction.guild.roles, name="Staff")
        if staff_role:
            await channel.set_permissions(staff_role, view_channel=True, send_messages=True, read_message_history=True)

        ticket_id = len(tickets) + 1
        tickets[str(ticket_id)] = {
            'guild_id': interaction.guild.id,
            'user_id': interaction.user.id,
            'channel_id': channel.id,
            'status': 'open',
            'type': 'classic',
            'created_at': datetime.now().isoformat()
        }
        save_json("tickets.json", tickets)

        embed = discord.Embed(
            title="🎫 **Ticket créé**",
            description=f"Bonjour {interaction.user.mention} !\n\n"
                       f"📌 Un membre du staff va s'occuper de ta demande.\n"
                       f"📌 Sois patient et précis dans ta description.\n\n"
                       f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                       f"🆔 **ID du ticket :** #{ticket_id}\n"
                       f"👤 **Créé par :** {interaction.user.mention}\n"
                       f"📅 **Date :** {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            color=0x5865F2,
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_footer(text="Clique sur 🔒 pour fermer le ticket")

        staff_mention = f"{staff_role.mention} " if staff_role else ""
        view = TicketCloseView()
        await channel.send(f"{staff_mention} {interaction.user.mention}", embed=embed, view=view)
        await interaction.response.send_message(f"✅ Ticket créé dans {channel.mention} !", ephemeral=True)

class TicketCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Fermer", style=ButtonStyle.danger, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        tickets = load_json("tickets.json")
        ticket_data = None
        ticket_id = None
        for key, data in tickets.items():
            if data.get('channel_id') == interaction.channel.id:
                ticket_data = data
                ticket_id = key
                break
        if not ticket_data:
            return await interaction.response.send_message("❌ Ticket non trouvé.", ephemeral=True)

        staff_role = discord.utils.get(interaction.guild.roles, name="Staff")
        is_staff = staff_role and staff_role in interaction.user.roles
        is_creator = ticket_data.get('user_id') == interaction.user.id
        if not (is_staff or is_creator or interaction.user.guild_permissions.administrator):
            return await interaction.response.send_message("❌ Tu n'as pas la permission de fermer ce ticket.", ephemeral=True)

        messages = []
        async for msg in interaction.channel.history(limit=200):
            messages.append(f"[{msg.created_at.strftime('%H:%M')}] {msg.author.name}: {msg.content}")
        transcript = "\n".join(messages[::-1])
        with open(f"transcript_{interaction.channel.id}.txt", "w", encoding='utf-8') as f:
            f.write(transcript)

        if ticket_id and ticket_id in tickets:
            tickets[ticket_id]['status'] = 'closed'
            tickets[ticket_id]['closed_at'] = datetime.now().isoformat()
            tickets[ticket_id]['closed_by'] = str(interaction.user.id)
            save_json("tickets.json", tickets)

        await interaction.response.send_message("🔒 Ticket fermé dans 5 secondes...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

# ==========================================
# MIDDLEMAN TICKETS
# ==========================================
class MiddlemanTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📝 Créer un ticket Middleman", style=ButtonStyle.primary, custom_id="create_middleman")
    async def create_middleman_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        tickets = load_json("tickets.json")
        for data in tickets.values():
            if (data.get('guild_id') == interaction.guild.id and 
                data.get('user_id') == interaction.user.id and 
                data.get('status') == 'open' and 
                data.get('type') == 'middleman'):
                return await interaction.response.send_message("❌ Tu as déjà un ticket middleman ouvert !", ephemeral=True)

        category = discord.utils.get(interaction.guild.categories, name="MIDDLEMAN")
        if not category:
            category = await interaction.guild.create_category("MIDDLEMAN")

        channel = await interaction.guild.create_text_channel(f"middleman-{interaction.user.name}", category=category)
        await channel.set_permissions(interaction.guild.default_role, view_channel=False)
        await channel.set_permissions(interaction.user, view_channel=True, send_messages=True, read_message_history=True)
        await channel.set_permissions(interaction.guild.me, view_channel=True, send_messages=True)

        middleman_role = discord.utils.get(interaction.guild.roles, name="Gérant middleman")
        if middleman_role:
            await channel.set_permissions(middleman_role, view_channel=True, send_messages=True, read_message_history=True)

        ticket_id = len(tickets) + 1
        tickets[str(ticket_id)] = {
            'guild_id': interaction.guild.id,
            'user_id': interaction.user.id,
            'channel_id': channel.id,
            'status': 'open',
            'type': 'middleman',
            'created_at': datetime.now().isoformat()
        }
        save_json("tickets.json", tickets)

        embed = discord.Embed(
            title="📝 **Ticket Middleman**",
            description=f"Bonjour {interaction.user.mention} !\n\n"
                       f"📌 Un **Gérant middleman** va s'occuper de ta demande.\n"
                       f"📌 Sois précis dans ta description.\n"
                       f"📌 Un middleman sert d'intermédiaire pour des échanges sécurisés.\n\n"
                       f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                       f"🆔 **ID du ticket :** #{ticket_id}\n"
                       f"👤 **Créé par :** {interaction.user.mention}\n"
                       f"📅 **Date :** {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            color=0xFEE75C,
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_footer(text="Clique sur 🔒 pour fermer le ticket")

        middleman_mention = f"{middleman_role.mention} " if middleman_role else ""
        view = MiddlemanTicketCloseView()
        await channel.send(f"{middleman_mention} {interaction.user.mention}", embed=embed, view=view)
        await interaction.response.send_message(f"✅ Ticket middleman créé dans {channel.mention} !", ephemeral=True)

class MiddlemanTicketCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Fermer", style=ButtonStyle.danger, custom_id="close_middleman")
    async def close_middleman_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        tickets = load_json("tickets.json")
        ticket_data = None
        ticket_id = None
        for key, data in tickets.items():
            if data.get('channel_id') == interaction.channel.id:
                ticket_data = data
                ticket_id = key
                break
        if not ticket_data:
            return await interaction.response.send_message("❌ Ticket non trouvé.", ephemeral=True)

        middleman_role = discord.utils.get(interaction.guild.roles, name="Gérant middleman")
        is_middleman = middleman_role and middleman_role in interaction.user.roles
        is_creator = ticket_data.get('user_id') == interaction.user.id
        if not (is_middleman or is_creator or interaction.user.guild_permissions.administrator):
            return await interaction.response.send_message("❌ Tu n'as pas la permission de fermer ce ticket.", ephemeral=True)

        messages = []
        async for msg in interaction.channel.history(limit=200):
            messages.append(f"[{msg.created_at.strftime('%H:%M')}] {msg.author.name}: {msg.content}")
        transcript = "\n".join(messages[::-1])
        with open(f"transcript_middleman_{interaction.channel.id}.txt", "w", encoding='utf-8') as f:
            f.write(transcript)

        if ticket_id and ticket_id in tickets:
            tickets[ticket_id]['status'] = 'closed'
            tickets[ticket_id]['closed_at'] = datetime.now().isoformat()
            tickets[ticket_id]['closed_by'] = str(interaction.user.id)
            save_json("tickets.json", tickets)

        await interaction.response.send_message("🔒 Ticket middleman fermé dans 5 secondes...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

# ==========================================
# STOCK AVEC PAGINATION
# ==========================================

class StockView(discord.ui.View):
    def __init__(self, ctx, pages, current_page=0):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.pages = pages
        self.current_page = current_page
        self.total_pages = len(pages)
        self.message = None

    async def update_message(self, interaction):
        embed = self.pages[self.current_page]
        embed.set_footer(text=f"Page {self.current_page + 1}/{self.total_pages}")

        self.children[0].disabled = self.current_page == 0
        self.children[1].disabled = self.current_page == self.total_pages - 1

        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="◀", style=ButtonStyle.secondary)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_message(interaction)

    @discord.ui.button(label="▶", style=ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            await self.update_message(interaction)

def create_stock_pages(ctx, stock):
    """Crée les pages du stock dans l'ordre : Monde 2, Monde 1, Steal"""
    pages = []

    categories = {
        "monde2": {"name": "🌿 Monde 2", "emoji": "🌿"},
        "monde1": {"name": "🌱 Monde 1", "emoji": "🌱"},
        "steal": {"name": "🎯 Steal à Brainrot", "emoji": "🎯"}
    }

    items_by_category = {"steal": [], "monde1": [], "monde2": []}

    for item, quantity in stock.items():
        data = PRICES.get(item, {"price": 0, "info": "", "category": "monde2"})
        category = data.get("category", "monde2")
        items_by_category[category].append((item, quantity, data))

    # Ordre des catégories : Monde 2, Monde 1, Steal
    category_order = ["monde2", "monde1", "steal"]

    for category in category_order:
        items = items_by_category.get(category, [])
        if items:
            cat_name = categories.get(category, {}).get("name", category)

            embed = discord.Embed(
                title=f"📦 **STOCK COMPLET**",
                description=f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                           f"**{cat_name}**\n"
                           f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                color=0x5865F2,
                timestamp=datetime.now()
            )

            if ctx.guild.icon:
                embed.set_thumbnail(url=ctx.guild.icon.url)

            for item, quantity, data in items:
                emoji = get_emoji(item)
                name = item.replace('_', ' ').title()
                embed.add_field(
                    name=f"{emoji} {name}",
                    value=f"Quantité: **{quantity}**",
                    inline=True
                )

            pages.append(embed)

    return pages

# ==========================================
# COMMANDES
# ==========================================
@bot.command(name='help')
async def help_cmd(ctx):
    embed = discord.Embed(title="🌟 MENU D'AIDE", color=0x5865F2)
    embed.add_field(name="🛡️ MODÉRATION", value="`ban`, `kick`, `mute`, `unmute`, `clear`, `lock`, `unlock`", inline=False)
    embed.add_field(name="🛒 BOUTIQUE", value="`monde1shop`, `monde2shop`, `stealshop`, `stock`", inline=False)
    embed.add_field(name="🎫 TICKETS", value="`ticketpanel`, `middleman`", inline=False)
    embed.add_field(name="🎁 GIVEAWAYS", value="`giveaway`, `reroll`", inline=False)
    embed.add_field(name="👑 OWNER", value="`ownerhelp`, `botstatus`, `guilds`, `broadcast`", inline=False)
    embed.add_field(name="🔧 UTILITAIRES", value="`ping`, `userinfo`, `serverinfo`, `avatar`", inline=False)
    embed.add_field(name="👋 BIENVENUE", value="`setupmembre`", inline=False)
    await ctx.send(embed=embed)

@bot.command(name='ping')
async def ping(ctx):
    await ctx.send(f"🏓 {round(bot.latency * 1000)}ms")

# ==========================================
# NOUVELLE BOUTIQUE (3 COMMANDES SANS BOUTONS)
# ==========================================

async def send_category_shop(ctx, category_key, category_name, category_emoji):
    """Fonction utilitaire pour afficher le shop d'une catégorie spécifique"""
    stock = load_stock()

    embed = discord.Embed(
        title=f"🛒 **BOUTIQUE - {category_name}**",
        description=f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        color=0xFEE75C,
        timestamp=datetime.now()
    )

    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)

    items_found = False

    for item, quantity in stock.items():
        if quantity > 0:
            data = PRICES.get(item, {"price": 0, "info": "", "category": "monde2"})

            if data.get("category") == category_key:
                items_found = True
                price = data["price"]

                if price >= 1:
                    price_str = f"{price:.2f}€"
                else:
                    price_str = f"{int(price * 100)} centime(s)"
                if data.get("info"):
                    price_str += f" {data['info']}"

                emoji = get_emoji(item)
                name = item.replace('_', ' ').title()

                embed.add_field(
                    name=f"{emoji} {name}",
                    value=f"📦 Stock: `{quantity}`\n💰 Prix: {price_str}",
                    inline=True
                )

    if not items_found:
        embed.description += f"\n\n❌ Aucun objet disponible dans cette catégorie pour le moment."
    else:
        embed.description += f"\n\n*Utilisez `!buy [nom]` pour acheter (si vous avez cette commande)*"

    await ctx.send(embed=embed)

@bot.command(name='monde1shop')
async def monde1_shop(ctx):
    await send_category_shop(ctx, "monde1", "🌱 Monde 1", "🌱")

@bot.command(name='monde2shop')
async def monde2_shop(ctx):
    await send_category_shop(ctx, "monde2", "🌿 Monde 2", "🌿")

@bot.command(name='stealshop')
async def steal_shop(ctx):
    await send_category_shop(ctx, "steal", "🎯 Steal à Brainrot", "🎯")

# ==========================================
# STOCK AVEC PAGINATION
# ==========================================
@bot.command(name='stock')
@commands.has_permissions(administrator=True)
async def show_stock(ctx):
    stock = load_stock()
    pages = create_stock_pages(ctx, stock)

    if not pages:
        return await ctx.send("❌ **Aucun article en stock.**")

    view = StockView(ctx, pages)
    embed = pages[0]
    embed.set_footer(text=f"Page 1/{len(pages)}")

    await ctx.send(embed=embed, view=view)

# ==========================================
# MODÉRATION
# ==========================================
@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="Aucune"):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 {member.mention} banni")

@bot.command(name='kick')
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="Aucune"):
    await member.kick(reason=reason)
    await ctx.send(f"👢 {member.mention} expulsé")

@bot.command(name='mute')
@commands.has_permissions(manage_messages=True)
async def mute(ctx, member: discord.Member, duration: str = None, *, reason="Aucune"):
    muted = discord.utils.get(ctx.guild.roles, name="Muted")
    if not muted:
        muted = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            try:
                await channel.set_permissions(muted, send_messages=False)
            except:
                pass
    await member.add_roles(muted)
    await ctx.send(f"🔇 {member.mention} mute")

@bot.command(name='unmute')
@commands.has_permissions(manage_messages=True)
async def unmute(ctx, member: discord.Member):
    muted = discord.utils.get(ctx.guild.roles, name="Muted")
    if muted and muted in member.roles:
        await member.remove_roles(muted)
        await ctx.send(f"🔊 {member.mention} unmute")

@bot.command(name='clear')
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 10):
    if amount > 100:
        return await ctx.send("❌ Max 100")
    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🗑️ {len(deleted)-1} supprimés", delete_after=3)

@bot.command(name='lock')
@commands.has_permissions(administrator=True)
async def lock(ctx, channel: discord.TextChannel = None):
    if not channel:
        channel = ctx.channel
    await channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send(f"🔒 {channel.mention} verrouillé")

@bot.command(name='unlock')
@commands.has_permissions(administrator=True)
async def unlock(ctx, channel: discord.TextChannel = None):
    if not channel:
        channel = ctx.channel
    await channel.set_permissions(ctx.guild.default_role, send_messages=None)
    await ctx.send(f"🔓 {channel.mention} déverrouillé")

# ==========================================
# TICKETS
# ==========================================
@bot.command(name='ticketpanel')
@commands.has_permissions(administrator=True)
async def ticketpanel(ctx):
    embed = discord.Embed(
        title="🎫 **Système de Tickets**",
        description="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                   "**📌 Règles à respecter :**\n"
                   "• Un seul ticket à la fois\n"
                   "• Sois précis dans ta demande\n"
                   "• Respecte le staff\n\n"
                   "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                   "**Clique sur le bouton ci-dessous pour créer un ticket !**",
        color=0x5865F2,
        timestamp=datetime.now()
    )
    embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
    embed.set_footer(text=f"Demandé par {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
    view = TicketView()
    await ctx.send(embed=embed, view=view)
    await ctx.send("✅ Panel de tickets créé avec succès !")

@bot.command(name='middleman')
@commands.has_permissions(administrator=True)
async def middleman_panel(ctx):
    middleman_role = discord.utils.get(ctx.guild.roles, name="Gérant middleman")
    if not middleman_role:
        await ctx.send("⚠️ Le rôle **Gérant middleman** n'existe pas sur ce serveur.")
        await ctx.send("📌 Crée-le d'abord dans les paramètres du serveur, puis réessaie.")
        return
    embed = discord.Embed(
        title="📝 **Système de Middleman**",
        description="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                   "**📌 Qu'est-ce qu'un middleman ?**\n"
                   "Un middleman est un intermédiaire de confiance qui sécurise\n"
                   "les échanges entre deux personnes.\n\n"
                   "**📌 Règles à respecter :**\n"
                   "• Un seul ticket middleman à la fois\n"
                   "• Sois précis dans ta demande\n"
                   "• Le **Gérant middleman** prendra en charge ta demande\n\n"
                   "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                   "**Clique sur le bouton ci-dessous pour créer un ticket Middleman !**",
        color=0xFEE75C,
        timestamp=datetime.now()
    )
    embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
    embed.set_footer(text=f"Demandé par {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
    view = MiddlemanTicketView()
    await ctx.send(embed=embed, view=view)
    await ctx.send(f"✅ Panel Middleman créé avec succès !\n📌 Rôle notifié : {middleman_role.mention}")

# ==========================================
# GIVEAWAYS
# ==========================================
@bot.command(name='giveaway')
@commands.has_permissions(manage_messages=True)
async def giveaway(ctx, duration: str, *, prize: str):
    embed = discord.Embed(title="🎉 GIVEAWAY", description=f"**Prix:** {prize}\n**Durée:** {duration}", color=0xFEE75C)
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🎉")
    await ctx.send("✅ Giveaway lancé !")

@bot.command(name='reroll')
@commands.has_permissions(manage_messages=True)
async def reroll(ctx, msg_id: int):
    msg = await ctx.channel.fetch_message(msg_id)
    users = []
    for r in msg.reactions:
        if str(r.emoji) == "🎉":
            async for u in r.users():
                if not u.bot:
                    users.append(u)
    if users:
        winner = random.choice(users)
        await ctx.send(f"🎉 Gagnant: {winner.mention}")

# ==========================================
# BIENVENUE
# ==========================================
@bot.command(name='setupmembre')
@commands.has_permissions(administrator=True)
async def setup_membre(ctx, role: discord.Role = None):
    if not ctx.guild.me.guild_permissions.manage_roles:
        return await ctx.send("❌ Je n'ai pas la permission `Gérer les rôles` !")
    if role is None:
        role = discord.utils.get(ctx.guild.roles, name="Membre")
        if not role:
            role = await ctx.guild.create_role(name="Membre")
            await ctx.send("✅ Le rôle **Membre** a été créé automatiquement.")
    if role.position >= ctx.guild.me.top_role.position:
        await ctx.send(f"❌ Je ne peux pas attribuer le rôle {role.mention}. Déplace mon rôle au-dessus de lui.")
        return
    embed = discord.Embed(
        title="👋 **Bienvenue !**",
        description=f"**Clique sur ✅ pour obtenir le rôle {role.mention}**",
        color=0x57F287,
        timestamp=datetime.now()
    )
    embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
    message = await ctx.send(embed=embed)
    await message.add_reaction("✅")
    config = load_json("config.json")
    if str(ctx.guild.id) not in config:
        config[str(ctx.guild.id)] = {}
    config[str(ctx.guild.id)]['membre_message_id'] = str(message.id)
    config[str(ctx.guild.id)]['membre_role_id'] = str(role.id)
    config[str(ctx.guild.id)]['membre_emoji'] = "✅"
    save_json("config.json", config)
    await ctx.send(f"✅ Système activé ! Clique sur ✅ dans <#{ctx.channel.id}> pour obtenir le rôle {role.mention}")

# ==========================================
# OWNER
# ==========================================
def is_owner(ctx):
    return ctx.author.id in OWNER_IDS

@bot.command(name='ownerhelp')
@commands.check(is_owner)
async def ownerhelp(ctx):
    embed = discord.Embed(title="👑 Owner", color=0xFEE75C)
    cmds = ["`botstatus`", "`guilds`", "`broadcast`"]
    embed.add_field(name="Commandes", value="\n".join(cmds))
    await ctx.send(embed=embed)

@bot.command(name='botstatus')
@commands.check(is_owner)
async def botstatus(ctx, *, status: str):
    await bot.change_presence(activity=discord.Streaming(name=f"owner = 2030.m", url="https://twitch.tv/votre_stream"))
    await ctx.send(f"✅ Statut: {status}")

@bot.command(name='guilds')
@commands.check(is_owner)
async def guilds(ctx):
    embed = discord.Embed(title="📊 Serveurs", description=f"{len(bot.guilds)} serveurs", color=0x5865F2)
    for g in bot.guilds[:10]:
        embed.add_field(name=g.name, value=f"ID: {g.id}\nMembres: {g.member_count}", inline=False)
    await ctx.send(embed=embed)

@bot.command(name='broadcast')
@commands.check(is_owner)
async def broadcast(ctx, *, msg: str):
    embed = discord.Embed(title="📢 Message du propriétaire", description=msg, color=0xFEE75C)
    count = 0
    for g in bot.guilds:
        try:
            channel = g.system_channel or g.text_channels[0]
            await channel.send(embed=embed)
            count += 1
            await asyncio.sleep(0.5)
        except:
            pass
    await ctx.send(f"✅ Message envoyé à {count} serveurs")

# ==========================================
# UTILITAIRES
# ==========================================
@bot.command(name='userinfo')
async def userinfo(ctx, member: discord.Member = None):
    if not member:
        member = ctx.author
    embed = discord.Embed(title=f"ℹ️ {member.name}", color=member.color)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="ID", value=member.id)
    embed.add_field(name="Créé le", value=member.created_at.strftime("%d/%m/%Y"))
    embed.add_field(name="Rejoint le", value=member.joined_at.strftime("%d/%m/%Y"))
    await ctx.send(embed=embed)

@bot.command(name='serverinfo')
async def serverinfo(ctx):
    g = ctx.guild
    embed = discord.Embed(title=f"📊 {g.name}", color=0x5865F2)
    if g.icon:
        embed.set_thumbnail(url=g.icon.url)
    embed.add_field(name="ID", value=g.id)
    embed.add_field(name="Propriétaire", value=g.owner.mention)
    embed.add_field(name="Membres", value=g.member_count)
    embed.add_field(name="Salons", value=len(g.channels))
    embed.add_field(name="Rôles", value=len(g.roles))
    await ctx.send(embed=embed)

@bot.command(name='avatar')
async def avatar(ctx, member: discord.Member = None):
    if not member:
        member = ctx.author
    embed = discord.Embed(title=f"🖼️ {member.name}")
    embed.set_image(url=member.display_avatar.url)
    await ctx.send(embed=embed)

# ==========================================
# EVENTS
# ==========================================
@bot.event
async def on_ready():
    # Changement pour éviter les doublons
    await bot.change_presence(activity=discord.CustomActivity(name="VERSION RENDER - 2030.m"))
    
    print(f'✅ [VERSION RENDER] Bot connecté: {bot.user}')
    print(f'📊 [VERSION RENDER] {len(bot.guilds)} serveurs')

    # RECREER LES VUES DES TICKETS
    try:
        tickets = load_json("tickets.json")
        for ticket_id, data in tickets.items():
            if data.get('status') == 'open':
                channel = bot.get_channel(data.get('channel_id'))
                if channel:
                    async for msg in channel.history(limit=1):
                        if msg.author == bot.user:
                            view = TicketCloseView()
                            await msg.edit(view=view)
                            print(f"✅ Vue recréée ticket #{ticket_id}")
                            break
        print("✅ Vues recréées !")
    except Exception as e:
        print(f"❌ Erreur lors de la recréation des vues: {e}")

@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return
    guild = bot.get_guild(payload.guild_id)
    if not guild:
        return
    config = load_json("config.json")
    guild_config = config.get(str(guild.id), {})
    if str(payload.message_id) != guild_config.get('membre_message_id'):
        return
    if str(payload.emoji) != guild_config.get('membre_emoji', '✅'):
        return
    member = guild.get_member(payload.user_id)
    if not member:
        return
    role_id = guild_config.get('membre_role_id')
    if not role_id:
        return
    role = guild.get_role(int(role_id))
    if not role:
        return
    try:
        await member.add_roles(role)
        print(f"✅ Rôle {role.name} attribué à {member.name}")
    except Exception as e:
        print(f"❌ Erreur: {e}")

# ==========================================
# LANCEMENT
# ==========================================
if __name__ == "__main__":
    TOKEN = os.getenv('DISCORD_TOKEN')
    if not TOKEN:
        print("❌ Token manquant !")
        sys.exit(1)

    for f in ["config.json", "stock.json", "tickets.json", "giveaways.json", "mutes.json"]:
        if not os.path.exists(f):
            save_json(f, {})

    print("🚀 Démarrage...")
    bot.run(TOKEN)
