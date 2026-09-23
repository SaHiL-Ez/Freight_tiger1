from typing import Optional, Dict, Any, Tuple

def check_verdict(card: Dict[str, Any], observed_rise_pct: float, tolerance: float = 5.0) -> Tuple[bool, str]:
    """
    Deterministic gate to check if a note justifies an observed rise.
    Assumes the note already passed the scope_routes and date window checks.
    
    Returns (is_justified, rejection_reason)
    """
    if card['effect'] != 'raises':
        return False, f"Note effect is '{card['effect']}', not 'raises'."
        
    if card['magnitude'] is not None:
        min_mag, max_mag = card['magnitude']
        # If the observed rise is much larger than the note's stated magnitude + tolerance
        if observed_rise_pct > (max_mag + tolerance):
            return False, f"Observed rise ({observed_rise_pct:.1f}%) far exceeds note magnitude ({max_mag}%)."
            
    return True, ""
