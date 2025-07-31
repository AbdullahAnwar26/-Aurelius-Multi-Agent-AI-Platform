from crewai import LLM, Task, Crew, Agent
from myapp.AI.Agents.Qna_Agent.qna_agent import qna_agent
from dotenv import load_dotenv
import os

load_dotenv()

rootkey  = os.getenv('GOOGLE_API_KEY')
rootllm = LLM(model= "gemini/gemini-2.0-flash", api_key=rootkey)

def manager_agent_function(query,file_path = None):
    manager_agent = Agent(llm=rootllm,
                    backstory="""You are the lead coordinator. You don't solve the problem directly, but you know which specialized crew to call.""",
                    role="Orchestrator",
                    tools=[qna_agent,],
                    goal="Understand complex user queries and decide which crew(s) to route them to.")

    managertask = Task(agent=manager_agent,
                    description=f"""For query = {query},
                    User query: {query}    
                    Instructions:
                    1. Break query into parts if needed
                    2. Route each part to the correct specialized crew
                    3. Compose and return the final answer
                    """,
                    expected_output="Final structured answer"
                    )
    crew = Crew(agents=[manager_agent,],
                tasks=[managertask],
                manager_agent=manager_agent,
                manager_llm=rootllm,                
                )
    response = crew.kickoff(inputs={"query": query})
    return response
    
# while True:
#     query = input("Enter your demands: ")
#     if query.lower() in ["exit", "quit", "bye"]:
#         break
#     result = manager_agent_function(query=query) 
# #     print(result)