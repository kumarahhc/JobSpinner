import autogen
from config import LLM_CONFIG
from tools.web_search import web_search

def create_job_search_agent() -> tuple:
    """Creates a job search agent that can search for job listings based on user input."""

    job_search_agent = autogen.AssistantAgent(
        name="JobSearchAgent",
        llm_config=LLM_CONFIG,
        system_message="""
        You are Job search agent, Your sole responsibility is to search the internet for real, live job
        postings that match the candidate's preferences. You will use the web search tool to find
        job listings based on the provided job title, location, and keywords.
        Your are provided with the following information about the candidate:
        - Desired job title,
        - Location preference,
        - Key skills,
        - Experience level.

        You must:
        1. Call the search_jobs tool with appropriate parameters,
        2. Review the returned resutls carefully,
        3. Filter the results to ensure they match the candidate's preferences,
        4. Return a list of relevant job postings, including the job title, company name, location, and a brief description,
        5. You should not return any job postings that do not match the candidate's preferences.

        Format your response as a JSON array of job postings, where each posting includes the following fields:
        - title: The title of the job,
        - company: The name of the company offering the job,
        - location: The location of the job,
        - content: The content of the job posting, which should include the description and requirements of the job,
        - description: A brief description of the job.
        - url: The URL to the job posting,
        - score: A relevance score between 0 and 1 indicating how well the job matches the candidate's preferences,
        - source: The source of the job posting (e.g., LinkedIn, Indeed, etc.)

        Note that the search quality matters more than quantity.
        If the first few results are not relevant, you should try to refine your search query and search again until you find relevant job postings
        ."""
    )

    # The executor that runs tool calls
    agent_executor = autogen.UserProxyAgent(
        name="JobSearchAgentExecutor",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=5,
        code_execution_config=False,
        default_auto_reply="Tool executed, Please continue."
    )

    # Register the tool with the agent and the executor
    autogen.register_function(
        web_search,
        caller=job_search_agent,
        executor=agent_executor,
        name="search_jobs",
        description="Search the web for job listings based on the given job title, location, and keywords."
    )
    return job_search_agent, agent_executor
    