import json
import logging
import argparse
import os
import re
import sys

import jsonlines
import openai
from pprint import pformat
from pathlib import Path

DEFAULT_JSON_CONFIG = "apiprompt.json"
DEFAULT_API_KEY = os.getenv("OPENAI_API_KEY")  # should never be exposed, can be specified with arg '--api_key'
EMAIL_REGEX = re.compile(
    r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])")


# TODO: persistence for already evaluated files

def get_paths_list(supplied_path_list: list) -> list:
    """
    Transform the supplied paths strings into Path() objects from pathlib.
    If the provided path is a directory, all files in that directory are extracted as single paths.

    :param supplied_path_list: strings supplied by the user
    :return: list with Path() objects
    """

    logging.debug(f"Called function '{get_paths_list.__name__}'")
    logging.debug(f"Your list contains the following items:\n{chr(10).join(supplied_path_list)}\n")
    logging.debug(f"The parameter has the type {type(supplied_path_list)}")
    path_list = []  # user supplied paths
    files_list = []  # fill with only file paths and no folder paths

    if len(supplied_path_list) == 0:  # The supplied list should never be empty
        logging.critical("Supplied path is empty, aborting")
        exit("EXIT: No path supplied")

    if len(supplied_path_list) >= 1:
        logging.debug(f"The following list of path objects is being appended {path_list} (it should be empty here)")
        for i in supplied_path_list:  # loop over the whole list
            i = i.strip('"')
            p = Path(i)  # create Path object from one item in list
            logging.debug(f"Appending the following path to the list:\n {p} \n")
            path_list.append(p)  # append the newly created Path to the path list

        logging.debug(f"Following list with paths was read from supplied arguments: \n{path_list}\n")
        logging.info(
            f"Following list with paths was read from supplied arguments: \n{chr(10).join(map(str, path_list))}\n")

        logging.debug(f"Checking if the paths are files or directories")

    logging.info("Extracting file paths from directories")
    for path in path_list:
        path = path.resolve()

        if path.is_file():
            logging.debug(f"The path '{path}' is a file path")
            files_list.append(path)

        elif path.is_dir():
            logging.debug(f"The path '{path}' is a folder path")
            for child_path in path.iterdir():
                files_list.append(child_path)

        else:
            logging.critical("Somehow the path is neither file or directory")
            logging.critical(f"Please check the path '{path}' and try again")
            pathstat = path.stat()
            logging.critical(f"The file info: {pathstat}")
            exit("EXIT: Error with supplied path")

    logging.debug(f"Following list with files was created: \n{files_list}\n")
    logging.info(f"Following list with files was created: \n{chr(10).join(map(str, files_list))}\n")

    return files_list


def open_file_list(files_list: list) -> dict:
    """
    Open all text files from the supplied path list and save the file contents in a dictionary,
    key being the filename and the value the file content.

    :param files_list: list with Path objects
    :return: Dictionary with content from loaded files
    """
    logging.debug(f"Called function '{open_file_list.__name__}' and using '{files_list}' as its parameter")

    msg_dict = {}  # declare empty dict which will be returned by this function

    for path in files_list:  # loop over the whole list with filepaths
        logging.debug(f"Working on the list item {path.name}")
        filename = path.name  # get the file name
        filecontent = open_message(path)  # call the function to open file at supplied path
        msg_dict[filename] = filecontent  # create new item in dict, key being filename and value being the content

    logging.debug(f"Following dict keys are present in the created dict: \n{msg_dict.keys()}\n")
    logging.info(f"Following files were read: \n{chr(10).join(map(str, msg_dict.keys()))}\n")
    # logging.debug(f"Following dict with filecontents was created: \n{msg_dict}\n")
    # logging.debug(f"Following dict with filecontents was created: \n{chr(10).join(map(str, msg_dict))}\n")

    return msg_dict


def open_message(textfile) -> str:
    """
    Open the supplied textfile and return the contents.

    :param textfile: the file to be opened
    :return: filecontents, newlines are stripped
    """
    logging.debug(f"Called function '{open_message.__name__}' and using '{textfile}' as its parameter")
    # Open the plain text file whose name is in textfile for reading.

    try:
        with open(textfile, encoding="utf-8", errors="ignore") as fp:
            # Create a text/plain message
            text_from_file = f'''{fp.read()}'''
            edited_text = custom_text_filter(text_from_file)

            return edited_text
    except FileNotFoundError:
        logging.critical(f"!!! THE FILE {textfile} WAS NOT FOUND, ABORTING EXECUTION !!!")
        exit("EXIT: Path was not found")


