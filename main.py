import json
from discord.ext import commands
from discord import Embed
import discord


with open('config.json') as config_file:
				config = json.load(config_file)
				TOKEN = config.get('token')
				WELCOME_CHANNEL_ID = int(config.get('welcome_channel_id'))
				PREFIX = config.get('prefix')
				NEWS_API_KEY = config.get('news_api_key')
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
				welcome_channel = bot.get_channel(WELCOME_CHANNEL_ID)
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

				# Corrected by removing the duplicate fields and moving the footer into the proper method
				embed.set_footer(text='Some footer text')

				await ctx.send(embed=embed)

# --- Utility Commands ---

# ping
@bot.command()
async def ping(ctx):
				latency = bot.latency * 1000
				await ctx.send(f'''
				Pong!
				Latency: {latency:.2f}ms''')

# giveaway
@bot.command()
async def giveaway(ctx, duration, prize):
		if ctx.author.guild_permissions.administrator:
				try:
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
				except Exception as e:
						error_embed = discord.Embed(description=f"An error occurred: {e}", color=discord.Color.red())
						await ctx.send(embed=error_embed)
		else:
				permissions_embed = discord.Embed(description="You do not have permission to start a giveaway.", color=discord.Color.red())
				await ctx.send(embed=permissions_embed)

	# calculate
@bot.command()
async def calculate(ctx):
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
					
# --- Moderation Commands ---

# Moderation commands gonna go here (trust)

bot.run(TOKEN)
