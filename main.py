import autogen
import json
import os
from datetime import datetime

from agents.cv_analizer_agent import create_cv_analizer_agent
from agents.job_search_agent import create_job_search_agent
from agents.doc_writer_agent import create_doc_writer_agent



def print_banner()->None:
    print("\n"+"="*75)
    print("Job Spinner : AI powered job search & applicaiton platform")
    print("\n"+"="*75)
    

def validate_inputs(cv_file_path:str)->None:
    """
    Validate input file for availability
    Args:
        dv_file_path (str): _description_
    """
    if not os.path.exists(cv_file_path):
        raise FileNotFoundError(
            f"CV file not found '{cv_file_path}\n'"
            f"Please place your cv in the project root:\n"
        )
    ext=os.path.splitext(cv_file_path)[1].lower()
    if ext not in [".pdf",".txt"]:
        raise ValueError(
            f"Unsupported file format: '{ext}'\n"
            f"  JobSpinner accepts .pdf or .txt CV files only."
        )
    size_kb=os.path.getsize(cv_file_path)/1024
    if size_kb<1:
        raise ValueError(
            f"CV file appears to be empty ({size_kb:.1f} KB).\n"
            f"  Please provide a valid CV file."
        )
    if size_kb>5000:
        raise ValueError(
            f"CV file is too large ({size_kb:.0f} KB).\n"
            f"  Maximum supported size is 5 MB."
        )
    print(f"CV file validated — {cv_file_path} ({size_kb:.1f} KB)")

def print_final_report(
    cv_file_path:str,
    profile:dict,
    jobs:list,
    matches:list,
    documents:list
):
    name   = profile.get("personal", {}).get("name", "Candidate")
    now    = datetime.now().strftime("%Y-%m-%d %H:%M")

    print(f"\n\n{'═' * 60}")
    print(f" JOBSPINNER — FINAL REPORT")
    print(f"{'═' * 60}")
    print(f"  Generated   : {now}")
    print(f"  CV File     : {cv_file_path}")
    print(f"  Candidate   : {name}")
    print(f"  Pattern     : AG2 Sequential Chats")
    print(f"{'─' * 60}")
    print(f"  Jobs found  : {len(jobs)}")
    print(f"  Shortlisted : {len(matches)}")
    print(f"  Documents   : {len(documents)} Word files")
    print(f"{'═' * 60}")


def run_process(cv_filepath: str):    

    # Single orchestrating executor for all sequential chats
    orchestrator = autogen.UserProxyAgent(
        name="Orchestrator",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=50,
        code_execution_config=False,
        default_auto_reply="Continue.",
        is_termination_msg=lambda msg: isinstance(msg, dict) and (
            any(kw in (msg.get("content") or "")
                for kw in ["COMPLETE", "TERMINATE", "===END_MATCHED_JOBS==="])
            or (
                (msg.get("content") or "").strip().startswith("{")
                and (msg.get("content") or "").strip().endswith("}")
            )
        ),
    )
    
    # Create assistant agents — discard their individual executors
    cv_analyzer, _ = create_cv_analizer_agent(executor=orchestrator)
    job_searcher, _ = create_job_search_agent(executor=orchestrator)
    doc_writer,   _ = create_doc_writer_agent(executor=orchestrator)

    # Sequential chats pipeline
    results = orchestrator.initiate_chats([
        # Chat 1: CV Analysis
        {
            "recipient"     : cv_analyzer,
            "message"       : (
                f'Analyze the CV located at "{cv_filepath}". '
                "Use the read_cv_pdf tool to read it, then extract all information "
                "into the structured JSON profile format defined in your instructions."
            ),
            "max_turns"     : 6,
            "summary_method": "reflection_with_llm",
            "summary_args"  : {
                "summary_prompt": (
                    "Return the candidate profile from this conversation as a single "
                    "compact JSON object. Include: name, current_title, "
                    "years_of_experience, skills (list), experience (list with role/job_title), "
                    "education (list), languages (list), preferences (dict with "
                    "locations list and work_types list). Return ONLY the JSON."
                )
            },
        },
        # Chat 2: Job Search
        {
            "recipient"     : job_searcher,
            "message"       : (
                "Using the candidate profile from the previous step, "
                "search for at least 5 matching job postings and return them "
                "in the structured format specified in your system message."
            ),
            "max_turns"     : 10,
            "summary_method": "reflection_with_llm",
            "summary_args"  : {
                "summary_prompt": (
                    "Extract all job postings from this conversation and return them "
                    "as a JSON array. Each element must have: title, company, location, "
                    "source, url, description,relavance_score. Return ONLY the JSON array."
                )
            },
        },
        # Chat 3: Cover Letter & Excel Update
        {
            "recipient"     : doc_writer,
            "message"       : (
                "The candidate profile and top matched jobs from the previous steps "
                "are available as context above.\n\n"
                "For EACH job:\n"
                "  1. Call save_cover_letter_docx with a tailored cover letter\n"
                "  2. Call update_job_excel with the job details\n"
                "Say TERMINATE when all jobs are processed."
            ),
            "max_turns"     : 25,
            "summary_method": "last_msg",
        },
    ])

    return results

def main():
    SAMPLE_CV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test/sample_cv.pdf")
    run_process(SAMPLE_CV_PATH)
    
    
if __name__=="__main__":
    main()