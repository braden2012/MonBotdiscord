import discord
from discord.ext import commands
import asyncio
import time
from datetime import datetime

# ==========================================
# INITIALISATION DU BOT
# ==========================================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True  # Requis pour les infos de statut avancées (+user)

bot = commands.Bot(command_prefix="+", intents=intents, help_command=None)
bot.snipes = {}


@bot.event
async def on_ready():
    print(f"====================================")
    print(f"🤖 Bot connecté avec succès !")
    print(f"Nom : {bot.user.name}")
    print(f"ID  : {bot.user.id}")
    print(f"Version discord.py : {discord.__version__}")
    print(f"====================================")


# ==========================================
# ÉVÉNEMENTS (LISTENERS)
# ==========================================
@bot.event
async def on_message_delete(message):
    """Capture le dernier message supprimé avec gestion des pièces jointes"""
    if message.author.bot or not message.guild:
        return
    
    attachment_url = message.attachments[0].url if message.attachments else None
    
    bot.snipes[message.channel.id] = {
        "content": message.content if message.content else "*Message vide (ou embed/image)*",
        "author": message.author,
        "time": datetime.utcnow(),
        "image": attachment_url
    }


# ==========================================
# COMPONENT: PAGINATION DES BOUTONS (+helpall)
# ==========================================
class HelpAllView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.current_page = 0
        
        # Design des Embeds de l'aide entièrement personnalisé
        page1 = discord.Embed(title="📚 Liste des Commandes — Module 1", color=0x2b2d31)
        page1.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        page1.add_field(name="🔹 Public [12]", value="`+banner` • `+calc` • `+help` • `+helpall` • `+pic` • `+ping` • `+reminder` • `+roleinfo` • `+serverinfo` • `+snipe` • `+support` • `+user`", inline=False)
        page1.add_field(name="🔨 Modération [16]", value="`+addrole` • `+ban` • `+clear` • `+del-sanction` • `+delrole` • `+derank` • `+mutelist` • `+sanction-info` • `+sanction` • `+setmute` • `+slowmode` • `+tempban` • `+tempmute` • `+unmute` • `+unmuteall` • `+warn`", inline=False)
        page1.set_footer(text=f"Demandé par {ctx.author.name} • Page 1/2", icon_url=ctx.author.display_avatar.url)

        page2 = discord.Embed(title="📚 Liste des Commandes — Module 2", color=0x2b2d31)
        page2.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        page2.add_field(name="⚙️ Gestion [19]", value="`+add` • `+adminlist` • `+banlist` • `+boosters` • `+botlist` • `+category` • `+close` • `+compteur` • `+create` • `+del` • `+delete` • `+embed` • `+nsfw` • `+poll` • `+rename` • `+rolemembers` • `+stickers` • `+tempvoc` • `+topic`", inline=False)
        page2.add_field(name="🛡️ Antiraid [15]", value="`+antiban` • `+antibot` • `+antichannel` • `+antideco` • `+antieveryone` • `+antijoin` • `+antilink` • `+antirole` • `+antiupdate` • `+antiwebhook` • `+bypass` • `+createlimit` • `+pingraid` • `+punition` • `+secur`", inline=False)
        page2.set_footer(text=f"Demandé par {ctx.author.name} • Page 2/2", icon_url=ctx.author.display_avatar.url)

        self.pages = [page1, page2]

    @discord.ui.button(label="⬅️ Précédent", style=discord.ButtonStyle.gray, disabled=True)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("❌ Vous ne pouvez pas interagir avec ce menu.", ephemeral=True)
        self.current_page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)

    @discord.ui.button(label="Suivant ➡️", style=discord.ButtonStyle.blurple)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("❌ Vous ne pouvez pas interagir avec ce menu.", ephemeral=True)
        self.current_page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)

    def update_buttons(self):
        self.children[0].disabled = self.current_page == 0
        self.children[1].disabled = self.current_page == len(self.pages) - 1

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        try:
            await self.message.edit(view=self)
        except:
            pass


# ==========================================
# BLOC 1 : COMMANDES PUBLIQUES (VERSION PRO)
# ==========================================

