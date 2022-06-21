# Phishing detection with GPT-3

Emails should be provided as simple .txt files. 
The script extract the text files from provided paths. 
If the path is referencing a directory, all files from the directory are used.

## Usage
A path to at least one file must be always set. 
The API key is loaded from the OPENAI_API_KEY var. 
It can also be specified manually at start using --api_key.
If no other json config is specified, the default is used.

Without an extra option the script only reads the files, 
to actually send them to the OpenAI API, the argument "--enable_api" has to be set.
(This might be changed in the future)

**email_phish_check.py** is the main script. Following arguments are available: 
```
.\email_phish_check.py -h
usage: email_phish_check.py [-h] [-v] [--enable_api] [--api_key API_KEY] [--json_config JSON_CONFIG] path [path ...]

positional arguments:
  path                  path to single or multiple message files; If a directory path is provided all files in the directory are extracted and analysed

options:
  -h, --help            show this help message and exit
  -v, --verbose         set output verbosity: -v for INFO; -vv for DEBUG
  --enable_api          enable the call to openai api
  --api_key API_KEY     API_KEY for openai, by default the environment variable OPENAI_API_KEY is used
  --json_config JSON_CONFIG
                        change the used api config, by default the following configfile is used: 'apiprompt.json'

```



## Background
This project was started as an assignment in the 6. semester of the Business Information Systems course at DHBW Stuttgart.

The topic being Natural Language Processing, the task was to develop a system 
which is related to DHBW Stuttgart. it should offer a concrete benefit for our university 
(and, if applicable, also for the course of studies in business informatics).
The focus is to develop a "presentable" prototype.
A base idea provided by our professor was to develop a chatbot.

But since in the same week we got multiple warnings from our infosec team about an ongoing phishing campain, 
we came up with the idea to focus on phishing. At the time, GPT-3 was one of the best models 
