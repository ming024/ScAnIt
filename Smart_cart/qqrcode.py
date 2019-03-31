import io
import time
from picamera import PiCamera
from pyzbar.pyzbar import decode
#import pyqrcode
#import qrtools
#qr = qrtools.QR()
from PIL import Image
def takepic():
    with PiCamera() as camera:
        camera.start_preview()
        time.sleep(3)
        camera.capture('itemqr.jpg')
#qr.decode("itemqr.jpg")
#print(qr.data)
#scanner = zbar.ImageScanner()
#scanner.parse_config('enable')
takepic()
data = decode(Image.open('itemqr.jpg'))
while len(data) == 0:
    print("no qrcode")
    takepic()
    data = decode(Image.open('itemqr.jpg'))

a = str(data[0].data)
print(a[9:11])

