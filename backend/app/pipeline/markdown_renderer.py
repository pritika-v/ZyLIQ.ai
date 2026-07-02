def render_markdown(extracted_json: dict) -> str:
    """
    Same markdown-building logic as inside save_results() (notebook Cell 15),
    pulled out so we can both (a) write it to disk via io_utils.save_results
    and (b) return it directly in the API response / store it in Postgres
    without parsing the file back off disk.
    """
    lines = []
    lines.append(f"#Listing {extracted_json.get('listing_number','')}")
    lines.append(f"**Title:** {extracted_json.get('title', '')}")
    if extracted_json.get('subtitle'):
        lines.append(f"**Subtitle:** {extracted_json.get('subtitle', '')}")
    lines.append("")

    columns = extracted_json.get("columns", [])
    rows = extracted_json.get("rows", [])

    if columns and rows:
        lines.append("| " + " | ".join(columns) + " |")
        lines.append("| " + " | ".join(["---"] * len(columns)) + " |")
        for row in rows:
            values = [str(row.get(col, "")).replace("|", "/") for col in columns]
            lines.append("| " + " | ".join(values) + " |")
    else:
        lines.append("*No rows extracted.*")

    return "\n".join(lines)
