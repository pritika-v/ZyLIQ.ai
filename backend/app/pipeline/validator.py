import json

from app.config import REVIEW_PROMPT_DOC
from app.pipeline.rtf_utils import load_prompt_from_txt
from app.pipeline.llm_client import call_llm
from app.pipeline.json_parser import parse_json_from_response
from app.models.pydantic_models import ValidationResult


#****VALIDATION FUNCTION--- REVIEWS EXTRACTED JSON AGAINST SOURCE +SCORES****
"""
    Sends both the original document text and the extracted JSON to the LLM.
    The LLM checks for accuracy, missing rows, wrong mappings, etc.
    Returns a validation report as a dict.
"""

def validate_extraction(extracted_json, original_text):
    print("Running Validation")

    # Load the review prompt template from the Word doc
    review_prompt_template = load_prompt_from_txt(REVIEW_PROMPT_DOC)

    # Use only first 3000 chars of original text to avoid token overflow
    # (enough for the LLM to check structure, column names, and a few rows)
    trimmed_text=original_text[:3000]

    # ── TRIM extracted JSON before sending to LLM ─────────────────────────
    # Sending 400+ rows causes 500 errors on the LLM server (prompt too large)
    # We send metadata + first 10 rows as a representative sample
    sampled_json = {
        "listing_number": extracted_json.get("listing_number", ""),
        "title":          extracted_json.get("title", ""),
        "columns":        extracted_json.get("columns", []),
        "total_rows":     len(extracted_json.get("rows", [])),  # tell LLM how many rows exist
        "rows_sample":    extracted_json.get("rows", [])[:10]   # only first 10 rows
    }

    #Fill in the template placeholders
    review_prompt=(review_prompt_template.replace("{document}",trimmed_text).replace("{extracted_json}", json.dumps(extracted_json, indent=2)))

    llm_response=call_llm(review_prompt, max_tokens=2000)
    # Parse AND validate through Pydantic — ensures all score fields exist with defaults
    validation_result=parse_json_from_response(llm_response,  pydantic_model=ValidationResult)
    if validation_result is None:
        print("WARNING: Validation response could not be parsed. Returning default failed result.")
        return ValidationResult()
    """
    you're manually computingone out of  four scores in Python code
    schema_score
    Because the LLM is unreliable for things Python can measure exactly
    """
    # ── SCHEMA SCORE: computed in Python (exact, not LLM's guess) ──────────
    # Checks whether all required top-level fields are present and non-empty
    required_fields=["listing_number","title", "columns","rows"]
    present=sum(1 for f in required_fields if extracted_json.get(f) not in [None,"",[]])
    validation_result.schema_score = round(present / len(required_fields), 2)

    # All other scores (grounding, completeness, consistency) come from LLM
    print(f"  is_valid           : {validation_result.is_valid}")
    print(f"  grounding_score    : {validation_result.grounding_score:.2f}   ← LLM")
    print(f"  schema_score       : {validation_result.schema_score:.2f}   ← Python")
    print(f"  completeness_score : {validation_result.completeness_score:.2f}   ← LLM")
    print(f"  consistency_score  : {validation_result.consistency_score:.2f}   ← LLM")
    print(f"  total_score        : {validation_result.total_score():.2f}")
    if validation_result.issues_found:
        print(f"  Issues: {validation_result.issues_found}")

    return validation_result

print("validate_extraction function defined.")
