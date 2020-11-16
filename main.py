#!/usr/bin/env python3

import base64
import sys
from concurrent import futures
from datetime import datetime
from threading import Thread
from time import sleep

import cv2
import grpc
import numpy as np
# libs for pylon
from pypylon import pylon

from api import Datas_pb2, Datas_pb2_grpc
from loggerClient import LoggerClient

# from aion.microservice import main_decorator, Options
# from aion.kanban import Kanban

log = LoggerClient("stream-basler-usb-video-by-x11")

SERVICE_NAME = "stream-basler-usb-video-by-x11"
# CAPTURE_WIDTH = 720
# CAPTURE_HEIGHT = 480
CAPTURE_WIDTH = 1920
CAPTURE_HEIGHT = 1200

# CAPTURE_WIDTH = 2048
# CAPTURE_HEIGHT = 1536
CAPTURE_FPS = 10
CAPTURE_GAIN = 200

DEBUG = True


def wait_fps(time_wait):
    sleep(time_wait)


class CameraServicer(Datas_pb2_grpc.MainServerServicer):

    def __init__(self):
        self.cnt = 0
        self.captureBuffer = None
        self.captureBuffer_b64e = None
        self.timestamp = None
        self.camera = None

    def getImage(self, request, context):
        # self.cnt += 1
        # print(f"send image: {self.cnt}")
        if self.captureBuffer is None or self.captureBuffer_b64e is None:
            log.print('not image')
            return

        old_timestamp = None
        while True:
            if old_timestamp != self.timestamp:
                log.print(f'send image captured at : {self.timestamp}')
                yield Datas_pb2.ImageReply(
                    image=self.captureBuffer_b64e, date=self.timestamp)
                old_timestamp = self.timestamp
            sleep(0.05)
        return

    def update_image(self, data):
        ret, buf = cv2.imencode('.jpg', data)
        if ret:
            self.captureBuffer = buf
            self.captureBuffer_b64e = base64.b64encode(self.captureBuffer)
        else:
            print("cant imencode")
        self.timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]

    def get_target_camera(self):
        camera = None
        
        ip_address = "192.168.2.10"
        info = pylon.DeviceInfo()
        #info.SetPropertyValue('IpAddress', ip_address)
        info.SetDeviceClass("BaslerUsb")
        camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice(info))
        
        # print(camera.GetNodeMap())
        return camera

    def setup(self):
        device = self.get_target_camera()
        if not device:
            log.print('not found camera device')
            return

        factory = pylon.TlFactory.GetInstance()
        self.camera = device
        # self.camera = pylon.InstantCamera(device)
        # self.camera = pylon.InstantCamera(factory.CreateDevice(device))
        if self.camera is None:
            log.print('not found camera')
            return
        self.camera.Open()
        self.set_camera_parameter()

    def set_camera_parameter(self):
        model = self.camera.GetDeviceInfo().GetModelName()
        log.print(f"found camera model: {model}")

        # set image size
        self.camera.Width = CAPTURE_WIDTH if CAPTURE_WIDTH <= self.camera.Width.Max else self.camera.Width.Max
        self.camera.Height = CAPTURE_HEIGHT if CAPTURE_HEIGHT <= self.camera.Height.Max else self.camera.Height.Max

        # self.camera.GainAuto = 'Continuous'

        # TODO: config.jsonにてモデルごとに設定を持たせる
        if model == 'acA1920-40gc':
            # camera.PixelFormat = "Mono8"
            self.camera.PixelFormat = "BayerRG8"
            # camera.PixelFormat = "BayerRG12"
            # camera.PixelFormat = "BayerRG12Packed"
            # camera.PixelFormat = "RGB8"
            # camera.PixelFormat = "BGR8"

            # gain raw
            if CAPTURE_GAIN < self.camera.GainRaw.Min:
                self.camera.GainRaw = self.camera.GainRaw.Min
            elif CAPTURE_GAIN > self.camera.GainRaw.Max:
                self.camera.GainRaw = self.camera.GainRaw.Max
            else:
                self.camera.GainRaw = CAPTURE_GAIN

        elif model == 'acA1920-40uc':
            self.camera.PixelFormat = "Mono8"
            # self.camera.PixelFormat = "BayerRG8"
            # self.camera.PixelFormat = "BayerRG12"
            # self.camera.PixelFormat = "BayerRG12Packed"
            # self.camera.PixelFormat = "RGB8"
            # self.camera.PixelFormat = "BGR8"

            # gain raw
            if CAPTURE_GAIN < self.camera.GainRaw.Min:
                self.camera.GainRaw = self.camera.GainRaw.Min
            elif CAPTURE_GAIN > self.camera.GainRaw.Max:
                self.camera.GainRaw = self.camera.GainRaw.Max
            else:
                self.camera.GainRaw = CAPTURE_GAIN

        elif model == 'acA1300-30gm':
            self.camera.PixelFormat = "Mono8"
            # self.camera.PixelFormat = "Mono12"
            # self.camera.PixelFormat = "Mono12Packed"
            # self.camera.PixelFormat = "YUV422Packed"
            # self.camera.PixelFormat = "YUV422_YUYV_Packed"

            # gain raw
            if CAPTURE_GAIN < self.camera.GainRaw.Min:
                self.camera.GainRaw = self.camera.GainRaw.Min
            elif CAPTURE_GAIN > self.camera.GainRaw.Max:
                self.camera.GainRaw = self.camera.GainRaw.Max
            else:
                self.camera.GainRaw = CAPTURE_GAIN

        elif model == 'acA2040-55uc':
            # camera.PixelFormat = "Mono8"
            self.camera.PixelFormat = "BayerRG8"
            # camera.PixelFormat = "BayerRG12"
            # camera.PixelFormat = "BayerRG12Packed"
            # camera.PixelFormat = "RGB8"
            # camera.PixelFormat = "BGR8"

            # gain raw
            if CAPTURE_GAIN < self.camera.Gain.Min:
                self.camera.Gain = self.camera.Gain.Min
            elif CAPTURE_GAIN > self.camera.Gain.Max:
                self.camera.Gain = self.camera.Gain.Max
            else:
                self.camera.Gain = CAPTURE_GAIN

        else:
            raise Exception(f'not supported model:{model}')

    def is_connect(self):
        return self.camera is not None

    @log.function_log
    def start_shooting(self):
        log.print('start shooting')
        # Grabing Continusely (video) with minimal delay
        self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

        converter = pylon.ImageFormatConverter()
        # converting to opencv bgr format
        converter.OutputPixelFormat = pylon.PixelType_BGR8packed
        # converter.OutputPixelFormat = pylon.PixelType_Mono8
        converter.OutputBitAlignment = pylon.OutputBitAlignment_LsbAligned

        while self.camera.IsGrabbing():
            try:
                wait = Thread(target=wait_fps, args=(1/CAPTURE_FPS, ))
                wait.start()
                result = self.camera.RetrieveResult(
                    int(100000/CAPTURE_FPS),
                    pylon.TimeoutHandling_ThrowException)

                if result.GrabSucceeded():
                    # Access the image data
                    image = converter.Convert(result)
                    data = np.ndarray(buffer=image.GetBuffer(),
                                      shape=(result.Height, result.Width, 3),
                                      dtype=np.uint8)
                    self.update_image(data)
                    if DEBUG:
                        cv2.imshow('network camera', data)
                        cv2.waitKey(1)

                result.Release()
                wait.join()  # wait for fps
            except Exception as e:
                log.print(str(e))
                break

        self.camera.StopGrabbing()


