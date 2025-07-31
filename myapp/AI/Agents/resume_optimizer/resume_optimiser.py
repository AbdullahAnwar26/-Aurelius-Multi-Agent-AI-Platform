from .resume_crew import ResumeOpt
from .resume_text_extractor import extract_text
from dotenv import load_dotenv
import os

load_dotenv()

def run(query=None, file_path=None):
    """
    Runs the ResumeOpt crew with a resume file and job title as input.
    """
    if not file_path or not query:
        raise ValueError("Both resume file path and job title (query) are required.")

    resume_text = extract_text(file_path)[:3000]

    inputs = {
        'resume': resume_text,
        'job_title': query,
    }

    print("--- Running Resume Optimization Crew ---")
    result = ResumeOpt().crew().kickoff(inputs=inputs)

    print("\n\n########################")
    print("✅ Resume Feedback Report:")
    print("########################\n")
    print(result)

    return result


if __name__ == "__main__":
    print("===== Resume Optimizer CLI =====")
    print("Type 'exit' at any prompt to quit.\n")