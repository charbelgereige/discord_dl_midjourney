# app.py
import os
import shutil
from dotenv import load_dotenv
from discord_bot import DiscordBot
from cv_image_analyzer import ImageAnalyzer
import logging
from tqdm import tqdm

# Setup logging with timestamps
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Load environment variables
load_dotenv('.env')
load_dotenv('local.env')

TOKEN = os.getenv('DISCORD_TOKEN')
DOWNLOAD_PATH = os.getenv('DOWNLOAD_PATH')
EXCLUDE_PATTERN = os.getenv('EXCLUDE_PATTERN')
MATRIX_SUBDIR = os.path.join(DOWNLOAD_PATH, "matrix_images")

# Create matrix images subdirectory if it doesn't exist
if not os.path.exists(MATRIX_SUBDIR):
    os.makedirs(MATRIX_SUBDIR)

# Go through existing images, rename if they have the prefix, and move matrix images to the subdirectory
all_files = os.listdir(DOWNLOAD_PATH)

for filename in tqdm(all_files, desc="Processing images"):
    if filename.startswith("charbelgereige_"):
        new_name = filename.replace("charbelgereige_", "")
        
        # Check if a file with the new name already exists
        if not os.path.exists(os.path.join(DOWNLOAD_PATH, new_name)):
            os.rename(os.path.join(DOWNLOAD_PATH, filename), os.path.join(DOWNLOAD_PATH, new_name))
            logging.info(f'Renamed {filename} to {new_name}')
            filename = new_name
        else:
            logging.warning(f"File {new_name} already exists. Skipping.")
    logging.info("Done moving local files")
   
# Start the Discord bot
bot = DiscordBot(TOKEN, DOWNLOAD_PATH, EXCLUDE_PATTERN)
bot.run()
