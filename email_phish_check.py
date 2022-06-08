import json
import logging
import argparse
import os
import openai
from pprint import pformat
from pathlib import Path

DEFAULT_JSON_CONFIG = "apiprompt.json"
DEFAULT_API_KEY = os.getenv("OPENAI_API_KEY")  # should never be exposed, can be specified with arg '--api_key'


def get_paths_list(supplied_path_list: list) -> list:
    # This function transforms the user supplied paths strings into Path() objects from pathlib.
    # The function returns a list with those objects
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
    logging.debug(f"Called function '{open_file_list.__name__}' and using '{files_list}' as its parameter")
    # This function opens all text files from the supplied path list and saves the contents of the files n a
    # dictionary where the key is the filename and the value the file content

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
    logging.debug(f"Called function '{open_message.__name__}' and using '{textfile}' as its parameter")
    # Open the plain text file whose name is in textfile for reading.

    try:
        with open(textfile) as fp:
            # Create a text/plain message
            text_from_file = f'''{fp.read()}'''
            return text_from_file
    except FileNotFoundError:
        logging.critical(f"!!! THE FILE {textfile} WAS NOT FOUND, ABORTING EXECUTION !!!")
        exit("EXIT: Path was not found")


def parse_api_json_config(configfile):
    logging.debug(f"Called function '{parse_api_json_config.__name__}'")
    logging.debug(f"First parameter is: '{configfile}'")
    # this function loads the configuration for the api call
    f = open(configfile)
    config = json.load(f)
    logging.info(f"\nThe following json config was loaded: \n {pformat(config)}\n")
    return config


def api_call_completion_endpoint(config: dict, msg_input: str):
    logging.debug(f"Called function '{api_call_completion_endpoint.__name__}'")
    logging.debug(f"First parameter is: '{config}'")
    logging.debug(f"Second parameter is: '{msg_input}'")

    # call to the openai web api with the supplied email text body as input
    # response = openai.Completion.create(
    #     engine="text-davinci-002",
    #     prompt=prompt + msg_input,
    #     temperature=0.1,
    #     max_tokens=256,
    #     top_p=1,
    #     frequency_penalty=0,
    #     presence_penalty=0
    # )
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
    logging.debug(f"Called function '{api_calls_on_dict.__name__}'")
    # logging.debug(f"First parameter is: '{msg_dict}'")
    logging.debug(f"First parameter is: '{config}'")
    logging.debug(f"Second parameter is a dictionary with the keys: '{msg_dict.keys()}'")

    api_result_dict = {}  # declare empty dict which will be returned by this function

    for key, value in msg_dict.items():  # loop over the whole msg_list with key and value of the msg_list
        response = api_call_completion_endpoint(config,
                                                value)  # get the api_call with the base_api_prompt and the value of the call
        api_result_dict[key] = response  # create new item in dict, that stores the response of the call
        logging.debug(f"The API call for {key} finished")

    return api_result_dict


def get_text_from_response_dict(api_result_dict: dict) -> dict:
    logging.debug(f"Called function '{get_text_from_response_dict.__name__}' without parameters.")
    # this function iterates over the given dictionary and gets the actual response text from the api response
    # return is a dictionary with the filename as key and the textual response as value
    api_result_text_dict = {}

    for key, value in api_result_dict.items():
        api_result_text_dict[key] = api_response_get_text(value)

    return api_result_text_dict


def prettyprint_api_text_response_dict(used_api_prompt: str, api_result_text_dict: dict):
    # this function prints all the api response to given files
    logging.debug(
        f"Called function '{prettyprint_api_text_response_dict.__name__}' and using '{api_result_text_dict}' as its parameter")
    prompt_without_linebreak = used_api_prompt.strip("\n")

    print(f"The textual promt for the API was: '{prompt_without_linebreak}' and the API responded with:")
    for key, value in api_result_text_dict.items():
        value = value.strip("\n")
        # print(f"For the file {key} the API responded with: '{value}'")
        print(f"{key} -> '{value}'")


def api_response_get_text(response) -> str:
    logging.debug(f"Called function '{api_response_get_text.__name__}' and using '{response}' as its parameter")
    return response['choices'][0]['text']


def setup_logging(verbosity_level):
    base_loglevel = 30  # base value is only to display warning messages
    verbosity_level = min(verbosity_level, 2)
    loglevel = base_loglevel - (verbosity_level * 10)  # loglevel goes from 10 to 50, intervals of 10
    # logging.DEBUG = 10; logging.CRITICAL = 50
    custom_format = "[%(asctime)s %(filename)s->%(funcName)s():%(lineno)s]%(levelname)s: %(message)s"
    if loglevel == 10:
        logging.basicConfig(level=loglevel, format=custom_format)
    if loglevel >= 20:
        logging.basicConfig(level=loglevel, format='%(levelname)s:%(message)s')


#######################################################################################################################
def main():
    # command line arguments handling:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="+", help="Path to single or multiple message files; If a directory path is "
                                                "provided all files in the directory are extracted and analysed")
    parser.add_argument("-v", "--verbose", action="count", default=0, dest="verbosity_level",
                        help="set output verbosity: -v for INFO; -vv for DEBUG")
    parser.add_argument("--enable_api", action="store_true",
                        help="enable the call to openai api")
    parser.add_argument("--api_key", default=DEFAULT_API_KEY,
                        help="API_KEY for openai, by default the environment variable OPENAI_API_KEY is used")
    parser.add_argument("--json_config", default=DEFAULT_JSON_CONFIG,
                        help=f"Change the used api config, by default the following configfile is used: '{DEFAULT_JSON_CONFIG}'")

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

    if args.enable_api:
        print("Api call is active")
        print("...")
        api_responses_dict = api_calls_on_dict(api_config, messages_dict)
        print("...")
        api_text_responses = get_text_from_response_dict(api_responses_dict)
        print("...")
        prettyprint_api_text_response_dict(api_config["prompt"], api_text_responses)

    else:
        logging.info(f"The argument '--enable_api' was not supplied, no api call")
        print("No actual api call performed to save credits. \n use argument '--enable_api' to use openai's api ")


if __name__ == '__main__':
    main()
