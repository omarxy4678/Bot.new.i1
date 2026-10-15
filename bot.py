import logging
import os
import discord
from discord.ext import commands
import google.generativeai as genai

# Logging setup for Render console
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

# Fetching environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini Model
ai_model = None
if GEMINI_API_KEY:
  try:
    genai.configure(api_key=GEMINI_API_KEY)
    ai_model = genai.GenerativeModel("gemini-1.5-flash")
    logging.info("Gemini AI API successfully configured.")
  except Exception as e:
    logging.error(f"Error configuring Gemini API: {e}")
else:
  logging.warning("GEMINI_API_KEY missing from environment variables.")

# Discord Bot setup with Intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
  logging.info(f"Bot successfully connected as {bot.user} (ID: {bot.user.id})")


@bot.event
async def on_message(message):
  # Ignore self messages
  if message.author == bot.user:
    return

  # Respond when mentioned
  if bot.user.mentioned_in(message):
    # Remove bot tag from prompt
    clean_prompt = message.content.replace(f"<@{bot.user.id}>", "").strip()

    if not clean_prompt:
      clean_prompt = "Hello!"

    if ai_model:
      try:
        # Show typing indicator while generating response
        async with message.channel.typing():
          response = ai_model.generate_content(clean_prompt)

        reply = (
            response.text
            if hasattr(response, "text") and response.text
            else "No response generated."
        )

        # Discord 2000 character limit protection (chunking)
        if len(reply) > 1900:
          chunks = [reply[i : i + 1900] for i in range(0, len(reply), 1900)]
          for chunk in chunks:
            await message.channel.send(chunk)
        else:
          await message.channel.send(reply)

      except Exception as err:
        logging.error(f"Error handling Gemini request: {err}")
        await message.channel.send(
            f"An error occurred while generating response: {err}"
        )
    else:
      await message.channel.send(
          "Gemini API key is not configured in Render environment variables."
      )

  await bot.process_commands(message)


# Entry point check
if __name__ == "__main__":
  if not DISCORD_TOKEN:
    logging.critical("DISCORD_TOKEN is missing! Bot cannot start.")
  else:
    bot.run(DISCORD_TOKEN)
