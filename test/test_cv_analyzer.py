import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.cv_analizer_agent import create_cv_analizer_agent,extract_profile_json

SAMPLE_CV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_cv.pdf")

def test_cv_analyzer():
    """Test the CV analyzer agent with a sample CV file."""
    print("\n"+"="*50)
    print("Testing CV Analyzer Agent with Sample CV File")
    print("="*50)

    # Create the CV analyzer agent
    cv_analyzer_agent, cv_analyzer_executor = create_cv_analizer_agent()

    # The executor initiates the conversation
    chat_result = cv_analyzer_executor.initiate_chat(
        cv_analyzer_agent,
        message=f"""
        Analyze the candidate's CV and extract relevant information about the candidate's skills, experience,
        and qualifications. The CV file is located at "{SAMPLE_CV_PATH}". Please use the read_cv_pdf tool to extract
        the text content from the CV file and analyze it.
        """,
        max_turns=5,
    )

    # Extract the candidate's profile information
    profile = extract_profile_json(chat_result)
    print("Extracted Profile Information:")
    print(json.dumps(profile, indent=2))
    
    
if __name__ == "__main__":
    test_cv_analyzer()