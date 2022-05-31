# Import the email modules we'll need
from email.message import EmailMessage
# import os
import openai


# openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = "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"


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


def open_message(textfile):
    # Open the plain text file whose name is in textfile for reading.
    with open(textfile) as fp:
        # Create a text/plain message
        text_from_file = fp.read()
        return text_from_file

        # msg = EmailMessage()
        # msg.set_content(readText)
        # msg_string = msg.as_string()
        # # print(msg)
        # return msg_string


def api_call(msg_input):
    # call to the openai web api with the supplied email text body as input
    response = openai.Completion.create(
        engine="text-davinci-002",
        # prompt="Determine if this email is a phishing email:\n\n" + msg_input,
        prompt="Determine if this email is a phishing email:\n\nDear Kelly,\n\nIt was great to talk to you at the seminar."
               "I thought Jane's talk was quite good.\n\nThank you for the book. Here's my address 2111 Ash Lane, "
               "Crestview CA 92002\n\nBest,\n\nMaya\n\n",

        temperature=0,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response


#######################################################################################################################

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

    # path = input("Enter the path to email file: ") # comment out when using hardcoded poath below
    path = r"C:\Users\tomas\OneDrive - Duale Hochschule Baden-Württemberg Stuttgart\Projekt\EmailFiles\Gremienwahlen.txt"  # hardcoded path for dev
    print("Using the following path: " + path) # comment out when using hardcoded path below

    msg_to_check = open_message(path)
    # print(msg)
    api_response = api_call(msg_to_check)
    print(api_response)
