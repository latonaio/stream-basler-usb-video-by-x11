#!/bin/bash

IMAGE_NAME="stream-basler-usb-video-by-x11"

docker build -t ${IMAGE_NAME}:latest .
docker tag ${IMAGE_NAME}:latest latonaio/${IMAGE_NAME}:latest
