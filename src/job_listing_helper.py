import json
from dataclasses import dataclass

from dataclasses_json import dataclass_json

from open_ai_helper import Assistant, AssistantDocs, Client, File, Thread

config = {
    "name": "job_listing_assistant",
    "job_description": "",
    "message": "Using the resume provided on file and the job description in this message, write 16 key words or skills to add to an area of expertise section in a new resume. Provide them in bullet point form. "
}


class JobListingHelper:
    def __init__(self, resume_path: str, listing_path: str, output_path: str = None):
        self.openai_client = Client()
        self.thread = Thread()
        self.output_path = output_path

        docs_dict = {"resume": resume_path, "job_listing": listing_path}

        self.assistant_docs = AssistantDocs(files=docs_dict)

        self.assistant = Assistant().create(
            document_ids=[
                self.assistant_docs.resume.id,
                self.assistant_docs.job_listing.id,
            ],
            assistant_name="Job Listing Assistant",
        )

    def extract_job_info(self):
        thread = self.thread.thread

        job_title_response = self.thread.ask_question(
            assistant_id=self.assistant.id,
            question="What is the job title for the job description provided?",
            document_ids=[self.assistant_docs.job_listing.id],
            one_word_answer=True,
        )

        # print(job_title_response)

        job_location_response = self.thread.ask_question(
            assistant_id=self.assistant.id,
            question="What is the job location for the job description provided?",
            document_ids=[self.assistant_docs.job_listing.id],
            one_word_answer=True,
        )

        # print(job_location_response)

        resume_changes = self.thread.ask_question(
            assistant_id=self.assistant.id,
            question=f"Based on the job description in this file {self.assistant_docs.job_listing.id}, \
                what changes would you make to the resume at this location {self.assistant_docs.resume.id}?",
            document_ids=[
                self.assistant_docs.resume.id,
                self.assistant_docs.job_listing.id,
            ],
        )

        cover_letter = self.thread.ask_question(
            assistant_id=self.assistant.id,
            question=f"Using the resume in this file {self.assistant_docs.resume.id}, \
                write a cover letter for the job description in the following file \
                    {self.assistant_docs.job_listing.id}",
            document_ids=[
                self.assistant_docs.resume.id,
                self.assistant_docs.job_listing.id,
            ],
        )

        return {
            "job_title": job_title_response,
            "job_location": job_location_response,
            "resume_changes": resume_changes,
            "cover_letter": cover_letter,
        }

    def process_listing(self):
        job_info = self.extract_job_info()

        try:
            with open(f"{self.output_path}/test_output.json", "w") as f:
                json.dump(job_info, f, indent=4)
        except FileNotFoundError:
            print("Output file not found, creating file")
            with open(f"{self.output_path}/test_output.json", "x") as f:
                json.dump(job_info, f, indent=4)


if __name__ == "__main__":
    job_listing_helper = JobListingHelper(
        resume_path="files/resume.docx",
        listing_path="files/job_listing.pdf",
        output_path="files/test_output",
    )

    job_listing_helper.process_listing()
