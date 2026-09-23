import pandas as pd
import sys
import json
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / 'src'))

from costwatch.ingest import ingest_shipments
from costwatch.baselines import calculate_baselines
from costwatch.detect import flag_anomalies
from costwatch.notes import load_note_cards, load_notes_text, get_applicable_notes
from costwatch.retrieval import NoteRetriever
from costwatch.verdict import check_verdict
from costwatch.explain import generate_reason

def format_pct(val):
    if pd.isna(val):
        return ""
    return f"+{val:.1f}%" if val > 0 else f"{val:.1f}%"

def main():
    # Load data
    df = ingest_shipments('data/shipment_records.csv')
    df = calculate_baselines(df)
    df = flag_anomalies(df)
    
    cards = load_note_cards('data/note_cards.json')
    notes_text = load_notes_text('data/context_notes.csv')
    retriever = NoteRetriever(notes_text)
    
    output_rows = []
    
    # Process only flagged candidates for output, as per brief (candidate rows only)
    candidates = df[df['flagged_candidate'] == True].copy()
    
    for _, row in candidates.iterrows():
        route = row['route']
        week_of = row['week_of']
        cost = row['cost_per_tonne_km']
        vs_own = row['vs_own_history_pct']
        vs_peers = row['vs_similar_routes_pct']
        
        # 1. Get applicable notes (strict filter)
        applicable = get_applicable_notes(cards, route, week_of)
        
        is_justified = False
        matched_note_id = ""
        reason = ""
        
        if applicable:
            # Rank applicable notes (though usually 1 or 2)
            query = f"{route} cost rise"
            ranked = retriever.rank_notes(query, applicable)
            best_note_id = ranked[0]
            
            # Check verdict
            card = cards[best_note_id]
            is_just, rej_reason = check_verdict(card, vs_own)
            
            if is_just:
                is_justified = True
                matched_note_id = best_note_id
                reason = generate_reason(True, best_note_id, notes_text[best_note_id], route, week_of)
            else:
                is_justified = False
                matched_note_id = ""
                # Could be unexplained due to effect being none or magnitude too high
                # For simplicity, if we have an applicable note but it doesn't justify:
                reason = generate_reason(False, best_note_id, notes_text[best_note_id], route, week_of)
        else:
            # If no applicable notes, find the closest note globally to see if it's a trap
            all_ids = list(cards.keys())
            query = f"{route} cost rise"
            ranked = retriever.rank_notes(query, all_ids)
            best_note_id = ranked[0] if ranked else None
            is_justified = False
            matched_note_id = ""
            reason = generate_reason(False, best_note_id, notes_text.get(best_note_id) if best_note_id is not None else None, route, week_of)
            
        # Format for output
        vs_own_str = f"{format_pct(vs_own)} vs this route's past average"
        vs_peers_str = f"{format_pct(vs_peers)} vs similar-length routes this week"
        flagged_str = "No (justified)" if is_justified else "Yes"
        
        output_rows.append({
            'route': route,
            'week_of': week_of,
            'cost_per_tonne_km': round(cost, 2),
            'vs_own_history': vs_own_str,
            'vs_similar_routes': vs_peers_str,
            'flagged': flagged_str,
            'matched_note_id': matched_note_id,
            'reason': reason
        })
        
    out_df = pd.DataFrame(output_rows)
    # The required columns exactly:
    cols = ['route', 'week_of', 'cost_per_tonne_km', 'vs_own_history', 'vs_similar_routes', 'flagged', 'matched_note_id', 'reason']
    out_df = out_df[cols]
    
    out_df.to_csv('outputs/output.csv', index=False)
    
    print(f"Pipeline complete. Generated {len(out_df)} candidate rows in outputs/output.csv")
    
if __name__ == '__main__':
    main()