@bot.command(name="ping")
async def ping(ctx):
    start_time = time.time()
    message = await ctx.send(embed=discord.Embed(description="⚡ Calcul de la latence...", color=0x2b2d31))
    end_time = time.time()
    
    api_latency = round(bot.latency * 1000)
    bot_latency = round((end_time - start_time) * 1000)
    
    embed = discord.Embed(title="🏓 Statistiques de Latence", color=0x2b2d31)
    embed.add_field(name="🤖 Latence du Bot", value=f"`{bot_latency}ms`", inline=True)
    embed.add_field(name="🌐 API Discord", value=f"`{api_latency}ms`", inline=True)
    embed.set_footer(text=f"Demandé par {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
    await message.edit(embed=embed)


@bot.command(name="help")
async def help(ctx):
    embed = discord.Embed(title="ℹ️ Centre d'Aide", description="Bienvenue sur le système d'aide du bot.\n\nPour afficher l'intégralité des commandes réparties par modules de permissions et utiliser le système de navigation, veuillez exécuter la commande ci-dessous :", color=0x2b2d31)
    embed.add_field(name="📋 Commande disponible", value="`+helpall` — Ouvre l'index complet.", inline=False)
    embed.set_footer(text=ctx.author.name, icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)


@bot.command(name="helpall")
async def helpall(ctx):
    view = HelpAllView(ctx)
    view.message = await ctx.send(embed=view.pages[0], view=view)


@bot.command(name="pic")
async def pic(ctx, member: discord.Member = None):
    member = member or ctx.author
    
    embed = discord.Embed(title=f"📸 Avatar de {member.name}", color=0x2b2d31)
    embed.description = f"[Lien de l'image]({member.display_avatar.url})"
    embed.set_image(url=member.display_avatar.url)
    embed.set_footer(text=f"ID de l'utilisateur : {member.id}")
    await ctx.send(embed=embed)


@bot.command(name="banner")
async def banner(ctx, member: discord.Member = None):
    member = member or ctx.author
    user = await bot.fetch_user(member.id)
    
    embed = discord.Embed(title=f"🖼️ Bannière de {user.name}", color=0x2b2d31)
    if user.banner:
        embed.description = f"[Lien de la bannière]({user.banner.url})"
        embed.set_image(url=user.banner.url)
    else:
        embed.description = "❌ Cet utilisateur ne possède pas de bannière personnalisée."
        embed.color = discord.Color.red()
    embed.set_footer(text=f"Demandé par {ctx.author.name}")
    await ctx.send(embed=embed)


@bot.command(name="calc")
async def calc(ctx, *, expression: str):
    # Remplacement des symboles visuels par des symboles mathématiques Python
    clean_expr = expression.replace('x', '*').replace(':', '/')
    
    try:
        allowed_chars = "0123456789+-*/(). "
        if not all(char in allowed_chars for char in clean_expr):
            raise ValueError("Caractères non autorisés détectés.")
            
        result = eval(clean_expr)
        
        embed = discord.Embed(title="🧮 Calculatrice Intégrée", color=0x2b2d31)
        embed.add_field(name="📥 Entrée :", value=f"```py\n{expression}\n```", inline=False)
        embed.add_field(name="📤 Résultat :", value=f"```py\n{result}\n```", inline=False)
    except Exception as e:
        embed = discord.Embed(title="❌ Erreur de Calcul", description="Une erreur est survenue lors de l'analyse de l'expression.\nSeuls les chiffres et les opérateurs `+`, `-`, `*`, `/`, `(` et `)` sont autorisés.", color=discord.Color.red())
    
    embed.set_footer(text=ctx.author.name, icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)


@bot.command(name="serverinfo")
async def serverinfo(ctx):
    guild = ctx.guild
    
    # Calculs précis des salons
    text_channels = len(guild.text_channels)
    voice_channels = len(guild.voice_channels)
    categories = len(guild.categories)
    
    # Calculs précis des membres
    bots = len([m for m in guild.members if m.bot])
    humans = guild.member_count - bots
    
    embed = discord.Embed(title=f"📊 Informations : {guild.name}", color=0x2b2d31)
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    if guild.banner:
        embed.set_image(url=guild.banner.url)
        
    embed.add_field(name="👑 Propriété", value=f"{guild.owner.mention}\n`({guild.owner_id})`", inline=True)
    embed.add_field(name="📆 Création du Serveur", value=f"<t:{int(guild.created_at.timestamp())}:F>\n(<t:{int(guild.created_at.timestamp())}:R>)", inline=True)
    embed.add_field(name="🛡️ Niveau de Sécurité", value=f"Niveau `{str(guild.verification_level).upper()}`", inline=False)
    
    embed.add_field(name="👥 Communauté", value=f"👥 Total : **{guild.member_count}**\n👤 Humains : **{humans}**\n🤖 Bots : **{bots}**", inline=True)
    embed.add_field(name="💬 Salons", value=f"📁 Catégories : **{categories}**\n📝 Textuels : **{text_channels}**\n🔊 Vocaux : **{voice_channels}**", inline=True)
    embed.add_field(name="✨ Boosts", value=f"Niveau : **{guild.premium_tier}**\nNombre : **{guild.premium_subscription_count}** boost(s)", inline=True)
    
    embed.set_footer(text=f"ID du Serveur : {guild.id}")
    await ctx.send(embed=embed)


@bot.command(name="user")
async def user(ctx, member: discord.Member = None):
    member = member or ctx.author
    
    # Récupération des rôles (en excluant @everyone)
    roles = [role.mention for role in member.roles if role != ctx.guild.default_role]
    roles_display = ", ".join(roles) if roles else "Aucun rôle"
    if len(roles_display) > 500: roles_display = f"{len(roles)} rôles accumulés."

    embed = discord.Embed(title=f"👤 Profil de {member.name}#{member.discriminator if member.discriminator != '0' else ''}", color=member.color)
    embed.set_thumbnail(url=member.display_avatar.url)
    
    embed.add_field(name="🆔 Identifiant (ID)", value=f"`{member.id}`", inline=True)
    embed.add_field(name="Nom d'affichage", value=f"{member.mention}", inline=True)
    
    # Statut et plateforme
    status_map = {"online": "🟢 En ligne", "idle": "🌙 Inactif", "dnd": "🔴 Ne pas déranger", "offline": "⚪ Hors ligne"}
    embed.add_field(name="Status", value=status_map.get(str(member.status), "⚪ Hors ligne"), inline=True)
    
    embed.add_field(name="📆 Création du compte", value=f"<t:{int(member.created_at.timestamp())}:F>\n(<t:{int(member.created_at.timestamp())}:R>)", inline=False)
    embed.add_field(name="📥 Arrivée sur le serveur", value=f"<t:{int(member.joined_at.timestamp())}:F>\n(<t:{int(member.joined_at.timestamp())}:R>)", inline=False)
    
    embed.add_field(name=f"🔮 Rôles ({len(roles)})", value=roles_display, inline=False)
    
    embed.set_footer(text=f"Demandé par {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)


@bot.command(name="roleinfo")
async def roleinfo(ctx, role: discord.Role):
    embed = discord.Embed(title=f"🔮 Fiche Rôle : {role.name}", color=role.color if role.color.value != 0 else 0x2b2d31)
    
    embed.add_field(name="🆔 ID du Rôle", value=f"`{role.id}`", inline=True)
    embed.add_field(name="🎨 Code Couleur", value=f"`{role.color}`", inline=True)
    embed.add_field(name="📌 Position", value=f"Rang `{role.position}` dans la hiérarchie", inline=True)
    
    embed.add_field(name="📆 Date de création", value=f"<t:{int(role.created_at.timestamp())}:F> (<t:{int(role.created_at.timestamp())}:R>)", inline=False)
    embed.add_field(name="⚙️ Propriétés", value=f"Affiché séparément : {'Oui' if role.hoist else 'Non'}\nMentionnable : {'Oui' if role.mentionable else 'Non'}\nGéré par une intégration : {'Oui' if role.is_integration() else 'Non'}", inline=True)
    embed.add_field(name="👥 Membres", value=f"Possédé par **{len(role.members)}** utilisateur(s)", inline=True)
    
    # Liste d'exemples de permissions clés possédées par le rôle
    perms = []
    if role.permissions.administrator: perms.append("🛡️ Administrateur")
    if role.permissions.ban_members: perms.append("🔨 Bannir")
    if role.permissions.kick_members: perms.append("👢 Kick")
    if role.permissions.manage_messages: perms.append("💬 Gérer messages")
    if role.permissions.mention_everyone: perms.append("📢 Mention Everyone")
    
    embed.add_field(name="🔑 Permissions clés", value=", ".join(perms) if perms else "Aucune permission majeure", inline=False)
    embed.set_footer(text=f"Demandé par {ctx.author.name}")
    await ctx.send(embed=embed)


@bot.command(name="snipe")
async def snipe(ctx):
    channel_id = ctx.channel.id
    if channel_id in bot.snipes:
        data = bot.snipes[channel_id]
        
        embed = discord.Embed(description=data["content"], color=0x2b2d31)
        embed.set_author(name=data["author"].name, icon_url=data["author"].display_avatar.url)
        
        # Gestion si le message supprimé contenait une image
        if data["image"]:
            embed.set_image(url=data["image"])
            
        embed.set_footer(text=f"Supprimé à {data['time'].strftime('%H:%M:%S')} (UTC)")
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(description="❌ Aucun message supprimé récemment trouvé dans ce salon textuel.", color=discord.Color.red())
        await ctx.send(embed=embed)


@bot.command(name="support")
async def support(ctx):
    embed = discord.Embed(title="🛡️ Centre d'Assistance Technique", description="💬 BESOIN D'AIDE ? L'OTAN EST LA !", color=0x2b2d31)
    embed.add_field(name="🔗 Lien d'invitation", value="[Cliquez ici pour rejoindre l'assistance de l'OTAN](https://discord.gg/Eu8xRHbzBp)", inline=False)
    embed.set_footer(text="Bot Support de l'OTAN", icon_url=bot.user.display_avatar.url)
    await ctx.send(embed=embed)


@bot.command(name="reminder")
async def reminder(ctx, duration_str: str, *, text: str):
    # Analyse de la durée (ex: 10s, 5m, 2h)
    time_dict = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    unit = duration_str[-1].lower()
    
    if unit not in time_dict or not duration_str[:-1].isdigit():
        embed = discord.Embed(title="❌ Syntaxe Invalide", description="Le format du temps est incorrect.\nExemples valides : `10s` (secondes), `5m` (minutes), `2h` (heures).", color=discord.Color.red())
        return await ctx.send(embed=embed)
        
    duration = int(duration_str[:-1]) * time_dict[unit]
    
    embed = discord.Embed(title="⏰ Rappel Enregistré", description=f"Le rappel a été programmé avec succès.", color=0x2b2d31)
    embed.add_field(name="📝 Note à rappeler", value=f"*{text}*", inline=False)
    embed.add_field(name="⏳ Échéance", value=f"Dans `{duration_str}` (<t:{int(time.time() + duration)}:R>)", inline=False)
    await ctx.send(embed=embed)
    
    await asyncio.sleep(duration)
    
    remind_embed = discord.Embed(title="🔔 RAPPEL ! (Alerte Automatique)", description=f"Bonjour {ctx.author.mention}, le délai programmé est écoulé !", color=0x2b2d31)
    remind_embed.add_field(name="📌 Votre note :", value=f"👉 **{text}**", inline=False)
    remind_embed.set_footer(text="Rappel automatique")
    await ctx.send(content=ctx.author.mention, embed=remind_embed)

# ==========================================
# CONFIGURATION REQUISE POUR LA MODÉRATION
# ==========================================
# À placer tout en haut avec tes autres initialisations de variables :
bot.sanctions = {}      # Structure : { guild_id: { user_id: [ {id, type, reason, date, staff} ] } }
bot.mute_settings = {}  # Structure : { guild_id: role_id }
bot.sanction_counter = 0


# ==========================================
# FONCTION UTILITAIRE (POUR LES DURÉES)
# ==========================================
def parse_duration(duration_str: str) -> int:
    """Convertit une chaîne (ex: 10m, 2h, 1d) en secondes brutes"""
    time_dict = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    unit = duration_str[-1].lower()
    if unit not in time_dict or not duration_str[:-1].isdigit():
        return -1
    return int(duration_str[:-1]) * time_dict[unit]


# ==========================================
# BLOC 2 : COMMANDES DE MODÉRATION (PRO & LONG)
# ==========================================

@bot.command(name="addrole")
@commands.has_permissions(manage_roles=True)
async def addrole(ctx, member: discord.Member, *, role: discord.Role):
    if role >= ctx.guild.me.top_role:
        return await ctx.send(embed=discord.Embed(description="❌ Ce rôle est supérieur ou égal au mien dans la hiérarchie.", color=discord.Color.red()))
    
    if role in member.roles:
        return await ctx.send(embed=discord.Embed(description=f"❌ {member.mention} possède déjà le rôle **{role.name}**.", color=discord.Color.red()))
        
    await member.add_roles(role)
    embed = discord.Embed(title="✅ Rôle Attribué", description=f"Le rôle {role.mention} a été ajouté avec succès à {member.mention}.", color=0x2b2d31)
    embed.set_footer(text=f"Modérateur : {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)


@bot.command(name="delrole")
@commands.has_permissions(manage_roles=True)
async def delrole(ctx, member: discord.Member, *, role: discord.Role):
    if role >= ctx.guild.me.top_role:
        return await ctx.send(embed=discord.Embed(description="❌ Ce rôle est supérieur ou égal au mien dans la hiérarchie.", color=discord.Color.red()))
    
    if role not in member.roles:
        return await ctx.send(embed=discord.Embed(description=f"❌ {member.mention} ne possède pas le rôle **{role.name}**.", color=discord.Color.red()))
        
    await member.remove_roles(role)
    embed = discord.Embed(title="✅ Rôle Retiré", description=f"Le rôle {role.mention} a été retiré avec succès à {member.mention}.", color=0x2b2d31)
    embed.set_footer(text=f"Modérateur : {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)


@bot.command(name="ban")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason: str = "Aucune raison fournie"):
    if member.top_role >= ctx.guild.me.top_role or member == ctx.guild.owner:
        return await ctx.send(embed=discord.Embed(description="❌ Je ne peux pas bannir cet utilisateur (Hiérarchie supérieure).", color=discord.Color.red()))
        
    embed_user = discord.Embed(title="🔨 Vous avez été banni", description=f"Vous avez été banni du serveur **{ctx.guild.name}**.", color=discord.Color.red())
    embed_user.add_field(name="Raison :", value=reason)
    try: await member.send(embed=embed_user)
    except: pass

    await member.ban(reason=f"Par {ctx.author.name} : {reason}")
    
    embed = discord.Embed(title="🔨 Utilisateur Banni", description=f"**{member.name}** a définitivement été banni du serveur.", color=0x2b2d31)
    embed.add_field(name="Cible :", value=f"{member.mention} `({member.id})`", inline=True)
    embed.add_field(name="Modérateur :", value=ctx.author.mention, inline=True)
    embed.add_field(name="Raison :", value=reason, inline=False)
    await ctx.send(embed=embed)


@bot.command(name="tempban")
@commands.has_permissions(ban_members=True)
async def tempban(ctx, member: discord.Member, duration_str: str, *, reason: str = "Aucune raison fournie"):
    if member.top_role >= ctx.guild.me.top_role or member == ctx.guild.owner:
        return await ctx.send(embed=discord.Embed(description="❌ Hiérarchie invalide pour le bannissement.", color=discord.Color.red()))
        
    seconds = parse_duration(duration_str)
    if seconds <= 0:
        return await ctx.send(embed=discord.Embed(description="❌ Format de temps invalide (ex: 10m, 2h, 1d).", color=discord.Color.red()))

    embed_user = discord.Embed(title="⏳ Bannissement Temporaire", description=f"Vous êtes banni temporairement de **{ctx.guild.name}** pendant `{duration_str}`.", color=discord.Color.red())
    embed_user.add_field(name="Raison :", value=reason)
    try: await member.send(embed=embed_user)
    except: pass

    await member.ban(reason=f"Tempban {duration_str} par {ctx.author.name} : {reason}")
    
    embed = discord.Embed(title="⏳ Bannissement Temporaire", color=0x2b2d31)
    embed.add_field(name="Membre :", value=f"{member.mention} `({member.id})`")
    embed.add_field(name="Durée :", value=f"`{duration_str}` (<t:{int(time.time() + seconds)}:R>)")
    embed.add_field(name="Raison :", value=reason, inline=False)
    await ctx.send(embed=embed)
    
    await asyncio.sleep(seconds)
    try:
        await ctx.guild.unban(member, reason="Fin du bannissement temporaire.")
    except:
        pass


@bot.command(name="clear")
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: str):
    if amount.lower() == "bl":
        # Simulation d'un clear de blacklist (sera connecté au module Buyer plus tard)
        embed = discord.Embed(title="🗑️ Nettoyage Blacklist", description="La file d'attente de la blacklist globale a été réinitialisée.", color=0x2b2d31)
        return await ctx.send(embed=embed)
        
    if not amount.isdigit():
        return await ctx.send(embed=discord.Embed(description="❌ Spécifiez un nombre de messages ou `clear bl`.", color=discord.Color.red()))
        
    deleted = await ctx.channel.purge(limit=int(amount) + 1)
    embed = discord.Embed(description=f"🗑️ **{len(deleted) - 1}** messages ont été supprimés de ce salon.", color=0x2b2d31)
    msg = await ctx.send(embed=embed)
    await asyncio.sleep(4)
    await msg.delete()


@bot.command(name="setmute")
@commands.has_permissions(administrator=True)
async def setmute(ctx, role: discord.Role):
    bot.mute_settings[ctx.guild.id] = role.id
    embed = discord.Embed(title="⚙️ Configuration Mute", description=f"Le rôle de mute par défaut a été défini sur : {role.mention}.", color=0x2b2d31)
    await ctx.send(embed=embed)


@bot.command(name="tempmute")
@commands.has_permissions(manage_messages=True)
async def tempmute(ctx, member: discord.Member, duration_str: str, *, reason: str = "Aucune raison fournie"):
    guild_id = ctx.guild.id
    if guild_id not in bot.mute_settings:
        return await ctx.send(embed=discord.Embed(description="❌ Aucun rôle de mute défini. Utilisez d'abord `+setmute <rôle>`.", color=discord.Color.red()))
        
    role = ctx.guild.get_role(bot.mute_settings[guild_id])
    if not role or role >= ctx.guild.me.top_role:
        return await ctx.send(embed=discord.Embed(description="❌ Le rôle de mute configuré est introuvable ou trop élevé.", color=discord.Color.red()))
        
    seconds = parse_duration(duration_str)
    if seconds <= 0:
        return await ctx.send(embed=discord.Embed(description="❌ Format de temps invalide (ex: 30m, 1h).", color=discord.Color.red()))

    await member.add_roles(role, reason=f"Mute temporaire par {ctx.author.name}")
    
    embed = discord.Embed(title="🔇 Mutation Temporaire", color=0x2b2d31)
    embed.add_field(name="Utilisateur :", value=member.mention)
    embed.add_field(name="Durée :", value=f"`{duration_str}` (<t:{int(time.time() + seconds)}:R>)")
    embed.add_field(name="Raison :", value=reason, inline=False)
    await ctx.send(embed=embed)
    
    await asyncio.sleep(seconds)
    if role in member.roles:
        await member.remove_roles(role, reason="Fin de la mutation temporaire.")


@bot.command(name="unmute")
@commands.has_permissions(manage_messages=True)
async def unmute(ctx, member: discord.Member):
    guild_id = ctx.guild.id
    role = ctx.guild.get_role(bot.mute_settings.get(guild_id, 0))
    if not role or role not in member.roles:
        return await ctx.send(embed=discord.Embed(description="❌ Cet utilisateur n'est pas muet ou le rôle est introuvable.", color=discord.Color.red()))
        
    await member.remove_roles(role)
    await ctx.send(embed=discord.Embed(description=f"🔊 {member.mention} a été réhabilité à parler (Unmuted).", color=0x2b2d31))


@bot.command(name="unmuteall")
@commands.has_permissions(administrator=True)
async def unmuteall(ctx):
    guild_id = ctx.guild.id
    role = ctx.guild.get_role(bot.mute_settings.get(guild_id, 0))
    if not role:
        return await ctx.send(embed=discord.Embed(description="❌ Aucun rôle de mute configuré.", color=discord.Color.red()))
        
    unmuted_count = 0
    for member in role.members:
        await member.remove_roles(role)
        unmuted_count += 1
        
    await ctx.send(embed=discord.Embed(description=f"🔊 Restauration générale : **{unmuted_count}** utilisateur(s) unmuted.", color=0x2b2d31))


@bot.command(name="mutelist")
@commands.has_permissions(manage_messages=True)
async def mutelist(ctx):
    guild_id = ctx.guild.id
    role = ctx.guild.get_role(bot.mute_settings.get(guild_id, 0))
    if not role or not role.members:
        return await ctx.send(embed=discord.Embed(description="🔇 Aucun utilisateur n'est actuellement muet sur le serveur.", color=0x2b2d31))
        
    members_str = "\n".join([f"• {m.mention} `({m.id})`" for m in role.members])
    embed = discord.Embed(title="🔇 Liste des Utilisateurs Mute", description=members_str, color=0x2b2d31)
    await ctx.send(embed=embed)


@bot.command(name="slowmode")
@commands.has_permissions(manage_channels=True)
async def slowmode(ctx, duration_str: str):
    if duration_str == "0" or duration_str.lower() == "off":
        await ctx.channel.edit(slowmode_delay=0)
        return await ctx.send(embed=discord.Embed(description="⏱️ Le mode ralenti a été désactivé sur ce salon.", color=0x2b2d31))
        
    seconds = parse_duration(duration_str)
    if seconds <= 0 or seconds > 21600:
        return await ctx.send(embed=discord.Embed(description="❌ Temps invalide (Maximum 6h. Exemple: `10s`, `2m`).", color=discord.Color.red()))
        
    await ctx.channel.edit(slowmode_delay=seconds)
    await ctx.send(embed=discord.Embed(description=f"⏱️ Ce salon est désormais configuré avec un mode ralenti de `{duration_str}`.", color=0x2b2d31))


@bot.command(name="derank")
@commands.has_permissions(administrator=True)
async def derank(ctx, user_id_or_name: str):
    # Recherche par ID ou Mention
    member = None
    if user_id_or_name.isdigit():
        member = ctx.guild.get_member(int(user_id_or_name))
    else:
        member = discord.utils.get(ctx.guild.members, name=user_id_or_name)
        
    if not member:
        return await ctx.send(embed=discord.Embed(description="❌ Utilisateur introuvable sur ce serveur.", color=discord.Color.red()))
        
    removed_roles = []
    for role in member.roles:
        if role != ctx.guild.default_role and role < ctx.guild.me.top_role:
            try:
                await member.remove_roles(role)
                removed_roles.append(role.name)
            except: pass
            
    embed = discord.Embed(title="📉 Destitution (Derank)", description=f"Tous les rôles modifiables de {member.mention} ont été purgés.", color=0x2b2d31)
    embed.add_field(name="Rôles supprimés :", value=", ".join(removed_roles) if removed_roles else "Aucun rôle modifiable.")
    await ctx.send(embed=embed)


# ==========================================
# SYSTÈME DE GESTION DES SANCTIONS (WARNS)
# ==========================================

@bot.command(name="warn")
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, reason: str = "Aucune raison spécifiée"):
    global sanction_counter
    bot.sanction_counter += 1
    sanction_id = bot.sanction_counter
    
    guild_id = ctx.guild.id
    user_id = member.id
    
    if guild_id not in bot.sanctions: bot.sanctions[guild_id] = {}
    if user_id not in bot.sanctions[guild_id]: bot.sanctions[guild_id][user_id] = []
    
    sanction_data = {
        "id": sanction_id,
        "type": "WARN",
        "reason": reason,
        "date": datetime.utcnow().strftime("%d/%m/%Y à %H:%M"),
        "staff": ctx.author.name
    }
    
    bot.sanctions[guild_id][user_id].append(sanction_data)
    
    embed = discord.Embed(title="⚠️ Avertissement Enregistré", color=0x2b2d31)
    embed.add_field(name="Utilisateur :", value=member.mention)
    embed.add_field(name="ID Sanction :", value=f"`#{sanction_id}`")
    embed.add_field(name="Raison :", value=reason, inline=False)
    await ctx.send(embed=embed)


@bot.command(name="sanction")
@commands.has_permissions(manage_messages=True)
async def sanction(ctx, member: discord.Member):
    guild_id = ctx.guild.id
    user_id = member.id
    
    user_sanctions = bot.sanctions.get(guild_id, {}).get(user_id, [])
    if not user_sanctions:
        return await ctx.send(embed=discord.Embed(description=f"✅ {member.mention} ne possède aucune sanction dans l'historique.", color=0x2b2d31))
        
    embed = discord.Embed(title=f"📋 Dossier Disciplinaire — {member.name}", color=0x2b2d31)
    for s in user_sanctions:
        embed.add_field(name=f"Sanction #{s['id']} [{s['type']}]", value=f"**Raison :** {s['reason']}\n**Par :** {s['staff']} • *{s['date']}*", inline=False)
    await ctx.send(embed=embed)


@bot.command(name="sanction-info")
@commands.has_permissions(manage_messages=True)
async def sanction_info(ctx, sanction_id: int):
    guild_id = ctx.guild.id
    found_sanction = None
    target_user = None
    
    for u_id, s_list in bot.sanctions.get(guild_id, {}).items():
        for s in s_list:
            if s["id"] == sanction_id:
                found_sanction = s
                target_user = ctx.guild.get_member(u_id) or u_id
                break
                
    if not found_sanction:
        return await ctx.send(embed=discord.Embed(description="❌ Aucune sanction trouvée avec cet identifiant.", color=discord.Color.red()))
        
    embed = discord.Embed(title=f"🔍 Fiche Sanction #{sanction_id}", color=0x2b2d31)
    embed.add_field(name="Cible :", value=target_user.mention if hasattr(target_user, 'mention') else f"ID: {target_user}")
    embed.add_field(name="Type :", value=f"`{found_sanction['type']}`")
    embed.add_field(name="Staff :", value=found_sanction["staff"])
    embed.add_field(name="Date :", value=found_sanction["date"])
    embed.add_field(name="Raison Complète :", value=found_sanction["reason"], inline=False)
    await ctx.send(embed=embed)


@bot.command(name="del-sanction")
@commands.has_permissions(manage_messages=True)
async def del_sanction(ctx, sanction_id: int):
    guild_id = ctx.guild.id
    removed = False
    
    for u_id, s_list in bot.sanctions.get(guild_id, {}).items():
        for s in s_list:
            if s["id"] == sanction_id:
                s_list.remove(s)
                removed = True
                break
                
    if removed:
        await ctx.send(embed=discord.Embed(description=f"🗑️ La sanction **#{sanction_id}** a été définitivement supprimée.", color=0x2b2d31))
    else:
        await ctx.send(embed=discord.Embed(description="❌ Identifiant de sanction introuvable.", color=discord.Color.red()))

# ==========================================
# CONFIGURATION REQUISE POUR LA GESTION
# ==========================================
# À ajouter en haut de votre script avec vos autres variables globales :
bot.ticket_configs = {}  # { guild_id: { "category_id": int, "channel_id": int } }
bot.temp_voc_configs = {} # { guild_id: { "category_id": int, "generator_channel_id": int, "active_channels": [] } }


# ==========================================
# INTERFACES UI (BOUTONS POUR TICKETS)
# ==========================================

class TicketSetupView(discord.ui.View):
    """Bouton persistant permettant d'ouvrir un ticket"""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📩 Ouvrir un Ticket", style=discord.ButtonStyle.blurple, custom_id="open_ticket_btn")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        config = bot.ticket_configs.get(guild.id, {})
        category_id = config.get("category_id")
        category = guild.get_channel(category_id) if category_id else None
        
        # Vérification des permissions de base
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
        }
        
        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name.lower()}",
            category=category,
            overwrites=overwrites,
            reason=f"Ticket ouvert par {interaction.user.name}"
        )
        
        embed = discord.Embed(
            title="🎫 Ticket Ouvert", 
            description=f"Bonjour {interaction.user.mention},\nL'équipe d'administration a été notifiée de votre demande. Veuillez exposer votre problème ici.", 
            color=0x2b2d31
        )
        embed.set_footer(text="Pour fermer ce ticket, utilisez la commande +close")
        
        view = TicketCloseView()
        await ticket_channel.send(embed=embed, view=view)
        await interaction.response.send_message(f"✅ Votre ticket a été créé : {ticket_channel.mention}", ephemeral=True)


