from openai import OpenAI
import os
import time
from dotenv import load_dotenv
load_dotenv()
client = OpenAI()

assistant = client.beta.assistants.create(
  name="quiz master",
  description="You are a master quiz creator.",
  model="gpt-4-turbo",
  tools=[{"type": "code_interpreter"}]

)
thread = client.beta.threads.create(
  messages=[
    {
      "role": "user",
      "content": "Create a 5 question multiple-choice quiz on the us civil war."
    
    }
  ]
)

message = client.beta.threads.messages.create(
  thread_id=thread.id,
  role="user",
  content="output the quiz as an interactive webpage using html and js."
)
run = client.beta.threads.runs.create(
  thread_id=thread.id,
  assistant_id=assistant.id,
  instructions="Please address the user as Gustave. Provide relevant code in output."
)
while run.status != "completed":
    time.sleep(5)
    run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
    print(f"\t\t{run}")
    
if run.status == 'completed':
  messages = client.beta.threads.messages.list(
    thread_id=thread.id
  )

  with open("output.txt", "w") as f:
      print(messages, file=f)
