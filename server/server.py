import os
import openai
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

OPEN_AI_KEY = os.getenv('OPEN_AI_KEY')
MAX_TOKENS = os.getenv('MAX_TOKENS')
TEMPRATURE = float(os.getenv('TEMPRATURE'))
MODEL = (os.getenv('MODEL') or "text-davinci-002")
base_prompt = (os.getenv("CUSTOM_BASE_PROMPT")
               or "You are ChatGPT, a large language model trained by OpenAI. You answer as concisely as possible for each response (e.g. Don't be verbose).\n")
if not OPEN_AI_KEY:
    print("Please add your OPEN AI KEY in .env")
    quit(0)

app = Flask(__name__)
# chatbot = Chatbot(api_key=OPEN_AI_KEY,
#                   temprature=TEMPRATURE, base_prompt=base_prompt, model=MODEL)
chatbot_officail = Chatbot(config={
    "session_token": "eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..c59rcjs69PLjoM7u.zPvTzuzkd72-OZmHoHCAGoLOgPFbqyla1rgZ3V4kLZ_j1Op5gLUBcs1VXIldkQMySUc9WgJJVyYPE1SdpptfdiqvghZIB13iKntIXjGOQ-l1oq64JA5-8FkmdoZrp1uHikem03qRBa5Zf7_4VnuZ_CwRqLGw8XSEX5QSg9y7vBtvoT0VUylQUKDUDXQGKGZ2cHmh7mzjxszzIVNkL38-BSiP-RtgGIg1kcqux42XLfh8MPR7jTGdtKRFMH0qKN3-D85x77cyYgTwiKpOtp7RrcqAlL6wBBHJr86LQgoMtIYZQxewC179DAXgcWZfvAuQK9IaMZPfK4-kr7y6IMFyGdQOdLQHTfMdQdv_rV8ylEApXs-zNz6Px2x8bMRvrTMfLcb6X2DzIEGNsRSXRdjIa6ks7hisHFnhYq-TMVS24axNXkqBGWJ64qlXoJhoMhi_nN4vGzIvTXh0DCfz-YbwX_eg1VcvrKiPe6FsDyV3w6Q1nmTfmT4olPe3gPxuJCvLmO4EZwtP7n7mbRizO1_59k2DtwKW41__IXoKHPvYOJntOeIhBZC6KzIOraAnx8E3LdidLQyVTI37nLUTyDQJfVn_c4OseBTbYaQaNI8QjWHDbvCEtUkyso5gDYx7-J2csqIOgz5UGwSjcYVodcw0eiUccfYdoXa16ksW1E_UTJ_5R_J1EkXAy8CsYoYvpf4jQAkQjFUeZFPqSVTUZ6YCzTkGMPn1OVajJZnfKdh-N7SK_g4NgAGBxFIqIvY7uw1saiDxAU0rmPA23GA47m7jSHzt4ilrRrGcLZP_M5PCE6FnSd9hzTHvxPSIhSuNvXAfY48VkOj9ezkzrOM16MlXvU6suBRCdiecYcukSZqHxEUepyDd-IRS0Ux7Ydf01vCU5vaaF2e5QcLHXZ6qCNMCqG9SxYtskDuTF0_YMQWv_A69ygA83V2AILYtcJU7WJd6wXmzRzsdyddslfY5QGTZXcX0PWWDsuh381h72_JDs2bYTiOPWOrFS9pRERlvHi8nHBUQnw7LMOYg3tIdo_-Z3M_Poxb7Q2ZjNn2ZOiTrzEIF7EbtqhEYgSLRVhDnARWsT_VLZlTUp1PNQ7NRFZq8nNJpmeyT-w6yJpOOuM2Jbs1QPhN5GPdaO4qu9W_ytLF7aYEwZtGiLxc6drMbQFl3iLc7qvOPBcicRM8i3zenm6YZPw8PIpiHtuiTCaZKQXRccIZ-zHWYVDu44QLFGbODVQGbWyQ-uCgl7caPw0-ApPdhu4xeAsVEpIHJlS4p45DtKKy-BSUMKt7waitcIy8vh2aZ_mU69N43kXSYuvS_n-CZtBceIbGovVp7eh-TDuWPVIHrv7iW1YNQ4xn3t60w1ysmCWJ3cqN64T4auWOqAdHrebkvUuwn0zAKdHTtAGTkotCGMTdGuxxwQYWv-ltUbByEeyoJVxBlKiE8Z8_WP0a3EziJfF23kUw4cfeHeomgmXf-zuOOiJRi3N4ldaXN4Ra8zyb12m8cfeJEbVjiDzMOMiux0Oo2roWmC8M-G91OkE5DTRL8bhohYqdCRn2ZXmmZP1Vj7mVkTW22qKbEyCkK980NVJz31S90tYrSDzKMfY89Yg_ytDe1tMt9V6Fpug0UeqtEVgoKpR4F76u6oZVpXbK6OXYDkUwE3hH5pWEVeqW9mpgJ49ldBgJ39LRaVgENdBzsqHtuzq4giK5mkJiHsmnCfsmkOttHj7nZuhRXtwKdjHsf7YwyubtgCHvtmQbEVaILV4dfBnS4uuTTlQ52See3-Z1SbK_GG3x__oTNEAcd0L5qIK1YIJwOtJDVw1tA6_qH_WoPFb09SmUFtWqk-renf2O2OgH7hy6I8U9a7Vu6NrSy8pIIhHkheJWI_RMe3mK6Qi9t7JwJyLvqjcK2LHSPwOq7CoPOpgIHW0vO-78gXtcVPlGMYAtfaF4iaW4x8d3Eo6JwuIXDD_Oq83OGjGuvqquhfRS-LylJ7E_ip_vFs6T1_rg3EKQZ2fOtDvi6CWGbeDetSg0RT8yyDnmzng17FqPwaD6oRz12mr8XF0JOiANNJ9Sx8VOUr5PI41ZB9yWuJeeJR3bc1U2Fq2HdX-T5U7xqqBgeIParaJGfdoH1iN8-vQpIA-SdzlCi8Om-KQDuU16Cw2Lg1CvP-sIFI6usN5v19EXq1ixnYRVraDXGFeJVJHkk30-XtOs0j3odt8L68MZKkDi62nGNB9hOmObvjy6M0s0OnuaYbQBddbtkTC5hGXlYGwCAXxRMuD1GMoxdCJ95aScU16DRseOz9fJIA6NhYMgilEPdTl5MLj6q0e0temB3cIcb6C-eDW1SeXnJzHuKQmR-Dj2ec5uQ2hrWLcISBaF0nLqMvbcDF19R-bjC8H2j_6ErGo7dS0gPvN9X6H8Y4IvxKaf6OYR0ELGa3oHR3fGEShzqAXofsDlh6MBFIuMoJqfSw1bODhMxmtu39rujkayIsLFbJ8DO2dNd2edRO4YbZKmOEcFfoAd4FvVcxeyDi46AEusW0IIB_2Cg4VAEnFdnh-J_BtCx_S3GkfPofDUaDbK3v0j24Y_8HU2h25sB-bYLNuWuOuf6fE8zaboknLSrr2JoazVH7EZAoZm-_kZoYPa4S6FchcnB0bxJzjDS-4Vn.-U2k6DPn5KcK21Zrq9Hb3Q",
    # "proxy": "http://127.0.0.1:1087",
    "accept_language": "en-US,en",
    "email": "westman021@qq.com",
    "password": "TlL&=Q;1crK'+J\"U"
})
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

    # Start chat
    PROMPT = user_request
    print("Chatbot: ")
    prev_text = ""
    for data in chatbot_officail.ask(
        PROMPT,
    ):
        message = data["message"][len(prev_text):]
        print(message, end="", flush=True)
        prev_text = data["message"]
    # print("prompt:" + PROMPT)
    # if PROMPT.startswith("!"):
    #     if chatbot_commands(PROMPT):
    #         print("continue")
    # response = chatbot.ask(PROMPT)
    # # print("ChatGPT: " + response["choices"][0]["text"])
    # message = response["choices"][0]["text"]
    # message = message.replace("\n\n", "")
    # print(message)
    return {"answers": prev_text}

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