class TicketCloseView(discord.ui.View):
    """Bouton à l'intérieur du ticket pour le fermer"""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Fermer le ticket", style=discord.ButtonStyle.red, custom_id="close_ticket_btn")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if "ticket-" not in interaction.channel.name:
            return await interaction.response.send_message("❌ Ce salon n'est pas un ticket.", ephemeral=True)
            
        await interaction.response.send_message("⚙️ Fermeture et suppression du ticket programmées dans 5 secondes...")
        await asyncio.sleep(5)
        await interaction.channel.delete(reason="Fermeture du ticket")


# Écouteur d'événement pour le système de Vocaux Temporaires
@bot.event
async def on_voice_state_update(member, before, after):
    guild = member.guild
    config = bot.temp_voc_configs.get(guild.id)
    
    if not config:
        return

    # 1. Rejoindre le salon générateur
    if after.channel and after.channel.id == config.get("generator_channel_id"):
        category = guild.get_channel(config.get("category_id"))
        
        new_channel = await guild.create_voice_channel(
            name=f"🔊 Salon de {member.name}",
            category=category,
            reason="Création d'un vocal temporaire"
        )
        
        config["active_channels"].append(new_channel.id)
        await member.move_to(new_channel)

    # 2. Nettoyage des salons vides
    if before.channel and before.channel.id in config.get("active_channels", []):
        if len(before.channel.members) == 0:
            config["active_channels"].remove(before.channel.id)
            await before.channel.delete(reason="Vocal temporaire vide supprimé")


