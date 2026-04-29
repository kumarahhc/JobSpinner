from datetime import datetime
import pandas as pd
import autogen
import os
from typing import Annotated
import json
from config import LLM_CONFIG
from tools.document_writer import save_cover_letter_docx,save_latex_file,update_job_excel


def create_doc_writer_agent() ->tuple:
    """
    Create and return 
           doc_writer_agent : the AG2 AssistantAgent
           agent_executor : the UserProxyAgent that executes tool calls

    Returns:
        tuple: _description_
    """
    # Agent 3: The Tailor (Writer)
    tailor = autogen.AssistantAgent(
        name="Tailor",
        system_message="""You are an automated career document writer.
        You will receive a candidate profile and a list of job matches.

        For EACH job in the list, you MUST complete ALL of the following steps before moving to the next job:

        STEP 1 — Write a tailored, professional cover letter (max 1 A4 page) that highlights the candidate's
                  most relevant skills and experience for that specific role. Do not hallucinate.

        STEP 2 — Call save_cover_letter_docx with:
                  - content: the full cover letter text
                  - company_name: the company name (used for the filename)

        STEP 3 — Call update_job_excel with:
                  - company: company name
                  - role: job title
                  - url: job URL
                  - status: "Applied"

        Do NOT skip STEP 3. Both tools MUST be called for every job.
        After ALL jobs are processed, say TERMINATE.""",
        llm_config=LLM_CONFIG,
    )

    tailor_user_proxy = autogen.UserProxyAgent(
        name="User_Proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=50,
        default_auto_reply="Continue with the next job.",
        is_termination_msg=lambda x: x.get("content") is not None and x.get("content").rstrip().endswith("TERMINATE"),
        code_execution_config=False,
    )
    
    autogen.agentchat.register_function(
        save_cover_letter_docx,
        caller=tailor,        # The Tailor decides to call it
        executor=tailor_user_proxy,  # The User_Proxy executes it on the local machine
        description="Saves the generated cover letter to a .docx file on disk.",
    )
    autogen.agentchat.register_function(
        save_latex_file,
        caller=tailor,
        executor=tailor_user_proxy,
        description="Saves the generated LaTeX cover letter to a local file",
    )

    autogen.agentchat.register_function(
        update_job_excel,
        caller=tailor,
        executor=tailor_user_proxy,
        description="Logs job application details to an Excel file with duplicate prevention",
    )
    
    return tailor,tailor_user_proxy
    
    