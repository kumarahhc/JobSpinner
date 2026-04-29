import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.cv_analizer_agent import create_cv_analizer_agent, extract_profile_json
from agents.job_search_agent import create_job_search_agent, extract_serched_jobs
from tools.job_ranker import score_job_match
from agents.doc_writer_agent import create_doc_writer_agent


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
    
    job_search_chat=job_search_executor.initiate_chat(
        job_search_agent,
        message=f"""
        Search for jobs matching this candidate profile:
        {json.dumps(profile)}

        Search for at least 5 real job postings and return them
        in the structured format specified in the system message.
        """,
        max_turns=10,
    )
    jobs=extract_serched_jobs(job_search_chat)
    
    print ("\n"+":="*50)
    print(jobs)
    print ("\n"+":="*50)
    
    # Step 3: Score each job directly — no LLM needed for deterministic scoring
    print("STARTING JOB RANKING-----------")
    scored = []
    for job in jobs:
        result = json.loads(score_job_match(profile, job))
        scored.append(result)
    print(scored)
    
    jobs_matched = [r for r in scored if r.get("total_score", 0) >= 0.1]
    jobs_matched.sort(key=lambda x: x.get("total_score", 0), reverse=True)
    jobs_matched = jobs_matched[:3]
    for i, r in enumerate(jobs_matched, start=1):
        r["rank"] = i

    #----- Print Result -----
    print("\n" + "=" * 50)
    print("JOBSPINNER — FINAL MATCH REPORT")
    print("=" * 50)

    for job in jobs_matched:
        print(f"""
        Rank   : {job.get('rank')}
        Score  : {job.get('total_score')}
        Job    : {job.get('job_title')}
        Company: {job.get('company')}
        URL    : {job.get('url')}
        Verdict: {job.get('recommendation')}""")
    
    # Step 4: Write cover letter
    doc_writer,doc_writer_executor= create_doc_writer_agent()
    doc_writer_chat=doc_writer_executor.initiate_chat(
        doc_writer,
        message=f"""
                Generate tailored cover letter for each of the matched jibs below.
                CANDIDATE PROFILE:
                {json.dumps(profile)}
                
                TOP MATCHED JOBS: {len(jobs_matched)} jobs
                
                {json.dumps(jobs_matched, indent=2)}
                
                For EACH job you must:
                1. Call save_cover_letter_docx tool with tailored cover letter content
                2. Call update_job_excel tool with job details to update the local excel file
                Once done return single word COMPLETE.               
                
        """,
        max_turns=5,
    )
    
    
if __name__ == "__main__":
    test_pipeline()