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
ws = obsws(OBSHOSTNAME, OBSPORT, OBSPASS)
ws.connect()


class ImageGenerator:
    def __init__(self):
        self.api = webuiapi.WebUIApi()
        self.current_frame = self.load_default_image()
        self.cam_thread = threading.Thread(target=self.virtualcam_loop)
        self.cam_thread.start()  # Start the thread
        atexit.register(self.cleanup)
        user_file = open('text/user.txt', 'w', encoding="utf-8")
        comment_file = open('text/comment.txt', 'w', encoding="utf-8")

    def load_default_image(self):
        default_image = Image.open('images/default.png')
        return np.array(default_image.convert('RGB'))

    async def generate_image(self, prompt, user, comment):
        ws.call(requests.SetCurrentProgramScene(sceneName="NoOverlay"))
        result = await self.api.txt2img(prompt="A beautiful image of " + prompt + ", trending on art station, HDR, 4k", restore_faces=True, steps=25, width=512, height=512,
                                        enable_hr=True, hr_upscaler=webuiapi.HiResUpscaler.Latent,
                                        hr_second_pass_steps=0, hr_resize_x=512, hr_resize_y=1024,
                                        denoising_strength=0.75, sampler_index='euler',
                                        negative_prompt="text, ugly, tiling, poorly drawn hands, poorly drawn feet, poorly drawn face, out of frame, extra limbs, disfigured, deformed, body out of frame, bad anatomy, watermark, signature, cut off, low contrast, underexposed, overexposed, bad art, beginner, amateur, distorted face",
                                        use_async=True)
        self.user_file.write("- " + user)
        os.fsync(self.user_file.fileno())
        self.comment_file.write("\"" + comment + "\"")
        os.fsync(self.comment_file.fileno())
        image = result.image
        # Save the image to disk
        if not os.path.exists('images'):
            os.makedirs('images')
        image.save(f'images/latest.png')
        self.current_frame = np.array(image.convert('RGB'))
        ws.call(requests.SetCurrentProgramScene(sceneName="Overlay"))

    def virtualcam_loop(self):
        with pyvirtualcam.Camera(width=self.current_frame.shape[1], height=self.current_frame.shape[0], fps=30) as cam:
            while True:
                if self.current_frame is not None:
                    cam.send(self.current_frame)
                time.sleep(1/cam.fps)  # sleep until next frame

    def cleanup(self):
        print("Cleaning up...")
        self.user_file.close()
        self.comment_file.close()