#!/bin/bash

IMAGE_NAME="stream-nw-video-by-grpc-client"

docker build -f Dockerfile-client -t ${IMAGE_NAME}:latest .
