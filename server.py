#!/usr/bin/env python3

import os
import sys
from datetime import datetime
from pathlib import Path
from time import time,sleep
import base64

# libs for pylon
from pypylon import pylon
import cv2
import numpy as np
from concurrent import futures
import grpc

from api import Datas_pb2
from api import Datas_pb2_grpc

# cap = cv2.VideoCapture(0)
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
# captureBuffer = None


class Server(Datas_pb2_grpc.MainServerServicer):

    def __init__(self):
        self.cnt = 0
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.captureBuffer = None
        self.timestamp = None

    def getImage(self, request, context):
        self.cnt += 1
        print(f"send image: {self.cnt}")
        self._getImage()
        ret, buf = cv2.imencode('.jpg', self.captureBuffer)
        if ret != 1:
            return
        b64e = base64.b64encode(buf)
        yield Datas_pb2.ImageReply(image=b64e, date=self.timestamp)

    def _getImage(self):

        ret, frame = self.cap.read()
        if ret != 1:
            return
        print('capture image')
        self.captureBuffer = frame
        self.timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]



server = grpc.server(futures.ThreadPoolExecutor(max_workers = 10))
Datas_pb2_grpc.add_MainServerServicer_to_server(Server(), server)

server.add_insecure_port(f'[::]:50051')
server.start()
print('server start')
server.wait_for_termination()

# while True:
#     sleep(10)

server.stop()