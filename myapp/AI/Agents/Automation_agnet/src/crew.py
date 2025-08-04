from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
# from crewai.tools import SerperDevTool
from pydantic import BaseModel, Field
from typing import List, Dict
from datetime import datetime
from .tools.email import send_email_smtp



class ResearchPoint(BaseModel):
    topic: str = Field(description="The main topic in query or area being discussed")
    findings: str = Field(description="The key findings or insights about this topic topic in query")
    relevance: str = Field(description="Why this finding is relevant or important")
    sources: List[Dict[str, str]] = Field(
        description="Sources with title and URL for each finding",
        default_factory=list
    )

class ResearchOutput(BaseModel):
    research_points: List[ResearchPoint] = Field(description="List of research findings")
    summary: str = Field(description="Brief summary of overall findings")

class ExecutiveReportSection(BaseModel):
    section_title: str = Field(description="Section title")
    section_content: str = Field(description="Main content of the section")
    key_insights: List[str] = Field(description="Key insights from this section")
    recommendations: List[str] = Field(
        default_factory=list,
        description="Optional recommendations based on findings"
    )
    sources: List[Dict[str, str]] = Field(
        description="Sources with title and URL for this section",
        default_factory=list
    )

class ExecutiveReport(BaseModel):
    report_title: str = Field(description="Title of the report")
    generation_date: str = Field(description="Report generation date")
    executive_summary: str = Field(description="A concise executive summary")
    key_findings: List[Dict[str, str]] = Field(
        description="List of key findings with their sources",
        default_factory=list
    )
    report_sections: List[ExecutiveReportSection] = Field(
        description="Detailed report sections"
    )
    next_steps: List[str] = Field(description="Recommended next steps")
    sources: List[Dict[str, str]] = Field(
        description="All sources used in the report",
        default_factory=list
    )
	
@CrewBase
class AutomationAgent():
    """AutomationAgent crew"""
    
    @agent
    def researcher(self) -> Agent:
        """        Researcher agent to uncover cutting-edge developments on a given topic.
        """
        return Agent(
            config=self.agents_config['researcher'],
            verbose=False,
            # tools=[SerperDevTool()],
        )

    @agent
    def reporting_analyst(self) -> Agent:
        """Reporting Analyst agent to create detailed reports based on research findings.
          Reporting Analyst agent to create detailed reports based on research findings."""
        return Agent(
            config=self.agents_config['reporting_analyst'],
            verbose=False
        )
    @agent
    def formatter(self) -> Agent:
        """ Formatter agent to format the report and prepare it for email if email adress is provided in query."""
        return Agent(
            config=self.agents_config['formatter'],
            verbose=False
       )
    @agent
    def email_assistant(self) -> Agent:
        """Email Assistant agent to send emails with the report and attachments."""
        return Agent(
            config=self.agents_config['email_assistant'],
            tools=[send_email_smtp],
            verbose=False
        )
   
    @task
    def research_task(self) -> Task:
        """Task to perform research on a given topic."""
        return Task(
            config=self.tasks_config['research_task'],
            output_json=ResearchOutput
        )

    @task
    def reporting_task(self) -> Task:
        """Task to create an executive report based on research findings."""
        return Task(
            config=self.tasks_config['reporting_task'],
            output_pydantic=ExecutiveReport
        )

    @task
    def formatting_task(self) -> Task:
        """Task to format the report and prepare it for email."""
        return Task(
            config=self.tasks_config['formatting_task']
        )

    @task
    def send_email_task(self) -> Task:
        """Task to send an email with the report and attachments."""
        return Task(
            config=self.tasks_config['send_email_task']
        )

    @crew
    def crew(self) -> Crew:
        """AutomationAgent crew fint agents and tasks to perform research, create reports, format them, and send emails. dont use other agents or tasks if not required in query ."""
        return Crew(
            agents=self.agents, 
            tasks=self.tasks,
            process=Process.sequential,
            verbose=False,
        )