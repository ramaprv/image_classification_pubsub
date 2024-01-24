# This file is used to load the config parameters

import json

from marshmallow import Schema, ValidationError, fields


class ConfigParams(Schema):
    """
    Class to hold the configuration parameters
    """

    video_path = fields.Str(required=True)
    fps = fields.Int(required=True)
    log_path = fields.Str(required=True)
    zmq_port = fields.Str(required=True)
    socket_timeout = fields.Int(required=True)
    stats_log_interval = fields.Int(required=True)
    max_threads = fields.Int(required=True)

    @classmethod
    def load_json(cls, json_path):
        """
        This function is used to parse the config json into the ConfigParams class
        """
        with open(json_path, "r") as file:
            config_data = json.load(file)

        try:
            config = cls().load(config_data)
            return config
        except ValidationError as e:
            raise ValueError(f"Invalid configuration: {e.messages}")
