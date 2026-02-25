import os
import json

from flask import Flask, render_template, request
from anthropic import Anthropic, beta_tool

app = Flask(__name__)

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

@beta_tool
def save_text_to_file(text: str, file_path: str) -> str:
    """Save the provided text to a file on disk.

    Args:
        text: The text to be saved in file.
        file_path: The file path.
    Returns:
        The path of the created file.
    """

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)

    return json.dumps(
        {
            "file_path": file_path,
        }
    )

@app.route("/", methods=["GET", "POST"])
def index():

    value = None
    if request.method == "POST":
        user_input = request.form.get("user_input", "").strip()

        resp = client.messages.create(
            model="claude-sonnet-4-6",   # pick a model you have access to
            max_tokens=512,
            messages=[
                {"role": "user", "content": user_input}
            ],
            tools=[
                {
                    "type": "web_search_20250305",  # web search tool (server tool)
                    "name": "web_search",
                    "max_uses": 3,
                },
                save_text_to_file.to_dict(),
            ],
        )
        value = "".join(block.text for block in resp.content if block.type == "text")

        if value == "":
            value = None
    return render_template("index.html", value=value)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)