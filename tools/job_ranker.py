import ast
import json
from typing import Union

def score_job_match(
    cv_profile: Union[str, dict],
    job_posting: Union[str, dict]
) ->str:
    """
    Tool: Score the relevance of a job posting to a candidate's profile.
    Args:
        cv_profile (Union[str, dict]): The candidate's profile information, either a JSON string or a dictionary.
        job_posting (Union[str, dict]): The job posting information, either a JSON string or a dictionary.

    Returns:
        str: A relevance score between 0 and 1 indicating how well the job matches the candidate's profile.
    """
    if isinstance(cv_profile, str):
        try:
            cv_profile = json.loads(cv_profile)
        except json.JSONDecodeError:
            try:
                cv_profile = ast.literal_eval(cv_profile)
            except (ValueError, SyntaxError):
                return "Invalid JSON format for cv_profile"
    if isinstance(job_posting, str):
        try:
            job_posting = json.loads(job_posting)
        except json.JSONDecodeError:
            try:
                job_posting = ast.literal_eval(job_posting)
            except (ValueError, SyntaxError):
                return "Invalid JSON format for job_posting"

    assert isinstance(cv_profile, dict)
    assert isinstance(job_posting, dict)

    #------ extract relevant information from cv_profile------------------
    cv_skills = []
    skills_data = cv_profile.get("skills", {})
    if isinstance(skills_data, dict):
        for skill_list in skills_data.values():
            if isinstance(skill_list, list):
                cv_skills.extend(skill_list)
    elif isinstance(skills_data, list):
        cv_skills = [s for s in skills_data if isinstance(s, str)]

    cv_experience = cv_profile.get("years_of_experience", 0)

    # Accept both "role" (structured profile) and "job_title" (CV-extracted profile)
    cv_roles = []
    for r in cv_profile.get("experience", []):
        if not isinstance(r, dict):
            continue
        role_str = r.get("role") or r.get("job_title") or ""
        if role_str:
            cv_roles.append(role_str.lower())
    cv_locations=cv_profile.get("preferences", {}).get("locations", [])
    cv_work_types=cv_profile.get("preferences", {}).get("work_types", [])
    cv_languages=[l.lower() for l in cv_profile.get("languages", []) if isinstance(l, str)]
    
    #------ extract relevant information from job_posting------------------
    job_title=job_posting.get("title", "").lower()
    job_location=job_posting.get("location", "")
    job_description=job_posting.get("description", "").lower()
    job_content=job_posting.get("content","").lower()
    job_source=job_posting.get("source", "").lower()
    job_url=job_posting.get("url", "")
    
    scores = {}
    reasoning = {}
    
    #------ skill match score (Weighted) [weight=45%]------------------
    matched_skills = [s for s in cv_skills if s.lower() in job_content]
    umatched_skills = [s for s in cv_skills if s.lower() not in job_content]
    if cv_skills:
        skill_score = min(len(matched_skills) / max(len(cv_skills),1), 1.0)
        scores["skills"] = round(skill_score * 0.45, 2)
        reasoning["skills"] = f"Matched skills: {matched_skills}, Unmatched skills: {umatched_skills}"
    else:
        scores["skills"] = 0.0
        reasoning["skills"] = "No skills listed in CV"
        
    #------ role match score (Weighted) [weight=25%]------------------
    role_score = 0.0
    matched_roles = []
    for role in cv_roles:
        if role in job_title or role in job_description:
            matched_roles.append(role)
    if matched_roles:
        role_score = len(matched_roles) / max(len(cv_roles),1)
        scores["roles"] = round(role_score * 0.35, 2)
        reasoning["roles"] = f"Matched roles: {matched_roles}"
    else:
        scores["roles"] = 0.0
        reasoning["roles"] = "No matching roles found"
        
    #------ location match score (Weighted) [weight=5%]------------------
    location_score = 0.0
    if not cv_locations:
        location_score=1.0
    else:
        if job_location:
            if job_location in cv_locations:
                location_score = 1.0            
            reasoning["location"] = f"Job location: {job_location}, Candidate preferred locations: {cv_locations}"
        else:
            location_score = 0.0  
            reasoning["location"] = "Location information missing in either CV or job posting"
    
    scores["location"] = round(location_score * 0.05, 2)
    
    #------ work type match score (Weighted) [weight=5%]------------------
    work_type_score = 0.0
    if not cv_work_types:
        work_type_score = 1.0
    else:
        if job_posting.get("work_type"):
            if job_posting["work_type"] in cv_work_types:
                work_type_score = 1.0
            reasoning["work_type"] = f"Job work type: {job_posting['work_type']}, Candidate preferred work types: {cv_work_types}"
        else:
            work_type_score = 0.0
            reasoning["work_type"] = "Work type information missing in either CV or job posting"
            
    scores["work_type"] = round(work_type_score * 0.05, 2)
    
    #------ Experience match score (Weighted) [weight=10%]------------------
    job_experience_requirement = job_posting.get("experience_required", 0)
    if not job_experience_requirement:
        experience_score = 1.0
        reasoning["experience"] = "No experience requirement specified in job posting"
    elif cv_experience:
        experience_score = min(cv_experience / job_experience_requirement, 1.0)
        reasoning["experience"] = f"Candidate experience: {cv_experience} years, Job experience requirement: {job_experience_requirement} years"
    else:
        experience_score = 0.0
        reasoning["experience"] = "Candidate experience not specified"

    scores["experience"] = round(experience_score * 0.10, 2)
    
    #------ language match score (Weighted) [weight=10%]------------------
    language_score = 0.0
    matched_languages = [l for l in cv_languages if l in job_description]
    if cv_languages:
        language_score = min(len(matched_languages) / len(cv_languages), 1.0)
        scores["languages"] = round(language_score * 0.10, 2)
        reasoning["languages"] = f"Matched languages: {matched_languages}"
    else:
        scores["languages"] = 0.0
        reasoning["languages"] = "No languages listed in CV"
        
    #------ Total score------------------
    total_score = round(sum(scores.values()), 2)
    # ------ Recomendation based on score------------------
    if total_score >= 0.8:
        recommendation = "Strong match — highly recommended to apply"
    elif total_score >= 0.65:
        recommendation = "Good match — worth applying with tailored CV"
    elif total_score >= 0.5:
        recommendation = "Moderate match — apply only if roles are limited or if you can tailor your CV to better fit the job"
    else:
        recommendation = "Weak match — not recommended"
        
    result = {
        "job_title": job_posting.get("title", "Unknown"),
        "company": job_posting.get("company", "Unknown"),
        "url": job_posting.get("url", ""),
        "source": job_posting.get("source", ""),
        "description": job_posting.get("description", ""),
        "total_score": total_score,
        "max_score": 1.0,
        "recommendation": recommendation,
        "score_breakdown": scores,
        "reasoning": reasoning
    }
    return json.dumps(result, indent=2)
