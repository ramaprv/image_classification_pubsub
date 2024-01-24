# This file monitors the log folder and classifies the images as they are dumped

import warnings

# Suppress torchvision UserWarning
warnings.filterwarnings("ignore")

import argparse
import concurrent.futures
import logging
import os
import time

import numpy as np
import zmq
from PIL import Image
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from params import ConfigParams
from utils import classify_image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageHandler(FileSystemEventHandler):
    def __init__(self, config, executor):
        """
        Initialize the ImageHandler.

        Parameters:
        - config (ConfigParams): Configuration parameters.

        Returns:
        - None
        """
        super().__init__()
        self.config = config
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind(f"tcp://*:{self.config['zmq_port']}")
        self.last_active = time.time()
        self.executor = executor

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Clean up resources when exiting the context manager.
        """
        self.socket.close()
        self.context.term()

    def publish_result(self, result):
        """
        Publish the result to the message queue.

        Parameters:
        - result (str): Result to be published.
        """
        self.socket.send_string(result)

    def load_image(self, image_path):
        """
        Load an image from the given path into memory.

        Parameters:
        - image_path (str): Path to the image file.

        Returns:
        - ndarray: Numpy array representing the image.
        """
        if not os.path.isfile(image_path):
            logger.error(f"No image file at {image_path}")
            return None

        return np.array(Image.open(image_path))

    def process_image(self, image_path):
        """
        Process and classify the image.

        Parameters:
        - image_path (str): Path to the image file.

        Returns:
        - None
        """
        try:
            img_frame = self.load_image(image_path)
            if img_frame is not None:
                class_index = classify_image(img_frame)
                self.publish_result(f"{class_index} {image_path}")

        except Exception as e:
            logger.error(f"Error processing image {image_path}: {e}")

    def on_created(self, event):
        """
        Handler for the 'created' event triggered by the file system observer.

        Parameters:
        - event (FileSystemEvent): Event object representing the file system event.

        """
        if event.is_directory:
            return

        if event.event_type == "created":
            image_path = event.src_path
            self.last_active = time.time()
            # Submit the processing task to the thread pool
            self.executor.submit(self.process_image, image_path)


def run_producer_service(config) -> None:
    """
    Run the producer service to monitor for images in the log folder.

    Parameters:
    - config (ConfigParams): Configuration parameters.

    Returns:
    - None
    """
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=config["max_threads"]
    ) as executor:
        with ImageHandler(config, executor) as handler:
            observer = Observer()
            observer.schedule(handler, path=config["log_path"], recursive=False)
            observer.start()

            try:
                while True:
                    time.sleep(1)
                    elapsed_time = time.time() - handler.last_active
                    if elapsed_time > config["socket_timeout"]:
                        logger.info(
                            f"Timeout reached {config['socket_timeout']}. Stopping producer service."
                        )
                        break
            except KeyboardInterrupt:
                pass
            finally:
                observer.stop()
                observer.join()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config_path", type=str, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = ConfigParams().load_json(args.config_path)
    run_producer_service(config)


if __name__ == "__main__":
    main()
