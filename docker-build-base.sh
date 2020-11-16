#!/bin/bash

IMAGE_NAME="stream-basler-usb-video-by-x11-base"

docker build -f Dockerfile-base -t ${IMAGE_NAME}:latest .
