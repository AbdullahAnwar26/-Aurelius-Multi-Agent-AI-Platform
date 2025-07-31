from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from crewai_tools import (
    CSVSearchTool,
    JSONSearchTool,
    TXTSearchTool,
    DOCXSearchTool,
    PDFSearchTool,
)

tool_config = dict(
    llm=dict(
        provider="google",
        config=dict(
            model="gemini-2.0-flash-lite",
        ),
    ),
    embedder=dict(
        provider="google",
        config=dict(
            model="models/embedding-001",
            task_type="retrieval_document",
        ),
    ),
)


@CrewBase
class Sentiment_analysis_crew:
    """Sentiment Analysi crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def fileloader(self) -> Agent:
        return Agent(
            config=self.agents_config["fileloader"],  # type: ignore
            tools=[
                CSVSearchTool(config=tool_config),
                JSONSearchTool(config=tool_config),
                DOCXSearchTool(config=tool_config),
                PDFSearchTool(config=tool_config),
                TXTSearchTool(config=tool_config),
            ],
            verbose=True,
        )

    @agent
    def sentiment_emotion_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config["sentiment_emotion_analyzer"],  # type: ignore
            tools=[],
        )

    @task
    def load_reviews(self) -> Task:
        return Task(
            config=self.tasks_config["load_reviews"],  # type: ignore
            tools=[],
        )

    @task
    def analyze_sentiment(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_sentiment_and_emotion"],  # type: ignore
            tools=[],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Sentiment_Analysis crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
