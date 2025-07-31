from myapp.AI.Agents.Qna_Agent import qna_agent
from myapp.AI.Agents.data_analysis import data_analysis_agent
from myapp.AI.Agents.talent_sourcing import talent_sourcing
from myapp.AI.Agents.stock_agent import Stock
from myapp.AI.Agents.resume_optimizer import resume_optimiser
from myapp.AI.Agents.sentiment_agent.src.Sentiment_Analysis_Crew.sentiment import run_sentiment_analysis
from myapp.AI.Agents.Automation_agnet.src import auto_main
from myapp.AI.Agents.RAG_researcher import AI_research
from myapp.AI import main  # Root agent
from datetime import datetime

def call_ai_agent(agent_type, query, file_path=None, csv_file=None):
    if agent_type == "qna":
        return qna_agent.qna_agent(query)
    elif agent_type == "data":
        return data_analysis_agent.sample_data_analysis_agent_response(query)
    elif agent_type == "talent":
        return talent_sourcing.getDetails(query)
    elif agent_type == "stock":
        return Stock.get_sample_stock_data(query)
    elif agent_type == "resume":
        return resume_optimiser.run(query, file_path)
    elif agent_type == "sentiment":
        return run_sentiment_analysis(query)
    elif agent_type == "auto":
        return auto_main.auto_run(query=query, file_path=file_path, csv_file=csv_file)
    elif agent_type == "rag":
        return AI_research.sample_rag_researcher(query, file_path)
    elif agent_type == "root":
        return main.manager_agent_function(query, file_path)
    else:
        return "Invalid agent_type"


