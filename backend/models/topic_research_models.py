from pydantic import BaseModel, Field
from typing import List

class WebLink(BaseModel):
    url: str = Field(description="The URL of the web page that was scraped.")
    title: str = Field(description="The title of the web page that was scraped.")

class WebScrapingPlannerTaskResult(BaseModel):
    search_queries: List[str] = Field(description="A list of search queries that will be used to scrape the web.")

class WebScrapingLinkCollectorTaskResult(BaseModel):
    links: List[WebLink] = Field(description="A list of links that were collected from the web.")

class BlogPostTaskResult(BaseModel):
    blog_post: str
    title: str


class FaqItem(BaseModel):
    question: str = Field(description="The question of the FAQ item.")
    answer: str = Field(description="The answer of the FAQ item.")

class FaqTaskResult(BaseModel):
    faq: List[FaqItem] = Field(description="A list of FAQ items.")


# class WebScrapingTaskSingleResult(BaseModel):
#     source: WebSource = Field(description="The source of the web page that was scraped.")
#     content: str = Field(description="The content of the web page that was scraped.")

# class WebScrapingTaskResult(BaseModel):
#     results: List[WebScrapingTaskSingleResult] = Field(description="A list of results from the web scraping task.")

# class ResearchTaskResult(BaseModel):
#     content: str = Field(description="The content of the research that was conducted.")
#     sources: List[WebSource] = Field(description="A list of sources that were used to conduct the research.")

# class WebSource(BaseModel):
#     url: str = Field(description="The URL of the web page that was scraped.")
#     title: str = Field(description="The title of the web page that was scraped.")


# class BlogTaskResult(BaseModel):
#     blog_post: str = Field(description="The content of the long blog post. A well-structured, engaging blog post that effectively communicates the research findings with proper citations in markdown format without '```' or '```markdown'")
#     sources: List[WebSource] = Field(description="A list of sources that were used to create the blog post.")
