# Test cases for image_processing_service_main.py

import os
import pytest
import cv2
import numpy as np

from params import ConfigParams
from image_processing_service_main import ImageProcessor


@pytest.fixture
def mock_config():
    return ConfigParams.load_json("/opt/code/config.json")


@pytest.fixture
def mock_image_processor(mock_config):
    return ImageProcessor(mock_config)


def test_load_video_success(mock_image_processor):
    # Verify cv image capture works
    mock_image_processor.load_video()
    assert mock_image_processor.vid.isOpened()


def test_load_video_invalid_path(mock_image_processor):
    # Test loading video with invalid path
    mock_image_processor.config["video_path"] = "invalid_path.mp4"

    with pytest.raises(ValueError):
        mock_image_processor.load_video()


def test_compute_frame_interval(mock_image_processor):
    mock_image_processor.load_video()
    mock_image_processor.compute_frame_interval()
    assert mock_image_processor.frame_interval > 0


def test_clear_log_dir(mock_config, mock_image_processor):
    # Create a dummy file in the log directory
    dummy_file_path = os.path.join(mock_config["log_path"], "dummy.txt")
    with open(dummy_file_path, "w") as dummy_file:
        dummy_file.write("This is a dummy file.")

    # Check if the dummy file exists before clearing
    assert os.path.exists(dummy_file_path)

    # Clear the log directory
    mock_image_processor.clear_log_dir()

    # Check if the log directory is empty after clearing
    assert not os.listdir(mock_config["log_path"])


def test_convert_video_to_images(mock_config, mock_image_processor):
    # Create a dummy video file for testing
    dummy_video_path = os.path.join(mock_config["log_path"], "dummy_video.mp4")
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    dummy_video = cv2.VideoWriter(dummy_video_path, fourcc, 30, (640, 480))  # 30 fps
    for _ in range(100):  # 100 frames
        dummy_frame = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
        dummy_video.write(dummy_frame)
    dummy_video.release()

    # Convert the dummy video to images
    mock_image_processor.config["video_path"] = dummy_video_path
    mock_image_processor.convert_video_to_images()

    # Check if the correct number of images are created
    # Video is at 30 fps and image processor config is at 15 fps. So output should be half of 100
    assert len(os.listdir(mock_config["log_path"])) == 50

    # Clean up - remove generated files after testing
    for file_name in os.listdir(mock_config["log_path"]):
        file_path = os.path.join(mock_config["log_path"], file_name)
        os.remove(file_path)
