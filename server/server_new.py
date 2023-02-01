import os
import openai
import urllib.parse
from os import environ
from flask import Flask, request
from flask_cors import cross_origin
from dotenv import load_dotenv
load_dotenv()
OPEN_AI_KEY = os.getenv('OPEN_AI_KEY')
MAX_TOKENS = os.getenv('MAX_TOKENS')
TEMPRATURE = float(os.getenv('TEMPRATURE'))

if not OPEN_AI_KEY:
    print("Please add your OPEN AI KEY in .env")
    quit(0)

app = Flask(__name__)

history = []
# history = history[-10:]  # keep only the last 10 messages in the history
history = [h.replace('\n', ' ') for h in history]  # remove newline characters
# remove carriage return characters
history = [h.replace('\r', ' ') for h in history]
history = [h.replace('\t', ' ') for h in history]  # remove tab characters
openai.api_key = OPEN_AI_KEY


class Chatbot:
    """
    Official ChatGPT API
    """

    def __init__(self, api_key: str) -> None:
        """
        Initialize Chatbot with API key (from https://platform.openai.com/account/api-keys)
        """
        openai.api_key = api_key or os.getenv('OPEN_AI_KEY')
        self.prompt = Prompt()

    def ask(self, user_request: str) -> dict:
        """
        Send a request to ChatGPT and return the response
        Response: {
            "id": "...",
            "object": "text_completion",
            "created": <time>,
            "model": "text-chat-davinci-002-20230126",
            "choices": [
                {
                "text": "<Response here>",
                "index": 0,
                "logprobs": null,
                "finish_details": { "type": "stop", "stop": "<|endoftext|>" }
                }
            ],
            "usage": { "prompt_tokens": x, "completion_tokens": y, "total_tokens": z }
        }
        """
        prompt = self.prompt.construct_prompt(user_request)
        completion = openai.Completion.create(
            engine="text-chat-davinci-002-20230126",
            prompt=prompt,
            temperature=TEMPRATURE,
            max_tokens=1024,
            stop=["\n\n\n"],
        )
        if completion.get("choices") is None:
            raise Exception("ChatGPT API returned no choices")
        if len(completion["choices"]) == 0:
            raise Exception("ChatGPT API returned no choices")
        if completion["choices"][0].get("text") is None:
            raise Exception("ChatGPT API returned no text")
        completion["choices"][0]["text"] = completion["choices"][0]["text"].replace(
            "<|im_end|>",
            "",
        )
        # Add to chat history
        self.prompt.add_to_chat_history(
            "You: "
            + user_request
            + "\n\n\n"
            + "ChatGPT: "
            + completion["choices"][0]["text"]
            + "\n\n\n",
        )
        return completion

    def rollback(self, num: int) -> None:
        """
        Rollback chat history num times
        """
        for _ in range(num):
            self.prompt.chat_history.pop()

    def reset(self) -> None:
        """
        Reset chat history
        """
        self.prompt.chat_history = []


class AsyncChatbot(Chatbot):
    """
    Official ChatGPT API (async)
    """

    async def ask(self, user_request: str) -> dict:
        """
        Send a request to ChatGPT and return the response
        {
            "id": "...",
            "object": "text_completion",
            "created": <time>,
            "model": "text-chat-davinci-002-20230126",
            "choices": [
                {
                "text": "<Response here>",
                "index": 0,
                "logprobs": null,
                "finish_details": { "type": "stop", "stop": "<|endoftext|>" }
                }
            ],
            "usage": { "prompt_tokens": x, "completion_tokens": y, "total_tokens": z }
        }
        """
        prompt = self.prompt.construct_prompt(user_request)
        completion = await openai.Completion.acreate(
            engine="text-chat-davinci-002-20230126",
            prompt=prompt,
            temperature=0.5,
            max_tokens=1024,
            stop=["\n\n\n"],
        )
        if completion.get("choices") is None:
            raise Exception("ChatGPT API returned no choices")
        if len(completion["choices"]) == 0:
            raise Exception("ChatGPT API returned no choices")
        if completion["choices"][0].get("text") is None:
            raise Exception("ChatGPT API returned no text")
        completion["choices"][0]["text"] = completion["choices"][0]["text"].replace(
            "<|im_end|>",
            "",
        )
        # Add to chat history
        self.prompt.add_to_chat_history(
            "You: "
            + user_request
            + "\n\n\n"
            + "ChatGPT: "
            + completion["choices"][0]["text"]
            + "\n\n\n",
        )
        return completion


class Prompt:
    """
    Prompt class with methods to construct prompt
    """

    def __init__(self) -> None:
        """
        Initialize prompt with base prompt
        """
        self.base_prompt = (
            environ.get("CUSTOM_BASE_PROMPT")
            or "You are ChatGPT, a large language model trained by OpenAI. You answer as concisely as possible for each response (e.g. Don't be verbose).\n"
        )
        # Track chat history
        self.chat_history: list = []

    def add_to_chat_history(self, chat: str) -> None:
        """
        Add chat to chat history for next prompt
        """
        self.chat_history.append(chat)

    def history(self) -> str:
        """
        Return chat history
        """
        return "\n\n\n\n".join(self.chat_history)

    def construct_prompt(self, new_prompt: str) -> str:
        """
        Construct prompt based on chat history and request
        """
        prompt = (
            self.base_prompt + self.history() + "You: " + new_prompt + "\nChatGPT:"
        )
        # Check if prompt over 4000*4 characters
        if len(prompt) > 4000 * 4:
            # Remove oldest chat
            self.chat_history.pop(0)
            # Construct prompt again
            prompt = self.construct_prompt(new_prompt)
        return prompt


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

    prompt = request.args.get('q')  
    # decode the `q` parameter from UTF-8 encoding
    prompt = urllib.parse.unquote(prompt)
    history.append(prompt)  # add the latest question to the history
    chatbot = Chatbot(api_key=OPEN_AI_KEY)
    # Start chat
    PROMPT = prompt
    if PROMPT.startswith("!"):
        if chatbot_commands(PROMPT):
            print("continue")
    response = chatbot.ask(PROMPT)
    print("ChatGPT: " + response["choices"][0]["text"])
    message = response["choices"][0]["text"]
    message = message.replace("\n\n", "")
    history.append(message)

    print(message)
    return {"answers": message}

@app.route("/asr", methods=["GET"])
@cross_origin()
def asr():
    file_path = "path/to/audio/file.mp3"
    response = openai.Audio.create(file=file_path, model="text-davinci-002")
    print(response["data"])


if __name__ == "__main__":
    app.run(host="localhost", port=5001, debug=True)
