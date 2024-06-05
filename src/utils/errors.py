import logging
from pymongo.errors import ConnectionFailure, ConfigurationError
from tenacity import RetryError
import traceback


class DatabaseError(Exception):
    """Error related to the database operations."""


class NetworkError(Exception):
    """Error related to network issues."""


class ArgumentParseError(Exception):
    """Error related to parsing arguments."""


class ValidationParseError(Exception):
    """Error related to validation."""


class ValidationFilterError(Exception):
    """Error related to validation."""


class ValidationFindError(Exception):
    """Error related to validation."""


def handle_error(e):
    """
    ConfigurationError: Issue connecting to mongodb
    ConnectionFailure: Error on mongodb side
    RetryError: Issue connecting to ChatGPT
    """
    # FOR NOW, USE TRACEBACK TO DEBUG

    # e.with_traceback()  # SHOULD I USE THIS?
    logging.error(f"Error: {traceback.format_exc()}")
    # logging.error(f"Error: {e}")

    if isinstance(e, ValidationFindError):
        arg_type = e.args[0]
        if arg_type == "events":
            error_msg = "Sorry, I can't find any relevant events for that."
        elif arg_type == "relations":
            error_msg = "Sorry, I can't find anything related to this person."
        return error_msg
    elif isinstance(e, ValidationFilterError):
        arg_type = e.args[0]
        if arg_type == "relations":
            error_msg = "Sorry, I don't have any record of the requested events involving this person."
        elif arg_type == "date range":
            error_msg = "Sorry, I don't have any record of the requested events within this dates."
        elif arg_type == "time range":
            error_msg = "Sorry, I don't have any record of the requested events within this timeframe."
        elif arg_type == "days":
            error_msg = "Sorry, I don't have any record of the requested events within those days."
        return error_msg
    elif isinstance(e, ValidationParseError):
        arg_type = e.args[0]
        if arg_type == "date range":
            error_msg = "I'm having trouble understanding the requested dates. Please try again."
        elif arg_type == "time range":
            error_msg = "I'm having trouble understanding the requested times. Please try again."
        elif arg_type == "days":
            error_msg = (
                "I'm having trouble understanding the requested days. Please try again."
            )
        return error_msg

    elif isinstance(e, ConfigurationError):
        return "Sorry, I'm having trouble connecting to the database. Please confirm your internet connection and try again."
    elif isinstance(e, ConnectionFailure):
        return "Sorry, I'm having trouble connecting to the database. Please try again in a few moments."
    elif isinstance(e, RetryError):
        return "Please check your internet connection and try again."
    # elif isinstance(e, NetworkError):
    #     return "I'm having network issues, please try again later."
    # elif isinstance(e, ArgumentParseError):
    #     return "I'm having trouble with this request. Please try something else."
    else:  # General error
        return "Oops, something unexpected went wrong. Please try again."
