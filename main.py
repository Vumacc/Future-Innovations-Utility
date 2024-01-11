from discord.ext import commands
from discord import Embed
import discord
import requests
import asyncio
import random
import time
import json
import re


with open('config.json') as config_file:
				config = json.load(config_file)
				TOKEN = config.get('token')
				WELCOME_CHANNEL_ID = int(config.get('welcome_channel_id'))
				PREFIX = config.get('prefix')
				NEWS_API_KEY = config.get('news_api_key')
				FIXER_API_KEY = config.get('fixer_api_key')	
bot = discord.Bot(command_prefix=PREFIX)

@bot.event
async def on_command_error(ctx, error):
	if isinstance(error, discord.ext.commands.CommandNotFound):
		await ctx.send("command not found, use !commands for help")

@bot.event
async def on_ready():
				print('The thing is online')

@bot.event
async def on_member_join(member):
				channel = bot.get_channel(WELCOME_CHANNEL_ID)
				await channel.send(
								f'Welcome to Future Innovators Hub, {member.mention}! we have fun this server. Hope you enjoy me server! If I don\'t kick you.')
				await member.send(f'Welcome to the server, {member.mention}! Enjoy your stay here.')


# --- Help Command ---

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
- **Giveaway `duration` `prize` |** Start a giveaway with a set prize and duration
- **Calculator |** A built-in calculator
- **News `query` |** Shows an article based on your query
- **convert `amount` `from_currency` `to_currency` |** Converts currency
		''',
		inline=False
	)
	
	embed.add_field(
		name='__Moderation commands__',
		value='''
