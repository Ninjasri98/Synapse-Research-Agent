"""
Task configurations for the sources research crew.
Each task is defined with its description and expected output.
"""

TASK_CONFIGS = {
    "web_scraping": {
        "description": """
        STRICTLY FOLLOW THESE INSTRUCTIONS TO EXTRACT RAW CONTENT FROM THIS URL {url}:

        1. Extract the content:
           - Use scrape_as_markdown to capture ALL raw text from {url}
        2. Return the raw text as a string

        CRITICAL REQUIREMENTS:
        - Extract and preserve ALL text exactly as it appears
        - Do NOT summarize or modify any content
        - Do NOT skip any text content
        - Include complete URL and page title
        - If page fails to load, return error status in output

        Current time: {current_time}""",
        "expected_output": "Complete raw text content with the page title and URL from the URL, with no modifications or summarization."
    },
    "research_analysis": {
        "description": """Synthesize research findings into a comprehensive and detailed final document using all available content sources including web scraping, provided textual content, and file content.

        Your mission is to transform all available content into a comprehensive, well-structured research analysis in markdown format.

        Scraped Data:
        ```
        {scraped_data}
        ```

        Provided Textual Content:
        ```
        {textual_content}
        ```

        Provided File Content:
        ```
        {file_content}
        ```

        Follow these steps meticulously:

        1. **Deep Analysis & Synthesis**
           - Review ALL content thoroughly (scraped text, provided text, and file content)
           - Identify key themes, patterns, relationships and contrasts across all sources
           - Synthesize information rather than just listing findings
           - Look for supporting evidence and conflicting viewpoints
           - Cross-reference insights between scraped content, provided content, and file content

        2. **Research Structure**
           Create a clear markdown structure that includes:
           - Title
           - Introduction providing overview and key findings
           - Main body with sections for each major theme/finding identified
           - Conclusion summarizing key points
           - References listing all sources used (scraped, provided, and file content)

        3. **Content Requirements**
           - Write clear, objective analysis supported by all available data
           - Use proper markdown formatting
           - Include direct quotes when relevant, cited with source URLs or references
           - Maintain academic tone and rigorous sourcing
           - Focus on factual content, avoid speculation
           - Let the research guide the number and organization of sections
           - Structure sections based on natural groupings of findings
           - Integrate insights seamlessly from all content sources
           - Incorporate relevant insights from uploaded file content

        Today's date and time is {current_time}""",
        "expected_output": "A markdown document with comprehensive research analysis, organized into logical sections based on the findings, with proper citations and references for all content sources including scraped content, provided content, and file content"
    },
    "content_creation": {
        "description": """Create an engaging and informative blog post based on the research analysis.

        Your task is to transform the given research findings into a compelling, engaging, and informative long-form blog post.

        Follow these steps meticulously:

        1. **Content Structure**
           Create a clear markdown structure with appropriate sections based on the research findings. The basic structure should include:
           - Title
           - Introduction that hooks readers and outlines key points
           - Multiple main sections exploring different aspects/themes from the research
           - Conclusion synthesizing key insights
           - References section listing all sources

        2. **Content Requirements**
           - Write in an engaging, authoritative voice
           - Support all claims with citations from the research
           - Use proper markdown formatting
           - Include relevant quotes with source attribution
           - Break up text with appropriate subheadings, lists, and emphasis
           - Maintain professional tone while being accessible
           - Focus on providing value to readers
           - Let the research guide the number and organization of sections

        3. **Citation Format**
           When citing sources use:
           > "Quote text" - [Source Title](url)

        4. **Output Format**
           - JSON object with the following keys:
             - "blog_post": the blog post in markdown format without '```' or '```markdown'
             - "title": the title of the blog post
           - Output should be well-structured, engaging long blog post that effectively communicates the research findings with proper citations
           - The output should be a JSON object with the following keys: 'blog_post' and 'title'
           - The 'blog_post' should be in markdown format without '```' or '```markdown'
           - The 'title' should be a string
           - JSON object should be formatted as a JSON object without '```' or '```json'

        Today's date and time is {current_time}""",
        "expected_output": "A well-structured, engaging long blog post that effectively communicates the research findings with proper citations in markdown format without '```' or '```markdown'. The content should be organized into logical sections based on the research material, with clear attribution of sources throughout. The output should be a JSON object with the following keys: 'blog_post' and 'title'. The JSON object should be formatted as a JSON object without '```' or '```json'"
    },
    "faq_generation": {
        "description": """Generate 10 frequently asked questions and detailed answers based on the given researched content.

        Your task is to create an informative FAQ section that addresses key questions readers may have based on the research findings.

        Follow these steps meticulously:

        1. **Question Requirements**
           - Generate 10 unique and relevant questions from the researched content
           - Questions should cover different aspects/themes from the research
           - Focus on questions readers are likely to ask
           - Ensure questions progress logically from basic to more advanced topics
           - Make questions clear and specific

        2. **Answer Requirements**
           - Provide detailed, accurate answers based on the research
           - Support answers with citations from sources
           - Use proper markdown formatting
           - Keep answers concise but comprehensive
           - Maintain professional tone while being accessible
           - Include relevant quotes when helpful
           - Cite sources for all factual claims

        3. **Citation Format**
           When citing sources use:
           > "Quote text" - [Source Title](url)

        4. **Output Format**
           - JSON object with an array of 10 FAQ items
           - Each FAQ item should have:
             - "question": the question text
             - "answer": the answer in markdown format with citations
           - Format as a clean JSON object without code block markers

        Today's date and time is {current_time}""",
        "expected_output": "A JSON object containing an array of 10 FAQ items, each with a question and detailed answer supported by citations from the research. Answers should be in markdown format with proper source attribution."
    },
}