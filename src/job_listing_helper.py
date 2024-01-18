import json
from dataclasses import dataclass
from dataclasses_json import dataclass_json

from open_ai_helper import (
    Assistant,
    AssistantDocs,
    Client,
    Document,
    Thread,
    ask_question,
    view_message,
)


class JobListingHelper:
    def __init__(self, resume_path: str, listing_path: str, output_path: str = None):
        self.openai_client = Client()
        self.thread = Thread(self.openai_client)
        self.output_path = output_path

        docs_dict = {"resume": resume_path, "job_listing": listing_path}

        self.assistant_docs = AssistantDocs(self.openai_client, files=docs_dict)

        self.assistant = Assistant(
            self.openai_client,
            document_ids=[
                self.assistant_docs.resume.document.id,
                self.assistant_docs.job_listing.document.id,
            ],
            assistant_name="Job Listing Assistant",
        )

    def extract_job_info(self):
        thread = self.thread.thread

        job_title_response = ask_question(
            client=self.openai_client,
            thread_id=thread.id,
            assistant_id=self.assistant.assistant.id,
            question="What is the job title for the job description provided?",
            document_ids=[self.assistant_docs.job_listing.document.id],
            one_word_answer=True,
        )

        print(job_title_response)

        job_location_response = ask_question(
            client=self.openai_client,
            thread_id=thread.id,
            assistant_id=self.assistant.assistant.id,
            question="What is the job location for the job description provided?",
            document_ids=[self.assistant_docs.job_listing.document.id],
            one_word_answer=True,
        )

        print(job_location_response)

        return job_title_response, job_location_response

    def process_listing(self):
        title_info, location_info = self.extract_job_info()

        response_dict = {"title": title_info, "location": location_info}

        try:
            with open(f"{self.output_path}/test_output.json", "w") as f:
                json.dump(response_dict, f, indent=4)
        except FileNotFoundError:
            print("Output file not found, creating file")
            with open(f"{self.output_path}/test_output.json", "x") as f:
                json.dump(response_dict, f, indent=4)


if __name__ == "__main__":
    job_listing_helper = JobListingHelper(
        resume_path="files/resume.docx",
        listing_path="files/job_listing.pdf",
        output_path="files/test_output",
    )

    job_listing_helper.process_listing()
