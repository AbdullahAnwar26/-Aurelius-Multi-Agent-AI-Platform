#!/usr/bin/env python
import sys
import os
from myapp.AI.Agents.sentiment_agent.src.Sentiment_Analysis_Crew.crew import Sentiment_analysis_crew

def run(query, file_path=None):
    """
    Run the sentiment analysis crew with either a text input or a review file.
    """
    inputs = {}

    if file_path and os.path.exists(file_path):
        # Try to infer file type
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".json":
            file_type = "json"
        elif ext == ".csv":
            file_type = "csv"
        elif ext == ".txt":
            file_type = "text"
        else:
            return {"error": f"Unsupported file format: {ext}"}

        inputs = {
            "reviews_file": file_path,
            "file_type": file_type
        }
    elif query:
        inputs = {
            "text_input": query,
            "file_type": "text"
        }
    else:
        return {"error": "No valid input provided. Pass a text query or a review file."}

    try:
        result = Sentiment_analysis_crew().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        return {"error": f"Sentiment analysis failed: {str(e)}"}


# def train():
#     inputs = {
#         "reviews_file": "dummy_Data/Reviews.json",
#         "file_type": "json",
#     }

#     try:
#         Sentiment_analysis_crew().crew().train(
#             n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs
#         )
#     except Exception as e:
#         raise Exception(f"An error occurred while training the crew: {e}")


# def replay():
#     try:
#         Sentiment_analysis_crew().crew().replay(task_id=sys.argv[1])
#     except Exception as e:
#         raise Exception(f"An error occurred while replaying the crew: {e}")


# def test():
#     inputs = {}
#     try:
#         Sentiment_analysis_crew().crew().test(
#             n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs
#         )
#     except Exception as e:
#         raise Exception(f"An error occurred while testing the crew: {e}")


# if __name__ == "__main__":
#     if len(sys.argv) < 2:
#         print("Usage: main.py <command> [<args>]")
#         sys.exit(1)

#     command = sys.argv[1]
#     if command == "run":
#         run("This is a test input.")
#     elif command == "train":
#         train()
#     elif command == "replay":
#         replay()
#     elif command == "test":
#         test()
#     else:
#         print(f"Unknown command: {command}")
#         sys.exit(1)
