from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from dotenv import load_dotenv

load_dotenv()

llm = LLM(model='gemini/gemini-2.0-flash')

@CrewBase
class ResumeOpt():
    """ResumeOpt crew"""
    agents_config = 'agents.yaml'
    tasks_config = 'tasks.yaml'

    @agent
    def scoring_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['scoring_agent'],
            llm=llm,
            verbose=True
        )

    @agent
    def feedback_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['feedback_agent'],
            llm=llm,
            verbose=True
        )

    @task
    def scoring_task(self) -> Task:
        return Task(
            config=self.tasks_config['scoring_task'],
            agent=self.scoring_agent()
        )

    @task        
    def feedback_task(self) -> Task:
        return Task(
            config=self.tasks_config['feedback_task'],
            agent=self.feedback_agent()
        )

    @crew
    def crew(self) -> Crew:
        """Creates the ResumeOpt crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )