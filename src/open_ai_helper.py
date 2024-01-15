import time

import yaml
from openai import OpenAI


class Client:
    def __init__(self):
        with open("keys.yaml", "r") as f:
            self.api_key = yaml.load(f, Loader=yaml.FullLoader)["open_ai_key"]
        self.client = OpenAI(api_key=self.api_key)

def delete_assistant(client, assistant_id: list):
        """delete_assistant deletes the assistant with the given id

        Delete the assistant with the given id

        Parameters
        ----------
        assistant_id : str
            Assistant id to be deleted
        """
        try:
            for assistant_id in assistant_id:
                client.client.beta.assistants.delete(assistant_id=assistant_id)
            print(f"Assistant deleted successfully: {assistant_id}")
        except Exception as e:
            print("Error while deleting assistant, assistant not found")
            print(f"Error: {e}")
            
def create_assistant(
        client,
        document,
        assistant_name: str,
        instructions: str = None,
        tools: list = None,
    ):
        """create_assistant creates an assistant with the given name

        Create an assistant with the name provided

        Parameters
        ----------
        assistant_name : str
            Name of the assistant to be created
        instructions : str, optional
            Any specific instructions to be provided for the assistant, by default None
        tools : list, optional
            Tools the assistant can use, by default None

        Returns
        -------
        openai.types.beta.assistant.Assistant
            Assistant object

        """
        document = document
        document_ids = [document.document.id]

        try:
            assistant_list = client.client.beta.assistants.list()
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
                assistant = client.client.beta.assistants.retrieve(assistant_id=id)
                delete_assistant(client=client, assistant_ids=id_list[1:])
            elif assistant_counter == 1:
                print("Assistant found")
                id = id_list[0]
                assistant = client.client.beta.assistants.retrieve(assistant_id=id)
            elif assistant_counter == 0:
                print("Assistant not found, creating new assistant")
                assistant = client.client.beta.assistants.create(
                    model="gpt-4-1106-preview",
                    name=assistant_name,
                    description="This is my first assistant",
                    instructions=instructions,
                    file_ids=document_ids,
                    tools=[{"type": "retrieval"}],
                )
            print(assistant)
            return assistant

        except Exception as e:
            print("Error while creating assistant")
            print(f"Error: {e}")

            


class Assistant:
    def __init__(self, client,
                 document_path: str = None,
                 assistant_name: str = None):
        self.client = client
        self.document = Document(client, document_path=document_path)
        self.document_path = document_path
        self.assistant = create_assistant(client=client, document=self.document, assistant_name="test_assistant")



class Document:
    def __init__(self, client, document_path: str = None):
        self.client = client
        self.document_path = document_path
        
        try:
            self.document = client.client.files.create(
            file=open(document_path, "rb"), purpose="assistants"
        )
        except Exception as e:
            print("Error while uploading document file")
            print(f"Error: {e}")

    def view_files(self, purpose: str = "assistants"):
        """view_files returns the list of files uploaded to the assistant

        Function to view the list of files uploaded to the assistant

        Parameters
        ----------
        purpose : str, optional
            Search term for the files uploaded to the openai account. If looking for
            files uploaded to the assistant set default to 'assistants', by default assistants

        Returns
        -------
        openai.types.file_object.FileObject
            File object for the document
        """
        files = self.client.client.files.list(purpose=purpose)
        return files

    def delete_file(self, file_id: str):
        """delete_file Delete file after use

        Deletes file uploaded to the openai account

        Parameters
        ----------
        file_id : str
            File id of the file to be deleted
        """
        try:
            self.client.client.files.delete(file_id=file_id)
            print(f"File deleted successfully: {file_id}")
        except Exception as e:
            print("Error while deleting file, file not found")
            print(f"Error: {e}")

    def delete_all_files(self):
        """delete_all_files Delete all files

        Deletes all files uploaded to the openai account
        """
        try:
            files = self.view_files()
            if len(files.data) == 0:
                print("No files found")
                return None
            print(f"Found {len(files.data)} files")
            for file in files.data:
                self.delete_file(file_id=file.id)
        except Exception as e:
            print("Error while deleting files")
            print(f"Error: {e}")


class Thread:
    def __init__(self, client):
        self.client = client
        self.assistant = Assistant(client, document_path="files/resume.docx")
        self.document = self.assistant.document
        self.thread = client.client.beta.threads.create()

    def summarize_document(self, document_path: str):
        """summarize_document Summarize the document

        Ask chatgpt to read and summarize a document to use it as a reference

        Parameters
        ----------
        document_path : str
            Document path
        """

        try:
            file_id = self.document.view_files().data[0].id
            print(f"File id: {file_id}")
        except Exception as e:
            file_id = None
            print("Error while reading resume file id")
            print(f"Error: {repr(e)}")

        summary = client.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content="What is the summary of the document?",
        )

        all_messages = self.client.client.beta.threads.messages.list(
            thread_id=self.thread.id
        )

        print(summary)
        print(all_messages)

        run = self.run_thread(thread=self.thread, assistant=self.assistant)

        self.view_run(thread_id=self.thread.id, run_id=run)

        self.check_for_message(thread_id=self.thread.id)

        self.document.delete_file(file_id=file_id)

    def run_thread(self, thread, assistant):
        run = self.client.client.beta.threads.runs.create(
            thread_id=thread.id, assistant_id=assistant.assistant.id
        )

        print(run)
        return run.id

    def view_run(self, thread_id: str, run_id: str):
        """view_run View a run

        View a run when it is completed

        Parameters
        ----------
        thread_id : str
            Thread ID for the run
        run_id : str
            Run ID

        Returns
        -------
        openai.types.beta.threads.run.Run
            Run object
        """
        completed = False
        while completed == False:
            run = self.client.client.beta.threads.runs.retrieve(
                thread_id=thread_id, run_id=run_id
            )

            if run.status == "completed":
                completed = True
            else:
                print("Run not completed yet")
                time.sleep(5)

        return run

    def check_for_message(self, thread_id: str):
        """check_for_message Check for messages

        Check for messages in a thread

        Parameters
        ----------
        thread_id : str
            Thread ID
        """
        messages = self.client.client.beta.threads.messages.list(thread_id=thread_id)
        print(messages)

    def view_thread(self, thread_id: str):
        while True:
            thread = self.client.client.beta.threads.retrieve(thread_id=thread_id)
            self.view_messages(thread_id=thread_id)
            print(thread)
            time.sleep(5)

    def view_messages(self, thread_id: str):
        messages = self.client.client.beta.threads.messages.list(thread_id=thread_id)
        print(messages)


if __name__ == "__main__":
    client = Client()
    thread = Thread(client)
    thread.summarize_document(document_path="files/resume.docx")
