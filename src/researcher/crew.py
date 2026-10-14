import os
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from researcher.tools.search_tool import WebSearchTool
from researcher.tools.scraper_tool import PageScraperTool


@CrewBase
class Researcher():
    """Researcher crew coordinating research, reporting, and editorial review."""

    agents: list[BaseAgent]
    tasks: list[Task]

    def _get_llm(self):
        """Initializes Gemini LLM."""
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        return LLM(model="gemini/gemini-2.5-flash", api_key=api_key)

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'],
            tools=[WebSearchTool(), PageScraperTool()],
            llm=self._get_llm(),
            verbose=True
        )

    @agent
    def reporting_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['reporting_analyst'],
            llm=self._get_llm(),
            verbose=True
        )

    @agent
    def fact_checker(self) -> Agent:
        return Agent(
            config=self.agents_config['fact_checker'],
            llm=self._get_llm(),
            verbose=True
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'],
        )

    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_task'],
        )

    @task
    def review_task(self) -> Task:
        return Task(
            config=self.tasks_config['review_task'],
            output_file='reports/latest_report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Researcher crew with sequential orchestration."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
