import os
import openai
import json
from chatbot import Chatbot
from prompt import Prompt
import urllib.parse
# from os import environ
from flask import Flask, request
from flask_cors import cross_origin
from dotenv import load_dotenv
from loguru import logger
from wechatpy.utils import check_signature
from wechatpy.exceptions import InvalidSignatureException
from wechatpy import parse_message
from wechatpy.replies import TextReply
from revChatGPT.V1 import Chatbot

load_dotenv()
logger.add("./log/runtime_{time}.log", retention="10 days", rotation="500 MB")

# OPEN_AI_KEY = os.getenv('OPEN_AI_KEY')
# MAX_TOKENS = os.getenv('MAX_TOKENS')
# TEMPRATURE = float(os.getenv('TEMPRATURE'))




# base_prompt = (os.getenv("CUSTOM_BASE_PROMPT")
#                or "You are ChatGPT, a large language model trained by OpenAI. You answer as concisely as possible for each response (e.g. Don't be verbose).\n")
# if not OPEN_AI_KEY:
#     print("Please add your OPEN AI KEY in .env")
#     quit(0)


def configure():
    """
    Looks for a config file in the following locations:
    """

    with open('config.json', encoding="utf-8") as f:
        config = json.load(f)
    return config

app = Flask(__name__)
# chatbot = Chatbot(api_key=OPEN_AI_KEY,
#                   temprature=TEMPRATURE, base_prompt=base_prompt, model=MODEL)

@app.route("/chat", methods=["GET"])
@cross_origin()
def chat():
    chatbot_officail = Chatbot(config=configure())
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
    conversation_id = request.args.get('conversation_id')
    print(conversation_id)
    # Start chat
    PROMPT = user_request
    print("Chatbot: ")
    prev_text = ""
    pre_conversation_id = ""
    for data in chatbot_officail.ask(
        PROMPT, conversation_id=conversation_id, 
    ):
        message = data["message"][len(prev_text):]
        print(message, end="", flush=False)
        prev_text = data["message"]
       
    # parent_id = chatbot_officail.parent_id
    pre_conversation_id = chatbot_officail.get_conversations(offset=0, limit=1)
    print(pre_conversation_id[0]['id'])
    # print(chatbot_officail.get_msg_history(
    #     "65b9d8df-ba0a-4712-b673-235704a81349", encoding="utf-8"))
    # chatbot_officail.gen_title(pre_conversation_id, "a3bb0188-133d-40cb-b9e6-6b8f937ac754")
    # print(chatbot_officail.get_conversations()[0])
    # print("prompt:" + PROMPT)
    # if PROMPT.startswith("!"):
    #     if chatbot_commands(PROMPT):
    #         print("continue")
    # response = chatbot.ask(PROMPT)
    # # print("ChatGPT: " + response["choices"][0]["text"])
    # message = response["choices"][0]["text"]
    # message = message.replace("\n\n", "")
    # print(message)
    return {"answers": prev_text, "conversation_id": pre_conversation_id[0]['id']}

@app.route('/', methods=["GET", "POST"])
def default():
      return "hello ,server running"

@app.route("/wx", methods=["GET", "POST"])

def index():
    if request.method == "GET":
        signature = request.args.get('signature')
        timestamp = request.args.get('timestamp')
        nonce = request.args.get('nonce')
        echostr = request.args.get('echostr')
        token = "021d"
        try:
            check_signature(token, signature, timestamp, nonce)
        except InvalidSignatureException:
            # 处理异常情况或忽略
            return "校验失败"
        # 校验成功
        return echostr
    if request.method == "POST":
        xml_str = request.data
        # 解析xml格式数据
        msg = parse_message(xml_str)
        # 1.目标用户信息
        target = msg.target
        # 2.发送用户信息
        source = msg.source
        # 3.消息类型
        msgType = msg.type
        # 4.消息内容
        msgCcontent = msg.content

        print(msgCcontent)

        reply = TextReply()
        reply.source = target
        reply.target = source

        # Start chat
        PROMPT = msgCcontent
        # print("prompt:" + PROMPT)
        if PROMPT.startswith("!"):
            if chatbot_commands(PROMPT):
                print("continue")
        response = chatbot.ask(PROMPT)
        # print("ChatGPT: " + response["choices"][0]["text"])
        logger.info("接收微信消息->\n"+str(msgCcontent))
        # response = requests.post('https://api.openai.com/v1/completions', headers=headers, json=json_data)
        reply.content = response["choices"][0]["text"].strip().replace("\n", "")
        logger.info("返回微信消息->\n"+str(reply.content))
        print(reply.content)
        # 包装成XML格式的数据
        xml = reply.render()
        return xml


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
