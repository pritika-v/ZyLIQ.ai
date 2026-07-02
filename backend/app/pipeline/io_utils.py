import os
import json

from app.config import OUTPUT_FOLDER


#***Save results to JSON and Markdown files
"""
    Saves the extracted data in two formats:
    1. JSON file — raw structured data
    2. Markdown file — human-readable table
    Also saves the validation report as a separate JSON file.
"""
def save_results(extracted_json, validation_result, base_filename):

    #Save extracted JSON
    json_path=os.path.join(OUTPUT_FOLDER, f"{base_filename}_extracted.json")
    with open(json_path,"w", encoding="utf-8") as f:
        json.dump(extracted_json, f, indent=2)  # pretty-print with 2-space indent
    print(f" Saved JSON: {json_path}")

    #save as Markdown table
    md_path=os.path.join(OUTPUT_FOLDER, f"{base_filename}_extracted.md")
    with open(md_path, "w", encoding="utf-8") as f:
        #Write header info
        f.write(f"#Listing {extracted_json.get('listing_number','')}\n")
        f.write(f"**Title:** {extracted_json.get('title', '')}\n")
        if extracted_json.get('subtitle'):
            f.write(f"**Subtitle:** {extracted_json.get('subtitle', '')}\n")
        f.write("\n")

        columns=extracted_json.get("columns",[])
        rows=extracted_json.get("rows",[])

        if columns and rows:
            # Write markdown table header
            f.write("| "+" | ".join(columns)+" |\n")  # Column haders
            f.write("| " + " | ".join(["---"] * len(columns)) + " |\n")  # Separator

            for row in rows:
                # Get value for each column in order, replace pipes to avoid breaking table
                values=[str(row.get(col,"")).replace("|","/") for col in columns]
                f.write("| "+" | ".join(values)+" |\n")
        else:
            f.write("*No rows extracted.*\n")
    print(f"Saved Markdown: {md_path}")

    #Save validation report
    if validation_result:
        val_path=os.path.join(OUTPUT_FOLDER, f"{base_filename}_validation.json")
        with open(val_path, "w", encoding="utf-8") as f:
            json.dump(validation_result, f, indent=2)
        print(f" Saved validation: {val_path}")

    # Return paths so callers (e.g. the API layer) know where files landed
    return {
        "json_path": json_path,
        "md_path": md_path,
        "validation_path": os.path.join(OUTPUT_FOLDER, f"{base_filename}_validation.json") if validation_result else None,
    }

print("save_results function defined.")
