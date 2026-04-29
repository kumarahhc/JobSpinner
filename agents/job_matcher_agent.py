import autogen
import json
from config import LLM_CONFIG
from tools.job_ranker import score_job_match


def create_job_matcher_agent() -> tuple:
    """
    Creates and returns:
      job_matcher_agent    : AG2 AssistantAgent
      job_matcher_executor : UserProxyAgent that runs tool calls
      job_results          : list populated with each score_job_match output
    """

    job_matcher_agent = autogen.AssistantAgent(
        name="JobMatcherAgent",
        llm_config=LLM_CONFIG,
        system_message="""
        You are a job matcher agent. Your task is to evaluate how well a given job posting matches a candidate's CV profile.
        You will receive two inputs: a CV profile in JSON format and a job posting in JSON format.
        Your task is to analyze both inputs and provide a relevance score between 0 and 1, where 0 means no match and 1 means a perfect match.
        Your evaluation should consider the following factors:
        1. Skill Match: Assess how well the skills listed in the CV match the requirements of the job posting.
        2. Experience Match: Evaluate how closely the candidate's experience aligns with the job requirements.
        3. Role Match: Consider how well the candidate's previous roles and job titles match the role described in the job posting.
        4. Location Match: If the job posting specifies a location, evaluate how well it matches the candidate's preferred locations.
        5. Work Type Match: If the job posting specifies a work type (e.g., remote, on-site, hybrid), evaluate how well it matches the candidate's preferred work types.
        6. Language Match: If the job posting specifies required languages, evaluate how well they match the candidate's language skills.

        IMPORTANT RULES:
        - You must call score_job_match tool for EVERY job posting provided.
        - Do not guess or fabricate information that is not present in the CV or job posting.
        
        Return your final output in EXACTLY in this format:
        
        ===MATCHED_JOBS===
        {
            "rank":1,
            "job_title":"",
            "company":"",
            "url":"",
            "source": "",
            "description": "",
            "total_score": total_score in the tool call result,
            "recommendation": recommendation from tool call result,
            "score_breakdown": {},
            "top_matched_skills": [],
            "reasoning": reasoning
        }
        {
            "rank":2,
            "job_title":"",
            "company":"",
            "url":"",
            "source": "",
            "description": "",
            "total_score": total_score in the tool call result,
            "recommendation": recommendation from tool call result,
            "score_breakdown": {},
            "top_matched_skills": [],
            "reasoning": reasoning
        }
        ...
        ===END_MATCHED_JOBS===
        """,
    )

    job_matcher_executor = autogen.UserProxyAgent(
        name="JobMatcherAgentExecutor",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=40,
        code_execution_config=False,
        default_auto_reply="Tool executed. Please continue with the next job posting.",
        is_termination_msg=lambda msg: isinstance(msg, dict) and "===END_MATCHED_JOBS===" in (msg.get("content") or ""),
    )

    autogen.register_function(
        score_job_match,
        caller=job_matcher_agent,
        executor=job_matcher_executor,
        name="score_job_match",
        description=(
            "Scores how well a candidate CV matches a job posting. "
            "Input: cv_profile (dict or JSON str) — the candidate profile, "
            "job_posting (dict or JSON str) — a single job posting. "
            "Returns a JSON string with total_score and full breakdown."
        ),
    )

    return job_matcher_agent, job_matcher_executor


def extract_match_results(chat_result) -> list:
    """Extracts ranked job matches from the ===MATCHED_JOBS=== block in chat history."""
    for message in reversed(chat_result.chat_history):
        content = message.get("content") or ""
        if "===MATCHED_JOBS===" not in content or "===END_MATCHED_JOBS===" not in content:
            continue

        start = content.index("===MATCHED_JOBS===") + len("===MATCHED_JOBS===")
        end = content.index("===END_MATCHED_JOBS===")
        block = content[start:end].strip()

        results = []
        decoder = json.JSONDecoder()
        idx = 0
        while idx < len(block):
            brace = block.find('{', idx)
            if brace == -1:
                break
            try:
                obj, end_pos = decoder.raw_decode(block, brace)
                results.append(obj)
                idx = end_pos
            except json.JSONDecodeError:
                idx = brace + 1

        return results

    return []
