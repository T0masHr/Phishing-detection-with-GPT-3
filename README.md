# Phishing detection with GPT-3

Emails should be provided as simple .txt files. 
The script extract the textfiles from provided paths. 
If the path is referencing a directory, all files from the directory are used.

By default the script only reads the files, 
to actually send them to the openai API, the argument "--enable_api" has to be set.


## Background
This project was started as an assignment in the 6. semester of the Business Information Systems course at DHBW Stuttgart.

The topic being Natural Language Processing, the task was to develop a system 
which is related to DHBW Stuttgart. it should offer a concrete benefit for our university 
(and, if applicable, also for the course of studies in business informatics).
The focus is to develop a "presentable" prototype. 