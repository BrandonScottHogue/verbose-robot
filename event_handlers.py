# event_handlers.py
from config import OBSHOSTNAME, OBSPORT, OBSPASS
import logging
from TikTokLive.types.events import CommentEvent, GiftEvent, DisconnectEvent, ConnectEvent
from image_generator import ImageGenerator
import asyncio
import tts_module
import random
from obswebsocket import obsws, requests
ws = obsws(OBSHOSTNAME, OBSPORT, OBSPASS)
ws.connect()

# Instantiate the image generator
image_generator = ImageGenerator()
# Start the image generator after the event loop has started
loop = asyncio.get_event_loop()
loop.run_until_complete(image_generator.start())

def register_event_handlers(client, gift_tracker):
    # Define how you want to handle specific events via decorator
    @client.on("connect")
    async def on_connect(_: ConnectEvent):
        print("Connected to Room ID:", client.room_id)
        await tts_module.generate_speech("Connected to room. I'm here everyone! Don't forget to sub to my only fans!")
        ws.call(requests.SetCurrentProgramScene(sceneName="Instructions"))

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
            await tts_module.generate_speech(choose_thanksdialog(client.available_gifts[gift_id].name))
        elif not event.gift.streakable:
            total_gift_value = gift_count * gift_price
            gift_tracker.update_gift_data(user_id, total_gift_value)
            print(
                f"{event.user.unique_id} sent \"{client.available_gifts[gift_id].name}\" for a total value of {total_gift_value}")
            await tts_module.generate_speech(choose_thanksdialog(client.available_gifts[gift_id].name))

    # Define how you want to handle comment events
    @client.on('comment')
    async def on_comment(event: CommentEvent):
        user_id = event.user.unique_id
        if gift_tracker.gift_data[user_id] > 0:

            await image_generator.generate_image(event.comment,event.user.nickname,event.comment)
            gift_tracker.gift_data[event.user.unique_id] -= 1
            gift_tracker.update_gift_data(user_id,-1)  # assuming update_gift_data adds the gift_count to the existing count
            await tts_module.generate_speech(choose_imagedialog(event.user.nickname))

    @client.on('disconnect')
    async def on_disconnect(event: DisconnectEvent):
        # Log the disconnection to the console
        logging.info("Disconnected from the live stream")

        # Save the gift_data dictionary to a pickle file
        gift_tracker.update_gift_data()

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

def choose_imagedialog(user_nickname):
    if(str(user_nickname).startswith("user")):
        user_nickname_choices = [
            f"Dude",
            f"Friend",
            f"Guy",
            f"Buddy"
        ]
        user_nickname = random.choice(user_nickname_choices)
    sentences = [
        f"Here's your picture! I hope it's what you wanted!",
        f"Tada! Here's your image!",
        f"I hope you like it."
    ]
    return random.choice(sentences)