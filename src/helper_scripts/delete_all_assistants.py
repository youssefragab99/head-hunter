from open_ai_helper import Assistant, Client

client = Client().client

assistants = client.beta.assistants.list()

assistant_ids = [assistant.id for assistant in assistants.data]

print(f"Found {len(assistant_ids)} assistants")


for id in assistant_ids:
    print(f"Deleting assistants: {id}")
    client.beta.assistants.delete(id)
