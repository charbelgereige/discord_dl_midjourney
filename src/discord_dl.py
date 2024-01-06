import discord
import aiohttp
import os
import logging
from tqdm import tqdm
import threading
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')
load_dotenv('local.env')

TOKEN = os.getenv('DISCORD_TOKEN')
DOWNLOAD_PATH = os.getenv('DOWNLOAD_PATH')
EXCLUDE_PATTERN = os.getenv('EXCLUDE_PATTERN')

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True

client = discord.Client(intents=intents)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


@client.event
async def on_ready():
    logging.info(f'We have logged in as {client.user}')

    # Create download directory if it doesn't exist
    if not os.path.exists(DOWNLOAD_PATH):
        os.makedirs(DOWNLOAD_PATH)

    await check_previous_messages()

@client.event
async def on_message(message):
    if message.content.startswith('!download'):
        for attachment in message.attachments:
            # Use threading to download with a specific thread name
            threading.Thread(target=await download_attachment(attachment, message.channel), name="DownloadThread-" + attachment.filename).start()

async def download_attachment(attachment, channel):
    if EXCLUDE_PATTERN and EXCLUDE_PATTERN in attachment.filename:
        return
    
    filepath = os.path.join(DOWNLOAD_PATH, attachment.filename)
    if os.path.exists(filepath):
        logging.info(f'File {attachment.filename} already exists. Skipping.')
        return

    if attachment.filename.endswith(('.jpg', '.png', '.gif')):
        async with aiohttp.ClientSession() as session:
            async with session.get(attachment.url) as resp:
                if resp.status == 200:
                    with open(filepath, 'wb') as f:
                        async for chunk in resp.content.iter_any():
                            f.write(chunk)
                        logging.info(f'Downloaded {attachment.filename} to {filepath}')
                        #await channel.send(f'Downloaded {attachment.filename}')

async def check_previous_messages():
    # On startup, go back in history and download undownloaded images
    for channel in client.get_all_channels():
        if isinstance(channel, discord.TextChannel):
            async for message in channel.history(limit=100):  # Limiting to last 100 messages for the example
                for attachment in message.attachments:
                    await download_attachment(attachment, channel)

client.run(TOKEN)
