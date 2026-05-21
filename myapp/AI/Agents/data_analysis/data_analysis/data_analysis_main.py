import warnings
from myapp.ai.agents.data_analysis.data_analysis.crew import AnalysisAgent
from crewai.tools import tool

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run_data_analysis(query: str, file_path: str):
    """Plain callable for use from ai_gateway."""
    inputs = {"query": query, "file_path": file_path}
    try:
        response = AnalysisAgent().crew().kickoff(inputs=inputs)
        return response.raw
    except Exception as e:
        raise Exception(f"An error occurred while running the data analysis crew: {e}")

@tool
def run_data_analysis_tool(query: str, file_path: str):
    """CrewAI tool version for use in agent tool lists."""
    return run_data_analysis(query, file_path)