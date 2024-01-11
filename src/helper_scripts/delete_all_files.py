from open_ai_helper import Client, Document

client = Client()

document = Document(client)

document.delete_all_files()

