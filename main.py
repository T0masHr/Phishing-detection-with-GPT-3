# Import the email modules we'll need
from email.message import EmailMessage
# import os
import openai
import logging

# openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = "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"


def open_message(textfile):
    logging.debug(f'Called function "{open_message.__name__}" and using "{textfile}" as its parameter')
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


def api_call_completion(msg_input):
    logging.debug(f'Called function "{api_call_completion.__name__}" and using "{msg_input}" as its parameter')
    # call to the openai web api with the supplied email text body as input
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt="Determine if this email is a phishing email:\n\n" + msg_input,
        # prompt="Determine if this email is a phishing email:\n\nDear Kelly,\n\nIt was great to talk to you at the seminar."
        #        "I thought Jane's talk was quite good.\n\nThank you for the book. Here's my address 2111 Ash Lane, "
        #        "Crestview CA 92002\n\nBest,\n\nMaya\n\n",
        # prompt="Determine if this email is a phishing email:\nLiebe Mitarbeiter,\n \nBeachten Sie dieses wichtige "
        #        "Update, dass unser neues Webmail mit einem neuen \nMessaging-System von Microsoft verbessert wurde, "
        #        "das auch eine schnellere Nutzung \nvon E-Mails, freigegebenen Kalendern, Webdokumenten und der neuen "
        #        "Anti-Spam-\nVersion 2021 umfasst. \n \nBitte verwenden Sie den unten stehenden Link, um Ihr Microsoft "
        #        "Web-Mail-\nBenutzerauthentifizierungsformular 2021 auszufüllen. \n \nKLICKEN Sie auf Outlook Web "
        #        "Access, um sofort zu aktualisieren. \n \nIT Service Center (Rechenzentrum) - DHBW Stuttgart \n© "
        #        "Copyright 2021 - DHBW Stuttgart. Alle Rechte vorbehalten.\n\n",
        # Bei so langen Nachrichten können einfach drei Hochkommas genutzt gerden um die Nachricht einfacher als String einzugeben
        # '''
        # Hier
        # kann
        # die
        # Nachricht
        # einfach
        # rein
        # '''
        temperature=0.1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response


#######################################################################################################################
def main():
    logging.info('Starting...')
    logging.debug(f'Called function "{main.__name__}"')

    path = input("Enter the path to email file: \n")

    if not path:
        logging.warning('Empty input, falling back to default path')
        path = r"emailMessages\asString_placeholderMessage.txt"  # hardcoded path for dev

    logging.info(f'Using the following path:  {path}')


    msg_to_check = open_message(path)
    print(msg_to_check)

    # api_response = api_call_completion(msg_to_check)
    # print("API response: \n")
    # print(api_response)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()


