from crewai import Agent, Crew, Task, Process
from loguru import logger
from models.chat_models import ChatMessage
from typing import List
from services.qdrant_service import qdrant_service
from config import llm
from services.notebook_repository import notebook_repository

async def get_relevant_sources(notebook_id: str, query: str):

  logger.info(f"Getting relevant sources from Qdrant for notebook: {notebook_id} with query: {query}")

  results = await qdrant_service.search(query, notebook_id)

  output = ""
  for result in results:
    source_info = "Source: Provided Text"
    if result.get('url'):
        page_title = result.get('page_title', '')
        source_info = f"Source: {page_title} ({result['url']})"
    output += f"Content: {result['content_chunk']}\n{source_info}\n---\n"

  logger.info(f"Relevant sources from Qdrant for notebook: {notebook_id} with query: {query} are: {output}")

  return output

def get_synapse_crew():
  synapse_agent = Agent(
    role="Synapse",
    goal="Analyze and decode the user's questions to provide precise answers based on the relevant sources",
    backstory="""You're Synapse, an analytical assistant specialized in breaking down complex queries and providing clear, accurate responses drawn from available source materials. Created by Sriparno Palit. You have expertise in "{topic}".
    """,
    verbose=True,
    llm=llm,
  )

  answer_question_task = Task(
    description="""Answer the user's question based on the relevant sources and previous chat context (if any). Do not include any other text than the answer to the question. Use the sources to answer the question while maintaining context from the chat history if it exists.

    If the user asks about you, you can explain that you are Synapse, an analytical assistant created by Sriparno Palit, specialized in analyzing questions and providing clear answers from source materials related to "{topic}".

    Chat History (may be empty for first query):
    ```
    {chat_history}
    ```

    User Question:
    ```
    {question}
    ```

    Relevant Sources:
    ```
    {relevant_sources}
    ```
    """,
    expected_output="""A markdown-formatted response with answer. Do not include any other text than the answer to the question. Add a **Sources:** section at the end of the response with the source citations in the following format:
    **Sources:**
    - [Source Title 1](url1)
    - [Source Title 2](url2)
    - [Source Title 3](url3)
    ...

    The source citations should be in the following format:
    - [Source Title 1](url1)
    - [Source Title 2](url2)
    - [Source Title 3](url3)
    ...""",
    agent=synapse_agent,
  )

  return Crew(
    agents=[synapse_agent],
    tasks=[answer_question_task],
    process=Process.sequential,
    verbose=True
  )

async def run_chat_agent(notebook_id: str, messages: List[ChatMessage]):
    logger.info(f"Running chat agent for notebook: {notebook_id} with messages: {messages}")

    notebook = await notebook_repository.get_notebook(notebook_id)

    chat_history = "\n".join(f"{message.role}: {message.content}" for message in messages[-10:-1])

    logger.info(f"Chat history: {chat_history}")

    # Rewrite question based on chat history for better vector search
    search_query = messages[-1].content
    if chat_history:
        search_query = llm.call(f"""
        Given the following chat history and current question, rewrite the question to include relevant context that would help with searching a vector database. Focus on key concepts and terminology that should match similar content.

        Chat History:
        ```
        {chat_history}
        ```

        Current Question:
        ```
        {messages[-1].content}
        ```

        Rewrite the question in a way that captures the full context. Only output the rewritten question, nothing else.
        """)

    relevant_sources = await get_relevant_sources(notebook_id, search_query)

    crew = get_synapse_crew()

    crew_result = await crew.kickoff_async(inputs={
      "question": messages[-1].content,
      "chat_history": chat_history,
      "relevant_sources": relevant_sources,
      "topic": notebook["title"] if notebook and "title" in notebook else "the notebook"
    })

    logger.info(f"Crew result for notebook: {notebook_id} with question: {messages[-1].content} is: {crew_result}")

    return crew_result.raw


