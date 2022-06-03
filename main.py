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
DEFAULT_API_PROMPT = "Determine if this email is a phishing email:\n\n"


# TODO:
#  - check if supplied path is file or folder
#  - supply the openai API_KEY with arg;

def open_path(supplied_path_list):
    logging.debug(f"Called function '{open_path.__name__}'")
    logging.debug(f"Your list contains the following items:\n{chr(10).join(supplied_path_list)}\n")
    logging.debug(f"The parameter has the type {type(supplied_path_list)}")
    path_list = []

    if len(supplied_path_list) == 0:
        logging.critical("Supplied path is empty, aborting")
        exit("No path supplied")

    if len(supplied_path_list) >= 1:
        logging.debug(f"The following list of path objects is being appended {path_list}")
        for i in supplied_path_list:
            p = Path(i)  # create Path object from one item in list
            path_list.append(p)  # append the newly created Path to the path list

        logging.debug(f"Following list with paths was created: \n{chr(10).join(map(str, path_list))}\n")

    # path = Path(supplied_path)
    # logging.info(f"Using the following path:  {path} \n")
    #
    # if path.is_file():
    #     logging.info("The supplied path is a file path")
    #
    # if path.is_dir():
    #     logging.info("The supplied path is a folder path")

    # msg_to_check = open_message(path)  # call the function to open file at supplied path
    # return msg_to_check


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
        exit("Path was not found")


def api_response_get_text(response) -> str:
    logging.debug(f"Called function '{api_response_get_text.__name__}' and using '{response}' as its parameter")
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


def setup_logging(verbosity_level):
    base_loglevel = 30
    verbosity_level = min(verbosity_level, 2)
    loglevel = base_loglevel - (verbosity_level * 10)  # loglevel goes from 10 to 50, intervals of 10
    # logging.DEBUG = 10; logging.CRITICAL = 50
    FORMAT = "[%(asctime)s %(filename)s->%(funcName)s():%(lineno)s]%(levelname)s: %(message)s"
    if loglevel == 10:
        logging.basicConfig(level=loglevel, format=FORMAT)
    if loglevel >= 20:
        logging.basicConfig(level=loglevel, format='%(levelname)s:%(message)s')


#######################################################################################################################
def main():
    # command line arguments handling:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="*", default=DEFAULT_PATH,
                        help="Path to single or multiple message files")
    parser.add_argument("--api_key", default=DEFAULT_API_KEY,
                        help="API_KEY for openai")
    parser.add_argument("-v", "--verbose", action="count", default=0, dest="verbosity_level",
                        help="set output verbosity: -v for INFO; -vv for DEBUG")
    parser.add_argument("--enable_api", action="store_true",
                        help="enable the call to openai api")
    parser.add_argument("--no_text", action="store_false", dest="print_text",
                        help="Do not reflect the supplied text back in console")
    parser.add_argument("--api_prompt", nargs="?", default=DEFAULT_API_PROMPT,
                        help=f"Change the base API prompt, otherwise the following prompt is used: '{DEFAULT_API_PROMPT}'")
    # parser.add_argument("--chatbot", action="store_true", help="switch to chatbot mode")
    options = parser.parse_args()
    setup_logging(options.verbosity_level)  # call the function to set up logging with provided verbosity level

    if options.api_key is DEFAULT_API_KEY:
        logging.info("No api_key supplied, using the default key")

    if options.path is DEFAULT_PATH:
        logging.info(f"No path supplied, using the default path: '{DEFAULT_PATH}'")

    openai.api_key = options.api_key
    print_text = options.print_text

    # END of args handling          #############################################

    logging.info("Starting...")
    logging.debug(f"The path supplied is: {type(options.path)}")

    msg_to_check = open_path(options.path)
    if print_text:
        logging.info("Opening message completed, following text was read: \n")
        print(msg_to_check)  # print the text back to user

    base_api_prompt = DEFAULT_API_PROMPT

    if options.enable_api:
        logging.info("Api call is active")
        # following is responsible for the api call, disabled to save credits:
        api_response = api_call_completion(base_api_prompt, msg_to_check)
        answered_text = api_response_get_text(api_response)
        print("API response: \n")
        print(answered_text)
        logging.debug(f"Full API response \n {api_response}")
    else:
        logging.info(f"The argument '--enable_api' was not supplied, no api call")
        print("No actual api call performed to save credits. \n use argument '--enable_api' to use openai's api ")


if __name__ == '__main__':
    main()
