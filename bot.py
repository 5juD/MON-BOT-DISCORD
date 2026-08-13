import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ {bot.user} est connecté !')
    print(f'🌐 Connecté à {len(bot.guilds)} serveurs')

@bot.command()
async def ping(ctx):
    await ctx.send(f'🏓 Pong ! Latence : {round(bot.latency * 1000)}ms')

@bot.command()
async def hello(ctx):
    await ctx.send(f'👋 Bonjour {ctx.author.mention} !')

# Récupère le token depuis les variables d'environnement
bot.run(os.getenv('DISCORD_TOKEN'))
