import sys
from myapp.AI.Agents.Automation_agnet.src import crew
from datetime import datetime

def auto_run(query, file_path=None, csv_file=None):
    inputs = {
        'query': query,
        'file_path': file_path,
        'csv_file': csv_file,
        'date': datetime.now().strftime('%Y-%m-%d')
    }
    crew.AutomationAgent().crew().kickoff(inputs=inputs)



# send an email to sk9893836@gmail.com with subject "Hello" and message "Hope youre doing well



