from crewai import Agent, Crew, Task, Process
from loguru import logger
from config import llm
from models.audio_overview_models import AudioOverviewTranscript
from services.qdrant_service import qdrant_service

def get_audio_overview_crew():
  # Define Agents
  research_analyst = Agent(
    name="Research Analyst",
    role="Content Analyst",
    goal="Extract and organize key insights from research content into a clear, structured summary",
    backstory="You are an expert research analyst who excels at distilling complex information into clear, actionable summaries while maintaining accuracy.",
    llm=llm,
    verbose=True
  )

  conversation_planner = Agent(
    name="Conversation Planner",
    role="Podcast Producer",
    goal="Structure research insights into an engaging podcast conversation outline",
    backstory="You are a podcast producer who specializes in transforming complex topics into natural, flowing conversations that educate and engage.",
    llm=llm,
    verbose=True
  )

  script_writer = Agent(
    name="Script Writer",
    role="Podcast Scriptwriter",
    goal="Write natural podcast dialogue that effectively communicates research insights",
    backstory="You are a scriptwriter who excels at crafting authentic podcast conversations that balance education with entertainment.",
    llm=llm,
    verbose=True
  )

  # Tasks
  analyze_research_task = Task(
    description="""
    Create a structured bullet-point summary of the research content that:
    - Identifies main themes and key insights
    - Highlights important supporting details
    - Maintains factual accuracy
    - Organizes points logically

    Research Content:
    ```
    {research}
    ```
    """,
    expected_output="A structured bullet-point summary of key research insights.",
    agent=research_analyst
  )

  create_conversation_outline_task = Task(
    description=f"""
    Create a comprehensive but concise podcast conversation outline between Michael (host) and Sarah (expert) that:
    - Starts with a brief welcome to "The Synapse Podcast" (1-2 sentences)
    - Covers all major insights and key findings from the research analysis above
    - Organizes points in a logical flow with clear transitions
    - Balances thoroughness with brevity (aim for 4-5 minutes total)
    - Focuses on substance over style - prioritize important content
    - Indicates where to include examples or elaboration without writing full dialogue

    Use the bullet-point summary from the research analysis task above.
    Create an outline/structure only, not a complete transcript.
    The goal is to capture all important points while keeping the format high-level.
    """,
    expected_output="A thorough conversation outline covering all key research points.",
    agent=conversation_planner,
    context=[analyze_research_task]
  )

  write_podcast_script_task = Task(
    description=f"""
    Write a 4-5 minute podcast conversation between Michael and Sarah that follows the outline from the previous task.
    The conversation should:
    - Opens with Michael's welcome to "The Synapse Podcast"
    - Uses casual, natural dialogue
    - Incorporates research points conversationally
    - Includes authentic reactions and interjections
    - Maintains engaging but focused discussion
    - Stays between 800-1000 words
    - Ensures comprehensive coverage of key insights
    - Allows time for proper explanation of complex topics
    - Includes meaningful back-and-forth discussion

    Use the outline from the previous task as the structure and flow for the conversation.
    Follow the outline's sequence of topics and key points while making the dialogue natural.

    Format each segment as:
    {{'name': 'Michael' or 'Sarah', 'transcript': 'dialogue'}}
    """,
    expected_output="A natural podcast transcript in the required format.",
    output_pydantic=AudioOverviewTranscript,
    agent=script_writer,
    context=[create_conversation_outline_task]
  )
  # Crew
  return Crew(
    agents=[research_analyst, conversation_planner, script_writer],
    tasks=[analyze_research_task, create_conversation_outline_task, write_podcast_script_task],
    process=Process.sequential,
    verbose=True,
  )


async def run_audio_overview_agent(notebook_id: str):
    logger.info(f"Running audio overview agent for notebook: {notebook_id}")

    chunks = await qdrant_service.get_all_chunks_by_notebook_id(notebook_id)

    research = "\n\n".join(
        chunk["content_chunk"]
        for chunk in chunks
    )

    logger.debug(f"Research content length: {len(research)} characters")

    crew = get_audio_overview_crew()

    crew_result = await crew.kickoff_async(inputs={
      "research": research,
    })

    logger.info(f"Audio overview result for notebook: {notebook_id} completed successfully")

    return [transcript.model_dump() for transcript in crew_result["transcript"]]


