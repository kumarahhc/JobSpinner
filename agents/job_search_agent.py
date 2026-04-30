import json
import re
import autogen
from config import LLM_CONFIG
from tools.web_search import web_search
from tools.job_ranker import score_job_match

def create_job_search_agent(executor=None) -> tuple:
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
        4. Calculate the relevance score of each job by calling the score_job_match tool.
           IMPORTANT: the score_job_match tool requires two arguments:
           - cv_profile: pass the COMPLETE candidate profile as a JSON object (dict), NOT as a plain text summary.
             Use the exact structured profile provided to you at the start of this conversation.
           - job_posting: pass the job details as a JSON object with fields: title, company, location, description, content, url, source.
        5. Return a list of relevant job postings, including the job title, company name, location, and a brief description,
        6. You should not return any job postings that do not match the candidate's preferences.

        Format your response as a JSON array of job postings, where each posting includes the following fields:
        - title: The title of the job,
        - company: The name of the company offering the job,
        - location: The location of the job,
        - content: The content of the job posting, which should include the description and requirements of the job,
        - description: A brief description of the job.
        - url: The URL to the job posting,
        - score: A relevance score between 0 and 1 indicating how well the job matches the candidate's preferences,
        - source: The source of the job posting (e.g., LinkedIn, Indeed, etc.)
        - relavance_score : total_score of tool score_job_match result
        - reasoning: reaconing based on result of tool score_job_match
        - score_breakdown: result from tool score_job_match

        Note that the search quality matters more than quantity.
        If the first few results are not relevant, you should try to refine your search query and search again until you find relevant job postings
        Order the result based on the relavance_score
        When you find minimum 5 jobs return the single word COMPLETE.
        ."""
    )

    # The executor that runs tool calls
    agent_executor = executor or autogen.UserProxyAgent(
        name="JobSearchAgentExecutor",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=5,
        code_execution_config=False,
        default_auto_reply="Tool executed, Please continue.",
        is_termination_msg=lambda msg: isinstance(msg, dict) and "COMPLETE" in (msg.get("content") or ""),
    )

    # Register the tool with the agent and the executor
    autogen.register_function(
        web_search,
        caller=job_search_agent,
        executor=agent_executor,
        name="search_jobs",
        description="Search the web for job listings based on the given job title, location, and keywords."
    )
    autogen.register_function(
        score_job_match,
        caller=job_search_agent,
        executor=agent_executor,
        name="score_job_match",
        description="Calculate the match score of a job against the candidate profile. Pass cv_profile as the full JSON object (not a text summary) and job_posting as a JSON object with title, company, location, description, content, url, source fields."
    )
    return job_search_agent, agent_executor

def extract_serched_jobs(chat_result) -> list:
    """Extracts the job listings JSON array from the agent's chat history."""
    for message in reversed(chat_result.chat_history):
        content = message.get("content") or ""
        if not content or content.strip() == "COMPLETE":
            continue

        # Try direct parse
        try:
            data = json.loads(content)
            if isinstance(data, list) and data and isinstance(data[0], dict):
                return data
        except (json.JSONDecodeError, ValueError):
            pass

        # Try ```json ... ``` code block
        match = re.search(r'```json\s*([\s\S]*?)\s*```', content)
        if match:
            try:
                data = json.loads(match.group(1))
                if isinstance(data, list) and data and isinstance(data[0], dict):
                    return data
            except (json.JSONDecodeError, ValueError):
                pass

        # Try finding first [ to last ]
        start = content.find('[')
        end = content.rfind(']')
        if start != -1 and end > start:
            try:
                data = json.loads(content[start:end + 1])
                if isinstance(data, list) and data and isinstance(data[0], dict):
                    return data
            except (json.JSONDecodeError, ValueError):
                pass

    return []
