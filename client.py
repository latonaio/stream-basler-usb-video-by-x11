#============================================================
# import packages
#============================================================
from concurrent import futures
import time
import cv2
import grpc
import base64
import numpy as np
import sys
from pathlib import Path
from api import Datas_pb2
from api import Datas_pb2_grpc

#============================================================
# class
#============================================================



#============================================================
# property
#============================================================



#============================================================
# functions
#============================================================
def run():

    # with grpc.insecure_channel('localhost:50051') as channel:
    with grpc.insecure_channel('127.0.0.1:50051') as channel:
        try:
            stub = Datas_pb2_grpc.MainServerStub(channel)
            # return generator
            while True:
                print("request image")
                responses = stub.getImage(Datas_pb2.ImageRequest())
                for res in responses:
                    # print(type(res))
                    b64d = base64.b64decode(res.image)
                    dBuf = np.frombuffer(b64d, dtype = np.uint8)
                    dst = cv2.imdecode(dBuf, cv2.IMREAD_COLOR)
                    cv2.imshow('Capture Image', dst)
                    k = cv2.waitKey(1)
                    if k == 27:
                        break
                    # print(type(res))
                    # print(res.image)
                    print('date:', res.date)
                # import pdb; pdb.set_trace()
                time.sleep(0.1)


        except grpc.RpcError as e:
            print(e.details())
            #break

    print("finish client")

#============================================================
# Awake
#============================================================



#============================================================
# main
#============================================================
if __name__ == '__main__':
    run()



#============================================================
# after the App exit
#============================================================
cv2.destroyAllWindows()
