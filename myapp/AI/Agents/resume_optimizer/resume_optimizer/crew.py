from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from typing import Optional, Dict, Any
from .extractor_tool import ResumeExtractorTool
from dotenv import load_dotenv
import os

load_dotenv()

key = os.getenv('GOOGLE_API_KEY')
llm = LLM(model="gemini/gemini-1.5-flash", api_key=key)

@CrewBase
class ResumeOpt:
    current_dir = os.path.dirname(__file__)
    agents_config = os.path.join(current_dir, 'agents.yaml')
    tasks_config = os.path.join(current_dir, 'tasks.yaml')

    extractor_tool = ResumeExtractorTool()

    def extract_resume_text(self, filepath: Optional[str] = None) -> str:
        return self.extractor_tool._run(filepath=filepath)

    @agent
    def scoring_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['scoring_agent'],
            verbose=False,
            llm=llm
        )

    @agent
    def feedback_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['feedback_agent'],
            verbose=False,
            llm=llm
        )

    def scoring_task(self, input_data: Dict[str, Any]) -> Task:
        return Task(
            config=self.tasks_config['scoring_task'],
            agent=self.scoring_agent(),
            input=input_data
        )


    def feedback_task(self, resume_text: str, job_title: str) -> Task:
        def input_function(scoring_output):
            return {
                "resume_text": resume_text,
                "job_title": job_title,
                "score": scoring_output
            }

        return Task(
            config=self.tasks_config['feedback_task'],
            agent=self.feedback_agent(),
            input=input_function  # Pass function, not dict
        )

    @crew
    def crew(self, filepath: Optional[str] = None, job_title: Optional[str] = "") -> Crew:
        resume_text = self.extract_resume_text(filepath)

        scoring_input = {
            "resume_text": resume_text,
            "job_title": job_title
        }

        scoring = self.scoring_task(input_data=scoring_input)
        feedback = self.feedback_task(resume_text, job_title)

        return Crew(
            agents=[self.scoring_agent(), self.feedback_agent()],
            tasks=[scoring, feedback],
            process=Process.sequential,
            verbose=False
        )
