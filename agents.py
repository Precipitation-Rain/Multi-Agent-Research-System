from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from tools import web_search , scrape_url
from dotenv import load_dotenv

llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)
# define the web_search_agentt
def web_search_agent():
    return create_agent(
        model=llm,
        tools=[web_search ]
    )

# define the scrape_url_agent
def scrape_url_agent():
    return create_agent(
        model = llm ,
        tools=[scrape_url]
    )

# create an writer_chain

writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
    ("human", """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional.""")
])

writer_chain = writer_prompt | llm | StrOutputParser()


# create an critics chain
critics_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
...""")
])

critics_chain = critics_prompt | llm | StrOutputParser()

