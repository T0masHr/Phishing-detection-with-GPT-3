
def api_call_chatbot(human_input):
    logging.debug(f'Called function "{api_call_chatbot.__name__}"')
    logging.debug(f'First parameter is: "{human_input}"')

    default_settings = """
        Human: talk to  me in german\n        
        AI:\n\nGuten Tag! Wie kann ich Ihnen helfen?\n
        Human: Ich frage bezüglich der DHBW Stuttgart, bitte beantworte alle Fragen im Kontext dieser Hochschule\n""",

    start_sequence = "\nAI:"
    restart_sequence = "\nHuman: "

    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt="""Human: talk to  me in german\n        
        AI:\n\nGuten Tag! Wie kann ich Ihnen helfen?\n
        Human: Ich frage bezüglich der DHBW Stuttgart, bitte beantworte alle Fragen im Kontext dieser Hochschule\n """
               + human_input,
        temperature=0.9,
        max_tokens=150,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6,
        stop=[" Human:", " AI:"]
    )

    return response


def chatbot():
    logging.debug(f'Called function "{chatbot.__name__}"')
    human_input = input("\nHuman: ")
    print(api_call_chatbot(human_input))

