import os

import yaml
from openai import OpenAI

with open("keys.yaml", "r") as f:
    open_ai_key = yaml.load(f, Loader=yaml.FullLoader)["open_ai_key"]
os.environ["OPENAI_API_KEY"] = ""


class OpenAiHelper:
    def __init__(self, api_key):
        self.api_key = api_key
        self.open_ai = OpenAI()

    def get_answer(self, question, context):
        # response = self.open_ai.complete(
        #     engine="turbo 3.5",
        #     prompt=f"Q: {question}\nA:",
        #     max_tokens=100,
        #     temperature=0.3,
        #     top_p=1,
        #     frequency_penalty=0,
        #     presence_penalty=0,
        #     stop=["\n"],
        # )
        response = self.open_ai.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"Q: {question}\nA:",
                }
            ],
            model="gpt-3.5-turbo",
        )
        answer = response.choices[0].text.strip()
        return answer


if __name__ == "__main__":
    open_ai_helper = OpenAiHelper(api_key=open_ai_key)
    question = "What is the capital of Italy?"
    context = "Rome is the capital of Italy."
    answer = open_ai_helper.get_answer(question, context)
    print(answer)