def custom_text_filter(text: str) -> str:
    filtered_text = text.replace("\n", "")
    filtered_text = filtered_text.replace("﻿", " ")
    filtered_text = filtered_text.replace(" ", " ")
    filtered_text = filtered_text.replace("­", " ")
    filtered_text = re.sub(EMAIL_REGEX, "[email_removed]", filtered_text)
    return filtered_text


def parse_api_json_config(configfile):
    """
    Parse the external JSON config file for the openai configuration.
    :param configfile: path to the config file
    :return: JSON form the config file parsed to dict
    """
    logging.debug(f"Called function '{parse_api_json_config.__name__}'")
    logging.debug(f"First parameter is: '{configfile}'")
    # this function loads the configuration for the api call
    f = open(configfile)
    config = json.load(f)
    logging.info(f"\nThe following json config was loaded: \n {pformat(config)}\n")
    return config


def api_call_completion_endpoint(config: dict, msg_input: str):
    """
    Perform the actual api call to the 'completion' endpoint.
    The parameter msg_input is appended to the 'prompt' specified in the config.
    :param config: API configuration as dict loaded from JSON
    :param msg_input: The actual message body to be analyzed.
    :return: The API response.
    """
    logging.debug(f"Called function '{api_call_completion_endpoint.__name__}'")
    logging.debug(f"First parameter is: '{config}'")
    logging.debug(f"Second parameter is: '{msg_input}'")

    try:
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=config["prompt"] + msg_input,
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            top_p=config["top_p"],
            frequency_penalty=config["frequency_penalty"],
            presence_penalty=config["presence_penalty"]
        )
    except openai.error.AuthenticationError as e:
        logging.critical(f"OPEN AI AUTHENTICATION ERROR: {e}")
        exit("EXIT: Openai authentication error")

    return response


def api_calls_on_dict(config: dict, msg_dict: dict) -> dict:
    """
    Perform multiple API calls, one call per key-value in the supplied dict.
    :param config: API configuration as dict loaded from JSON.
    :param msg_dict: Dictionary with messages to be analyzed.
    :return: Dictionary with all api responses.
    """
    logging.debug(f"Called function '{api_calls_on_dict.__name__}'")
    # logging.debug(f"First parameter is: '{msg_dict}'")
    logging.debug(f"First parameter is: '{config}'")
    logging.debug(f"Second parameter is a dictionary with the keys: '{msg_dict.keys()}'")

    api_result_dict = {}  # declare empty dict which will be returned by this function
    with jsonlines.open("nogit/response_log_test.jsonl", mode='w') as writer:
        for key, value in msg_dict.items():  # loop over the whole msg_list with key and value of the msg_list
            response = api_call_completion_endpoint(config,
                                                    value)  # get the api_call with the base_api_prompt and the value of the call
            api_result_dict[key] = response  # create new item in dict, that stores the response of the call
            writer.write({"file": key, "response text": api_response_get_text(response), "response json": response})
            logging.debug(f"The API call for {key} finished")

    return api_result_dict


def get_text_from_response_dict(api_result_dict: dict) -> dict:
    """
    Iterate over the given dictionary and extract only the actual response text from the api response.
    Return the response texts in dict.
    :param api_result_dict: Dict with the API JSON responses.
    :return: Dict with the filename as key and the textual response as value.
    """
    logging.debug(f"Called function '{get_text_from_response_dict.__name__}' without parameters.")
    api_result_text_dict = {}

    for key, value in api_result_dict.items():
        api_result_text_dict[key] = api_response_get_text(value)

    return api_result_text_dict


def prettyprint_api_text_response_dict(used_api_prompt: str, api_result_text_dict: dict):
    """
    Print the API responses from a dict with the corresponding initial prompt in a pretty way.
    :param used_api_prompt: The base API prompt, should be loaded from the used JSON config.
    :param api_result_text_dict: Dict with text extracted from the API responses.
    :return: None
    """
    # this function prints all the api response to given files
    logging.debug(
        f"Called function '{prettyprint_api_text_response_dict.__name__}' and using '{api_result_text_dict}' as its parameter")
    prompt_without_linebreak = used_api_prompt.strip("\n")

    print(f"The textual prompt for the API was: '{prompt_without_linebreak}' and the API responded with:")
    for key, value in api_result_text_dict.items():
        value = value.strip("\n")
        # print(f"For the file {key} the API responded with: '{value}'")
        print(f"{key} -> '{value}'")

    return None


