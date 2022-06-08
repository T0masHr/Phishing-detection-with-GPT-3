import json
import logging
import argparse
import openai

from email_phish_check import *  # import all functions from main file


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="+", help="Path to single or multiple message files; If a directory path is "
                                                "provided all files in the directory are extracted and analysed")
    parser.add_argument("-v", "--verbose", action="count", default=0, dest="verbosity_level",
                        help="set output verbosity: -v for INFO; -vv for DEBUG")
    options = parser.parse_args()
    setup_logging(options.verbosity_level)  # call the function to set up logging with provided verbosity level


if __name__ == '__main__':
    main()
