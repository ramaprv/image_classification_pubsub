# Test cases for producer_service_main.py

import os
import pytest
import cv2
import numpy as np
from unittest.mock import MagicMock
from PIL import Image

from params import ConfigParams
from producer_service_main import ImageHandler


@pytest.fixture
def mock_executor():
    return MagicMock()


@pytest.fixture
def mock_config():
    return ConfigParams.load_json("/opt/code/config.json")


@pytest.fixture
def mock_image_handler(mock_config, mock_executor):
    return ImageHandler(mock_config, mock_executor)


def test_load_image_exists(mock_config, mock_image_handler):
    img_path = os.path.join(mock_config["log_path"], "dummy.jpg")
    img = Image.fromarray(np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8))
    img.save(img_path)

    image = mock_image_handler.load_image(img_path)
    assert image is not None


def test_load_image_not_exists(mock_image_handler):
    image_path = "path/to/nonexistent/image.jpg"
    image = mock_image_handler.load_image(image_path)
    assert image is None