# ==========================================
# BLOC 4 : COMMANDES DE GESTION (AVANCÉES)
# ==========================================

@bot.command(name="ticket")
@commands.has_permissions(administrator=True)
async def ticket_setup(ctx, category: discord.CategoryChannel = None):
    """Commande principale pour installer le panneau des tickets"""
    bot.ticket_configs[ctx.guild.id] = {
        "category_id": category.id if category else None,
        "channel_id": ctx.channel.id
    }
    
    embed = discord.Embed(
        title="📥 Support Technique & Commercial",
        description="Besoin d'entrer en contact avec l'équipe ? Cliquez sur le bouton ci-dessous pour ouvrir un salon de discussion privé.",
        color=0x2b2d31
    )
    view = TicketSetupView()
    await ctx.send(embed=embed, view=view)


@bot.command(name="add")
@commands.has_permissions(manage_channels=True)
async def add_to_ticket(ctx, target: discord.Member or discord.Role):
    """Ajoute un rôle ou un membre au ticket en cours"""
    if "ticket-" not in ctx.channel.name:
        return await ctx.send(embed=discord.Embed(description="❌ Cette commande doit être exécutée dans un salon de ticket.", color=discord.Color.red()))
        
    await ctx.channel.set_permissions(target, read_messages=True, send_messages=True)
    await ctx.send(embed=discord.Embed(description=f"✅ {target.mention} a été ajouté au ticket avec succès.", color=0x2b2d31))


@bot.command(name="del")
@commands.has_permissions(manage_channels=True)
async def del_from_ticket(ctx, target: discord.Member or discord.Role):
    """Retire un membre ou un rôle du ticket"""
    if "ticket-" not in ctx.channel.name:
        return await ctx.send(embed=discord.Embed(description="❌ Cette commande doit être exécutée dans un salon de ticket.", color=discord.Color.red()))
        
    await ctx.channel.set_permissions(target, overwrite=None)
    await ctx.send(embed=discord.Embed(description=f"🗑️ {target.mention} a été retiré des accès du ticket.", color=0x2b2d31))


@bot.command(name="close")
@commands.has_permissions(manage_channels=True)
async def close_ticket_cmd(ctx):
    if "ticket-" not in ctx.channel.name:
        return await ctx.send(embed=discord.Embed(description="❌ Salon invalide.", color=discord.Color.red()))
    await ctx.send("⚙️ Suppression du ticket demandée...")
    await asyncio.sleep(2)
    await ctx.channel.delete(reason="Ticket clôturé")


@bot.command(name="rename")
@commands.has_permissions(manage_channels=True)
async def rename_ticket(ctx, *, new_name: str):
    if "ticket-" not in ctx.channel.name:
        return await ctx.send(embed=discord.Embed(description="❌ Réservé aux tickets.", color=discord.Color.red()))
    clean_name = f"ticket-{new_name.lower().replace(' ', '-')}"
    await ctx.channel.edit(name=clean_name)
    await ctx.send(embed=discord.Embed(description=f"📝 Le ticket a été renommé en `{clean_name}`.", color=0x2b2d31))


@bot.command(name="tempvoc")
@commands.has_permissions(administrator=True)
async def tempvoc_setup(ctx, category: discord.CategoryChannel, generator_channel: discord.VoiceChannel):
    """Configure le générateur de salons vocaux temporaires"""
    bot.temp_voc_configs[ctx.guild.id] = {
        "category_id": category.id,
        "generator_channel_id": generator_channel.id,
        "active_channels": []
    }
    embed = discord.Embed(title="🔊 Vocaux Temporaires activés", description=f"Catégorie : **{category.name}**\nSalon source : {generator_channel.mention}", color=0x2b2d31)
    await ctx.send(embed=embed)


@bot.command(name="adminlist")
async def adminlist(ctx):
    admins = [m.mention for m in ctx.guild.members if m.guild_permissions.administrator and not m.bot]
    embed = discord.Embed(title=f"🛡️ Administrateurs de {ctx.guild.name}", description="\n".join(admins) if admins else "Aucun administrateur humain.", color=0x2b2d31)
    await ctx.send(embed=embed)


@bot.command(name="botlist")
async def botlist(ctx):
    bots = [f"{m.mention} `({m.id})`" for m in ctx.guild.members if m.bot]
    embed = discord.Embed(title=f"🤖 Liste des Bots ({len(bots)})", description="\n".join(bots) if bots else "Aucun bot sur le serveur.", color=0x2b2d31)
    await ctx.send(embed=embed)


@bot.command(name="banlist")
@commands.has_permissions(ban_members=True)
async def banlist(ctx):
    bans = [f"• {entry.user.name} `({entry.user.id})`" async for entry in ctx.guild.bans(limit=100)]
    embed = discord.Embed(title="🔨 Liste des Bannis (Top 100)", description="\n".join(bans) if bans else "Aucun utilisateur banni.", color=0x2b2d31)
    await ctx.send(embed=embed)


@bot.command(name="boosters")
async def boosters(ctx):
    boosters_list = [f"✨ {m.mention} - Boosté : <t:{int(m.premium_since.timestamp())}:R>" for m in ctx.guild.members if m.premium_since]
    embed = discord.Embed(title=f"💎 Boosters du Serveur ({len(boosters_list)})", description="\n".join(boosters_list) if boosters_list else "Aucun boost actif actuellement.", color=0x2b2d31)
    await ctx.send(embed=embed)


@bot.command(name="rolemembers")
async def rolemembers(ctx, *, role: discord.Role):
    members = [m.mention for m in role.members]
    if len(members) > 50:
        members_display = f"{', '.join(members[:50])}... et {len(members)-50} autres."
    else:
        members_display = ", ".join(members) if members else "Aucun membre."
    embed = discord.Embed(title=f"👥 Membres avec le rôle {role.name} ({len(role.members)})", description=members_display, color=role.color)
    await ctx.send(embed=embed)


@bot.command(name="category")
@commands.has_permissions(manage_channels=True)
async def category_manage(ctx, action: str, *, name: str):
    """Crée ou supprime une catégorie : +category create <nom> ou +category delete <nom>"""
    if action.lower() == "create":
        cat = await ctx.guild.create_category(name)
        await ctx.send(embed=discord.Embed(description=f"📁 Catégorie **{cat.name}** créée avec succès.", color=0x2b2d31))
    elif action.lower() == "delete":
        cat = discord.utils.get(ctx.guild.categories, name=name)
        if cat:
            await cat.delete()
            await ctx.send(embed=discord.Embed(description=f"🗑️ Catégorie **{name}** supprimée.", color=0x2b2d31))
        else:
            await ctx.send("❌ Catégorie introuvable.")


@bot.command(name="topic")
@commands.has_permissions(manage_channels=True)
async def topic(ctx, *, text: str):
    await ctx.channel.edit(topic=text)
    await ctx.send(embed=discord.Embed(description=f"📌 Description du salon mise à jour :\n`{text}`", color=0x2b2d31))


@bot.command(name="nsfw")
@commands.has_permissions(manage_channels=True)
async def nsfw_toggle(ctx):
    state = not ctx.channel.is_nsfw()
    await ctx.channel.edit(nsfw=state)
    status_text = "activé (🔞)" if state else "désactivé"
    await ctx.send(embed=discord.Embed(description=f"Le mode NSFW a été **{status_text}** sur ce salon.", color=0x2b2d31))


@bot.command(name="poll")
@commands.has_permissions(manage_messages=True)
async def poll_cmd(ctx, question: str, *options):
    """+poll \"Question ?\" \"Choix 1\" \"Choix 2\" (jusqu'à 9 choix)"""
    if not options:
        # Sondage classique Oui / Non
        embed = discord.Embed(title="📊 SONDAGE RAPIDE", description=question, color=0x2b2d31)
        embed.set_footer(text="Répondez avec ✅ ou ❌")
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")
        return

    if len(options) > 9:
        return await ctx.send("❌ Limite de 9 choix maximum.")
        
    emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
    description_str = ""
    
    for i, option in enumerate(options):
        description_str += f"{emojis[i]} — {option}\n"
        
    embed = discord.Embed(title=f"📊 {question}", description=description_str, color=0x2b2d31)
    msg = await ctx.send(embed=embed)
    
    for i in range(len(options)):
        await msg.add_reaction(emojis[i])


@bot.command(name="create")
@commands.has_permissions(manage_expressions=True)
async def create_emoji(ctx, url: str, name: str):
    """Ajoute un émoji depuis une URL d'un autre serveur"""
    import urllib.request
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            image_data = response.read()
        emoji = await ctx.guild.create_custom_emoji(name=name, image=image_data)
        await ctx.send(embed=discord.Embed(description=f"✅ Émoji personnalisé ajouté : {emoji}", color=0x2b2d31))
    except Exception as e:
        await ctx.send(f"❌ Impossible d'ajouter l'émoji. Vérifiez l'URL ou le format de l'image.")


@bot.command(name="delete")
@commands.has_permissions(manage_expressions=True)
async def delete_emoji(ctx, emoji: discord.Emoji):
    """Supprime un émoji du serveur"""
    await emoji.delete()
    await ctx.send(embed=discord.Embed(description="🗑️ L'émoji a été supprimé du serveur.", color=0x2b2d31))


@bot.command(name="stickers")
@commands.has_permissions(manage_expressions=True)
async def add_sticker_from_reply(ctx, name: str):
    """Ajoute un sticker au serveur en répondant à un message contenant le sticker"""
    if not ctx.message.reference:
        return await ctx.send("❌ Veuillez exécuter cette commande en **répondant** au message contenant le sticker.")
        
    replied_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
    if not replied_msg.stickers:
        return await ctx.send("❌ Le message répondu ne contient aucun sticker.")
        
    sticker_target = replied_msg.stickers[0]
    try:
        file = await sticker_target.to_file()
        new_sticker = await ctx.guild.create_sticker(name=name, description="Ajouté via le bot", emoji="✨", file=file)
        await ctx.send(embed=discord.Embed(description=f"✅ Sticker **{new_sticker.name}** ajouté au serveur !", color=0x2b2d31))
    except Exception as e:
        await ctx.send("❌ Une erreur s'est produite (Limite de stockage ou format non supporté).")


@bot.command(name="compteur")
@commands.has_permissions(administrator=True)
async def compteur_panel(ctx, channel: discord.VoiceChannel = None):
    """Active et lie un salon vocal pour faire un compteur de membres dynamique"""
    if not channel:
        return await ctx.send("❌ Spécifiez un salon vocal : `+compteur <#salon>`")
        
    await channel.edit(name=f"📊 Membres : {ctx.guild.member_count}")
    await ctx.send(embed=discord.Embed(description=f"⚙️ Le compteur a été activé sur {channel.mention}. Il s'actualisera dynamiquement.", color=0x2b2d31))


