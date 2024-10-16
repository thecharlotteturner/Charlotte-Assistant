from dotenv import load_dotenv
import os
import openai

# Load environment variables
load_dotenv()

# Initialize OpenAI client with your API key
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Capability to read files
file = client.files.create(
    file=open('poorly_written_horse_paper.txt', 'rb'), # Open file in read-binary mode
    purpose='fine-tune'  # You can adjust this depending on your goal
)

# Create the assistant
assistant = client.beta.assistants.create(
  name="Grammar Police",
  description="You are the world's best editor. You know all the grammar rules, help edit text to be concise & simple. You will improve grammar, make papers more concise, and ensure documents are clear and easy to read.",
  model="gpt-4",  # Correcting model typo
  tools=[{"type": "code_interpreter"}],
  tool_resources={
    "code_interpreter": {
      "file_ids": [file.id]
    }
  }
)

# Create the thread
thread = client.beta.threads.create(
  messages=[
    {
      "role": "user",
      "content": "Please edit and revise this file using grammar rules.",
      "attachments": [
        {
          "file_id": file.id,
          "tools": [{"type": "code_interpreter"}]
        }
      ]
    }
  ]
)

# Send additional message if needed (optional)
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Please revise this file using grammar rules."
)

# Run the assistant and poll for the result
run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id,
    assistant_id=assistant.id,
    instructions='please refer to the user as Charlotte'
)

# Check if the run completed
if run.status == 'completed':
    messages = client.beta.threads.messages.list(thread_id=thread.id)

    # Save output to a file
    with open('edited.txt', 'w') as f:
        for msg in messages:
            f.write(msg['content'] + "\n")

    print("Revised version saved to 'edited.txt'")