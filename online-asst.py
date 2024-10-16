from dotenv import load_dotenv, find_dotenv
import time
from openai import OpenAI
client = OpenAI()
import logging
from datetime import datetime
import requests
import json
load_dotenv()

assistant_id = "asst_5H074IxwDozPXWSarsLzwusn"
def create_thread(ass_id,prompt):
    #Get Assitant
    assistant = client.beta.assistants.retrieve(ass_id)


    #create a thread
    thread = client.beta.threads.create()
    my_thread_id = thread.id

    #create a message
    message = client.beta.threads.messages.create(
        thread_id=my_thread_id,
        role="user",
        content=prompt
    )
    #run
    run = client.beta.threads.runs.create(
        thread_id=my_thread_id,
        assistant_id=ass_id,
    )
    return run.id, thread.id

def check_status(run_id,thread_id):
    run = client.beta.threads.runs.retrieve(
        thread_id=thread_id,
        run_id=run_id,
    )
    return run.status

my_run_id, my_thread_id = create_thread(assistant_id,"[topic]: ask me a hard quiz question about the civil war. output as interactive html and js.")

status = check_status(my_run_id,my_thread_id)

while (status != "completed"):
    status = check_status(my_run_id,my_thread_id)
    time.sleep(2)

response = client.beta.threads.messages.list(
  thread_id=my_thread_id
)

if response.data:
    print(response.data[0].content[0].text.value)