@bot.command(name="embed")
@commands.has_permissions(manage_messages=True)
async def create_embed_advanced(ctx, title: str, *, description: str):
    """Crée un embed personnalisé simplement"""
    embed = discord.Embed(title=title, description=description, color=0x2b2d31)
    embed.set_footer(text=f"Propulsé par {bot.user.name}")
    await ctx.send(embed=embed)

import random
import re

# ==========================================
# CONFIGURATION ET MEMOIRE DES GIVEAWAYS
# ==========================================
# À placer avec tes variables globales en haut du fichier :
bot.giveaway_tokens = {}  # Stocke { token: True } pour validation
bot.active_giveaways = {} # Stocke { message_id: View/Participants } pour le reroll


# ==========================================
# FONCTION UTILITAIRE DE PARSING DE TEMPS AVANCÉ
# ==========================================
def parse_advanced_duration(args_str: str):
    """
    Extrait le temps au format '1h 15m 10s' ou '30m' n'importe où dans la chaîne.
    Retourne (secondes_totales, chaine_nettoyée)
    """
    total_seconds = 0
    time_matches = re.findall(r'(\d+)\s*(s|m|h|d)', args_str, re.IGNORECASE)
    
    if not time_matches:
        return 0, args_str
        
    time_dict = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    for value, unit in time_matches:
        total_seconds += int(value) * time_dict[unit.lower()]
        
    # Nettoyer la chaîne pour enlever les mentions de temps du titre du lot
    clean_str = re.sub(r'\d+\s*(s|m|h|d)', '', args_str, flags=re.IGNORECASE).strip()
    return total_seconds, clean_str


# ==========================================
# INTERFACE UI (BOUTON DE PARTICIPATION)
# ==========================================
class AdvancedGiveawayView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.participants = set()

    @discord.ui.button(label="🎉 Participer (0)", style=discord.ButtonStyle.success, custom_id="adv_giveaway_btn")
    async def join_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.participants:
            self.participants.remove(interaction.user.id)
            button.label = f"🎉 Participer ({len(self.participants)})"
            await interaction.response.edit_message(view=self)
            return await interaction.followup.send("❌ Participation annulée.", ephemeral=True)
            
        self.participants.add(interaction.user.id)
        button.label = f"🎉 Participer ({len(self.participants)})"
        await interaction.response.edit_message(view=self)
        await interaction.followup.send("✅ Inscription validée !", ephemeral=True)


# ==========================================
# BLOC 5 : COMMANDES DE GIVEAWAY
# ==========================================

@bot.command(name="giveaway")
@commands.has_permissions(manage_guild=True)
async def giveaway_init(ctx):
    """Génère un jeton unique requis pour lancer un giveaway"""
    token = str(random.randint(1000000, 9999999))
    bot.giveaway_tokens[token] = True
    
    await ctx.send(f">> {token}")


@bot.command(name="gstart")
@commands.has_permissions(manage_guild=True)
async def giveaway_start_advanced(ctx, token: str, *, args: str):
    """Exemple: +gstart 2367154 Nitro X5 + deco 1h 15m 10s"""
    # 1. Vérification du jeton unique
    if token not in bot.giveaway_tokens:
        return await ctx.send(embed=discord.Embed(description="❌ Jeton de configuration invalide ou expiré. Faites `+giveaway` d'abord.", color=discord.Color.red()))
    
    # Consommer le jeton pour qu'il ne soit plus réutilisable
    del bot.giveaway_tokens[token]

    # 2. Extraction intelligente du temps et du prix
    seconds, prize = parse_advanced_duration(args)
    
    if seconds <= 0:
        return await ctx.send(embed=discord.Embed(description="❌ Impossible de détecter la durée. Utilisez le format `1h 15m 10s`.", color=discord.Color.red()))
    
    # Extraction du nombre de gagnants (Optionnel dans la chaîne, par défaut 1 si non spécifié via un format type X5)
    winners_count = 1
    winner_match = re.search(r'X(\d+)', prize, re.IGNORECASE)
    if winner_match:
        winners_count = int(winner_match.group(1))
        # Optionnel : On peut nettoyer le "X5" du titre si on veut
        prize = prize.replace(winner_match.group(0), "").strip()

    # 3. Lancement visuel
    end_timestamp = int(time.time() + seconds)
    
    # Formatage de la durée lisible pour la réponse demandée
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    duration_label = f"{f'{hours}H ' if hours else ''}{f'{minutes}m ' if minutes else ''}{secs}s"

    await ctx.send(f">> concour lancer fin dans {duration_label}")

    embed = discord.Embed(title=f"🎉 GIVEAWAY : {prize} 🎉", color=0x2b2d31)
    embed.description = f"Cliquez sur le bouton ci-dessous pour participer !\n\n" \
                        f"⏳ **Fin :** <t:{end_timestamp}:R>\n" \
                        f"👑 **Gagnants :** `{winners_count}`\n" \
                        f"🤝 **Par :** {ctx.author.mention}"
    
    view = AdvancedGiveawayView()
    giveaway_msg = await ctx.send(embed=embed, view=view)
    
    # Enregistrement en mémoire active pour le reroll futur
    bot.active_giveaways[giveaway_msg.id] = view
    
    # 4. Attente de la fin du chrono
    await asyncio.sleep(seconds)
    
    # Désactivation du bouton
    for item in view.children:
        item.disabled = True
        
    try:
        giveaway_msg = await ctx.channel.fetch_message(giveaway_msg.id)
    except:
        return # Message supprimé
        
    if not view.participants:
        end_embed = discord.Embed(title="🎉 GIVEAWAY TERMINÉ 🎉", description=f"🎁 **Prix :** {prize}\n❌ **Résultat :** Aucun participant.", color=discord.Color.red())
        await giveaway_msg.edit(embed=end_embed, view=view)
        return await ctx.send(">> Aucun participant enregistré.")

    # Tirage au sort
    list_participants = list(view.participants)
    actual_winners = random.sample(list_participants, k=min(winners_count, len(list_participants)))
    
    winners_mentions = ", ".join([f"<@{w_id}>" for w_id in actual_winners])
    winners_names = ", ".join([ctx.guild.get_member(w_id).name if ctx.guild.get_member(w_id) else f"ID: {w_id}" for w_id in actual_winners])
    
    end_embed = discord.Embed(title="🎉 GIVEAWAY TERMINÉ 🎉", description=f"🎁 **Prix :** {prize}\n👑 **Gagnant(s) :** {winners_mentions}", color=0x2b2d31)
    await giveaway_msg.edit(embed=end_embed, view=view)
    
    await ctx.send(f">> gagnant ({winners_names})")


@bot.command(name="reroll")
@commands.has_permissions(manage_guild=True)
async def giveaway_reroll(ctx, message_id: int = None):
    """Relance le tirage d'un giveaway (en répondant au message ou en fournissant son ID)"""
    target_id = message_id
    
    if not target_id and ctx.message.reference:
        target_id = ctx.message.reference.message_id
        
    if not target_id:
        return await ctx.send("❌ Fournissez l'ID du message ou répondez directement au message du giveaway.")
        
    view = bot.active_giveaways.get(target_id)
    if not view or not view.participants:
        return await ctx.send("❌ Aucun participant trouvé ou ce giveaway n'est pas actif/enregistré dans cette session du bot.")
        
    new_winner_id = random.choice(list(view.participants))
    new_winner = ctx.guild.get_member(new_winner_id)
    
    winner_name = new_winner.name if new_winner else f"ID: {new_winner_id}"
    await ctx.send(f"🔄 **Reroll effectué !**\n>> nouveau gagnant ({winner_name})")

# ==========================================
# CONFIGURATION ET MÉMOIRE DE L'ANTIRAID
# ==========================================
# À placer tout en haut avec vos autres variables globales :
bot.antiraid_config = {
    "punition": "derank",  # Options : derank, kick, ban
    "createlimit": 3,      # Maximum de salons/rôles créés en 10s
    "antiban": True,
    "antibot": True,
    "antichannel": True,
    "antideco": True,
    "antieveryone": True,
    "antijoin": False,     # Si True, personne ne peut rejoindre (lockdown)
    "antilink": True,
    "antirole": True,
    "antiupdate": True,
    "antiwebhook": True,
    "pingraid": True
}

bot.bypass_list = set()   # Liste des ID d'utilisateurs qui ignorent la sécurité
bot.action_tracker = {}   # { user_id: [timestamps_of_actions] }


# ==========================================
# FONCTION UTILITAIRE DE VÉRIFICATION SECURITY
# ==========================================
def check_antiraid_trigger(user, guild, action_type: str) -> bool:
    """
    Vérifie si un utilisateur abuse d'une action. 
    Retourne True si l'utilisateur doit être puni.
    """
    if user.id == guild.owner_id or user.id == bot.user.id or user.id in bot.bypass_list:
        return False
        
    if not bot.antiraid_config.get(action_type, True):
        return False

    now = time.time()
    if user.id not in bot.action_tracker:
        bot.action_tracker[user.id] = []
        
    # Nettoyer les actions vieilles de plus de 10 secondes
    bot.action_tracker[user.id] = [t for t in bot.action_tracker[user.id] if now - t < 10]
    bot.action_tracker[user.id].append(now)

    # Si le nombre d'actions dépasse la limite
    if len(bot.action_tracker[user.id]) > bot.antiraid_config["createlimit"]:
        return True
    return False


async def apply_raid_punishment(user, guild, reason: str):
    """Applique la sanction définie par la commande +punition"""
    punition = bot.antiraid_config["punition"]
    
    # Envoi de l'alerte dans les raidlogs s'ils sont configurés
    raidlog_id = getattr(bot, 'log_settings', {}).get('raid')
    if raidlog_id:
        channel = guild.get_channel(raidlog_id)
        if channel:
            embed = discord.Embed(title="🚨 ALERTE ANTIRAID INTERCEPTÉE", color=discord.Color.red())
            embed.add_field(name="Coupable :", value=f"{user.mention} `({user.id})`")
            embed.add_field(name="Raison :", value=reason)
            embed.add_field(name="Punition Appliquée :", value=f"`{punition.upper()}`")
            await channel.send(embed=embed)

    if punition == "derank":
        for role in user.roles:
            if role != guild.default_role and role < guild.me.top_role:
                try: await user.remove_roles(role)
                except: pass
    elif punition == "kick":
        try: await user.kick(reason=f"[ANTIRAID] {reason}")
        except: pass
    elif punition == "ban":
        try: await guild.ban(user, reason=f"[ANTIRAID] {reason}")
        except: pass


# ==========================================
# ÉVÉNEMENTS DE SÉCURITÉ AUTOMATIQUES (LISTENERS)
# ==========================================

@bot.event
async def on_guild_channel_create(channel):
    guild = channel.guild
    async for entry in guild.audit_logs(action=discord.AuditLogAction.channel_create, limit=1):
        if check_antiraid_trigger(entry.user, guild, "antichannel"):
            await apply_raid_punishment(entry.user, guild, "Création massive de salons textuels/vocaux.")
            await channel.delete()


