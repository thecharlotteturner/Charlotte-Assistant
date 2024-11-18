from quart import Quart, request, render_template_string
from openai import OpenAI

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
    <title>ChatGPT Response</title>
<style>
html, body {
font-family: sans-serif;
font-size:1.2em;
margin: 0;
}
form {
max-width: 480px;
margin: 0 auto;
padding: 16px;
border: 1px solid black;
}
h2 {
text-align: center;
}

</style>
</head>
<body>
    <h2>Chat with ChatGPT</h2>
    <form action="/chat" method="post">
        <label for="user_input">What topic would you like trivia on?</label><br>
        <input type="text" size="60"  id="user_input" name="user_input" required><br><br>
        <input type="submit" value="Send">
    </form>
    {% if assistant_reply %}
    <h2>ChatGPT's Response:</h2>
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
            name="quiz master",
            description="You are a trivia master. Share 3 interesting facts about the 'user_input' variable in this python file.",
            model="gpt-4-turbo",
            tools=[{"type": "code_interpreter"}]
        )
        thread = client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": user_input

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
            instructions="Provide only the text in your output."
        )

        while run.status != "completed":
            time.sleep(5)

            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            print(f"\t\t{run}")

        if run.status == 'completed':
            messages = client.beta.threads.messages.list(
                thread_id=thread.id
            )

        # Extract the assistant's response
        assistant_reply = messages
        # Render the HTML page with the ChatGPT response
        return await render_template_string(html_template, assistant_reply=assistant_reply)

    except Exception as e:
        # Log any errors
        app.logger.error(f"Error: {e}")
        return await render_template_string(html_template, assistant_reply="Something went wrong, please try again.")

if __name__ == '__main__':
    app.run(debug=True)