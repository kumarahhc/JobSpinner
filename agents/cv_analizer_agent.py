import autogen
import os
import json
from config import LLM_CONFIG
from tools.file_reader import read_cv_pdf

#agent cv analizer
def create_cv_analizer_agent(executor=None) -> tuple:
    """
    Creates and return CV analizer agent : AG2 assistantAgent.
    agent_executor : UserProxyAgent that runs tool calls for the agent."""
    cv_analyzer_agent = autogen.AssistantAgent(
        name="CVAnalyzerAgent",
        llm_config=LLM_CONFIG,
        system_message="""
        You are a CV analyzer agent. Your task is to analyze the candidate's CV and extract relevant 
        information about the candidate's skills, experience, and qualifications.
        structure your response in a JSON format with the following fields:
        Your workflow:
        1. Call the read_cv_pdf tool to extract the text content from the CV file.
        2. Analyze the extracted text to identify key information about the candidate, such as:
        3. Extract all relevant information
        4. Return single JSON object with the following structure:
        {
            "name": "Candidate's name",
            "contact_info": {
                "email": "Candidate's email",
                "phone": "Candidate's phone number"
                "linkedin": "Candidate's LinkedIn profile URL (if available)",
                "github": "Candidate's GitHub profile URL (if available)"
                "location": "Candidate's location"
            },
            "summary": "A brief summary of the candidate's background and career objectives",
            "current_title": "Candidate's current job title",
            "years_of_experience": "Total years of professional experience",
            "skills": ["List of candidate's skills"],
            "experience": [
                {
                    "job_title": "Previous job title",
                    "company": "Previous company name",
                    "duration": "Duration of employment",
                    "description": "Brief description of responsibilities and achievements"
                },
                ...
            ],
            "education": [
                {
                    "degree": "Degree obtained",
                    "institution": "Educational institution name",
                    "duration": "Duration of study",
                    "description": "Brief description of coursework and achievements"
                },
                    ...
            ]
        }
        
        Rules:
        - Never invent information not present in the CV,
        - If a filed in not present in the CV, return null for objects and [] for lists,
        - Years of experience should be a number, if the CV states a range (e.g., 3-5 years), take the average (e.g., 4 years),
        - skills must be properly categorized even if the CV grouped them together (e.g., if the CV lists "Python, Java, and SQL" under a single "Skills" section, you should extract them as separate skills in the skills list),
        - Be concise and focus on the most relevant information that highlights the candidate's qualifications and suitability
        - Return only the JSON object as specified, without any additional commentary or explanation.
        """
    )
    
    #the executor that runs tool calls
    agent_executor = executor or autogen.UserProxyAgent(
        name="CVAnalyzerAgentExecutor",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=5,
        code_execution_config=False,
        default_auto_reply="Tool executed, Please continue.",
        is_termination_msg=lambda msg: (
            isinstance(msg, dict)
            and isinstance(msg.get("content", ""), str)
            and msg.get("content", "").strip().startswith("{")
            and msg.get("content", "").strip().endswith("}")
        )                        
    )
    
    #register tool
    autogen.register_function(
        read_cv_pdf,
        caller=cv_analyzer_agent,
        executor=agent_executor,
        name="read_cv_pdf",
        description="Read CV content from a PDF or TEXT file and return the extracted text."
    )
    return cv_analyzer_agent, agent_executor

def extract_profile_json(chat_result)-> dict:
    """
    Extract the JSON object from the agent's final response and return it.
    Args: chat result,
    Returns: dict with the candidate's profile information.
    """
    for message in reversed(chat_result.chat_history):
        content = message.get("content", "") if isinstance(message, dict) else message
        if isinstance(content, str) and content.strip().startswith("{") and content.strip().endswith("}"):
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                continue
    return {}