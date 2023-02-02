import os
import openai
from chatbot import Chatbot
from prompt import Prompt
import urllib.parse
# from os import environ
from flask import Flask, request
from flask_cors import cross_origin
from dotenv import load_dotenv


load_dotenv()
OPEN_AI_KEY = os.getenv('OPEN_AI_KEY')
MAX_TOKENS = os.getenv('MAX_TOKENS')
TEMPRATURE = float(os.getenv('TEMPRATURE'))
base_prompt = (os.getenv("CUSTOM_BASE_PROMPT")
               or "You are ChatGPT, a large language model trained by OpenAI. You answer as concisely as possible for each response (e.g. Don't be verbose).\n")
if not OPEN_AI_KEY:
    print("Please add your OPEN AI KEY in .env")
    quit(0)

app = Flask(__name__)

@app.route("/chat", methods=["GET"])
@cross_origin()
def chat():
    def chatbot_commands(cmd: str) -> bool:
        """
        Handle chatbot commands
        """
        if cmd == "!help":
            print(
                """
            !help - Display this message
            !rollback - Rollback chat history
            !reset - Reset chat history
            !exit - Quit chat
            """,
            )
        elif cmd == "!exit":
            exit()
        elif cmd == "!rollback":
            chatbot.rollback(1)
        elif cmd == "!reset":
            chatbot.reset()
        else:
            return False
        return True

    user_request = request.args.get('q')
    # decode the `q` parameter from UTF-8 encoding
    user_request = urllib.parse.unquote(user_request)
    chatbot = Chatbot(api_key=OPEN_AI_KEY,
                      temprature=TEMPRATURE, base_prompt=base_prompt)
    # Start chat
    PROMPT = user_request
    if PROMPT.startswith("!"):
        if chatbot_commands(PROMPT):
            print("continue")
    response = chatbot.ask(PROMPT)
    print("ChatGPT: " + response["choices"][0]["text"])
    message = response["choices"][0]["text"]
    message = message.replace("\n\n", "")
    # print(message)
    return {"answers": message}

@app.route("/asr", methods=["GET"])
@cross_origin()
def asr():
    file_path = "path/to/audio/file.mp3"
    response = openai.Audio.create(file=file_path, model="text-davinci-002")
    print(response["data"])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
