from enum import IntEnum

APP_NAME = "Your Next Travel"
APP_TAGLINE = "Your Travel Portal"
APP_SLUG = "your-next-travel"


class ResponseCode(IntEnum):
    SUCCESS = 100
    ERROR = 101
    FATAL_ERROR = 102
    SKIP = 103
    NOT_IMPLEMENTED = 104
