# PubSub based Image Classification

Main componenets of this are:
* `image_processing_service` which converts video file to images to a log folder based on the desired fps
* `producer_service` which monitors the log folder and classifies them using a pretrained ResNet101 in `classify_image` and publishes the result to socket using `pyzmp`
* `stats_reporting_service` consumes these from the socket message queue and logs the results to stdout every 10s

These configurations can be changed in `config.json`

## Setup
1. Install [docker](https://docs.docker.com/engine/install/). Recommended version is `23.0.3`.
2. `git clone https://github.com/ramaprv/image_classification_pubsub.git`
3. `cd image_classification_pubsub`
4. `docker-compose build`
5. `docker-compose up`

Example output:
```
[+] Running 3/0
 ⠿ Container producer_service         Created   0.0s
 ⠿ Container stats_reporter_service   Created   0.0s
 ⠿ Container image_processor_service  Created   0.0s
Attaching to image_processor_service, producer_service, stats_reporter_service
image_processor_service  | + case "$SERVICE_NAME" in
image_processor_service  | + python -u src/image_processing_service_main.py --config_path config.json
stats_reporter_service   | + case "$SERVICE_NAME" in
stats_reporter_service   | + python -u src/stats_reporting_service_main.py --config_path config.json
stats_reporter_service   | Running stats reporting service
producer_service         | + case "$SERVICE_NAME" in
producer_service         | + python -u src/producer_service_main.py --config_path config.json
image_processor_service exited with code 0
stats_reporter_service   | In the past 10 s:
stats_reporter_service   | class 654 detected 41 times
stats_reporter_service   | In the past 10 s:
stats_reporter_service   | class 654 detected 18 times
stats_reporter_service   | class 468 detected 5 times
stats_reporter_service   | class 627 detected 31 times
stats_reporter_service   | class 407 detected 2 times
stats_reporter_service   | In the past 10 s:
stats_reporter_service   | class 627 detected 27 times
stats_reporter_service   | class 468 detected 15 times
stats_reporter_service   | class 407 detected 14 times
stats_reporter_service   | class 612 detected 1 times
stats_reporter_service   | In the past 10 s:
stats_reporter_service   | class 407 detected 49 times
stats_reporter_service   | class 468 detected 1 times
stats_reporter_service   | class 656 detected 1 times
stats_reporter_service   | class 654 detected 6 times
...
```

## Test
1. docker-compose -f docker-compose-tests.yml build
2. docker-compose -f docker-compose-tests.yml up

Example test results:
```
  | ============================= test session starts ==============================
  | platform linux -- Python 3.10.13, pytest-7.4.4, pluggy-1.4.0
  | rootdir: /opt/code
  | collected 8 items
  | 
  | test/test_image_processing_service.py .....                              [ 62%]
  | test/test_producer_service.py ..                                         [ 87%]
  | test/test_stats_reporting_service.py .                                   [100%]
  | 
  | ============================== 8 passed in 2.61s ===============================
exited with code 0
```
