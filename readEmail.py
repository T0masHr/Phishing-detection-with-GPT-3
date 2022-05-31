# Import the email modules we'll need
from email.message import EmailMessage


# Open the plain text file whose name is in textfile for reading.

def open_message(textfile):
    with open(textfile) as fp:
        # Create a text/plain message
        msg = EmailMessage()
        msg.set_content(fp.read())

        print(msg)
