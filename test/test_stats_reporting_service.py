# Test cases for producer_service_main.py

import os
import pytest
import numpy as np
from unittest.mock import Mock, patch
from PIL import Image

from params import ConfigParams
from stats_reporting_service_main import run_reporting_service, print_stats


@pytest.fixture
def mock_config():
    return ConfigParams.load_json("/opt/code/config.json")


def test_print_stats(capsys):
    class_results = {0: 3, 1: 5, 2: 2}
    print_stats(class_results)
    captured = capsys.readouterr()
    assert "class 0 detected 3 times" in captured.out
    assert "class 1 detected 5 times" in captured.out
    assert "class 2 detected 2 times" in captured.out
