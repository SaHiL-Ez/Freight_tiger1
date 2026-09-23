from typing import Dict, Any, Optional

def generate_reason(is_justified: bool, 
                    note_id: Optional[str], 
                    note_text: Optional[str],
                    route: str,
                    week_of: str) -> str:
    """
    Generates a fallback template reason if LLM is not used or if LLM output fails validation.
    """
    if is_justified and note_id and note_text:
        return f"Matches note {note_id} dated {week_of}: {note_text}. The cost rise has a clear explanation."
    elif not is_justified and note_id:
        return f"The closest note ({note_id}) does not describe a valid reason for a cost rise on this route. No genuine justification found; flagged for review."
    else:
        return "No matching note found for this route or date range. Cost rise looks unexplained and worth a human review."

class ExplanationValidator:
    def validate(self, generated_text: str, is_justified: bool, note_id: Optional[str]) -> bool:
        if is_justified and note_id:
            if note_id not in generated_text:
                return False
        return True