- **Ban `@user` `reason` |** Bans a member from the guild
- **Unban `userID` |**Unbans a member from the guild
- **Kick `@user` `reason` |** Kicks a member from the guild
- **Clear `amount` |** Deletes the amount of messages specified
- **mute `@user` `reason` |** Mutes a a specified user
''', 
		inline=False
	)
				
	embed.set_footer(text='Future Innovations Utility v1.0')

	await ctx.send(embed=embed)


# --- Utility Commands ---

# Ping
@bot.command()
async def ping(ctx):
	latency = bot.latency * 1000
	await ctx.send(f'''
	Pong!
	atency: {latency:.2f}ms''')

# Giveaway
@bot.command()
async def giveaway(ctx, duration: str, prize: str):
    if not ctx.author.guild_permissions.administrator:
        embed = discord.Embed(description="You do not have permission to start a giveaway.", color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    if not re.match(r"^\d+(s|m|h|d)$", duration):
        embed = discord.Embed(description="Invalid duration format. Please use a number followed by s (seconds), m (minutes), h (hours), or d (days).", color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    numeric_part = int(duration[:-1])
    if numeric_part < 1 or numeric_part > 10080:
        embed = discord.Embed(description="Duration value must be between 1 and 10,080.", color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    time_conversion = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    unit = duration[-1]
    duration_in_seconds = int(duration[:-1]) * time_conversion[unit]

    giveaway_embed = discord.Embed(title="🎉 **Giveaway** 🎉", description=f"**Prize**: {prize}\n**Duration**: {duration}\nReact with 🎉 to enter!", color=discord.Color.blue())
    giveaway_embed.set_footer(text=f"Hosted by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
    giveaway_msg = await ctx.send(embed=giveaway_embed)
    await giveaway_msg.add_reaction("🎉")
    await asyncio.sleep(duration_in_seconds)

    updated_giveaway_msg = await ctx.fetch_message(giveaway_msg.id)
    reactions = [reaction for reaction in updated_giveaway_msg.reactions if str(reaction.emoji) == "🎉"]
    winner = None

    if len(reactions) > 0:
        users = await reactions[0].users().flatten()
        users.remove(bot.user)
        if len(users) > 0:
            winner = random.choice(users)

    if winner:
        winner_embed = discord.Embed(description=f"🎉 Congratulations to {winner.mention} for winning the {prize}! 🎉", color=discord.Color.green())
        await ctx.send(embed=winner_embed)
    else:
        no_winner_embed = discord.Embed(description="The giveaway has ended, and no one participated. Better luck next time!", color=discord.Color.orange())
        await ctx.send(embed=no_winner_embed)

# Calculate
@bot.command()
async def calculator(ctx):
		help_message = """To use the calculator, enter a equation, then the bot will solve it and send it to you. example: `5 + 3`

		`+ = plus`
		`- = minus`
		`/ = divide`
		`* = multiply`
		"""                           
		await ctx.send(help_message)

		try:
				msg = await bot.wait_for("message", check=lambda message: message.author == ctx.author, timeout=60)
				equation = msg.content
				if not equation.startswith('!calculate'):
						equation = '!calculate ' + equation
				equation = equation[len('!calculate '):]

				valid_characters = set("0123456789+-*/() ")
				if not all(char in valid_characters for char in equation):
						await ctx.send("Invalid characters in the expression.")
						return

				result = eval(equation)
				await ctx.send(f'Result: {result}')
		except asyncio.TimeoutError:
				await ctx.send("Calculation request timed out. Please try again.")

# News
@bot.command()
async def news(ctx, *, query):
				news_url = f'https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}'
				try:
								response = requests.get(news_url)
								data = response.json()
								articles = data['articles'][:5]
								embed = discord.Embed(
												title=f"News for {query}",
												color=0x00ff00
								)
								for article in articles:
												embed.add_field(name=article['title'], value=article['url'], inline=False)
								await ctx.send(embed=embed)
				except Exception as e:
								await ctx.send(f"Error: {e}")


@bot.command()
async def convert(ctx, amount: float = None, from_currency: str = None, to_currency: str = None):
		try:
				if amount is None or from_currency is None or to_currency is None:
						await ctx.send("Please provide all required arguments: amount, from_currency, and to_currency")
						return
				url = f"http://data.fixer.io/api/latest?access_key={FIXER_API_KEY}&format=1{from_currency}"
				response = requests.get(url)
				if response.status_code == 200:
						data = response.json()
						if 'rates' in data and to_currency in data['rates']:
								exchange_rate = data['rates'][to_currency]
								converted_amount = amount * exchange_rate
								response_message = (
										f"Converting {amount} {from_currency} to {to_currency}:\n"
										f"Result: {amount} {from_currency} is {converted_amount} {to_currency}"
								)
								await ctx.send(response_message)
						else:
								await ctx.send(f"Currency {to_currency} not found.")
				else:
						await ctx.send("Unable to fetch exchange rates. Please try again later.")
		except requests.exceptions.RequestException as e:
				await ctx.send(f"An error occurred during the API request: {e}")
		except ValueError as e:
				await ctx.send(f"An error occurred while processing the response data: {e}")
		except Exception as e:
				await ctx.send(f"An unexpected error occurred: {e}")


# --- Moderation Commands ---

# Ban command
@bot.command()
async def ban(ctx, member: discord.Member, *, reason=None):
	if ctx.author.guild_permissions.ban_members:

		if member.guild_permissions.administrator:
			await ctx.send('Could not ban member')
			time.sleep(1)
			await ctx.purge(limit=1)
		
		await member.ban(reason=reason)

		embed = discord.Embed(
		title=f'User has been banned',
		color=0x00ff00
			)

		embed.add_field(
		name=f'{member} has been banned!',
		value=f'**Ban reason:** {reason}'
			)

		await ctx.send(embed=embed)
	
	else:
		await ctx.send('You do not have permissions to ban members')
		time.sleep(1)
		await ctx.purge(limit=1)

# Unban command
@bot.command()
async def unban(ctx, member: discord.Member):
	if ctx.author.guild_permissions.ban_members:

		embed = discord.Embed(
		title=f'User has been unbanned',
		color=0x00ff00
			)

		embed.add_field(
		name=f'{member} has been banned!',
		value=''
			)

		await ctx.send(embed=embed)
	
	else:
		await ctx.send('You do not have permissions to unban members')
		time.sleep(1)
		await ctx.purge(limit=1)

# Kick command
@bot.command()
async def kick(ctx, member: discord.Member, *, reason=None):
	if ctx.author.guild_permissions.kick_members:
		
		if member.guild_permissions.administrator:
			await ctx.send('Could not kick member')
			time.sleep(1)
			await ctx.purge(limit=1)
		
		await member.kick(reason=reason)

		embed = discord.Embed(
		title=f'User has been kicked',
		color=0x00ff00
			)

		embed.add_field(
		name=f'{member} has been kicked!',
		value=f'**kick reason:** {reason}'
			)

		await ctx.send(embed=embed)
	
	else:
		await ctx.send('You do not have permissions to kick members')
		time.sleep(1)
		await ctx.purge(limit=1)

# Clear command
@bot.command()
async def clear(ctx, amount: int):
    if ctx.author.guild_permissions.manage_messages:
        amount = min(amount, 100)

        try:
            deleted = await ctx.channel.purge(limit=amount)
            message_count = len(deleted)
            if message_count > 1:
                await ctx.send(f'Cleared {message_count} messages!')
            elif message_count == 1:
                await ctx.send(f'Cleared {message_count} message!')
        except discord.HTTPException:
            await ctx.send('The bot is rate-limited. Please try again later')
    else:
        await ctx.send('You do not have the permissions to clear messages')

# mute command
@bot.command()
async def mute(ctx, member: discord.Member, *, reason=None):
    if not ctx.author.guild_permissions.mute_members:
        await ctx.send('You do not have the permission to mute members')
        time.sleep(1)
        await ctx.purge(limit=1)
        return

    await member.mute(reason=reason)

    if member.guild_permissions.administrator:
        await ctx.send('Targeted member is an administrator')
        time.sleep(1)
        await ctx.purge(limit=1)

    embed = discord.Embed(
        title=f'User has been muted',
        color=0x00ff00
    )

    embed.add_field(
        name=f'{member} has been muted!',
        value=f'**Mute reason:** {reason}'
    )

    await ctx.send(embed=embed)

bot.run(TOKEN)