# main.py
import asyncio
import logging
from TikTokLive import TikTokLiveClient
from config import USERNAME, PICKLE_FILE
from gift_tracker import GiftTracker
from event_handlers import register_event_handlers
from display import display_table
from image_generator import ImageGenerator  # import ImageGenerator
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Instantiate the client with the user's username
client = TikTokLiveClient(unique_id=USERNAME, enable_detailed_gifts=True)

# Instantiate the gift tracker
gift_tracker = GiftTracker(PICKLE_FILE)

# Instantiate the image generator
image_generator = ImageGenerator()

# Register the event handlers
register_event_handlers(client, gift_tracker)

# Create an asyncio task for the client
client_task = asyncio.ensure_future(client.start())

# Create an asyncio task for the display_table coroutine
display_table_task = asyncio.ensure_future(display_table(gift_tracker))

# Start the virtual camera
virtualcam_task = asyncio.ensure_future(image_generator.start_virtualcam())

# Run all tasks in the same event loop
asyncio.get_event_loop().run_until_complete(asyncio.gather(client_task, display_table_task, virtualcam_task))
