import os
import asyncio
from quart import Quart, render_template, request

app = Quart(__name__)

@app.route('/', methods=['GET', 'POST'])

async def index():
    if request.method == "POST":
        await(request).form
        name = (await request.form).get('name')
        return f"Hello, {name}!"
    return await render_template("index.html")

if __name__ == '__main__':
    app.run()
