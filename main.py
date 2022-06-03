import logging
import argparse
import sys

import openai
from pathlib import Path

import chatbot  # import file with chatbot functions
# import os
# Import the email modules we'll need
from email.message import EmailMessage
import dev_defaults

DEFAULT_PATH = dev_defaults.DEFAULT_PATH
DEFAULT_API_KEY = dev_defaults.API_KEY  # the key should be loaded from envvar # os.getenv("OPENAI_API_KEY")


# TODO:
#  - check if supplied path is file or folder
#  - supply the openai API_KEY with arg;

def open_path(supplied_path: str):
    logging.debug(f"Called function '{open_path.__name__}' and using '{supplied_path}' as its parameter")

    path = Path(supplied_path)
    logging.info(f"Using the following path:  {path} \n")

    msg_to_check = open_message(path)  # call the function to open file at supplied path
    logging.info("Opening message completed, following text was read: \n")
    return msg_to_check


def open_message(textfile) -> str:
    logging.debug(f"Called function '{open_message.__name__}' and using '{textfile}' as its parameter")
    # Open the plain text file whose name is in textfile for reading.

    try:
        with open(textfile) as fp:
            # Create a text/plain message
            text_from_file = f'''{fp.read()}'''
            return text_from_file
    except FileNotFoundError:
        logging.critical(f"!!! THE FILE {textfile} WAS NOT FOUND, ABORTING EXECUTION !!!")
        exit()


def api_response_get_text(response) -> str:
    return response['choices'][0]['text']


def api_call_completion(prompt, msg_input):
    logging.debug(f"Called function '{api_call_completion.__name__}'")
    logging.debug(f"First parameter is: '{prompt}'")
    logging.debug(f"Second parameter is: '{msg_input}'")

    # call to the openai web api with the supplied email text body as input
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt + msg_input,
        temperature=0.1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response


def demo_devmode():
    logging.warning("DEMO MODE ACTIVE")
    path = DEFAULT_PATH  # hardcoded path here


def setup_logging(verbosity_level):
    base_loglevel = 30
    verbosity_level = min(verbosity_level, 2)
    loglevel = base_loglevel - (verbosity_level * 10)  # loglevel goes from 10 to 50, intervals of 10
    # logging.DEBUG = 10; logging.CRITICAL = 50
    logging.basicConfig(level=loglevel, format='%(levelname)s:%(message)s')


#######################################################################################################################
def main():
    # command line arguments handling:
    parser = argparse.ArgumentParser()
    parser.add_argument("api_key", nargs="?", default=DEFAULT_API_KEY, help="API_KEY for openai")
    parser.add_argument("path", nargs="?", default=DEFAULT_PATH, help="uses this string as path to single file")
    parser.add_argument("-v", "--verbose", action="count", default=0, dest="verbosity_level",
                        help="set output verbosity: -v for INFO; -vv for DEBUG")
    parser.add_argument("--enable_api", action="store_true", help="enable the call to openai api")
    parser.add_argument("--demo", action="store_true", help="use demo values")
    parser.add_argument("--no_text", action="store_false", dest="print_text", help="Do not reflect the supplied text back in console")

    # parser.add_argument("--chatbot", action="store_true", help="switch to chatbot mode")
    options = parser.parse_args()
    setup_logging(options.verbosity_level)  # call the function to set up logging with provided verbosity level

    print_text = options.print_text

    if options.api_key is DEFAULT_API_KEY:
        logging.info("No api_key supplied, using the default key")

    openai.api_key = options.api_key

    if options.demo:  # check if user input is empty, if it is, use following hardcoded path:
        demo_devmode()



    # END of args handling          #############################################

    logging.info("Starting...")
    logging.debug(f"Called function '{main.__name__}'")

    msg_to_check = open_path(options.path)
    if print_text:
        print(msg_to_check)  # print the text back to user

    default_api_prompt = "Determine if this email is a phishing email:\n\n"

    if options.enable_api:
        # following is responsible for the api call, disabled to save credits:
        api_response = api_call_completion(default_api_prompt, msg_to_check)
        answered_text = api_response_get_text(api_response)
        print("API response: \n")
        print(answered_text)
        logging.debug(f"Full API response \n {api_response}")
    else:
        print("no actual api call performed to save credits. \n use argument '--enable_api' to use openai's api ")


if __name__ == '__main__':
    main()
