import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from costwatch.ingest import ingest_shipments
from costwatch.baselines import calculate_baselines

def main():
    df = ingest_shipments('data/shipment_records.csv')
    df_base = calculate_baselines(df)
    
    # 1. Delhi-Jaipur 2024-11-11 at +35.5% / +21.0%
    r1 = df_base[(df_base['route'] == 'Delhi-Jaipur') & (df_base['week_of'] == '2024-11-11')]
    print(r1[['route', 'week_of', 'cost_per_tonne_km', 'vs_own_history_pct', 'vs_similar_routes_pct']])

    # 2. Ahmedabad-Mumbai 2025-01-20 at +29.5% / +22.5%
    r2 = df_base[(df_base['route'] == 'Ahmedabad-Mumbai') & (df_base['week_of'] == '2025-01-20')]
    print(r2[['route', 'week_of', 'cost_per_tonne_km', 'vs_own_history_pct', 'vs_similar_routes_pct']])

    # 3. Mumbai-Pune 2025-09-15 at +9.2% / +23.6%
    r3 = df_base[(df_base['route'] == 'Mumbai-Pune') & (df_base['week_of'] == '2025-09-15')]
    print(r3[['route', 'week_of', 'cost_per_tonne_km', 'vs_own_history_pct', 'vs_similar_routes_pct']])

if __name__ == '__main__':
    main()
