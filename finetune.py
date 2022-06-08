import json
import logging
import argparse
import openai
import jsonlines

from email_phish_check import *  # import all functions from main file

DEFAULT_JSON_CONFIG = "apiprompt.json"


def craft_jsonl(prompt: str, msg_list: dict, desired_output: str):
    # {"prompt": "<prompt text>", "completion": "<ideal generated text>"}
    # "prompt": "Determine if this email is a phishing email:\n",
    with jsonlines.open('output.jsonl', mode='w') as writer:
        for value in msg_list.values():
            writer.write({"prompt": prompt + value, "completion": desired_output})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="+", help="Path to single or multiple message files; If a directory path is "
                                                "provided all files in the directory are extracted and analysed")
    parser.add_argument("-v", "--verbose", action="count", default=0, dest="verbosity_level",
                        help="set output verbosity: -v for INFO; -vv for DEBUG")
    parser.add_argument("--api_key", default=DEFAULT_API_KEY,
                        help="API_KEY for openai, by default the environment variable OPENAI_API_KEY is used")
    parser.add_argument("--enable_api", action="store_true",
                        help="enable the call to openai api")
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

    print("Extracting provided paths...\n")
    messages_dict = open_file_list(get_paths_list(args.path))  # convert the user supplied arguments in
    # args.path into a list of path objects. Then open all files in this list and return a dictionary with the
    # filename as a key and the contents s the value - this is the messages_dict
    print(f"Following files were read: \n{chr(10).join(map(str, messages_dict.keys()))}\n")

    craft_jsonl(api_config["prompt"], messages_dict, 'This email is not a phishing email.')

    if args.enable_api:
        print("Api call is active")
        print("...")

    else:
        logging.info(f"The argument '--enable_api' was not supplied, no api call")
        print("No actual api call performed to save credits. \n use argument '--enable_api' to use openai's api ")


if __name__ == '__main__':
    main()
