from crewai import Agent, Crew, Task, Process
from mcp import StdioServerParameters
from crewai_tools import MCPServerAdapter
import os
from loguru import logger
from datetime import datetime
import time
from models.topic_research_models import WebScrapingPlannerTaskResult, WebScrapingLinkCollectorTaskResult, WebLink, BlogPostTaskResult, FaqTaskResult
from config import llm, TOPIC_RESEARCH_AGENT_CONFIGS, TOPIC_RESEARCH_TASK_CONFIGS
server_params = StdioServerParameters(
    command="npm",
    args=["exec", "-y", "@brightdata/mcp"],
    env={
        "API_TOKEN": os.environ.get("BRIGHT_DATA_API_TOKEN"),
        "BROWSER_AUTH": os.environ.get("BRIGHT_DATA_BROWSER_AUTH"),
    },
)

# Initialize MCPAdapt with CrewAI adapter
async def run_research_crew(topic: str):
    logger.info(f"Running topic research crew for topic: {topic}")

    start_time = time.time()
    try:
        with MCPServerAdapter(server_params) as tools:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            logger.info(f"Tools: {tools}")

            web_scraping_link_collector_tools = [tool for tool in tools if tool.name in ["search_engine"]]

            web_scraping_tools = [tool for tool in tools if tool.name in ["scrape_as_markdown"]]

            # Planning crew agents
            web_scraping_planner = Agent(
                role=TOPIC_RESEARCH_AGENT_CONFIGS["web_scraping_planner"]["role"],
                goal=TOPIC_RESEARCH_AGENT_CONFIGS["web_scraping_planner"]["goal"],
                backstory=TOPIC_RESEARCH_AGENT_CONFIGS["web_scraping_planner"]["backstory"],
                verbose=True,
                llm=llm,
            )

            # Planning crew tasks

            planner_task = Task(
                description=TOPIC_RESEARCH_TASK_CONFIGS["planner"]["description"],
                expected_output=TOPIC_RESEARCH_TASK_CONFIGS["planner"]["expected_output"],
                agent=web_scraping_planner,
                max_retries=5,
                output_pydantic=WebScrapingPlannerTaskResult
            )

            # Planning crew
            planning_crew = Crew(
                agents=[web_scraping_planner],
                tasks=[planner_task],
                verbose=True,
                process=Process.sequential,
                output_log_file=f"logs/planning_crew_{current_time}.log",
                max_rpm=20
            )

            # Web scraping link collector agents
            web_scraping_link_collector = Agent(
                role=TOPIC_RESEARCH_AGENT_CONFIGS["web_scraping_link_collector"]["role"],
                goal=TOPIC_RESEARCH_AGENT_CONFIGS["web_scraping_link_collector"]["goal"],
                backstory=TOPIC_RESEARCH_AGENT_CONFIGS["web_scraping_link_collector"]["backstory"],
                verbose=True,
                tools=web_scraping_link_collector_tools,
                llm=llm,
            )

            # Web scraping link collector tasks
            link_collector_task = Task(
                description=TOPIC_RESEARCH_TASK_CONFIGS["link_collector"]["description"],
                expected_output=TOPIC_RESEARCH_TASK_CONFIGS["link_collector"]["expected_output"],
                agent=web_scraping_link_collector,
                max_retries=5,
                output_pydantic=WebScrapingLinkCollectorTaskResult
            )

            # Web scraping link collector crew
            web_scraping_link_collector_crew = Crew(
                agents=[web_scraping_link_collector],
                tasks=[link_collector_task],
                verbose=True,
                process=Process.sequential,
                output_log_file=f"logs/web_scraping_link_collector_crew_{current_time}.log",
                max_rpm=20
            )

            # Web scraping agents
            web_scraper = Agent(
                role=TOPIC_RESEARCH_AGENT_CONFIGS["web_scraper"]["role"],
                goal=TOPIC_RESEARCH_AGENT_CONFIGS["web_scraper"]["goal"],
                backstory=TOPIC_RESEARCH_AGENT_CONFIGS["web_scraper"]["backstory"],
                verbose=True,
                tools=web_scraping_tools,
                llm=llm,
                max_iter=50,
            )

            # Web scraping tasks
            web_scraping_task = Task(
                description=TOPIC_RESEARCH_TASK_CONFIGS["web_scraping"]["description"],
                expected_output=TOPIC_RESEARCH_TASK_CONFIGS["web_scraping"]["expected_output"],
                agent=web_scraper,
                max_retries=5
            )

            # Web scraping crew
            web_scraping_crew = Crew(
                agents=[web_scraper],
                tasks=[web_scraping_task],
                verbose=True,
                process=Process.sequential,
                output_log_file=f"logs/web_scraping_crew_{current_time}.log",
                max_rpm=20
            )

            # Research and content creation agents
            researcher = Agent(
                role=TOPIC_RESEARCH_AGENT_CONFIGS["researcher"]["role"],
                goal=TOPIC_RESEARCH_AGENT_CONFIGS["researcher"]["goal"],
                backstory=TOPIC_RESEARCH_AGENT_CONFIGS["researcher"]["backstory"],
                verbose=True,
                llm=llm,
            )

            content_writer = Agent(
                role=TOPIC_RESEARCH_AGENT_CONFIGS["content_writer"]["role"],
                goal=TOPIC_RESEARCH_AGENT_CONFIGS["content_writer"]["goal"],
                backstory=TOPIC_RESEARCH_AGENT_CONFIGS["content_writer"]["backstory"],
                verbose=True,
                llm=llm,
            )

            # Research and content creation tasks
            research_task = Task(
                description=TOPIC_RESEARCH_TASK_CONFIGS["research_analysis"]["description"],
                expected_output=TOPIC_RESEARCH_TASK_CONFIGS["research_analysis"]["expected_output"],
                agent=researcher,
                max_retries=5,
            )

            content_task = Task(
                description=TOPIC_RESEARCH_TASK_CONFIGS["content_creation"]["description"],
                expected_output=TOPIC_RESEARCH_TASK_CONFIGS["content_creation"]["expected_output"],
                agent=content_writer,
                context=[research_task],
                max_retries=5,
                output_pydantic=BlogPostTaskResult
            )

            faq_task = Task(
                description=TOPIC_RESEARCH_TASK_CONFIGS["faq_generation"]["description"],
                expected_output=TOPIC_RESEARCH_TASK_CONFIGS["faq_generation"]["expected_output"],
                agent=researcher,
                context=[research_task],
                max_retries=5,
                output_pydantic=FaqTaskResult
            )

            # Research and content creation crew
            research_content_crew = Crew(
                agents=[researcher, content_writer],
                tasks=[research_task, faq_task, content_task],
                verbose=True,
                process=Process.sequential,
                output_log_file=f"logs/research_content_crew_{current_time}.log",
                max_rpm=20
            )

            planning_crew_result = await planning_crew.kickoff_async(inputs={
                "topic": topic,
                "current_time": current_time
            })
    except Exception as e:
        logger.error(f"Error in topic research agent: {e}")
        raise e
    finally:
        logger.info(f"Time taken by topic research agent: {round(time.time() - start_time, 2)} seconds")

