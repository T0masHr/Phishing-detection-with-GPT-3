import logging
import argparse
import openai
# import os
# Import the email modules we'll need
from email.message import EmailMessage

openai.api_key = "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"  # the key should be loaded from envvar # os.getenv("OPENAI_API_KEY")


# TODO: -
#  implement additional args:
#  1. - the ability to disable the actual api call to openai to save credits;
#  2. - provide the file path per arg instead of stdin;
#  3. - supply the openai API_KEY with arg;
#  extract the actual "text" field from the api response, maybe display the whole response when logging is set to debug
#  add the ability to check multiple files at once or rather to supply a folder with files to check



def open_message(textfile):
    logging.debug(f'Called function "{open_message.__name__}" and using "{textfile}" as its parameter')
    # Open the plain text file whose name is in textfile for reading.
    with open(textfile) as fp:
        # Create a text/plain message
        text_from_file = f'''{fp.read()}'''
        return text_from_file

        # handling the file as email message using the email module:
        # msg = EmailMessage()
        # msg.set_content(readText)
        # msg_string = msg.as_string()
        # # print(msg)
        # return msg_string


def api_call_completion(prompt, msg_input):
    logging.debug(f'Called function "{api_call_completion.__name__}"')
    logging.debug(f'First parameter is: "{prompt}"')
    logging.debug(f'Second parameter is: "{msg_input}"')

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


#######################################################################################################################
def main():
    # command line arguments handling:
    parser = argparse.ArgumentParser()
    parser.add_argument('-debug', action='store_true', help='Turn DEBUG output ON')
    options = parser.parse_args()

    if options.debug is True:
        logging.basicConfig(level=logging.DEBUG)
        # Print the Library's installation path
    else:
        logging.basicConfig(level=logging.WARNING)

    logging.info('Starting...')
    logging.debug(f'Called function "{main.__name__}"')

    path = input("Enter the path to email file: \n")

    if not path:  # check if user input is empty, if it is, use following hardcoded path:
        logging.warning('Empty input, falling back to default path')
        path = r"emailMessages\placeholderMessage.txt"  # hardcoded path here

    logging.info(f'Using the following path:  {path} \n')

    msg_to_check = open_message(path)  # call the function to open file at supplied path
    logging.info('Opening message completed, following text was read: \n')
    print(msg_to_check)  # print the text back to user

    default_api_prompt = "Determine if this email is a phishing email:\n\n"

    # following is responsible for the api call, disabled to save credits:
    # api_response = api_call_completion(default_api_prompt, msg_to_check)
    # print("API response: \n")
    # print(api_response)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # log level is now set using cmd args
    # logging.basicConfig(level=logging.DEBUG) # set the logging level, DEBUG displays all messages, INFO is less chatty
    main()
