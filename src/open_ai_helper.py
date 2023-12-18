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

    def delete_duplicate_assistants(self, assistant_ids: list):
        for assistant_id in assistant_ids:
            self.client.client.beta.assistants.delete(assistant_id=assistant_id)
            print(f"Deleted assistant {assistant_id}")

    def create_assistant(self, assistant_name: str):
        try:
            assistant_list = self.client.client.beta.assistants.list()
            assistant_counter = 0
            id_list = []
            for assistant in assistant_list.data:
                if assistant.name == assistant_name:
                    assistant_counter += 1
                    id_list.append(assistant.id)

            if assistant_counter > 1:
                print(
                    "More than one assistant with the same name, selecting the first one"
                )
                id = id_list[0]
                assistant = self.client.client.beta.assistants.retrieve(assistant_id=id)
                self.delete_duplicate_assistants(assistant_ids=id_list[1:])
            elif assistant_counter == 1:
                print("Assistant found")
                id = id_list[0]
                assistant = self.client.client.beta.assistants.retrieve(assistant_id=id)
            elif assistant_counter == 0:
                print("Assistant not found, creating new assistant")
                assistant = self.client.client.beta.assistants.create(
                    model="gpt-4",
                    name=assistant_name,
                    description="This is my first assistant",
                )

            return assistant

        except Exception as e:
            print("Error while creating assistant")
            print(f"Error: {e}")


# if __name__ == "__main__":
#     client = Client(open_ai_key)

#     assistant = Assistant(client)

#     test_assistant = assistant.create_assistant("test_assistant")

#     print(type(test_assistant))
#     print(test_assistant)


# # Detele all assistants:
# client = Client(open_ai_key)
# assistant = Assistant(client)
# assistant_list = client.client.beta.assistants.list()
# for id in assistant_list.data:
#     assistant.client.client.beta.assistants.delete(assistant_id=id.id)
#     print(f"Deleted assistant {id.id}")