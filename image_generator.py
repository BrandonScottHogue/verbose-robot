# image_generator.py
import webuiapi

class ImageGenerator:
    def __init__(self):
        self.api = webuiapi.WebUIApi()

    async def generate_image(self, prompt):
        result = await self.api.txt2img(prompt=prompt,restore_faces=True,steps=25,width=512,height=1024,sampler_index='euler',negative_prompt="text, ugly, tiling, poorly drawn hands, poorly drawn feet, poorly drawn face, out of frame, extra limbs, disfigured, deformed, body out of frame, bad anatomy, watermark, signature, cut off, low contrast, underexposed, overexposed, bad art, beginner, amateur, distorted face", use_async=True)
        return result.image
