from crewai import Agent, Crew, Task, Process
from mcp import StdioServerParameters
from crewai_tools import MCPServerAdapter
import os
from loguru import logger
from datetime import datetime
import time
from models.topic_research_models import WebLink, BlogPostTaskResult, FaqTaskResult
from models.task_models import ResearchSource
from typing import List
from config import llm, SOURCES_RESEARCH_AGENT_CONFIGS, SOURCES_RESEARCH_TASK_CONFIGS
import asyncio
from services.markitdown_service import markdown_converter

server_params = StdioServerParameters(
    command="npm",
    args=["exec", "-y", "@brightdata/mcp"],
    env={
        "API_TOKEN": os.environ.get("BRIGHT_DATA_API_TOKEN"),
        "BROWSER_AUTH": os.environ.get("BRIGHT_DATA_BROWSER_AUTH"),
    },
)

async def run_sources_research_crew(sources: List[ResearchSource]):
    logger.info(f"Running sources research crew for {len(sources)} sources")

    start_time = time.time()
    try:
        with MCPServerAdapter(server_params) as tools:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            logger.info(f"Tools: {tools}")

            web_scraping_tools = [tool for tool in tools if tool.name in ["scrape_as_markdown"]]

            # Web scraping agents
            web_scraper = Agent(
                role=SOURCES_RESEARCH_AGENT_CONFIGS["web_scraper"]["role"],
                goal=SOURCES_RESEARCH_AGENT_CONFIGS["web_scraper"]["goal"],
                backstory=SOURCES_RESEARCH_AGENT_CONFIGS["web_scraper"]["backstory"],
                verbose=True,
                tools=web_scraping_tools,
                llm=llm,
                max_iter=50,
            )

            # Web scraping tasks
            web_scraping_task = Task(
                description=SOURCES_RESEARCH_TASK_CONFIGS["web_scraping"]["description"],
                expected_output=SOURCES_RESEARCH_TASK_CONFIGS["web_scraping"]["expected_output"],
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

            researcher = Agent(
                role=SOURCES_RESEARCH_AGENT_CONFIGS["researcher"]["role"],
                goal=SOURCES_RESEARCH_AGENT_CONFIGS["researcher"]["goal"],
                backstory=SOURCES_RESEARCH_AGENT_CONFIGS["researcher"]["backstory"],
                verbose=True,
                llm=llm,
            )

            content_writer = Agent(
                role=SOURCES_RESEARCH_AGENT_CONFIGS["content_writer"]["role"],
                goal=SOURCES_RESEARCH_AGENT_CONFIGS["content_writer"]["goal"],
                backstory=SOURCES_RESEARCH_AGENT_CONFIGS["content_writer"]["backstory"],
                verbose=True,
                llm=llm,
            )

            # Research and content creation tasks
            research_task = Task(
                description=SOURCES_RESEARCH_TASK_CONFIGS["research_analysis"]["description"],
                expected_output=SOURCES_RESEARCH_TASK_CONFIGS["research_analysis"]["expected_output"],
                agent=researcher,
                max_retries=5,
            )

            content_task = Task(
                description=SOURCES_RESEARCH_TASK_CONFIGS["content_creation"]["description"],
                expected_output=SOURCES_RESEARCH_TASK_CONFIGS["content_creation"]["expected_output"],
                agent=content_writer,
                context=[research_task],
                max_retries=5,
                output_pydantic=BlogPostTaskResult
            )

            faq_task = Task(
                description=SOURCES_RESEARCH_TASK_CONFIGS["faq_generation"]["description"],
                expected_output=SOURCES_RESEARCH_TASK_CONFIGS["faq_generation"]["expected_output"],
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

            scraped_data = []

            links: List[WebLink] = [WebLink(url=source.source_url, title=source.source_url)
                    for source in sources
                    if source.source_type == "URL"]

            logger.info(f"Unique Links Collected: {links}")

            logger.info(f"Running web scraping crew for {len(links)} links")

            # Create tasks for parallel web scraping
            web_scraping_tasks = []
            for link in links:
                web_scraping_tasks.append(
                    web_scraping_crew.kickoff_async(inputs={
                        "url": link.url,
                        "current_time": current_time,
                    })
                )

            # Execute all web scraping tasks in parallel
            web_scraping_results = await asyncio.gather(*web_scraping_tasks)

            # Process results and collect scraped data
            for link, result in zip(links, web_scraping_results):
                logger.info(f"Web scraping crew result for link {link}: {result}")
                scraped_data.append({
                    "url": link.url,
                    "content": result.raw
                })

            logger.info(f"Scraped data: {scraped_data}")

            # Get textual content from sources
            textual_content = ""
            for source in sources:
                if source.source_type == "MANUAL":
                    textual_content += f"\n---\n- {source.source_content}\n---\n"

            logger.info(f"Textual content: {textual_content}")

            file_content = ""
            file_data = []

            if any(source.source_type == "UPLOAD" for source in sources):
                markdown_files = await markdown_converter.convert_urls_to_markdown(
                    [source.source_url for source in sources if source.source_type == "UPLOAD"]
                )
                for url, markdown_content in markdown_files.items():
                    file_content += f"\n---\n- File: {url}\n---\n{markdown_content}\n---\n"
                    file_data.append({
                        "file_name": url,
                        "content": markdown_content
                    })

            logger.info(f"File content: {file_content}")

            research_content_crew_result = await research_content_crew.kickoff_async(inputs={
                "scraped_data": scraped_data,
                "textual_content": textual_content,
                "file_content": file_content,
                "current_time": current_time,
            })

            faq_result = faq_task.output.pydantic.faq
            logger.info(f"FAQ task result: {faq_result}")

            logger.info(f"Research and content creation crew result: {research_content_crew_result}")

            return {
                "blog_post": research_content_crew_result["blog_post"],
                "title": research_content_crew_result["title"],
                "links": [link.model_dump() for link in links],
                "scraped_data": scraped_data,
                "faq": [faq.model_dump() for faq in faq_result],
                "file_data": file_data
            }
    except Exception as e:
        logger.error(f"Error in topic research agent: {e}")
        raise e
    finally:
        logger.info(f"Time taken by topic research agent: {round(time.time() - start_time, 2)} seconds")
