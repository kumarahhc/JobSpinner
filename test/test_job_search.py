import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import autogen
from agents.job_search_agent import create_job_search_agent

# Sample candidate profile to test the job search agent
SAMPLE_PROFILE = """
Candidate Profile:
- Desired job title: Software Engineer
- Location preference: Helsinki, Finland
- Key skills: Python, Machine Learning, Data Analysis
- Experience level: Mid-level (3-5 years)
- Additional preferences: Remote work, flexible hours
"""

def test_job_search():
    """Test the job search agent with a sample candidate profile."""
    print("\n"+"="*50)
    print("Testing Job Search Agent with Sample Candidate Profile")
    print("="*50)
    
    #Crate the job search agent
    job_search_agent, job_search_executor = create_job_search_agent()
    
    #the executor initiate the conversation
    job_search_executor.initiate_chat(
        job_search_agent,
        message=f"""
        Search for jobs matching this candidate profile:
        {SAMPLE_PROFILE}

        Search for at least 5 real job postings and return them
        in the structured format specified in the system message.
        """,
        max_turns=5,
    )
    
if __name__ == "__main__":
    test_job_search()