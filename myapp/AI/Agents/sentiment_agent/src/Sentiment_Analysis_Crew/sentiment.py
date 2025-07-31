from .crew import Sentiment_analysis_crew

def run_sentiment_analysis(file_path: str = None, file_type: str = "csv") -> str:
    """
    Run sentiment analysis using the Sentiment_analysis_crew from crewAI.
    Args:
        file_path (str): Path to the reviews file (CSV/JSON).
        file_type (str): 'csv' or 'json'. Default is 'csv'.

    Returns:
        str: Output of the analysis.
    """
    try:
        inputs = {
            "reviews_file": file_path,
            "file_type": file_type,
        }

        result = Sentiment_analysis_crew().crew().kickoff(inputs=inputs)
        return str(result)

    except Exception as e:
        return f"Sentiment analysis failed: {e}"
