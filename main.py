from discord.ext import commands
from discord import Embed
import discord

bot = discord.Bot(command_prefix='!')
TOKEN = 'No token 4 you'


@bot.event
async def on_ready():
    print('The thing is online')

@bot.event
async def on_member_join(member):
    welcome_channel = bot.get_channel(1193859832466378752)
    await welcome_channel.send(
        f'Welcome to Future Innovators Hub, {member.mention}! we have fun this server. Hope you enjoy me server! If I don\'t kick you.')
    await member.send(f'Welcome to the server, {member.mention}! Enjoy your stay here.')

@bot.command()
async def commands(ctx):
    embed = Embed(
        title='Commands',
        description='A list of all the commands available',
        color=0x00ff00
    )

    embed.add_field(
        name='__Utility commands__',
        value='''
    - **Ping |** Shows the latency of the bot
    ''',
        inline=False
    )

    embed.add_field(
        name='Command 2',
        value='Description of command 2.',
        inline=False
    )

    embed.add_field(
        name='Command 3',
        value='Description of command 3.',
        inline=False
    )

    await ctx.send(embed=embed)
    embed.add_field(
        name="Command 1",
        value="Description of command 1.",
        inline=False
    )

    embed.add_field(
        name="Command 2",
        value="Description of command 2.",
        inline=False
    )

    embed.add_field(
        name="Command 3",
        value="Description of command 3.",
        inline=False
    )

    embed.footer(

    )

    await ctx.send(embed=embed)

# --- Utility Commands ---
@bot.command()
async def ping(ctx):
    latency = ctx.latency
    await ctx.send(f'''
    Pong!
    Latency: {latency}ms''')

# --- Moderation Commands ---


bot.run(TOKEN)