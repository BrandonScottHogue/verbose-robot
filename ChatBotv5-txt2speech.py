import asyncio
import json
import time
from typing import Dict
from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import CommentEvent, GiftEvent, ConnectEvent
import aiohttp
from aiohttp import web
import base64
import io
import os
from PIL import Image,ImageDraw, ImageFont
import pickle

# create a dictionary to store the credit balance for each user
user_credits: Dict[str, int] = {}

# Instantiate the client with the user's unique id
client = TikTokLiveClient("soundswithsasha")

# url of stable-diffusion server running a webserver on port 7860
sd_url = "http://127.0.0.1:7860/sdapi/v1/txt2img"


async def display_images(folder_path: str):
    print("\n\n****display_images called*****\n\n")
    async def handle(request):
        images = []
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".jpg") or file_name.endswith(".jpeg") or file_name.endswith(".png"):
                images.append(file_name)
                print("Appended image: " + file_name)

        index = 0
        while True:
            response = """
            <html>
                <body>
                    <img src='""" + folder_path + "/" + images[index] + """' />
                </body>
            </html>
            """
            index = (index + 1) % len(images)
            await asyncio.sleep(10)
            return web.Response(text=response, content_type='text/html')

    app = web.Application()
    app.add_routes([web.get('/', handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()
    await asyncio.sleep(float(500))

def add_text_overlay(image: Image, user: str,comment: str):
    draw = ImageDraw.Draw(image)
    #text_width, text_height = draw.textbbox(str(user), font=font)
    #image_width, image_height = image.size
    x = 10
    y = 20
    stroke_color = "black"
    text_color = "white"
    font = ImageFont.truetype("arial.ttf", 16)
    draw.text((x, y - 10),"\"" + comment + "\"", font=font, stroke_width=1, fill=text_color, stroke_fill=stroke_color)
    font = ImageFont.truetype("arial.ttf", 12)
    draw.text((x + 10 , y+20), " - " + user, font=font, stroke_width=1, fill=text_color, stroke_fill=stroke_color)


# function to check the size of the queue
async def get_queue_size():
    url = "http://127.0.0.1:7860/queue/status"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                queue_size = data['queue_size']
                print("Queue size:", queue_size)
                return int(queue_size)
            else:
                print("Failed to retrieve queue size. API returned status code:", response.status)


# function to handle the "connect" event
@client.on("connect")
async def on_connect(event: ConnectEvent):
    print("Connected to Room ID:", client.room_id)


import pickle

@client.on("gift")
async def on_gift(event: GiftEvent):
    # If it's type 1 and the streak is over
    if event.gift.gift_type == 1:
        if event.gift.repeat_end == 1:
            print(f"{event.user.uniqueId} sent {event.gift.repeat_count}x \"{event.gift.extended_gift.name}\"")
            user_credits[event.user.uniqueId] = user_credits.get(event.user.uniqueId, 0) + event.gift.repeat_count
            with open("user_credits.pickle", "wb") as handle:
                pickle.dump(user_credits, handle)

    # It's not type 1, which means it can't have a streak & is automatically over
    elif event.gift.gift_type != 1:
        print(f"{event.user.uniqueId} sent \"{event.gift.extended_gift.name}\"")
        user_credits[event.user.uniqueId] = user_credits.get(event.user.uniqueId, 0) + 1
        with open("user_credits.pickle", "wb") as handle:
            pickle.dump(user_credits, handle)


# function to handle the "comment" event
@client.on("comment")
async def on_comment(event: CommentEvent):
    if event.user.uniqueId in user_credits and user_credits[event.user.uniqueId] > 0:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://127.0.0.1:7860/queue/status") as response:
                if response.status == 200:
                    data = await response.json()
                    queue_size = data['queue_size']
                    if queue_size == 0:
                        user_credits[event.user.uniqueId] -= 1
                        with open("user_credits.pickle", "wb") as handle:
                            pickle.dump(user_credits, handle)
                        image_file_path = await txt2img_save_image(event.comment, event)
                        print(f"{event.user.uniqueId} -> {event.comment} - Image saved at {image_file_path}")
                    else:
                        print(f"{event.user.uniqueId} -> {event.comment} - Queue is not empty, image generation will be delayed")
                else:
                    print("Failed to retrieve queue size. API returned status code:", response.status)
    else:
        print(f"{event.user.uniqueId} -> {event.comment} - Not enough credits")

async def txt2img_save_image(prompt: str, event: CommentEvent):
    """
    Asynchronously calls the REST API with the user's comment as the prompt,
    saves the resulting image to disk and returns the file path.
    """
    # Make the POST request to the REST API
    async with aiohttp.ClientSession() as session:
        async with session.post(sd_url, json={
            'prompt': "High res, CGI, beautiful,trending on Artstation, a photo of " + prompt,
            'steps' : 22,
            "cfg_scale": 9,
            'restore_faces': "true",
            'sampler_index': "Euler"
                                              }) as response:
            if response.status == 200:
                # Read the response and save it to a variable
                data = await response.json()
                for i in data['images']:
                    image = Image.open(io.BytesIO(base64.b64decode(i.split(",", 1)[0])))
                # Save the image to disk
                file_path = "images/" + event.user.uniqueId + str(time.time()) + ".jpg"
                add_text_overlay(image, event.user.uniqueId, event.comment)
                image.save(file_path)
                print(f"Image saved at {file_path}")
                return file_path
            else:
                print(f"Error: POST request to {sd_url} returned status code {response.status}")


client.add_listener("comment", on_comment)
client.add_listener("gift", on_gift)

async def main():
    #await display_images("C:\\Users\\brand\\PycharmProjects\\TikTokBot\\venv\\images")
    await client.start()


if __name__ == '__main__':
    try:
        with open("user_credits.pickle", "rb") as handle:
            user_credits = pickle.load(handle)
    except FileNotFoundError:
        user_credits = {}
    client.run();
    asyncio.run(main())