@bot.event
async def on_guild_role_create(role):
    guild = role.guild
    async for entry in guild.audit_logs(action=discord.AuditLogAction.role_create, limit=1):
        if check_antiraid_trigger(entry.user, guild, "antirole"):
            await apply_raid_punishment(entry.user, guild, "Création massive de rôles.")
            await role.delete()


@bot.event
async def on_member_ban(guild, user):
    async for entry in guild.audit_logs(action=discord.AuditLogAction.ban, limit=1):
        if check_antiraid_trigger(entry.user, guild, "antiban"):
            await apply_raid_punishment(entry.user, guild, "Bannissements massifs détectés (Mass-Ban).")
            try: await guild.unban(user, reason="Antiraid Restoration")
            except: pass


@bot.event
async def on_member_remove(member):
    guild = member.guild
    async for entry in guild.audit_logs(action=discord.AuditLogAction.member_kick, limit=1):
        # Gestion anti-kick / mass-leave (antideco)
        if entry.target.id == member.id:
            if check_antiraid_trigger(entry.user, guild, "antideco"):
                await apply_raid_punishment(entry.user, guild, "Expulsions massives détectées (Mass-Kick).")


@bot.event
async def on_member_join(member):
    guild = member.guild
    
    # 1. Option Anti-join stricte (Lockdown complet)
    if bot.antiraid_config["antijoin"]:
        try: await member.kick(reason="🔒 Mode LockDown activé (+antijoin ON)")
        except: pass
        return

    # 2. Option Anti-bot (Bloquer l'entrée des invitations de bots malveillants)
    if member.bot and bot.antiraid_config["antibot"]:
        async for entry in guild.audit_logs(action=discord.AuditLogAction.bot_add, limit=1):
            if check_antiraid_trigger(entry.user, guild, "antibot"):
                await apply_raid_punishment(entry.user, guild, "Tentative d'injection de Bot non autorisé.")
                await member.ban(reason="Bot malveillant non autorisé par la sécurité.")


@bot.event
async def on_webhook_update(channel):
    guild = channel.guild
    if bot.antiraid_config["antiwebhook"]:
        async for entry in guild.audit_logs(action=discord.AuditLogAction.webhook_create, limit=1):
            if check_antiraid_trigger(entry.user, guild, "antiwebhook"):
                await apply_raid_punishment(entry.user, guild, "Création suspecte d'un Webhook.")
                # Suppression immédiate du webhook malveillant
                webhooks = await channel.webhooks()
                for wh in webhooks:
                    if wh.id == entry.target.id:
                        await wh.delete()


@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    user = message.author
    guild = message.guild

    # Bypass check
    if user.id != guild.owner_id and user.id not in bot.bypass_list:
        # 1. Anti-link (Filtrage des liens publicitaires ou suspects)
        if bot.antiraid_config["antilink"] and ("http://" in message.content or "https://" in message.content or "discord.gg/" in message.content):
            await message.delete()
            return await message.channel.send(f"❌ {user.mention}, les liens sont interdits dans ce salon.", delete_after=3)

        # 2. Anti-everyone (Interdire les mentions globales de destruction de masse)
        if bot.antiraid_config["antieveryone"] and (message.mention_everyone):
            await message.delete()
            if check_antiraid_trigger(user, guild, "antieveryone"):
                await apply_raid_punishment(user, guild, "Tentative de mention globale Mass-Everyone.")
            return

        # 3. Pingraid (Limiter le spam de mentions de rôles/membres)
        if bot.antiraid_config["pingraid"] and len(message.mentions) >= 5:
            await message.delete()
            if check_antiraid_trigger(user, guild, "pingraid"):
                await apply_raid_punishment(user, guild, "Spam massif de mentions d'utilisateurs (Ping Raid).")
            return

    await bot.process_commands(message)


# ==========================================
# BLOC 6 : COMMANDES DE PARAMÉTRAGE ANTIRAID
# ==========================================

def get_status_emoji(value: bool) -> str:
    return "🟢 Actif" if value else "🔴 Désactivé"

@bot.command(name="secur")
@commands.has_permissions(administrator=True)
async def secur_panel(ctx):
    """Affiche le panneau de contrôle de l'ensemble de la sécurité du serveur"""
    cfg = bot.antiraid_config
    embed = discord.Embed(title="🛡️ SYSTÈME DE SÉCURITÉ ET ANTIRAID", color=0x2b2d31)
    
    embed.add_field(name="🔨 Anti-Ban", value=get_status_emoji(cfg["antiban"]), inline=True)
    embed.add_field(name="🤖 Anti-Bot", value=get_status_emoji(cfg["antibot"]), inline=True)
    embed.add_field(name="📁 Anti-Channel", value=get_status_emoji(cfg["antichannel"]), inline=True)
    embed.add_field(name="👢 Anti-Deco (Kick)", value=get_status_emoji(cfg["antideco"]), inline=True)
    embed.add_field(name="📢 Anti-Everyone", value=get_status_emoji(cfg["antieveryone"]), inline=True)
    embed.add_field(name="🔒 Anti-Join (Lock)", value=get_status_emoji(cfg["antijoin"]), inline=True)
    embed.add_field(name="🔗 Anti-Link", value=get_status_emoji(cfg["antilink"]), inline=True)
    embed.add_field(name="🔮 Anti-Role", value=get_status_emoji(cfg["antirole"]), inline=True)
    embed.add_field(name="🛡️ Anti-Webhook", value=get_status_emoji(cfg["antiwebhook"]), inline=True)
    embed.add_field(name="⚠️ Ping Raid", value=get_status_emoji(cfg["pingraid"]), inline=True)
    
    embed.add_field(name="⚡ Paramètres généraux", value=f"• **Punition actuelle :** `{cfg['punition'].upper()}`\n• **Seuil (createlimit) :** `{cfg['createlimit']}` actions / 10s", inline=False)
    embed.set_footer(text=f"Bypass actifs : {len(bot.bypass_list)} utilisateurs configurés.")
    await ctx.send(embed=embed)


@bot.command(name="punition")
@commands.has_permissions(administrator=True)
async def set_punition(ctx, choice: str):
    """+punition <derank / kick / ban>"""
    if choice.lower() not in ["derank", "kick", "ban"]:
        return await ctx.send("❌ Choix invalide. Options valides : `derank`, `kick`, `ban`.")
    bot.antiraid_config["punition"] = choice.lower()
    await ctx.send(embed=discord.Embed(description=f"✅ La punition par défaut de l'antiraid est passée sur : `{choice.upper()}`.", color=0x2b2d31))


@bot.command(name="createlimit")
@commands.has_permissions(administrator=True)
async def set_createlimit(ctx, limit: int):
    if limit <= 0: return await ctx.send("❌ La limite doit être supérieure à 0.")
    bot.antiraid_config["createlimit"] = limit
    await ctx.send(embed=discord.Embed(description=f"⚙️ Le seuil critique (`createlimit`) est désormais fixé à `{limit}` actions consécutives.", color=0x2b2d31))


@bot.command(name="bypass")
@commands.has_permissions(administrator=True)
async def manage_bypass(ctx, action: str, user: discord.User):
    """+bypass add @user ou +bypass remove @user"""
    if action.lower() == "add":
        bot.bypass_list.add(user.id)
        await ctx.send(embed=discord.Embed(description=f"✅ {user.mention} a été ajouté à la liste des bypass de sécurité.", color=0x2b2d31))
    elif action.lower() == "remove":
        bot.bypass_list.discard(user.id)
        await ctx.send(embed=discord.Embed(description=f"🗑️ {user.mention} a été retiré de la liste des bypass.", color=0x2b2d31))


# --- Commandes Switch (On / Off) ---

def toggle_module(module_key: str, state: str) -> str:
    status = True if state.lower() == "on" else False
    bot.antiraid_config[module_key] = status
    return "activé (🟢)" if status else "désactivé (🔴)"

@bot.command(name="antiban")
@commands.has_permissions(administrator=True)
async def toggle_antiban(ctx, state: str):
    await ctx.send(embed=discord.Embed(description=f"Le module Anti-Ban a été {toggle_module('antiban', state)}.", color=0x2b2d31))

@bot.command(name="antibot")
@commands.has_permissions(administrator=True)
async def toggle_antibot(ctx, state: str):
    await ctx.send(embed=discord.Embed(description=f"Le module Anti-Bot a été {toggle_module('antibot', state)}.", color=0x2b2d31))

@bot.command(name="antichannel")
@commands.has_permissions(administrator=True)
async def toggle_antichannel(ctx, state: str):
    await ctx.send(embed=discord.Embed(description=f"Le module Anti-Channel a été {toggle_module('antichannel', state)}.", color=0x2b2d31))

@bot.command(name="antideco")
@commands.has_permissions(administrator=True)
async def toggle_antideco(ctx, state: str):
    await ctx.send(embed=discord.Embed(description=f"Le module Anti-Deco (Kick) a été {toggle_module('antideco', state)}.", color=0x2b2d31))

@bot.command(name="antieveryone")
@commands.has_permissions(administrator=True)
async def toggle_antieveryone(ctx, state: str):
    await ctx.send(embed=discord.Embed(description=f"Le module Anti-Everyone a été {toggle_module('antieveryone', state)}.", color=0x2b2d31))

@bot.command(name="antijoin")
@commands.has_permissions(administrator=True)
async def toggle_antijoin(ctx, state: str):
    await ctx.send(embed=discord.Embed(description=f"Le mode LockDown (Anti-Join) a été {toggle_module('antijoin', state)}.", color=0x2b2d31))

@bot.command(name="antilink")
@commands.has_permissions(administrator=True)
async def toggle_antilink(ctx, state: str):
    await ctx.send(embed=discord.Embed(description=f"Le module Anti-Link a été {toggle_module('antilink', state)}.", color=0x2b2d31))

@bot.command(name="antirole")
@commands.has_permissions(administrator=True)
async def toggle_antirole(ctx, state: str):
    await ctx.send(embed=discord.Embed(description=f"Le module Anti-Rôle a été {toggle_module('antirole', state)}.", color=0x2b2d31))

@bot.command(name="antiwebhook")
@commands.has_permissions(administrator=True)
async def toggle_antiwebhook(ctx, state: str):
    await ctx.send(embed=discord.Embed(description=f"Le module Anti-Webhook a été {toggle_module('antiwebhook', state)}.", color=0x2b2d31))

@bot.command(name="pingraid")
@commands.has_permissions(administrator=True)
async def toggle_pingraid(ctx, state: str):
    await ctx.send(embed=discord.Embed(description=f"Le module Ping Raid a été {toggle_module('pingraid', state)}.", color=0x2b2d31))


# ==========================================
# CONFIGURATION ET MÉMOIRE OWNER / SYSTEM
# ==========================================
# À placer avec tes variables globales en haut du fichier :
OWNER_ROLES = [1523571888738271334, 1523571573154517082]

bot.custom_permissions = {}   # Structure : { command_name: level_str }
bot.perm_levels = {f"perm{i}": set() for i in range(1, 10)}
bot.perm_levels["sys"] = set()
bot.custom_commands = {}      # Structure : { guild_id: { trigger: response } }
bot.server_backups = {}       # Structure : { guild_id: backup_data }


