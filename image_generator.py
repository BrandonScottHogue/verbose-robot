#image_generator.py
import asyncio
import threading
import atexit
import numpy as np
import pyvirtualcam
from PIL import Image
import webuiapi
import os
import time
from config import OBSPASS,OBSHOSTNAME,OBSPORT
from obswebsocket import obsws, requests
import tts_module
import random

ws = obsws(OBSHOSTNAME, OBSPORT, OBSPASS)
ws.connect()

class ImageGenerator:
    def __init__(self):
        self.api = webuiapi.WebUIApi()
        self.current_frame = self.load_default_image()
        self.cam_thread = threading.Thread(target=self.virtualcam_loop)
        self.cam_thread.start()  # Start the thread
        self.user_file = open('text/user.txt', 'w', encoding="utf-8")
        self.comment_file = open('text/comment.txt', 'w', encoding="utf-8")
        atexit.register(self.cleanup)
        self.last_image_time = time.time()
        self.idle_timer_task = None

    def load_default_image(self):
        default_image = Image.open('images/default.png')
        return np.array(default_image.convert('RGB'))
    async def set_scene_after_delay(self, scene_name, delay):
        await asyncio.sleep(delay)
        ws.call(requests.SetCurrentProgramScene(sceneName=scene_name))
    async def start(self):
        self.idle_timer_task = asyncio.create_task(self.idle_timer())
    async def generate_image(self, prompt, user, comment):
        result = await self.api.txt2img(prompt="A beautiful image of " + prompt + ", trending on art station, HDR, 4k",
                                        restore_faces=True, steps=10, width=512, height=512,
                                        enable_hr=True, hr_upscaler=webuiapi.HiResUpscaler.Latent,
                                        hr_second_pass_steps=5, hr_resize_x=512, hr_resize_y=1024,
                                        denoising_strength=0.75, sampler_index='euler',
                                        negative_prompt="text, ugly, tiling, poorly drawn hands, poorly drawn feet, poorly drawn face, out of frame, extra limbs, disfigured, deformed, body out of frame, bad anatomy, watermark, signature, cut off, low contrast, underexposed, overexposed, bad art, beginner, amateur, distorted face",
                                        use_async=True)
        self.user_file.seek(0)
        self.user_file.truncate()
        self.comment_file.seek(0)
        self.comment_file.truncate()
        self.user_file.write("- " + user + "\n")
        self.user_file.flush()
        os.fsync(self.user_file.fileno())
        self.comment_file.write("\"" + comment + "\"\n")
        self.comment_file.flush()
        os.fsync(self.comment_file.fileno())
        ws.call(requests.SetCurrentProgramScene(sceneName="NoOverlay"))
        image = result.image
        asyncio.create_task(self.set_scene_after_delay("Overlay", 1))
        # Save the image to disk
        if not os.path.exists('images'):
            os.makedirs('images')
        image.save(f'images/latest.png')
        self.current_frame = np.array(image.convert('RGB'))

    def virtualcam_loop(self):
        with pyvirtualcam.Camera(width=self.current_frame.shape[1], height=self.current_frame.shape[0], fps=30) as cam:
            while True:
                if self.current_frame is not None:
                    cam.send(self.current_frame)
                time.sleep(1/cam.fps)  # sleep until next frame

    async def idle_timer(self):
        while True:
            wait_time = random.randint(10, 30)  # generate a random integer between 10 and 30
            await asyncio.sleep(wait_time)  # wait for the generated amount of time
            if time.time() - self.last_image_time > wait_time:  # if it's been more than the wait time since the last image
                # generate a speech event
                speech = self.choose_thanksdialog()  # assuming this function returns the text for the speech
                await tts_module.generate_speech(speech)
    def cleanup(self):
        print("Cleaning up...")
        self.user_file.close()
        self.comment_file.close()

    def choose_thanksdialog(self):
        sentences = [
            "Leave a gift and a comment, and I'll generate art for you!",
            "Lets see those comments guys, don't be shy!",
            "We're making some lovely A.I. art today!",
            "Thanks for joining my stream!",
            "I love you guys! Keep those gifts and comments coming!",
            "Don't forget to follow me so you catch my next stream!",
            "O M G - You guys are the best!",
            "Your gifts and comments fuel my creativity!",
            "Can't wait to see what we'll create next!",
            "Your support means the world to me!",
            "Keep those comments coming, I love hearing from you!",
            "Every gift and comment brings a new piece of art to life!",
            "You're all amazing! Let's keep the creativity flowing!",
            "I'm so excited to be here with all of you!",
            "Your comments and gifts make this stream possible!",
            "I'm so grateful for your support!",
            "Let's make some magic together!",
            "Your gifts and comments inspire me!",
            "I can't wait to see what we'll create together!",
            "Your support helps me create more amazing art!",
            "I'm so lucky to have such an amazing audience!",
            "Your comments and gifts make my day!",
            "I'm so excited to see what we'll create next!",
            "Let's keep the creativity flowing!",
            "Your support makes all of this possible!",
            "I'm so grateful for each and every one of you!",
            "Let's make some art together!",
            "I can't wait to see what comments and gifts you'll bring!",
            "Your support is what makes this stream possible!",
            "I'm so excited to create with you!",
            "Let's make some magic happen!",
            "I'm so grateful for your gifts and comments!",
            "Your support helps me bring art to life!",
            "I can't wait to see what we'll create together next!",
            "Your gifts and comments make this all possible!",
            "Let's keep the creativity going!",
            "I'm so excited to see what we'll make next!",
            "Your support means everything to me!"
        ]
        return random.choice(sentences)
