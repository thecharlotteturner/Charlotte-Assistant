import html
from quart import Quart, request, render_template_string
from openai import OpenAI
import json
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()
import time

import logging

# Set up logging to display errors
logging.basicConfig(level=logging.DEBUG)

# Initialize Quart app
app = Quart(__name__)
# HTML template for the page
html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Makeup Product Master Response</title>
    <style>
    html, body {
font-family: sans-serif;
font-size:1.5em;
margin: 0;
background: rgb(218, 177, 250);
}
form {
max-width: 650px;
margin: 0 auto;
padding: 16px;
border: 0.5px solid black;
text-align: center;
}
h1, h2, h3 {
text-align: center;
}
p {
    white-space: pre-wrap;
    word-break: break-all;
    margin: 0 120px;
    }
    #user_input {
    margin-top: 32px;
    padding: 15px 0;
    text-align: center;
    font-size: 20px;
    }
    </style>
</head>
<body>
    <h1>Makeup Product Master</h1>
    <form action="/chat" method="post">
        <label for="user_input">Enter your desired makeup product here:</label><br>
        <input type="text" size="60" id="user_input" name="user_input" required><br><br>
        <input type="submit" value="Send">
    </form>
    {% if assistant_reply %}
    <h2>Makeup Master's Response:</h2>
    <p>{{ assistant_reply }}</p>
    {% endif %}
</body>
</html>
'''

@app.route('/')
async def index():
    # Render the initial HTML page with no response yet
    return await render_template_string(html_template)

@app.route('/chat', methods=['POST'])
async def chat():
    try:
        # Get user input from the form
        form_data = await request.form
        user_input = form_data['user_input']

        # Interact with OpenAI API
        assistant = client.beta.assistants.create(
            name="Makeup Product Master",
            description="You are a makeup product master. You know everything about makeup and how to find the best products online.",
            model="gpt-4-turbo",
            tools=[{"type": "code_interpreter"}]
        )
        thread = client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": "Create a list of 3 makeup products and where to buy the products online based on the value of user_input."
                }
            ]
        )
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input
        )
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id,
            instructions="Output as HTML text."
        )
        while run.status != "completed":
            time.sleep(5)
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            print(f"\t\t{run}")

        if run.status == 'completed':
            messages = client.beta.threads.messages.list(
                thread_id=thread.id
            ).model_dump_json()

        # Extract the assistant's response
        json_data = json.loads(messages)
        values = []
        for item in json_data['data']:
            values.append(item['content'][0]['text']['value'])
            values = values.pop()
            assistant_response = values
            # Render the HTML page with the ChatGPT response
            return await render_template_string(html_template, assistant_reply=assistant_response)

    except Exception as e:
        # Log any errors
        app.logger.error(f"Error: {e}")
        return await render_template_string(html_template, assistant_reply="Something went wrong, please try again.")


if __name__ == '__main__':
    app.run(debug=True)