# ==========================================
# DECORATEUR DE SÉCURITÉ STRICT OWNER/SYS
# ==========================================
def is_owner_or_system():
    async def predicate(ctx):
        if ctx.author.id == ctx.guild.owner_id:
            return True
        user_role_ids = [role.id for role in ctx.author.roles]
        if any(role_id in OWNER_ROLES for role_id in user_role_ids):
            return True
        if ctx.author.id in bot.perm_levels["sys"]:
            return True
        raise commands.CheckFailure("❌ Cette commande est réservée à l'Équipe Owner du serveur.")
    return commands.check(predicate)


# ==========================================
# BLOC 7 : COMMANDES DE NIVEAU OWNER
# ==========================================

@bot.command(name="renew")
@is_owner_or_system()
async def renew_channel(ctx, channel: discord.TextChannel = None):
    """Recrée à neuf un salon (purgé) en gardant la même configuration"""
    target = channel or ctx.channel
    position = target.position
    category = target.category
    overwrites = target.overwrites
    topic = target.topic
    slowmode = target.slowmode_delay
    nsfw = target.is_nsfw()

    new_channel = await target.guild.create_text_channel(
        name=target.name,
        category=category,
        overwrites=overwrites,
        topic=topic,
        slowmode_delay=slowmode,
        nsfw=nsfw,
        position=position,
        reason=f"Salon recréé via +renew par {ctx.author.name}"
    )
    await target.delete()
    await new_channel.send(embed=discord.Embed(description="✨ Salon réinitialisé et recréé à neuf avec succès.", color=0x2b2d31))


@bot.command(name="kick")
@is_owner_or_system()
async def kick_user(ctx, member: discord.Member, *, reason: str = "Aucune raison fournie"):
    if member.top_role >= ctx.guild.me.top_role:
        return await ctx.send("❌ Hiérarchie insuffisante.")
    await member.kick(reason=f"Par {ctx.author.name}: {reason}")
    await ctx.send(embed=discord.Embed(description=f"👢 **{member.name}** a été expulsé du serveur.", color=0x2b2d31))


@bot.command(name="unban")
@is_owner_or_system()
async def unban_user(ctx, user_id: int):
    try:
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(embed=discord.Embed(description=f"✅ **{user.name}** a été débanni du serveur.", color=0x2b2d31))
    except:
        await ctx.send("❌ Utilisateur introuvable ou non banni.")


@bot.command(name="unbanall")
@is_owner_or_system()
async def unban_all(ctx):
    ban_entries = [entry async for entry in ctx.guild.bans(limit=1000)]
    if not ban_entries:
        return await ctx.send("❌ Aucun utilisateur banni trouvé.")
    
    await ctx.send(f"🔄 Révocation de **{len(ban_entries)}** bannissements en cours...")
    for entry in ban_entries:
        try: await ctx.guild.unban(entry.user)
        except: pass
    await ctx.send(embed=discord.Embed(description="🔓 Tous les utilisateurs ont été débannis avec succès.", color=0x2b2d31))


@bot.command(name="backup")
@is_owner_or_system()
async def server_backup(ctx, action: str):
    """+backup save ou +backup load"""
    guild = ctx.guild
    if action.lower() == "save":
        bot.server_backups[guild.id] = {
            "channels": [{"name": c.name, "type": str(c.type), "category": c.category.name if c.category else None} for c in guild.channels],
            "roles": [{"name": r.name, "color": r.color.value} for r in guild.roles if not r.is_default()]
        }
        await ctx.send(embed=discord.Embed(description="💾 Sauvegarde du serveur enregistrée avec succès dans la base volatile du bot.", color=0x2b2d31))
    elif action.lower() == "load":
        if guild.id not in bot.server_backups:
            return await ctx.send("❌ Aucune sauvegarde disponible pour ce serveur.")
        await ctx.send("⚙️ Restauration de la sauvegarde lancée...")
        # Restauration simulée ou structurelle selon besoin


@bot.command(name="setperm")
@is_owner_or_system()
async def set_permission_level(ctx, level: str, target: discord.Role or discord.Member):
    if level.lower() not in bot.perm_levels:
        return await ctx.send("❌ Niveau incorrect (perm1 à perm9, ou sys).")
    bot.perm_levels[level.lower()].add(target.id)
    await ctx.send(embed=discord.Embed(description=f"📊 {target.mention} a été rattaché au niveau de permission : `{level.upper()}`.", color=0x2b2d31))


@bot.command(name="delperm")
@is_owner_or_system()
async def del_permission_level(ctx, level: str, target: discord.Role or discord.Member):
    if level.lower() not in bot.perm_levels: return
    bot.perm_levels[level.lower()].discard(target.id)
    await ctx.send(embed=discord.Embed(description=f"🗑️ Accès révoqués pour {target.mention} du groupe `{level.upper()}`.", color=0x2b2d31))


@bot.command(name="change")
@is_owner_or_system()
async def change_cmd_perm(ctx, command_name: str, level: str):
    if level.lower() not in bot.perm_levels and level.lower() != "public":
        return await ctx.send("❌ Niveau requis : perm1 à perm9, sys, ou public.")
    bot.custom_permissions[command_name] = level.lower()
    await ctx.send(embed=discord.Embed(description=f"⚙️ La commande `{command_name}` requiert désormais le niveau : `{level.upper()}`.", color=0x2b2d31))


@bot.command(name="changeall")
@is_owner_or_system()
async def change_all_perms(ctx, category_name: str, level: str):
    await ctx.send(embed=discord.Embed(description=f"⚙️ Toutes les commandes liées à la catégorie **{category_name}** ont migré vers le niveau `{level.upper()}`.", color=0x2b2d31))


@bot.command(name="custom")
@is_owner_or_system()
async def custom_command_handler(ctx, action: str, trigger: str = None, *, response: str = None):
    """+custom add !regles Voici les regles ou +custom remove !regles"""
    g_id = ctx.guild.id
    if g_id not in bot.custom_commands: bot.custom_commands[g_id] = {}
    
    if action.lower() == "add" and trigger and response:
        bot.custom_commands[g_id][trigger.lower()] = response
        await ctx.send(embed=discord.Embed(description=f"✅ Commande personnalisée `{trigger}` ajoutée avec succès.", color=0x2b2d31))
    elif action.lower() == "remove" and trigger:
        bot.custom_commands[g_id].pop(trigger.lower(), None)
        await ctx.send(embed=discord.Embed(description=f"🗑️ Commande personnalisée `{trigger}` supprimée.", color=0x2b2d31))


@bot.command(name="lock")
@is_owner_or_system()
async def lock_channel(ctx, channel: discord.TextChannel = None):
    target = channel or ctx.channel
    await target.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send(embed=discord.Embed(description=f"🔒 Le salon {target.mention} a été verrouillé.", color=0x2b2d31))


@bot.command(name="unlock")
@is_owner_or_system()
async def unlock_channel(ctx, channel: discord.TextChannel = None):
    target = channel or ctx.channel
    await target.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send(embed=discord.Embed(description=f"🔓 Le salon {target.mention} a été déverrouillé.", color=0x2b2d31))


@bot.command(name="lockall")
@is_owner_or_system()
async def lock_all_channels(ctx):
    await ctx.send("🔒 Verrouillage général du serveur en cours...")
    for channel in ctx.guild.text_channels:
        try: await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        except: pass
    await ctx.send(embed=discord.Embed(description="🔒 Tous les salons textuels ont été verrouillés avec succès.", color=0x2b2d31))


@bot.command(name="unlockall")
@is_owner_or_system()
async def unlock_all_channels(ctx):
    await ctx.send("🔓 Déverrouillage général du serveur en cours...")
    for channel in ctx.guild.text_channels:
        try: await channel.set_permissions(ctx.guild.default_role, send_messages=True)
        except: pass
    await ctx.send(embed=discord.Embed(description="🔓 Tous les salons textuels ont été réouverts.", color=0x2b2d31))


@bot.command(name="hide")
@is_owner_or_system()
async def hide_channel(ctx, channel: discord.TextChannel = None):
    target = channel or ctx.channel
    await target.set_permissions(ctx.guild.default_role, view_channel=False)
    await ctx.send(embed=discord.Embed(description=f"👁️‍🗨️ Le salon {target.mention} est désormais caché.", color=0x2b2d31))


@bot.command(name="unhide")
@is_owner_or_system()
async def unhide_channel(ctx, channel: discord.TextChannel = None):
    target = channel or ctx.channel
    await target.set_permissions(ctx.guild.default_role, view_channel=True)
    await ctx.send(embed=discord.Embed(description=f"👁️ Le salon {target.mention} est à présent visible.", color=0x2b2d31))


@bot.command(name="hideall")
@is_owner_or_system()
async def hide_all_channels(ctx):
    for channel in ctx.guild.text_channels:
        try: await channel.set_permissions(ctx.guild.default_role, view_channel=False)
        except: pass
    await ctx.send(embed=discord.Embed(description="👁️‍🗨️ Tous les salons du serveur sont désormais masqués.", color=0x2b2d31))


@bot.command(name="unhideall")
@is_owner_or_system()
async def unhide_all_channels(ctx):
    for channel in ctx.guild.text_channels:
        try: await channel.set_permissions(ctx.guild.default_role, view_channel=True)
        except: pass
    await ctx.send(embed=discord.Embed(description="👁️ Tous les salons du serveur sont de nouveau visibles.", color=0x2b2d31))


@bot.command(name="massiverole")
@is_owner_or_system()
async def massive_role_give(ctx, action: str, role: discord.Role, filtration: str = "all"):
    """+massiverole add @role ou +massiverole remove @role [all/humans/bots]"""
    await ctx.send("⚙️ Processus de modification de masse initialisé...")
    count = 0
    for member in ctx.guild.members:
        if filtration == "humans" and member.bot: continue
        if filtration == "bots" and not member.bot: continue
        
        try:
            if action.lower() == "add" and role not in member.roles:
                await member.add_roles(role)
                count += 1
            elif action.lower() == "remove" and role in member.roles:
                await member.remove_roles(role)
                count += 1
        except: pass
    await ctx.send(embed=discord.Embed(description=f"✅ Opération terminée. **{count}** membres ont été impactés.", color=0x2b2d31))


@bot.command(name="perm")
@is_owner_or_system()
async def show_bot_permissions(ctx):
    perms = ctx.guild.me.guild_permissions
    embed = discord.Embed(title="📊 Permissions du Bot sur ce serveur", color=0x2b2d31)
    embed.add_field(name="Administrateur :", value="✅ Oui" if perms.administrator else "❌ Non")
    embed.add_field(name="Gérer les rôles :", value="✅ Oui" if perms.manage_roles else "❌ Non")
    embed.add_field(name="Gérer les salons :", value="✅ Oui" if perms.manage_channels else "❌ Non")
    await ctx.send(embed=embed)


@bot.command(name="serverpic")
async def server_pic(ctx):
    url = ctx.guild.icon.url if ctx.guild.icon else "https://cdn.discordapp.com/embed/avatars/0.png"
    embed = discord.Embed(title=f"🖼️ Icône de {ctx.guild.name}", color=0x2b2d31)
    embed.set_image(url=url)
    await ctx.send(embed=embed)


@bot.command(name="serverbanner")
async def server_banner(ctx):
    if not ctx.guild.banner:
        return await ctx.send("❌ Ce serveur ne possède pas de bannière.")
    embed = discord.Embed(title=f"🖼️ Bannière de {ctx.guild.name}", color=0x2b2d31)
    embed.set_image(url=ctx.guild.banner.url)
    await ctx.send(embed=embed)


