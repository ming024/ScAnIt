import socket, pickle
import time
import numpy as np

# Internet video stream serial client
class video_serial_client():
    def __init__(self, ip, port):
        self.HOST = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.connect((self.HOST, self.port))
        self.data = np.array([])
        
    def get(self):
        while True:
            # iteratively fetch video frames
            
            array = []
            while True:
                # iteratively fetch a video frame, which is divided into several parts
                
                try:
                    # send an ready signal and receive data from the remote Rpi device
                    message = 'ready'
                    self.socket.send(message.encode(encoding = 'UTF-8', errors = 'strict'))
                    time.sleep(0.001)
                    received = self.socket.recv(4096)
                    decoded = pickle.loads(received)        
                    
                    if decoded == b'':
                        # exit upon an end signal, which mark the end of transmision of one frame
                        break
                    else:
                        array = array + [decoded[i] for i in range(len(decoded))]
                    
                except KeyboardInterrupt:
                    self.socket.close()
        
            image = np.asarray(array)
        
            # convert OpenCV BGR format into relular RGB format
            self.data = np.transpose(image, (1, 0, 2))
