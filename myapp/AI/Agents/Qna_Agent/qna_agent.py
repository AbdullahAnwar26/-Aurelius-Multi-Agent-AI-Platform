from crewai import Agent,Task,Crew,LLM
from googlesearch import googlesearch
from crewai.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from dotenv import load_dotenv
load_dotenv()
import os
import requests


# @tool
# def search_tool(query:str)->str:
#     """"Use this tool to search the web reagarding the user query ONLY when needed"""    
#     search = DuckDuckGoSearchRun()
#     return search.run(query)  

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

@tool
def search_tool_2(query: str) -> str:
    """Use this tool to search the web regarding the user query ONLY when needed."""
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        return "Missing Google API Key or Custom Search Engine ID in environment."

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,                  #https://cse.google.com/cse?cx=016989684b1e74964
        "cx": GOOGLE_CSE_ID,
        "q": query,
        "num": 5
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        results = response.json()
        output = ""
        for item in results.get("items", []):
            output += f"{item.get('title')}\n{item.get('snippet')}\n{item.get('link')}\n\n"
        return output.strip() or "No search results found."
    except Exception as e:
        return f"Search failed: {str(e)}"

key=os.getenv('GEMINI_API_KEY')
llm = LLM(model= "gemini/gemini-2.0-flash", api_key=key)

chat_memory = []


def qna_agent(user_input:str):
    """Answers the user's query using search tool and LLM"""
    context = "\n".join([f"User: {q}\nAssistant: {a}" for q, a in chat_memory[-5:]])
    
    
    agent1 = Agent(llm=llm,
        tools=[search_tool_2,],
        backstory="""You are a helpful assistant who can answer questions using 
        your knowledge. When you don't know something, you search the web for 
        accurate information.""",
        role="QnA Assistant",
        goal="Answer the query of the user as per your knowledge and use search tool ONLY when needed"
        )
    task = Task(agent=agent1,
                description=f"""{context}
                Answer this user question: {user_input}            
                Instructions:
                1. First try to answer from your knowledge
                2. For context related queries, use context 
                2. If you need more information, use the search tool
                3. Provide a clear, helpful answer
                4. Remember this conversation for context""",
                expected_output="A clear, helpful answer to the user's question")
    
    crew = Crew(agents= [agent1],
                tasks=[task],
                verbose=False,
                memory=False,
                )
    
    
    response=crew.kickoff()
    chat_memory.append((user_input,response))
    return response

# if __name__ == "__main__":
#     while True:
#         query = input("Enter query: ")
#         if query in ["quit", "exit", "bye"]:
#             break    
#         ans = qna_agent(user_input=query)
#         print(ans)
