import os
import openai
import urllib.parse
from flask import Flask, request
from flask_cors import cross_origin
from dotenv import load_dotenv
load_dotenv()

OPEN_AI_KEY = os.getenv('OPEN_AI_KEY')
MAX_TOKENS = os.getenv('MAX_TOKENS')
TEMPRATURE = os.getenv('TEMPRATURE')
if not OPEN_AI_KEY:
    print("Please add your OPEN AI KEY in .env")
    quit(0)

app = Flask(__name__)

history = []
# history = history[-10:]  # keep only the last 10 messages in the history
history = [h.replace('\n', ' ') for h in history]  # remove newline characters
history = [h.replace('\r', ' ') for h in history]  # remove carriage return characters
history = [h.replace('\t', ' ') for h in history]  # remove tab characters
openai.api_key = OPEN_AI_KEY


@app.route("/ask", methods=["GET"])
@cross_origin()
def ask():

    prompt = request.args.get('q')  # add this line
    conversation_id = request.args.get('conversation_id')
    print("conversation_id" + conversation_id)
    prompt = urllib.parse.unquote(prompt)  # decode the `q` parameter from UTF-8 encoding
    history.append(prompt)  # add the latest question to the history
    completions = openai.Completion.create(
        engine="text-davinci-003",
        prompt = ' '.join(history),
        max_tokens=MAX_TOKENS,
        n=1,
        stop=None,
        temperature=TEMPRATURE
    )
    id = completions.id
    message = completions.choices[0].text
    message = message.replace("\n\n", "")
    history.append(message)

    print(message)
    print("id in ask" + id)
    return {"answers": message, "id": id}  # add this line

@app.route("/new-conversation", methods=["GET"])
@cross_origin()
def new_conversation():
    history.clear() # clear the history
    completions = openai.Completion.create(
        engine="text-davinci-003",
        prompt='',  # pass an empty prompt to start a new conversation
        max_tokens=MAX_TOKENS,
        n=1,
        stop=None,
        temperature=TEMPRATURE
    )
    
    id = completions.id
    print("id in new:" + id)
    return {"id": id}

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5001,debug=True)