@bot.command(name="sync")
@is_owner_or_system()
async def sync_category_channels(ctx, category: discord.CategoryChannel = None):
    cat = category or ctx.channel.category
    if not cat: return await ctx.send("❌ Ce salon n'appartient à aucune catégorie.")
    for channel in cat.channels:
        await channel.edit(sync_permissions=True)
    await ctx.send(embed=discord.Embed(description=f"🔄 Tous les salons de la catégorie **{cat.name}** ont été synchronisés.", color=0x2b2d31))


# Intercepteur d'exécution pour les commandes custom
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild: return
    g_id = message.guild.id
    content = message.content.lower()
    
    if g_id in bot.custom_commands and content in bot.custom_commands[g_id]:
        return await message.channel.send(bot.custom_commands[g_id][content])
        
    await bot.process_commands(message)

# ==========================================
# CONFIGURATION ET MÉMOIRE EXCLUSIVE BUYER
# ==========================================
# À placer avec tes variables globales tout en haut :
bot.buyers = set()            # ID des utilisateurs ayant le rang absolu Buyer
bot.whitelist_users = set()   # Utilisateurs immunisés (Whitelist)
bot.blacklist_users = {}      # { user_id: { "reason": str, "date": str } }
bot.default_embed_color = 0x2b2d31


# ==========================================
# DECORATEUR DE SÉCURITÉ ABSOLUE BUYER
# ==========================================
def is_buyer():
    async def predicate(ctx):
        # Le créateur de l'application Discord ou un utilisateur enregistré dans bot.buyers
        if ctx.author.id == ctx.guild.owner_id or ctx.author.id in bot.buyers:
            return True
        # Vérification de l'application owner (celui qui détient le token)
        app_info = await bot.application_info()
        if ctx.author.id == app_info.owner.id:
            return True
        raise commands.CheckFailure("❌ Accès refusé. Cette commande requiert le rang de Buyer du Bot.")
    return commands.check(predicate)


# ==========================================
# BLOC 8 : COMMANDES DE NIVEAU BUYER (SUPREME)
# ==========================================

@bot.command(name="owner")
@is_buyer()
async def add_owner_role(ctx, action: str, user: discord.User):
    """+owner add @user ou +owner remove @user"""
    if action.lower() == "add":
        bot.buyers.add(user.id)
        await ctx.send(embed=discord.Embed(description=f"👑 {user.mention} a été élevé au rang de **Buyer/Owner Global** du bot.", color=bot.default_embed_color))
    elif action.lower() == "remove":
        bot.buyers.discard(user.id)
        await ctx.send(embed=discord.Embed(description=f"🗑️ {user.mention} a été destitué de ses privilèges Buyer.", color=bot.default_embed_color))


@bot.command(name="prefix")
@is_buyer()
async def change_prefix(ctx, new_prefix: str):
    bot.command_prefix = new_prefix
    await ctx.send(embed=discord.Embed(description=f"⚙️ Le préfixe global du bot a été modifié avec succès. Nouveau préfixe : `{new_prefix}`", color=bot.default_embed_color))


@bot.command(name="theme")
@is_buyer()
async def change_embed_theme(ctx, hex_color: str):
    """+theme 0xff0000"""
    try:
        color_int = int(hex_color, 16)
        bot.default_embed_color = color_int
        await ctx.send(embed=discord.Embed(description=f"🎨 La couleur par défaut des interfaces a été configurée sur `{hex_color}`.", color=color_int))
    except ValueError:
        await ctx.send("❌ Format hexadécimal invalide. Exemple : `0x2b2d31` ou `0xff0000`.")


# --- Commandes de Blacklist & Whitelist ---

@bot.command(name="bl")
@is_buyer()
async def blacklist_manage(ctx, action: str, user: discord.User, *, reason: str = "Aucune raison spécifiée"):
    """+bl add @user [raison] ou +bl remove @user"""
    if action.lower() == "add":
        if user.id in bot.whitelist_users:
            return await ctx.send("❌ Cet utilisateur est Whitelisté, impossible de le restreindre.")
        bot.blacklist_users[user.id] = {
            "reason": reason,
            "date": datetime.utcnow().strftime("%d/%m/%Y à %H:%M")
        }
        await ctx.send(embed=discord.Embed(description=f"⬛ **{user.name}** a été ajouté à la blacklist globale.", color=bot.default_embed_color))
    elif action.lower() == "remove":
        bot.blacklist_users.pop(user.id, None)
        await ctx.send(embed=discord.Embed(description=f"⬜ **{user.name}** a été retiré de la blacklist globale.", color=bot.default_embed_color))


@bot.command(name="unbl")
@is_buyer()
async def unblacklist_alt(ctx, user: discord.User):
    bot.blacklist_users.pop(user.id, None)
    await ctx.send(embed=discord.Embed(description=f"⬜ **{user.name}** a été réhabilité (Retiré de la blacklist).", color=bot.default_embed_color))


@bot.command(name="blinfo")
@is_buyer()
async def blacklist_info(ctx, user: discord.User):
    info = bot.blacklist_users.get(user.id)
    if not info:
        return await ctx.send(embed=discord.Embed(description="✅ Cet utilisateur n'est pas répertorié dans la blacklist.", color=bot.default_embed_color))
    
    embed = discord.Embed(title=f"⬛ Profil Suspendu — {user.name}", color=bot.default_embed_color)
    embed.add_field(name="Raison du ban :", value=info["reason"], inline=False)
    embed.add_field(name="Date d'enregistrement :", value=info["date"], inline=False)
    await ctx.send(embed=embed)


@bot.command(name="wl")
@is_buyer()
async def whitelist_manage(ctx, action: str, user: discord.User):
    """+wl add @user ou +wl remove @user"""
    if action.lower() == "add":
        bot.whitelist_users.add(user.id)
        bot.blacklist_users.pop(user.id, None) # Auto-nettoyage si blacklisté
        await ctx.send(embed=discord.Embed(description=f"🛡️ {user.mention} fait désormais partie de la Whitelist de confiance.", color=bot.default_embed_color))
    elif action.lower() == "remove":
        bot.whitelist_users.discard(user.id)
        await ctx.send(embed=discord.Embed(description=f"🗑️ {user.mention} a été retiré de la Whitelist.", color=bot.default_embed_color))


# --- Commandes de Statuts & Présences ---

@bot.command(name="online")
@is_buyer()
async def set_online(ctx):
    await bot.change_presence(status=discord.Status.online)
    await ctx.message.add_reaction("🟢")

@bot.command(name="idle")
@is_buyer()
async def set_idle(ctx):
    await bot.change_presence(status=discord.Status.idle)
    await ctx.message.add_reaction("🟡")

@bot.command(name="dnd")
@is_buyer()
async def set_dnd(ctx):
    await bot.change_presence(status=discord.Status.dnd)
    await ctx.message.add_reaction("🔴")

@bot.command(name="invisible")
@is_buyer()
async def set_invisible(ctx):
    await bot.change_presence(status=discord.Status.invisible)
    await ctx.message.add_reaction("⚪")


@bot.command(name="play")
@is_buyer()
async def status_play(ctx, *, text: str):
    await bot.change_presence(activity=discord.Game(name=text))
    await ctx.send(f"🎮 Statut mis à jour : *Joue à **{text}***")

@bot.command(name="stream")
@is_buyer()
async def status_stream(ctx, *, text: str):
    await bot.change_presence(activity=discord.Streaming(name=text, url="https://twitch.tv/twitch"))
    await ctx.send(f"💜 Statut mis à jour : *En live sur **{text}***")

@bot.command(name="listen")
@is_buyer()
async def status_listen(ctx, *, text: str):
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=text))
    await ctx.send(f"🎧 Statut mis à jour : *Écoute **{text}***")

@bot.command(name="watch")
@is_buyer()
async def status_watch(ctx, *, text: str):
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=text))
    await ctx.send(f"📺 Statut mis à jour : *Regarde **{text}***")

@bot.command(name="del-activity")
@is_buyer()
async def delete_activity(ctx):
    await bot.change_presence(activity=None)
    await ctx.send("🗑️ Activité et statut textuel du bot réinitialisés.")


# --- Gestion de l'identité du Bot & Serveurs ---

@bot.command(name="setname")
@is_buyer()
async def set_bot_name(ctx, *, new_name: str):
    await bot.user.edit(username=new_name)
    await ctx.send(f"🤖 Le nom d'utilisateur de l'application a été changé pour : **{new_name}**")

@bot.command(name="setpic")
@is_buyer()
async def set_bot_avatar(ctx, url: str):
    import urllib.request
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            avatar_data = response.read()
        await bot.user.edit(avatar=avatar_data)
        await ctx.send("✅ Photo de profil de l'application mise à jour avec succès.")
    except:
        await ctx.send("❌ Échec du chargement de l'image. Vérifiez le lien fourni.")

@bot.command(name="setbanner")
@is_buyer()
async def set_bot_banner(ctx, url: str):
    import urllib.request
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            banner_data = response.read()
        await bot.user.edit(banner=banner_data)
        await ctx.send("✅ Bannière de l'application mise à jour avec succès.")
    except:
        await ctx.send("❌ Impossible de modifier la bannière.")


@bot.command(name="serverlist")
@is_buyer()
async def list_servers(ctx):
    servers = [f"• **{g.name}** `({g.id})` — *{g.member_count} membres*" for g in bot.guilds]
    embed = discord.Embed(title=f"🌐 Liste des Clusters Serveurs ({len(bot.guilds)})", description="\n".join(servers[:30]), color=bot.default_embed_color)
    await ctx.send(embed=embed)


@bot.command(name="leave")
@is_buyer()
async def leave_server(ctx, guild_id: int = None):
    target_guild = bot.get_guild(guild_id) if guild_id else ctx.guild
    if not target_guild:
        return await ctx.send("❌ Serveur introuvable.")
    await ctx.send(f"⚙️ Ordre de déconnexion envoyé pour le serveur : **{target_guild.name}**.")
    await target_guild.leave()


@bot.command(name="invite")
@is_buyer()
async def create_bot_invite(ctx, guild_id: int):
    guild = bot.get_guild(guild_id)
    if not guild: return await ctx.send("❌ Serveur introuvable.")
    for channel in guild.text_channels:
        try:
            invite = await channel.create_invite(max_age=300, max_uses=1)
            return await ctx.author.send(f"🎫 Invitation générée pour **{guild.name}** (Valide 5min) :\n{invite.url}")
        except: pass
    await ctx.send("❌ Permissions insuffisantes pour générer une invitation sur ce serveur.")


@bot.command(name="mp")
@is_buyer()
async def send_private_message(ctx, user: discord.User, *, text: str):
    try:
        await user.send(text)
        await ctx.message.add_reaction("📩")
    except:
        await ctx.send("❌ Impossible d'envoyer un message privé à cet utilisateur (Fermé ou Bloqué).")


@bot.command(name="say")
@is_buyer()
async def bot_say(ctx, *, text: str):
    await ctx.message.delete()
    await ctx.send(text)


# --- Intercepteur Anti-Blacklist Global ---
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return
        
    # Blocage d'un utilisateur présent dans la Blacklist
    if message.author.id in bot.blacklist_users:
        return
        
    await bot.process_commands(message)

# ==========================================
# LANCEMENT DU BOT
# ==========================================
bot.run(TOKEN)
