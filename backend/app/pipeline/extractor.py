import os
import re
import json

from app.config import EXTRACTION_PROMPT_DOC
from app.pipeline.rtf_utils import (
    rtf_to_clean_text,
    split_into_pages,
    clean_page_text,
    extract_metadata_from_raw_rtf,
    load_prompt_from_txt,
)
from app.pipeline.llm_client import call_llm
from app.pipeline.json_parser import parse_json_from_response

# Load the prompt template once (same as notebook Cell 4)
extraction_prompt_template = load_prompt_from_txt(EXTRACTION_PROMPT_DOC)


#****MAIN EXTRACTION FUNCTION- HANDLING MULTIPLE PAGES ***
"""
    Full extraction pipeline for one RTF file:
    1. Convert RTF to text
    2. Split into pages
    3. Extract listing number, title, columns from page 1
    4. Extract rows from ALL pages and combine
    5. Return final combined JSON
"""
"""
Take the first page first, collect the column names from it, and then take the remaining pages
"""
def extract_from_rtf(rtf_path):
    print(f"\nProcessing: {os.path.basename(rtf_path)}")

    # Read raw RTF first (needed for metadata — striprtf drops header rows)
    with open(rtf_path, "r", encoding="latin-1", errors="ignore") as f:  # latin-1 handles special chars
        raw_rtf = f.read()
    # Extract listing number and title from raw RTF BEFORE striprtf runs
    # (striprtf drops the header table rows, so metadata is lost after conversion)
    metadata = extract_metadata_from_raw_rtf(raw_rtf)
    print(f"Metadata extracted: {metadata}")

    # Step 1: Convert RTF to plain text for table data extraction
    full_text = rtf_to_clean_text(rtf_path)

    #step 2: Split into pages
    pages=split_into_pages(full_text)

    if not pages:
        print("Error: No text extracted from RTF file.")
        return None

    # Step 3: Extract structure from PAGE 1 (listing number, title, columns + first rows)
    print("Extracting structure rom page 1..")
    page1_clean=clean_page_text(pages[0])
    CHUNK_SIZE=1500

    page1_chunks=[
        page1_clean[i:i+CHUNK_SIZE]
        for i in range(0,len(page1_clean), CHUNK_SIZE)
    ]

    print(f"Page 1 split into {len(page1_chunks)} chunks")
    """
    page1_chunks becomes:
    Chunk 1 : chars 0-1499
    Chunk 2 : chars 1500-2999
    Chunk 3 : chars 3000-4499 etccc...
    """
    base_result = None
    all_rows = []

    for chunk_num, chunk_text in enumerate(page1_chunks, start=1):

        print(f"Processing chunk {chunk_num}/{len(page1_chunks)}")

        extraction_prompt = extraction_prompt_template.replace("{document}",chunk_text)  # Inserting each chunk into the prompt

        llm_response = call_llm(extraction_prompt,max_tokens=1000)  # SEnd prompt to LLM
        """print(llm_response[:1000])"""

        chunk_result = parse_json_from_response(llm_response)  # Convert response into python dictionary
        print("chunk_result type:", type(chunk_result))
        if chunk_result is None:
            print("Chunk parsing failed")
            continue
        if chunk_result is None:
            continue

        print("Rows extracted from chunk:",len(chunk_result.get("rows", [])))  # Shows number of extracted rows

        #This runs only for this first valid chunk. Initialising base result only once
        if base_result is None:

            #Creating meta data structure
            base_result = {
                "listing_number": chunk_result.get("listing_number", ""),
                "title": chunk_result.get("title", ""),
                #"subtitle": chunk_result.get("subtitle", ""),
                "columns": chunk_result.get("columns", []),
                "rows": []
            }

        all_rows.extend(chunk_result.get("rows", []))  # Collect all rows

    if base_result is None:
        print("ERROR: No valid extraction returned from any chunk")
        return None

    base_result["rows"] = all_rows
    base_result["listing_number"] = metadata["listing_number"]
    base_result["title"] = metadata["title"]
    print("Total rows collected:", len(all_rows))

    columns=base_result.get("columns",[])

    print(
    f"Page 1 complete. "
    f"Columns={len(columns)}, "
    f"Rows={len(all_rows)}"
    )

    #Extract rows from remaining pages (pae 2,3,4..)
    for page_num, page_text in enumerate(pages[1:], start=2):
        print(f" Extracting rows from page {page_num}...")
        page_clean=clean_page_text(page_text)  # Clean each page

        # For pages 2+, we tell the LLM the column names so it maps correctly
        continuation_prompt = f"""You are a clinical trial row extraction engine.

The column headers for this table are:
{columns}

Extract ONLY the data rows from the text below.
Rules:
- Return ONLY valid JSON. Nothing else.
- Output must be a JSON array: [{{...}}, {{...}}]
- Each row is a dict with the column names as keys.
- Skip any repeated header rows (lines starting with 'Subject ID' that look like headers).
- Skip footers, dates, abbreviations, page numbers.
- If a cell is blank, use empty string "".
- Continuation lines (wrapped text) belong to the SAME row.

Document page text:
{page_clean}"""

        llm_response=call_llm(continuation_prompt, max_tokens=3000)

        if llm_response:
            # Response is an array this time, not a full object
            text = llm_response.strip()
            text = re.sub(r'^```json\s*', '', text)  # strip markdown fences
            text = re.sub(r'^```\s*', '', text)
            text = re.sub(r'\s*```$', '', text)
            text = text.strip()

            # Find the JSON array
            start = text.find('[')
            end = text.rfind(']')

            if start!=-1 and end!=-1:
                try:
                    page_rows=json.loads(text[start:end+1])  # parse array
                    all_rows.extend(page_rows)  # Add to running list
                    print(f" Page{page_num}: added {len(page_rows)} rows. Total: {len(all_rows)}")
                except json.JSONDecodeError as e:
                    print(f"    WARNING: Could not parse rows from page {page_num}: {e}")
            else:
                print(f"    WARNING: No array found in response for page {page_num}")

    base_result["rows"]=all_rows
    print(f" DONE. Total rows extracted: {len(all_rows)}")

    return base_result

print("extract_from_rtf function defined")
