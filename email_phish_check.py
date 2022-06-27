import json
import logging
import argparse
import os
import re

import jsonlines
import openai
from pprint import pformat

from helpers import get_paths_list, open_file_list, query_yes_no, setup_logging

DEFAULT_JSON_CONFIG = "apiprompt.json"
DEFAULT_API_KEY = os.getenv("OPENAI_API_KEY")  # should never be exposed, can be specified with arg '--api_key'
EMAIL_REGEX = re.compile(
    r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])")


# TODO: persistence for already evaluated files
# TODO: ability to set expected result for each file (for multiple files based on source folder)
# TODO: compare expected result with actual result
# TODO: argument to specify the response file

def main():
    """
    This is where the main functionality of this script resides. First the user supplied arguments are handled,
    such as the path to files or customized config file. By default, the OpenAI API key is loaded from an environment
    variable but can be also set manually using the appropriate argument. For some attributes,such as the JSON
    config, there are default values set. This external config is parsed to a dictionary.

    After the arguments are handled, the actual execution follows.
    At first, all the supplied paths which are loaded as a list are converted to Path() objects for better handling.
    If a path points at a directory, it is converted to multiple paths to all files in the directory.
    Afterwards all loaded files are opened and saved to a dictionary where the filename is the key and
    the file contents the value.

    The keys are printed to confirm with the user if he actually wants to send these files to the API.
    This is done using the known [y/n] prompt.
    If this is denied, the script terminates.
    After confirming the prompt, all files are sent to the API one by one.
    Each response is being logged to a file and also internally to a dictionary.
    After all API calls are finished, the simplified dictionary with all responses is printed.

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
        try:
            print(f"Using key '************************************************{args.api_key[-3:]}'")
        except TypeError:
            logging.error("No API key was loaded, it will not be possible to perform the API request")
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
            response = api_call_completion_endpoint(config, value)
            # get the api_call with the base_api_prompt and the value of the call
            api_result_dict[key] = response  # create new item in dict, that stores the response of the call
            writer.write({"file": key, "response_text": api_response_get_text(response), "response_json": response})
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


if __name__ == '__main__':
    main()
