import pandas as pd

def ingest_shipments(file_path: str) -> pd.DataFrame:
    """
    Reads shipment records and aggregates them by route and week.
    Returns a dataframe with columns:
    - route (origin-destination)
    - route_type
    - week_of (Monday date)
    - cost_per_tonne_km (volume-weighted)
    """
    df = pd.read_csv(file_path)
    
    # Create route column
    df['route'] = df['origin'].astype(str) + '-' + df['destination'].astype(str)  # type: ignore
    
    # Parse dates and get the Monday of that week
    df['shipment_date'] = pd.to_datetime(df['shipment_date'])
    df['week_of'] = df['shipment_date'] - pd.to_timedelta(df['shipment_date'].dt.weekday, unit='d')  # type: ignore
    
    # Calculate tonne_km per shipment
    df['tonne_km'] = df['quantity_tonnes'] * df['distance_km']
    
    # Aggregate by route and week
    grouped = df.groupby(['route', 'route_type', 'week_of']).agg(
        total_cost=('freight_cost_inr', 'sum'),
        total_tonne_km=('tonne_km', 'sum'),
        shipment_count=('shipment_id', 'count')
    ).reset_index()
    
    # Calculate volume-weighted cost per tonne-km
    grouped['cost_per_tonne_km'] = grouped['total_cost'] / grouped['total_tonne_km']
    
    # Format week_of as YYYY-MM-DD
    grouped['week_of'] = grouped['week_of'].dt.strftime('%Y-%m-%d')  # type: ignore
    
    # Sort for baseline calculation
    grouped = grouped.sort_values(by=['route', 'week_of']).reset_index(drop=True)
    
    return grouped
