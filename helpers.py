import json
import logging
import re
import sys
from pathlib import Path
from pprint import pformat

EMAIL_REGEX = re.compile(
    r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])")


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
    """
    All the filtering options applied to the message body.

    :param text: Text to be filtered.
    :return: Filtered text.
    """
    filtered_text = text.replace("\n", "")
    # filtered_text = filtered_text.replace("﻿", " ")
    # filtered_text = filtered_text.replace(" ", " ")
    # filtered_text = filtered_text.replace("­", " ")
    filtered_text = re.sub(EMAIL_REGEX, "[email_removed]", filtered_text)
    return filtered_text


def query_yes_no(question: str, default="no") ->  bool:
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
