import json
import os
import sys
import autogen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.cv_analizer_agent import create_cv_analizer_agent, extract_profile_json
from agents.job_search_agent import create_job_search_agent

def test_pipeline():
    """Test the end-to-end pipeline from CV analysis to job search."""
    print("\n"+"="*50)
    print("Testing End-to-End Pipeline: CV Analysis to Job Search")
    print("="*50)

    # Step 1: Create the CV analyzer agent and analyze the sample CV
    cv_analyzer_agent, cv_analyzer_executor = create_cv_analizer_agent()
    SAMPLE_CV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_cv.pdf")
    
    chat_result = cv_analyzer_executor.initiate_chat(
        cv_analyzer_agent,
        message=f"""
        Analyze the candidate's CV and extract relevant information about the candidate's skills, experience,
        and qualifications. The CV file is located at "{SAMPLE_CV_PATH}". Please use the read_cv_pdf tool to extract
        the text content from the CV file and analyze it.
        """,
        max_turns=5,
    )

    profile = extract_profile_json(chat_result)
    print("Extracted Profile Information:")
    print(json.dumps(profile, indent=2))

    # Step 2: Create the job search agent and search for jobs based on the extracted profile
    job_search_agent, job_search_executor = create_job_search_agent()
    
    job_search_executor.initiate_chat(
        job_search_agent,
        message=f"""
        Search for jobs matching this candidate profile:
        {json.dumps(profile)}

        Search for at least 5 real job postings and return them
        in the structured format specified in the system message.
        """,
        max_turns=5,
    )
    
if __name__ == "__main__":
    test_pipeline()