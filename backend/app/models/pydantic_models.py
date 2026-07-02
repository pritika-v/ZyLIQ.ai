"""
You define
Age-must be integer, Price-must be positive, Name-minimum 3 letters

Now User sends Price=-500
Pydantic immediately rejects it.

It also converts data.
Client sends
"25" Pydantic converts it into 25(integer) automatically when possible.

It also converts Python objects into JSON.
FastAPI relies heavily on Pydantic.
"""

#****PYDANTIC MODELS -Define what valid LLM output looks like ****
#Pydantic checks that the LLM's json has the right fields and types
#IF a field is missing, it uses the default value instead of crashing

from pydantic import BaseModel, Field
from typing import List, Optional

class ExtractionResult(BaseModel):
    listing_number: str=""  # e.g. "16.2.4.1"
    title: str=""  #plain text title
    columns: List[str]=Field(default_factory=list)  #column headers
    rows:List[dict]=Field(default_factory=list)  #data rows
    #defines two model fields with empty lists as their default values.

class ValidationResult(BaseModel):
    is_valid: bool = False             # overall pass/fail
    listing_number_ok: bool = False    # listing number matched?
    title_ok: bool = False             # title matched?
    columns_ok: bool = False           # columns correct?
    rows_ok: bool = False              # rows correct?
    grounding_score: float = 0.0       # 0.0-1.0: values match source
    schema_score: float = 0.0          # 0.0-1.0: required fields present
    completeness_score: float = 0.0    # 0.0-1.0: fraction of rows captured
    consistency_score: float = 0.0     # 0.0-1.0: internal consistency
    issues_found: List[str] = Field(default_factory=list)   # list of issue descriptions
    corrected_rows: List[dict] = Field(default_factory=list)  # any corrected rows
    summary: str = ""                  # one sentence verdict

    def total_score(self) -> float:
        #Average of all four scores - used to compare attempts
        return (self.grounding_score+self.schema_score+ self.completeness_score+self.consistency_score)/4
