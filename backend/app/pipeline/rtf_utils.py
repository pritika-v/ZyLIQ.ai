import os
import re
from striprtf.striprtf import rtf_to_text


#****CREATE A FUNCTION TO READ THE text PROMPT FILE AND RETURN ITS TEXT***

def load_prompt_from_txt(txt_path):
    with open(txt_path, "r", encoding="utf-8") as f:
        return f.read()


#***CREATE A FUNCTION TO READ RTF FILES AND CONVERT TO PLAIN TEXT***
""" rtf is something like this
{\rtf1\ansi
{\fonttbl\f0 Arial;}
\b Listing 16.2.1.1\b0
} The LLM would see all the formatting garbage. therefore convert rtf to plain text and give it to the llm endpoint
"""
def rtf_to_clean_text(rtf_path):
    with open(rtf_path, "r", encoding="latin-1") as f:  # latin-1 handles special chars
        rtf_content=f.read()  # read raw rtf content
    plain_text=rtf_to_text(rtf_content)  # Convert rtf content to plain text. rtf_to_text comes from striprtf
    return plain_text
print("rtf_to_clean_text function defined.")


#*** FUNCTION TO SPLIT TEXT INTO PAGES
def split_into_pages(text):
    """
    Split text into pages.

    Detect repeated table headers(first column = Subject ID) and
    use them as page boundaries.
    """
    matches=list(
        re.finditer(
            r'Subject ID',
            text
        )
    )  # finditer - searches the entire text and returns all occurrences of a pattern.
    # In our case it is Subject ID
    print("Subject ID occurrences:", len(matches))

    if len(matches)<=1:  # How many Subject ID headers were found?
        print("Total pages found: 1")
        return [text]

    pages=[]
    """
    pages = [
               page1,
               page2,
               page3
            ]
    """

    for i in range(len(matches)):  # Loop over every "Subject ID" found.
        start=matches[i].start()
        if i<len(matches)-1:
            end=matches[i+1].start()  # text from match till next match
        else:
            end=len(text)
        page_text=text[start:end].strip()
        if page_text:
            pages.append(page_text)
    print(f"Total pages found using SUbject ID headers: {len(pages)}")
    return pages

print ("split_into_pages function defined")


#*** FUNCTION TO REMOVE FOOTER/HEADER NOISE FROM EACH PAGE***
"""
    Removes common noise from clinical trial RTF pages:
    - Footer lines (abbreviations, dates, program paths, page numbers)
    - Separator lines made of dashes or equals signs
    - Lines that are just whitespace

    We keep: listing number line, title line, column headers, data rows.
"""
def clean_page_text(page_text):
    lines=page_text.split("\n")  # split page into individual lines
    cleaned=[]

    for line in lines:
        stripped=line.strip()

        #Skip empty lines
        if not stripped:
            continue

        #SKip separator lines (dashes or equals)
        if re.match(r'^[-=_]{5,}$', stripped):
            continue

        # Skip footer patterns: abbreviations, notes, program paths, timestamps
        if re.match(r'^(Abbreviations?|Notes?|a\s*=|b\s*=|c\s*=|Source:|Program:|Run)',stripped,re.IGNORECASE):
            continue

        # Skip lines that are just a page number like "Page 1 of 5"
        if re.match(r'^Page\s+\d+\s+of\s+\d+', stripped, re.IGNORECASE):
            continue

        cleaned.append(stripped)  # Keep each line if it passed all checks

    return "\n".join(cleaned)  # rejoin cleaned lines

print("clean_page_text function defined")


#*** EXTRACT LISTING NUMBER AND TITLE DIRECTLY FROM RAW RTF ***
# WHY: striprtf drops the header rows entirely — listing number and title
# only exist in the raw RTF cell text, using the \loch\fN TEXT\cell pattern.
# We read those cells directly before striprtf ever runs.

def extract_metadata_from_raw_rtf(raw_rtf):
    # RTF stores visible text in cells as: \loch\fN TEXT\cell
    cell_pattern = re.compile(r'\\loch\\f\d+\s+(.*?)\\cell', re.DOTALL)
    raw_cells=cell_pattern.findall(raw_rtf)  # get all raw cell matches

    clean_cells=[]
    for cell in raw_cells:
        text = re.sub(r'\{[^{}]*\}', '', cell)        # remove embedded RTF groups like {...}
        text = re.sub(r'\\[a-zA-Z]+\d*\s?', '', text)  # remove RTF control words like \fs16
        text = text.replace('\n', ' ').strip()         # flatten newlines, trim whitespace
        if text:
            clean_cells.append(text)
    listing_number=""
    title=""

    for i, cell in enumerate(clean_cells):
        # Find the cell that is exactly "Listing X.X.X.X"
        m = re.match(r'^Listing\s+([\d\.]+)\s*$', cell.strip(), re.IGNORECASE)
        if m:
            listing_number=m.group(1)  # capture just the number e.g. "16.2.4.1"
            for j in range(i + 1, min(i + 6, len(clean_cells))):
                candidate = clean_cells[j].strip()
                # Skip known non-title cells
                if re.match(r'^(Page|Protocol|Source:|Program:|Safety Analysis|Treatment|Age is)', candidate, re.IGNORECASE):
                    continue
                if re.match(r'^[\d\s\.]+$', candidate):
                    continue  # skip number-only cells
                title = candidate  # first clean candidate is the title
                break
            break  # stop after finding the listing number cell

    return {"listing_number": listing_number, "title": title}

print("extract_metadata_from_raw_rtf function defined")