def api_response_get_text(response) -> str:
    """
    Get the response text from the response JSON.
    :param response: Response JSON.
    :return: Extracted text.
    """
    logging.debug(f"Called function '{api_response_get_text.__name__}' and using '{response}' as its parameter")
    return response['choices'][0]['text']


def query_yes_no(question, default="no"):
    """
    Ask a yes/no question via raw_input() and return their answer.

    :param question: String that is presented to the user.
    :param default: The presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).
    :return: The "answer" return value is True for "yes" or False for "no".
    """
    # stolen from: https://stackoverflow.com/a/3041990
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")


def setup_logging(verbosity_level):
    """
    Configure the logging module used in this script.
    :param verbosity_level:  Verbosity level is set with args.
    :return: None
    """
    base_loglevel = 30  # base value is only to display warning messages
    verbosity_level = min(verbosity_level, 2)
    loglevel = base_loglevel - (verbosity_level * 10)  # loglevel goes from 10 to 50, intervals of 10
    # logging.DEBUG = 10; logging.CRITICAL = 50
    custom_format = "[%(asctime)s %(filename)s->%(funcName)s():%(lineno)s]%(levelname)s: %(message)s"
    if loglevel == 10:
        logging.basicConfig(level=loglevel, format=custom_format)
    if loglevel >= 20:
        logging.basicConfig(level=loglevel, format='%(levelname)s:%(message)s')


def main():
    """
    First the supplied arguments are handled.
    Check if any default values are changed.
    Load the API key to be able to communicate with OpenAI.
    All the supplied paths are saved to a dictionary and opened.
    :return: None
    """
    # command line arguments handling:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="+", help="path to single or multiple message files; If a directory path is "
                                                "provided all files in the directory are extracted and analysed")
    parser.add_argument("-v", "--verbose", action="count", default=0, dest="verbosity_level",
                        help="set output verbosity: -v for INFO; -vv for DEBUG")
    parser.add_argument("--api_key", default=DEFAULT_API_KEY,
                        help="API_KEY for openai, by default the environment variable OPENAI_API_KEY is used")
    parser.add_argument("--json_config", default=DEFAULT_JSON_CONFIG,
                        help=f"change the used api config, by default the following configfile is used: '{DEFAULT_JSON_CONFIG}'")

    args = parser.parse_args()
    setup_logging(args.verbosity_level)  # call the function to set up logging with provided verbosity level

    if args.api_key is DEFAULT_API_KEY:
        print("No api_key supplied, using the key from environment variable")
        print(f"Using key '************************************************{args.api_key[-3:]}'")

    if args.json_config is DEFAULT_JSON_CONFIG:
        print(f"No json config file supplied, using the default '{DEFAULT_JSON_CONFIG}'")

    openai.api_key = args.api_key
    api_config = parse_api_json_config(args.json_config)
    print(f"\nThe following json config was loaded: \n {pformat(api_config)}\n")

    # END of args handling          #############################################

    logging.info("Starting...")

    logging.debug(f"The path supplied is type: {type(args.path)}")

    print("Extracting provided paths...\n")
    messages_dict = open_file_list(get_paths_list(args.path))  # convert the user supplied arguments in
    # args.path into a list of path objects. Then open all files in this list and return a dictionary with the
    # filename as a key and the contents s the value - this is the messages_dict
    print(f"Following files were read: \n{chr(10).join(map(str, messages_dict.keys()))}\n")

    perform_call = query_yes_no("Follow with the actual API call? Watch the costs.")
    if perform_call:

        print("Api call is active, performing calls")
        print("...")
        api_responses_dict = api_calls_on_dict(api_config, messages_dict)
        print("...")
        api_text_responses = get_text_from_response_dict(api_responses_dict)
        print("...")
        prettyprint_api_text_response_dict(api_config["prompt"], api_text_responses)

    elif not perform_call:
        print("Answered no, the actual API calls will not be performed.")


if __name__ == '__main__':
    main()
