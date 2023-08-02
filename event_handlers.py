# event_handlers.py
import logging
from TikTokLive.types.events import CommentEvent, GiftEvent, DisconnectEvent, ConnectEvent
from image_generator import ImageGenerator
import os
import tts_module
import random

# Instantiate the image generator
image_generator = ImageGenerator()

def register_event_handlers(client, gift_tracker):
    # Define how you want to handle specific events via decorator
    @client.on("connect")
    async def on_connect(_: ConnectEvent):
        print("Connected to Room ID:", client.room_id)
        tts_module.generate_speech("Connected to room. I'm here everyone!")

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
            tts_module.generate_speech(choose_thanksdialog(client.available_gifts[gift_id].name))
        elif not event.gift.streakable:
            total_gift_value = gift_count * gift_price
            gift_tracker.update_gift_data(user_id, total_gift_value)
            print(
                f"{event.user.unique_id} sent \"{client.available_gifts[gift_id].name}\" for a total value of {total_gift_value}")
            tts_module.generate_speech(choose_thanksdialog(client.available_gifts[gift_id].name))

    # Define how you want to handle comment events
    @client.on('comment')
    async def on_comment(event: CommentEvent):
        user_id = event.user.unique_id
        if gift_tracker.gift_data[user_id] > 0:
            image = await image_generator.generate_image(event.comment)
            # Save the image to disk
            if not os.path.exists('images'):
                os.makedirs('images')
            image.save(
                f'images/{event.user.unique_id}_{event.comment}.png')  # Save the image before converting to numpy array
            # Update the current_frame of the image_generator
            image_array = np.array(image.convert('RGB'))  # Convert the image to numpy array after saving
            image_generator.current_frame = image_array
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

def choose_thanksdialog(gift_name):
    sentences = [
        f"OMG! Thanks for the {gift_name}!",
        f"{gift_name}, my favorite! Thank you!",
        f"Thanks! I love {gift_name}'s",
        f"{gift_name}'s! You shouldn't have!",
        f"{gift_name}'s! You're so sweet!",
        f"Oh! Thank you for the {gift_name}!",
        f"{gift_name}! You're the best!",
        f"{gift_name}! You're too kind!",
        f"Awe, {gift_name}"
    ]
    return random.choice(sentences)

