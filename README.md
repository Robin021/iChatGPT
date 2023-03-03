# ChatGPT Website (Flask)

A quick testing of OpenAI ChatGPT
![screenshot](demo.png)

## BackEnd
run on your local environments

```shell
pip install -r requirements.txt

python server/server.py
```

## Docker
quick start with docker-compose: 

1. copy your env file
` mv env.example .env `
2. change the OPEN_AI_KEY which you need get from OpenAI. Change CUSTOM_BASE_PROMPT which you want the chatGPT act as therole.

```text
OPEN_AI_KEY="sk-xxx"
TEMPRATURE="0.5"
MAX_TOKENS="1024"
CUSTOM_BASE_PROMPT="You are ChatGPT, a large language model trained by OpenAI. You answer as concisely as possible for each response (e.g. Don't be verbose).\n"
```

3. Start service

```shell
docker-compose up -d 
```

## Next steps

1. Add voice recognition
2. Add different prompt 
3.
