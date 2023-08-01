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
    user_id = event.user.unique_id
    gift_id = event.gift.id
    gift_count = event.gift.count
    gift_price = client.available_gifts[gift_id].diamond_count

    if event.gift.streakable and not event.gift.streaking:
        total_gift_value = gift_count * gift_price
        gift_tracker.update_gift_data(user_id, total_gift_value)
        print(
            f"{event.user.unique_id} sent {gift_count}x \"{client.available_gifts[gift_id].name}\" for a total value of {total_gift_value}")
    elif not event.gift.streakable:
        total_gift_value = gift_count * gift_price
        gift_tracker.update_gift_data(user_id, total_gift_value)
        print(
            f"{event.user.unique_id} sent \"{client.available_gifts[gift_id].name}\" for a total value of {total_gift_value}")



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
