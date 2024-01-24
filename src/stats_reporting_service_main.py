# This file listens to the message queue and logs the class frequency

import argparse
import time
from collections import defaultdict

import zmq

from params import ConfigParams


def print_stats(class_results):
    """
    Print classification results to stdout
    """
    for class_index, count in class_results.items():
        print(f"class {class_index} detected {count} times")


def run_reporting_service(config) -> None:
    """
    Runs listening service to monitor classification results published

    Parameters:
    - config (ConfigParams): Configuration parameters.

    Returns:
    - None
    """
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(f"tcp://producer:{config['zmq_port']}")
    socket.setsockopt_string(zmq.SUBSCRIBE, "")

    # Store classification results in this dictionary
    class_results = defaultdict(int)

    # Timeout params
    socket_start_time = time.time()
    log_start_time = time.time()

    # Start checking message queue
    try:
        while True:
            # Receive message
            msg = socket.recv_string()
            class_index, image_path = msg.split()

            if not msg:
                # Exit loop if timeout reached
                if time.time() - socket_start_time > config["socket_timeout"]:
                    print(
                        f"Timeout reached {config['socket_timeout']}. Stopping reporting service."
                    )
                    break

                continue

            class_results[class_index] += 1

            # Reset the socket timeout counter
            socket_start_time = time.time()

            # Log results
            if time.time() - log_start_time >= config["stats_log_interval"]:
                print(f"In the past {config['stats_log_interval']} s:")
                print_stats(class_results)

                # Reset the classification results
                class_results.clear()

                # Reset the log timeout counter
                log_start_time = time.time()

    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        pass
    except Exception as e:
        print(f"Error: {e}")
    finally:
        socket.close()
        context.term()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config_path", type=str, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = ConfigParams().load_json(args.config_path)
    run_reporting_service(config)


if __name__ == "__main__":
    print("Running stats reporting service")
    main()
