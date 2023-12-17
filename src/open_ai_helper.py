import os

import yaml
from openai import OpenAI

with open("keys.yaml", "r") as f:
    open_ai_key = yaml.load(f, Loader=yaml.FullLoader)["open_ai_key"]
os.environ["OPENAI_API_KEY"] = ""


class Client:
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)


class Assistant:
    def __init__(self, client):
        self.client = client 
        
    def retrieve_client(self)


# if __name__ == "__main__":
#     open_ai_helper = OpenAiHelper(api_key=open_ai_key)
#     question = "What is the capital of Italy?"
#     context = "Rome is the capital of Italy."
#     answer = open_ai_helper.get_answer(question, context)
#     print(answer)
