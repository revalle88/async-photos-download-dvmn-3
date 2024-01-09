import argparse
import os

INTERVAL_SECS = 0
CHUNK_SIZE = 100000

args = None
logging_enabled = None
response_delay = INTERVAL_SECS
photos_directory = None


def init_config():
    parser = argparse.ArgumentParser(description="AioHTTP Photos Archive Server")
    parser.add_argument(
        "--logging", action="store_true", dest="logging_enabled", help="Enable logging"
    )
    parser.add_argument(
        "--delay", dest="response_delay", type=int, help="Response delay in seconds"
    )
    parser.add_argument(
        "--photos-dir",
        dest="photos_directory",
        type=str,
        help="Path to the directory with photos",
    )
    args = parser.parse_args()
    global logging_enabled
    logging_enabled = (
        args.logging_enabled
        if args.logging_enabled is not None
        else os.getenv("LOGGING_ENABLED", "true").lower() == "true"
    )
    global response_delay
    response_delay = (
        args.response_delay
        if args.response_delay is not None
        else int(os.getenv("RESPONSE_DELAY", INTERVAL_SECS))
    )
    global photos_directory
    photos_directory = (
        args.photos_directory
        if args.photos_directory is not None
        else os.getenv("PHOTOS_DIRECTORY", None)
    )
