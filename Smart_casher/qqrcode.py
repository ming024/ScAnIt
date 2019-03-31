import io
import time
from picamera import PiCamera
from pyzbar.pyzbar import decode
import pyodbc
from PIL import Image
import RPi.GPIO as GPIO
print("===========================================")
print("\n")
print("                  CASHIER                  ")
print("\n")
print("===========================================")
dsn = 'rpitestsqlserverdatasource'
user = 'deng-fat@deng-fat-goshopping'
password = 'TJG1ul3au4a83'
database = 'Shopping_Mall_Example'
connString = 'DSN={0};UID={1};PWD={2};DATABASE={3};'.format(dsn,user,password,database)
conn = pyodbc.connect(connString)
cursor = conn.cursor()
total_spend = 0
def takepic():
    with PiCamera() as camera:
        camera.start_preview()
        time.sleep(3.5)
        camera.capture('itemqr.jpg')
    camera.close()

def my_callback(channel):
    global total_spend
    takepic()
    data = decode(Image.open('itemqr.jpg'))
    while len(data) == 0:
        #print("no qrcode")
        takepic()
        data = decode(Image.open('itemqr.jpg'))
    cstr = str(data[0].data)
    cint = int(cstr[2:4])
    print(cint)
    sqlcomand_plus ="Update Item Set PPW = PPW + 1 WHERE Class = "+str(cint)+";"
    sqlcomand_minus ="Update Item Set Remaining = Remaining - 1 WHERE Class = "+str(cint)+";"
    cursor.execute(sqlcomand_plus)
    cursor.execute(sqlcomand_minus)
    sqlcomand_sel = "SELECT Price From Item where Class = "+str(cint)+";"
    cursor.execute(sqlcomand_sel)
    temp = cursor.fetchone()
    total_spend = total_spend + int(temp[0])
    conn.commit()
    print('price : '+str(temp[0]))
    print('Total : '+str(total_spend))

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
try:
    while True:
        if GPIO.input(18) == GPIO.LOW:
            my_callback(18)
        time.sleep(0.25)
except KeyboardInterrupt:
    print('close')
finally:
    GPIO.cleanup

