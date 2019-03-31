from PIL import Image
import time
from picamera import PiCamera

with PiCamera() as camera:
    camera.start_preview()
    time.sleep(2)
    camera.capture('fat.jpg')
    im = Image.open('fat.jpg')
    im.show()

