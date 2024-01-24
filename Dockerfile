FROM python:3.10-bullseye

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 -y

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

RUN wget https://download.pytorch.org/models/resnet101-63fe2227.pth
RUN mv resnet101-63fe2227.pth /root/.cache/torch/hub/checkpoints/resnet101-63fe2227.pth

WORKDIR /opt/code
CMD /opt/code/run_service.sh
