import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
  print(f"Logged in successfully as {bot.user}")


@bot.event
async def on_message(message):
  if message.author == bot.user:
    return

  if bot.user.mentioned_in(message):
    await message.channel.send(
        f"Hello {message.author.mention}, I am online and working properly!"
    )

  await bot.process_commands(message)


TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
