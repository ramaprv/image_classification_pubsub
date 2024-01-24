# This file converts video to images and dumps them to a log folder

import argparse
import os
import shutil

import cv2

from params import ConfigParams


class ImageProcessor:
    """
    Converts video to images and dumps to log folder
    """

    def __init__(self, config):
        """
        Initialize the ImageProcessor.

        Parameters:
        - config (ConfigParams): Configuration parameters.

        """
        self.config = config
        self.vid = None
        self.frame_interval = 1

    def load_video(self):
        """
        Opens and validates the video file
        """
        # Open the video file
        self.vid = cv2.VideoCapture(self.config["video_path"])

        # Verify video opened successfully
        if not self.vid.isOpened():
            raise ValueError(
                f"Error: Could not open video file at {self.config['video_path']}"
            )

    def compute_frame_interval(self):
        """
        Compute the interval between the frames to get the desired fps
        """
        # Get the fps of the video
        video_fps = self.vid.get(cv2.CAP_PROP_FPS)

        if video_fps <= 0:
            raise ValueError(f"Error: Video has invalid fps value {video_fps}")

        fps = min(
            self.config["fps"], video_fps
        )  # Incase desired fps is less than video fps
        self.frame_interval = int(video_fps / fps)

    def clear_log_dir(self):
        # Create the output folder if it doesn't exist
        os.makedirs(self.config["log_path"], exist_ok=True)

        # Clear the log folder
        try:
            # Get all files in folder
            files = os.listdir(self.config["log_path"])

            # Iterate and delete files
            for file in files:
                os.remove(os.path.join(self.config["log_path"], file))

        except Exception as e:
            print(f"Error while clearing log dir: {e}")

    def convert_video_to_images(self):
        """
        Processes the video to dump images
        """
        try:
            # Open video file
            self.load_video()

            # Compute at what frequency to save images
            self.compute_frame_interval()

            # Prepare the log dir
            self.clear_log_dir()

            frame_count = 0

            while True:
                # Read frame by frame from the video
                ret, frame = self.vid.read()

                # Break loop if video ended
                if not ret:
                    break

                # Save frame to log dir
                if frame_count % self.frame_interval == 0:
                    output_path = os.path.join(
                        self.config["log_path"],
                        f"frame_{frame_count//self.frame_interval}.jpg",
                    )
                    cv2.imwrite(output_path, frame)

                frame_count += 1

        except Exception as e:
            print(f"Error: {e}")

    def __del__(self):
        # Releaes the video capture object in destructor
        if self.vid is not None and self.vid.isOpened():
            self.vid.release()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config_path", type=str, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = ConfigParams().load_json(args.config_path)
    processor = ImageProcessor(config)
    processor.convert_video_to_images()


if __name__ == "__main__":
    main()
