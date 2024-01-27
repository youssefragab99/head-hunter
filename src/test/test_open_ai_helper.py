from open_ai_helper import *

client = Client()

assistants = Assistant()

assistant = assistants.create(assistant_name="test")

print(assistant)

file = File()

test_file = file.create(document_path="files/resume.dox")

print(test_file)

thread = Thread()

response = thread.ask_question(assistant_id=assistant.id, question="how are you")


print(response)
