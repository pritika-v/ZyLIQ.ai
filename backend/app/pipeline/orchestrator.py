from app.config import MAX_RETRIES
from app.pipeline.rtf_utils import rtf_to_clean_text
from app.pipeline.extractor import extract_from_rtf
from app.pipeline.validator import validate_extraction
from app.pipeline.corrector import run_correction
from app.models.pydantic_models import ValidationResult


#**** ORCHESTRATOR — Extract → Validate → Correct loop ****
def process_document(rtf_path):
    attempt=1
    # Read and clean the document once — reused in every loop iteration
    original_text=rtf_to_clean_text(rtf_path)  # plain text for validation/correction

    #Initial extraction
    extracted=extract_from_rtf(rtf_path)
    if extracted is None:
        print("ERROR: Initial extraction failed. Stopping.")
        return None, None

    best_json = extracted     # track the best result so far
    best_validation = None    # track the validation of the best result
    best_score = -1.0         # track the highest total score seen

    while attempt<=MAX_RETRIES:
        print(f"\n========== Attempt {attempt}/{MAX_RETRIES} ==========")

        #Validate current extraction
        validation=validate_extraction(extracted, original_text)
        if validation is None:
            print("Validation returned None. Stopping loop.")
            break

        # Compute total score for this attempt
        if isinstance(validation, ValidationResult):
            score=validation.total_score()
        else:  # fall back if Pydantic failed and we got a raw dict
            score = (validation.get("grounding_score", 0) +
                     validation.get("schema_score", 0) +
                     validation.get("completeness_score", 0) +
                     validation.get("consistency_score", 0)) / 4
            #Consistency- if row and columns are consistent
        print(f"Total score this attempt: {score:.2f}")
        # Save this as best if it's the highest scoring so far
        if score > best_score:
            best_score = score
            best_json = extracted
            best_validation = validation
            print(f"  New best score: {best_score:.2f}")

        is_valid=validation.is_valid if isinstance(validation,ValidationResult) else validation.get("is_valid",False)
        if is_valid:
            print("Validation passed! Stopping early.")
            break
        # If we've used all retries, stop before running another correction
        if attempt >= MAX_RETRIES:
            print(f"Max retries ({MAX_RETRIES}) reached. Saving best result.")
            break
        # Run correction agent and loop again
        print("Validation failed. Sending to correction agent...")
        extracted = run_correction(original_text, extracted, validation)

        if extracted is None:
            print("Correction failed. Stopping loop.")
            break

        attempt += 1

    return best_json, best_validation

print("process_document function defined")
