import yaml
from openai import OpenAI

with open("keys.yaml", "r") as f:
    open_ai_key = yaml.load(f, Loader=yaml.FullLoader)["open_ai_key"]


class Client:
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)


class Assistant:
    def __init__(self, client):
        self.client = client

    def delete_duplicate_assistants(self, assistant_ids: list):
        """delete_duplicate_assistants deletes all assistants in the list except the first one

        If there are more than one assistant with the same name, this function will delete all of them except the first one

        Parameters
        ----------
        assistant_ids : list
            List of assistant ids to be deleted
        """
        for assistant_id in assistant_ids:
            self.client.client.beta.assistants.delete(assistant_id=assistant_id)
            print(f"Deleted assistant {assistant_id}")

    def create_assistant(
        self, assistant_name: str, instructions: str = None, tools: list = None
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
                    instructions=instructions,
                )
            return assistant

        except Exception as e:
            print("Error while creating assistant")
            print(f"Error: {e}")

    def delete_assistant(self, assistant_id: str):
        """delete_assistant deletes the assistant with the given id

        Delete the assistant with the given id

        Parameters
        ----------
        assistant_id : str
            Assistant id to be deleted
        """
        try:
            self.client.client.beta.assistants.delete(assistant_id=assistant_id)
            print(f"Assistant deleted successfully: {assistant_id}")
        except Exception as e:
            print("Error while deleting assistant, assistant not found")
            print(f"Error: {e}")


class Document:
    def __init__(self, client):
        self.client = client

    def upload_document_file(self, file_path: str, purpose: str = "assistants"):
        """upload_document_file uploads the document file

        Uploads the document file to the assistant object

        Parameters
        ----------
        file_path : str
            Document file local path to upload
        purpose : str, optional
            Purpose required by the openai api, by default "assistants"

        Returns
        -------
        'openai.types.file_object.FileObject
            File object for the document
        """
        try:
            document = self.client.client.files.create(
                file=open(file_path, "rb"), purpose=purpose
            )
            print("Document file uploaded successfully")
            return document
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


class Thread:
    def __init__(self, client):
        self.client = client
        self.assistant = Assistant(client).create_assistant(assistant_name="test")
        self.document = Document(client)
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
            self.document.upload_document_file(
                file_path=document_path, purpose="assistants"
            )
        except Exception as e:
            print("Error while uploading document file")
            print(f"Error: {repr(e)}")

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
            content="Reply by saying good night",
        )

        all_messages = client.client.beta.threads.messages.list(
            thread_id=self.thread.id
        )

        print(summary)
        print(all_messages)
        print(type(all_messages))

        self.document.delete_file(file_id=file_id)

    def run_thread(self, thread, assistant):
        run = client.client.beta.threads.runs.create(
            thread_id=thread.id, assistant_id=assistant.id
        )

        return run.id

    def view_run(self, thread_id: str, run_id: str):
        run = client.client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run)
        print(run)
        return run


if __name__ == "__main__":
    client = Client(open_ai_key)
    thread = Thread(client)
    # thread.summarize_document(document_path="files/resume.docx")

    run_id = thread.run_thread(thread=thread.thread, assistant=thread.assistant)

    thread.view_run(thread_id=thread.thread.id, run_id=run_id)

# run_4MZiplCyhGDraoD5mKeskrT1
