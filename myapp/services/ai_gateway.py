from myapp.ai import main  # Root agent
from datetime import datetime
import os

def call_ai_agent(agent_type, query, file_path=None, csv_file=None):
    if agent_type == "qna":
        from myapp.ai.agents.qna_agent.qna_user_agent import run_qna
        return run_qna(query)

    elif agent_type == "data":
        from myapp.ai.agents.data_analysis.data_analysis.data_analysis_main import run_data_analysis
        return run_data_analysis(query, file_path)

    elif agent_type == "talent":
        from myapp.ai.agents.talent_sourcing1.talent_main import run_recruitment_crew
        return run_recruitment_crew(query)

    elif agent_type == "stock":
        from myapp.ai.agents.stock_agent.src.new_decision_support.stock_main import run_stock
        return run_stock(query)

    elif agent_type == "resume":
        try:
            from myapp.ai.agents.resume_optimizer.resume_optimizer.resume_opt_agent import (
                ResumeOpt,
                run_resume_opt,
                extract_text
            )

            # Extract resume and JD text (JD can be a string or a file path)
            resume_text = extract_text(file_path)[:3000]
            jd_text = extract_text(query)[:3000] if os.path.isfile(query) else query[:3000]

            # Option 2: Manual crew (switch if needed)
            result = ResumeOpt().crew().kickoff(inputs={
                'resume': resume_text,
                'job_description': jd_text
            })

            return result

        except Exception as e:
            return f"Error in Resume Agent: {str(e)}"

    elif agent_type == "sentiment":
        from myapp.ai.agents.sentiment_analysis.sentiment_tool import run_sentiment
        return run_sentiment.func(f"file_path={file_path}, csv_file={csv_file}")

    elif agent_type == "auto":
        from myapp.ai.agents.automation_agent2.src.automation.main import auto_run
        return auto_run(query=query, file_path=file_path, csv_file=csv_file)

    elif agent_type == "rag":
        from myapp.ai.agents.rag_researcher.rag_researcher.src.research import rag_main
        return rag_main.rag_run(query, file_path)

    elif agent_type == "root":
        from myapp.ai import main
        return main.manager_agent_function(query=query, file=file_path)

    else:
        return {"error": "Invalid agent_type"}
