import os
import asyncio
import logging
import pickle
from tabulate import tabulate
from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import GiftEvent, CommentEvent, ConnectEvent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize a dictionary to store gift data
gift_data = {}

# Load the gift_data dictionary from a pickle file if it exists
if os.path.exists('gift_data.pkl'):
    with open('gift_data.pkl', 'rb') as f:
        gift_data = pickle.load(f)

# Instantiate the client with the user's username
client = TikTokLiveClient(unique_id="@whatever")


# Define how you want to handle specific events via decorator
@client.on("connect")
async def on_connect(_: ConnectEvent):
    print("Connected to Room ID:", client.room_id)


# Define how you want to handle gift events
@client.on("gift")
async def on_gift(event: GiftEvent):
    # Add the gift to the gift_data dictionary
    if event.user.unique_id not in gift_data:
        gift_data[event.user.unique_id] = 0
    gift_data[event.user.unique_id] += event.gift.count

    # If the gift is the end of a streak, log it to the console
    if not event.gift.streaking:
        logging.info(f"Received a gift from {event.user.unique_id}: {event.gift.info.name} x {event.gift.count}")

    # Save the gift_data dictionary to a pickle file
    with open('gift_data.pkl', 'wb') as f:
        pickle.dump(gift_data, f)


# Define how you want to handle comment events
async def on_comment(event: CommentEvent):
    # Log the comment to the console
    logging.info(f"Received a comment from {event.user.unique_id}: {event.comment}")


# Define handling an event via "callback"
client.add_listener("comment", on_comment)


# Coroutine to display the table every 30 seconds
async def display_table():
    while True:
        # Display a table of the top ten gifters
        top_gifters = sorted(gift_data.items(), key=lambda x: x[1], reverse=True)[:10]
        print(tabulate(top_gifters, headers=["User", "Number of Gifts"]))

        # Sleep for 30 seconds
        await asyncio.sleep(30)


if __name__ == '__main__':
    # Create an asyncio task for the client
    client_task = asyncio.ensure_future(client.start())

    # Create an asyncio task for the display_table coroutine
    display_table_task = asyncio.ensure_future(display_table())

    # Run both tasks in the same event loop
    asyncio.get_event_loop().run_until_complete(asyncio.gather(client_task, display_table_task))
