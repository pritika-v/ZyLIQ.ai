import json

from app.config import CORRECTION_PROMPT_DOC
from app.pipeline.rtf_utils import load_prompt_from_txt
from app.pipeline.llm_client import call_llm
from app.pipeline.json_parser import parse_json_from_response
from app.models.pydantic_models import ExtractionResult, ValidationResult


#**** CORRECTION AGENT — Fixes issues found by the validator ****
def run_correction(document_text, extracted_json, validation_result):
    print("Running correction agent..")
    correction_prompt_template = load_prompt_from_txt(CORRECTION_PROMPT_DOC)

    #Convert the Pydantic object into a normal Python dictionary.
    # Convert validation_result to dict if it's a Pydantic object
    if isinstance(validation_result, ValidationResult):
        validation_dict=validation_result.model_dump()  # model_dump converts it into dict
    else:
        validation_dict=validation_result  # already a dict

    prompt=(correction_prompt_template.replace("{documet}", document_text[:3000]).replace("{json}", json.dumps(extracted_json, indent=2)).replace("{validation}", json.dumps(validation_dict, indent=2)))  # Trim to void token overflow
    llm_response=call_llm(prompt,max_tokens=4000)
    corrected=parse_json_from_response(llm_response, pydantic_model=ExtractionResult)

    if corrected is None:
        print("Warning: Correction agent returned unparseable response.Keeping previous version.")
        return extracted_json  # fall back to the previous extraction if correction failed
    # Convert Pydantic object back to plain dict for compatibility with rest of pipeline
    if isinstance(corrected, ExtractionResult):
        corrected=corrected.model_dump()
    print(f" Corection complete. Rows in corrected JSON: {len(corrected.get('rows',[]))}")
    return corrected
print("run_correction function defined")
