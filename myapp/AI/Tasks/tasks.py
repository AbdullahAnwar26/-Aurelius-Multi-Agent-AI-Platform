from crewai import Task, Agent
from Agents.Qna_Agent.qna_agent import sample_qna_agent
from Agents.Sentiment_Agent.sentiment_agent import sample_sentiment_agent
from Agents.data_analysis.data_analysis_agent import sample_data_analysis_agent_response
from Agents.stock_agent.Stock import get_sample_stock_data
from Agents.RAG_researcher.AI_research import sample_rag_researcher
from Agents.Automation_agent.automation_agent import generate_draft_with_optional_file

# Wrapping sample functions inside Agent objects
qna_agent_wrapper = Agent(
    role="QnA Agent",
    goal="Answer user queries using the sample function.",
    backstory="This agent wraps the sample_qna_agent() function for testing.",
    verbose=True,
    allow_delegation=False
)

sentiment_agent_wrapper = Agent(
    role="Sentiment Agent",
    goal="Analyze sentiment using a static function.",
    backstory="Wraps sample_sentiment_agent() function.",
    verbose=True
)

data_analysis_agent_wrapper = Agent(
    role="Data Analysis Agent",
    goal="Performs mock data analysis.",
    backstory="Wraps sample_data_analysis_agent_response().",
    verbose=True
)

stock_agent_wrapper = Agent(
    role="Stock Comparison Agent",
    goal="Simulate stock comparison and generate investment report.",
    backstory="Wraps get_sample_stock_data().",
    verbose=True
)

rag_agent_wrapper = Agent(
    role="RAG Research Agent",
    goal="Provide mock RAG-based answers.",
    backstory="Wraps sample_rag_researcher().",
    verbose=True
)

report_email_agent_wrapper = Agent(
    role="Report + Email Agent",
    goal="Generate report and simulate email sending.",
    backstory="Wraps generate_draft_with_optional_file().",
    verbose=True
)

# Sample task using QnA Agent
task1 = Task(
    agent=qna_agent_wrapper,
    description="""The QnA Agent handles user questions by intelligently deciding when to use real-time web search tools and when to rely on internal knowledge.
                   It ensures high response quality and factual accuracy for both static and dynamic queries.""",
    expected_output="A well-structured text response that directly answers the user's query with appropriate context."
)

# Add more tasks as needed
def list_of_tasks():
    return [task1,]
