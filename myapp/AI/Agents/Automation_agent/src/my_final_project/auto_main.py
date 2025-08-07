import sys
from .crew import AutomationAgent
from datetime import datetime
from crewai.tools import tool


def auto_run(query, file_path=None,csv_file=None):
    """
    Automation agent automaticaclly searches for info and sends email.
    Run the crew.
    """
    inputs = {
        'query': query,
        'file_path':file_path,
        'csv_file':csv_file,
        'date': datetime.now().strftime('%Y-%m-%d')
    }
    AutomationAgent().crew().kickoff(inputs=inputs)





