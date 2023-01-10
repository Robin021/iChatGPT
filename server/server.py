import os
import openai
import urllib.parse
from flask import Flask, request
from flask_cors import cross_origin
from dotenv import load_dotenv
load_dotenv()

OPEN_AI_KEY = os.getenv('OPEN_AI_KEY')
if not OPEN_AI_KEY:
    print("Please add your OPEN AI KEY in .env")
    quit(0)

app = Flask(__name__)

history = []
history = history[-10:]  # keep only the last 10 messages in the history
history = [h.replace('\n', ' ') for h in history]  # remove newline characters
history = [h.replace('\r', ' ') for h in history]  # remove carriage return characters
history = [h.replace('\t', ' ') for h in history]  # remove tab characters

@app.route("/ask", methods=["GET"])
@cross_origin()
def ask():
    openai.api_key = OPEN_AI_KEY

    conversation_id = 'your-conversation-id'
    prompt = request.args.get('q')  # add this line
    prompt = urllib.parse.unquote(prompt)  # decode the `q` parameter from UTF-8 encoding
    history.append(prompt)  # add the latest question to the history
    completions = openai.Completion.create(
        engine="text-davinci-003",
        # engine="davinci",
        prompt='\n'.join(history),  # pass the entire history as the prompt
        max_tokens=128,
        n=1,
        stop=None,
        temperature=0.5,
        conversation_id=conversation_id
    )
    
    message = completions.choices[0].text
    history.append(message)
    return {"answers": message}


if __name__ == "__main__":
    app.run(debug=True)
