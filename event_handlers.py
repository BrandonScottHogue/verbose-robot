# event_handlers.py
import logging
from TikTokLive.types.events import CommentEvent, GiftEvent, DisconnectEvent, ConnectEvent
from gift_tracker import GiftTracker
from image_generator import ImageGenerator
import webuiapi
import os

# Instantiate the image generator
image_generator = ImageGenerator()

def register_event_handlers(client, gift_tracker):
    # Define how you want to handle specific events via decorator
    @client.on("connect")
    async def on_connect(_: ConnectEvent):
        print("Connected to Room ID:", client.room_id)

    @client.on("gift")
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
    @client.on('comment')
    async def on_comment(event: CommentEvent):
        user_id = event.user.unique_id
        if gift_tracker.gift_data[user_id] > 0:
            image = await image_generator.generate_image(event.comment)
            # Save the image to disk
            if not os.path.exists('images'):
                os.makedirs('images')
            image.save(f'images/{event.user.unique_id}_{event.comment}.png')
            gift_tracker.gift_data[event.user.unique_id] -= 1
            gift_tracker.update_gift_data(user_id, -1)  # assuming update_gift_data adds the gift_count to the existing count
    @client.on('disconnect')
    async def on_disconnect(event: DisconnectEvent):
        # Log the disconnection to the console
        logging.info("Disconnected from the live stream")

        # Save the gift_data dictionary to a pickle file
        gift_tracker.save_gift_data()

    # Define handling an event via "callback"
    client.add_listener("comment", on_comment)