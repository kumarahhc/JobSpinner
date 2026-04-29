# test_job_matcher.py

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.job_matcher_agent import (
    create_job_matcher_agent,
    extract_match_results
)

# ── Mock data — simulates output from Agents 1 and 2 ─────────

MOCK_CV_PROFILE = {
    "personal"           : {"name": "Sarah Johnson", "location": "Helsinki"},
    "current_title"      : "Backend Developer",
    "years_of_experience": 3,
    "skills": {
        "languages" : ["Python", "JavaScript", "SQL", "Bash"],
        "frameworks": ["FastAPI", "Django", "React"],
        "databases" : ["PostgreSQL", "Redis", "MongoDB"],
        "devops"    : ["Docker", "GitHub Actions", "AWS"],
        "other"     : ["REST APIs", "Git", "Linux"]
    },
    "languages"  : ["English", "Finnish"],
    "experience" : [
        {"role": "Backend Developer", "company": "Startup Oy", "years": 2},
        {"role": "Full Stack Developer", "company": "Agency Ltd", "years": 1}
    ],
    "preferences": {
        "target_roles"    : ["Backend Developer", "Full Stack Developer"],
        "locations"       : ["Helsinki, Finland"],
        "work_types"      : ["Hybrid", "Remote"],
        "preferred_salary": "60,000–75,000 EUR"
    }
}

MOCK_JOB_LISTINGS = [
    {
        "title"      : "Senior Python Developer",
        "company"    : "Wolt",
        "location"   : "Helsinki, Finland",
        "source"     : "linkedin.com",
        "url"        : "https://linkedin.com/jobs/wolt-python",
        "description": (
            "We are looking for a Senior Python Developer with 5+ years "
            "of experience. You will work with Python, FastAPI, PostgreSQL, "
            "Docker and AWS in a high-scale environment. Experience with "
            "Redis and REST APIs is a plus. Hybrid work available."
        )
    },
    {
        "title"      : "Full Stack Engineer",
        "company"    : "Reaktor",
        "location"   : "Helsinki, Finland / Remote",
        "source"     : "reaktor.com",
        "url"        : "https://reaktor.com/careers/fullstack",
        "description": (
            "Join Reaktor as a Full Stack Engineer. We use JavaScript, "
            "React, Node.js and Python. 3+ years of experience required. "
            "PostgreSQL and MongoDB experience preferred. Remote friendly."
        )
    },
    {
        "title"      : "Backend Developer",
        "company"    : "Nokia",
        "location"   : "Espoo, Finland",
        "source"     : "nokia.com",
        "url"        : "https://nokia.com/careers/backend",
        "description": (
            "Nokia seeks a Backend Developer with experience in Python, "
            "SQL and Linux. Docker and AWS knowledge is beneficial. "
            "3 years experience needed. On-site position in Espoo."
        )
    },
    {
        "title"      : "Java Developer",
        "company"    : "Accenture",
        "location"   : "Helsinki, Finland",
        "source"     : "accenture.com",
        "url"        : "https://accenture.com/jobs/java",
        "description": (
            "We need an experienced Java developer with Spring Boot, "
            "Hibernate and Oracle DB. 5+ years of Java experience required. "
            "On-site position."
        )
    },
    {
        "title"      : "DevOps Engineer",
        "company"    : "Futurice",
        "location"   : "Helsinki, Finland",
        "source"     : "futurice.com",
        "url"        : "https://futurice.com/careers/devops",
        "description": (
            "Futurice is hiring a DevOps Engineer. Skills needed: "
            "Docker, Kubernetes, AWS, GitHub Actions, Linux and Bash. "
            "Python scripting is a plus. Hybrid work. 3+ years experience."
        )
    }
]


def test_job_matcher():
    print("\n" + "=" * 55)
    print("JobSpinner — Job Matcher Agent Test")
    print("=" * 55)

    matcher_agent, matcher_executor = create_job_matcher_agent()

    # Build the matching request
    match_message = f"""
        Please score and rank the following job postings against
        this candidate profile.

        CANDIDATE PROFILE:
        {json.dumps(MOCK_CV_PROFILE, indent=2)}

        JOB POSTINGS TO SCORE ({len(MOCK_JOB_LISTINGS)} jobs):
        {json.dumps(MOCK_JOB_LISTINGS, indent=2)}

        Score each job using the score_job_match tool, then return results in the required format.
        """

    chat_result = matcher_executor.initiate_chat(
        matcher_agent,
        message=match_message,
        max_turns=20,
    )

    # ---- Extracts and print result -----------
    job_matches = extract_match_results(chat_result)

    print("\n" + "=" * 55)
    print("MATCH RESULTS")
    print("=" * 55)

    if not job_matches:
        print("No matches extracted — check agent output above")
        return

    for i, match in enumerate(job_matches):
        print(f"""
        RANK {i+1} — {match.get('total_score', 'N/A')} score
        Job    : {match.get('job_title', 'N/A')}
        Company: {match.get('company', 'N/A')}
        URL    : {match.get('url', 'N/A')}
        Verdict: {match.get('recommendation', 'N/A')}""")

        breakdown = match.get("score_breakdown", {})
        if breakdown:
            print(f"   Scores :", end="")
            for dim, score in breakdown.items():
                print(f" {dim}={score}", end="")
            print()


if __name__ == "__main__":
    test_job_matcher()