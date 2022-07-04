import argparse
import logging
import re
import sys

from jsonlines import jsonlines

from helpers import setup_logging, open_file_list, get_paths_list, query_yes_no

DEFAULT_JSONL_DB = "nogit/messagesDB.jsonl"
EMAIL_REGEX = re.compile(
    r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])")


def main():
    """
    This is module is used to load (multiple) message files from a directory, assign the expected classification and
    append them to a JSONL file which is used in further processing.

    :return: None
    """
    # command line arguments handling:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="+", help="path to single or multiple message files; If a directory path is "
                                                "provided all files in the directory are extracted and analysed")
    parser.add_argument("-v", "--verbose", action="count", default=0, dest="verbosity_level",
                        help="set output verbosity: -v for INFO; -vv for DEBUG")
    parser.add_argument("messagesDB", nargs="?", default=DEFAULT_JSONL_DB,
                        help="path to the JSONL which stores all loaded messages ")
    args = parser.parse_args()
    setup_logging(args.verbosity_level)  # call the function to set up logging with provided verbosity level

    # END of args handling          #############################################

    logging.info("Starting...")
    db_path = args.messagesDB

    print(f"The extracted files will be saved in '{db_path}'")

    logging.debug(f"The path supplied is type: {type(args.path)}")

    print("Extracting provided paths...\n")
    messages_dict = open_file_list(get_paths_list(args.path))  # convert the user supplied arguments in
    # args.path into a list of path objects. Then open all files in this list and return a dictionary with the
    # filename as a key and the contents s the value - this is the messages_dict
    print(f"Following files were read: \n{chr(10).join(map(str, messages_dict.keys()))}\n")

    messages_are_phishing = query_yes_no("Are the loaded messages phishing?")
    if messages_are_phishing:
        print("Setting the attribute 'phishing' to YES for all loaded messages")
        craft_jsonl(db_path, messages_dict, messages_are_phishing)

    elif not messages_are_phishing:
        print("Setting the attribute 'phishing' to NO for all loaded messages")
        craft_jsonl(db_path, messages_dict, messages_are_phishing)


def craft_jsonl(output_file: str, msg_dict: dict, desired_output: bool):
    """
    Transform the data in the jsonlines format needed by OpenAI for model fine tuning.
    :param output_file: Path to file where output will be saved.

    :param prompt: Baseline API prompt.
    :param msg_dict: Dictionary with loaded messages.
    :param desired_output: This is the desired answer from the API
    :return: None
    """

    lineslist = []  # list of objects/lines from the JSONL

    with jsonlines.open(output_file, mode='r') as reader:
        for obj in reader.iter(type=dict, skip_invalid=True):
            lineslist.append(obj)  # list of json objects loaded from file
    # the appending mode of open could b used insted
    with jsonlines.open(output_file, mode='w') as writer:
        for item in lineslist:
            writer.write(item)
        for msg_key, msg_text in msg_dict.items():
            # writer.write({"file": msg_key, "phishing": desired_output, "api_result": None, "message_text": msg_text})
            writer.write({"file": msg_key, "phishing": desired_output, "message_text": msg_text})

    return None


def custom_text_filter(text: str) -> str:
    """
    All the filtering options applied to the message body.
sign
    :param text: Text to be filtered.
    :return: Filtered text.
    """
    filtered_text = text.replace("\n", " ")
    # filtered_text = filtered_text.replace("﻿", " ")
    # filtered_text = filtered_text.replace(" ", " ")
    # filtered_text = filtered_text.replace("­", " ")
    filtered_text = re.sub(EMAIL_REGEX, "[email_removed]", filtered_text)
    return filtered_text


if __name__ == '__main__':
    main()
