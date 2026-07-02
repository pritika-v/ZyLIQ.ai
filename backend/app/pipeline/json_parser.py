import re
import json


#**** FUNCTION TO SAFELY PARSE JSON FROM LLM RESPONSE***
"""
    LLMs sometimes wrap JSON in markdown code fences or add extra text.
    This function strips that and extracts the pure JSON object.
    # Optionally validates the parsed dict against a Pydantic model.
"""
def parse_json_from_response(llm_response, pydantic_model=None):
    if not llm_response:
        return None
    text=llm_response.strip()

    # Remove markdown code fences if present (```json ... ``` or ``` ... ```)
    text = re.sub(r'^```json\s*', '', text)   # remove opening ```json
    text = re.sub(r'^```\s*', '', text)       # remove opening ```
    text = re.sub(r'\s*```$', '', text)       # remove closing ```
    text = text.strip()

    #Find the JSON object: everything from first to last
    start=text.find('{')  # Find opening bracket
    end=text.rfind('}')  # Find last closing bracket

    if start==-1 or end==-1:
        print("Error: No valid JSON object found in LLM response.")
        print("raw response was:", text[:300])  # Show first 300 characters for debugging
        return None

    json_str=text[start:end+1]  # Extract just the JSON part

    #This line is creating an instance of a Pydantic model and validating the parsed JSON data against that model.
    """
    if pydantic model is
    from pydantic import BaseModel

    class Person(BaseModel):
        name: str
        age: int

    parsed = {
    "name": "Alice",
    "age": 25
    } --->pyhton dict got from json.loads

    after "pydantic_model(**parsed)", it becomes

    Person(
    name="Alice",
    age=25
    )
    """
    try:
        parsed=json.loads(json_str)  # parse string into Python dict
        #If a pydantic model is provided, validate through it
        if pydantic_model is not None:
            try:
                validated=pydantic_model(**parsed)  # creates model instance, validates types
                return validated
            except Exception as e:
                print(f"WARNING: Pydantic validation failed:{e}")
                print("Returning raw dict instead")
                return parsed
        return parsed  # if no model provided, retur raw dict

        #json.loads() converts a JSON string into a Python object (usually a dictionary or list).
    except json.JSONDecodeError as e:
        print(f"ERROR: JSON parsing failed: {e}")
        print("Attempted to parse:",json_str[:300])
        return None

print("parse_json_from_response function define with optional pydantic validation")