@log.function_log
def camera_start(camera):
    camera.start_shooting()


@log.function_log
def server_start(camera, ip=None, port=50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    Datas_pb2_grpc.add_MainServerServicer_to_server(camera, server)

    if ip:
        server.add_insecure_port(f'{ip}:{port}')
        print(f"========== server start: {ip}:{port} ==============")
    else:
        server.add_insecure_port('[::]:50051')
        print(f"========== server start: localhost:{port} ==============")

    server.start()
    camera.start_shooting()
    server.wait_for_termination()

    log.print('server stop')
    server.stop(1)

# @main_decorator(SERVICE_NAME)
# def main(opt: Options):


def main():
    # get cache kanban
    #    conn = opt.get_conn()
    #    num = opt.get_number()
    #    kanban = conn.get_one_kanban(SERVICE_NAME, num)
    #
    #    # get output data path
    #    data_path = kanban.get_data_path()

    try:
        camera = CameraServicer()
        camera.setup()
        if not camera.is_connect():
            log.print('can not connect camera')
            sys.exit(1)

        server_start(camera)
        # exectutor = futures.ThreadPoolExecutor(max_workers = 2)
        # future_server = exectutor.submit(server_start, camera)
        # future_shoot = exectutor.submit(camera_start, camera)

        # monitor thread
        # while True:
        #    if not future_shoot.running():
        #        future_server.cancel()
        #        raise Exception('camera shoot is fail')
        #        break
        #    sleep(10)
        # output after kanban
#        conn.output_kanban(
#            result=True,
#            connection_key="default",
#            output_data_path=data_path,
#            process_number=num + 1,
#            # metadata={"test": ["test", "test2"]},
#        )

    except Exception as e:
        log.print(str(e))


if __name__ == '__main__':
    main()
