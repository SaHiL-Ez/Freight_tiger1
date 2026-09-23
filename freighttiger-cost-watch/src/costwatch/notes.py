import json
import pandas as pd
from typing import Dict, Any, List

def load_note_cards(cards_path: str) -> Dict[str, Dict[str, Any]]:
    with open(cards_path, 'r') as f:
        cards = json.load(f)
    return {card['note_id']: card for card in cards}

def load_notes_text(csv_path: str) -> Dict[str, str]:
    df = pd.read_csv(csv_path)
    return dict(zip(df['note_id'], df['note']))

def get_applicable_notes(cards: Dict[str, Dict[str, Any]], route: str, week_of: str) -> List[str]:
    """
    Hard metadata filter: returns note_ids that apply to the route and overlap with the week.
    """
    week_start = pd.to_datetime(week_of)
    # week ends on Sunday
    week_end = week_start + pd.Timedelta(days=6)
    
    applicable = []
    for note_id, card in cards.items():
        # Check route
        if route not in card['scope_routes'] and "All Routes" not in card['scope_routes']:
            continue
            
        # Check dates
        note_start = pd.to_datetime(card['start'])
        note_end = pd.to_datetime(card['end'])
        
        # Overlap condition: week_start <= note_end AND week_end >= note_start
        if week_start <= note_end and week_end >= note_start:
            applicable.append(note_id)
            
    return applicable
