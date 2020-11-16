FROM stream-basler-usb-video-by-x11-base:latest

# Definition of a Device & Service
ENV POSITION=Runtime \
    SERVICE=stream-basler-usb-video-by-x11 \
    AION_HOME=/var/lib/aion

WORKDIR ${AION_HOME}/$POSITION/$SERVICE/
ADD . .

CMD ["python3", "-u", "main.py"]
