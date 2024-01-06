import discord
import aiohttp
import os
import logging
from image_analyzer import TorchCVImageAnalyzer

class DiscordBot:
    def __init__(self, token, download_path, exclude_pattern):
        self.TOKEN = token
        self.DOWNLOAD_PATH = download_path
        self.EXCLUDE_PATTERN = exclude_pattern
        self.intents = discord.Intents.default()
        self.intents.messages = True
        self.intents.message_content = True
        self.intents.guilds = True
        self.client = discord.Client(intents=self.intents)

        # Configure logging with timestamps
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

        @self.client.event
        async def on_ready():
            logging.info(f'We have logged in as {self.client.user}')
            await self.check_previous_messages()

        @self.client.event
        async def on_message(message):
            # Check if the message has attachments
            if message.attachments:
                # Loop through each attachment and download it
                for attachment in message.attachments:
                    await self.download_attachment(attachment, message.channel)

    async def download_attachment(self, attachment, channel):
        if self.EXCLUDE_PATTERN and self.EXCLUDE_PATTERN in attachment.filename:
            return

        # Trim the filename to remove the prefix
        filename = attachment.filename.replace("charbelgereige_", "")
        filepath = os.path.join(self.DOWNLOAD_PATH, filename)

        if os.path.exists(filepath):
            logging.info(f'File {filename} already exists. Skipping.')
            return
        
        if attachment.filename.endswith(('.jpg', '.png', '.gif')):
            async with aiohttp.ClientSession() as session:
                async with session.get(attachment.url) as resp:
                    if resp.status == 200:
                        with open(filepath, 'wb') as f:
                            async for chunk in resp.content.iter_any():
                                f.write(chunk)
                        logging.info(f'Downloaded {filename}')

                        # Analyze the image to see if it's a matrix or upscale
                        analyzer = TorchCVImageAnalyzer(filepath)
                        if not analyzer.is_upscale():
                            matrix_folder = os.path.join(self.DOWNLOAD_PATH, 'matrix_images')
                            if not os.path.exists(matrix_folder):
                                os.makedirs(matrix_folder)
                            os.rename(filepath, os.path.join(matrix_folder, filename))
                            logging.info(f'Moved {filename} to matrix subdirectory {matrix_folder}.')

    async def check_previous_messages(self):
        # On startup, go back in history and download undownloaded upscale images
        for channel in self.client.get_all_channels():
            if isinstance(channel, discord.TextChannel):
                already_downloaded_count = 0
                undownloaded_attachments = []

                async for message in channel.history(limit=None):  # Fetch all messages
                    if already_downloaded_count >= 100:
                        break

                    for attachment in message.attachments:
                        filename = attachment.filename.replace("charbelgereige_", "")
                        filepath = os.path.join(self.DOWNLOAD_PATH, filename)

                        if os.path.exists(filepath):
                            already_downloaded_count += 1
                        else:
                            undownloaded_attachments.append((attachment, channel))

                # Reverse the list to start downloading from the oldest undownloaded image
                undownloaded_attachments.reverse()

                for attachment, channel in undownloaded_attachments[:100]:  # Limit to the last 100 undownloaded images
                    await self.download_attachment(attachment, channel)

    def run(self):
        self.client.run(self.TOKEN)
