import pandas as pd
import sys

def check_format(csv_path: str):
    try:
        df = pd.read_csv(csv_path, dtype=str)
    except Exception as e:
        print(f"Failed to read CSV: {e}")
        return False
        
    expected_cols = [
        'route', 'week_of', 'cost_per_tonne_km', 
        'vs_own_history', 'vs_similar_routes', 
        'flagged', 'matched_note_id', 'reason'
    ]
    
    # 1. Check columns exactly
    if list(df.columns) != expected_cols:
        print(f"Column mismatch.\nExpected: {expected_cols}\nGot: {list(df.columns)}")
        return False
        
    # 2. Check flagged values
    invalid_flags = df[~df['flagged'].isin(['Yes', 'No (justified)'])]
    if not invalid_flags.empty:
        print(f"Invalid values in 'flagged' column. Must be exactly 'Yes' or 'No (justified)'. Found: {invalid_flags['flagged'].unique()}")
        return False
        
    print("Format check passed. 0 errors.")
    return True

if __name__ == '__main__':
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = 'outputs/output.csv'
    
    success = check_format(path)
    if not success:
        sys.exit(1)
