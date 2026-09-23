import pandas as pd
import numpy as np

def calculate_baselines(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates baselines for each route-week:
    - past_8w_avg: trailing 8-week average (strictly before current week)
    - peer_avg: average of other routes of the same route_type in the same week
    """
    # 1. vs own history (8-week trailing average, no look-ahead)
    # Since weeks are continuous and we sorted by route and week, we can use rolling on cost_per_tonne_km
    # with shift(1) to avoid look-ahead.
    
    # We first ensure the data has consecutive weeks (it was said no nulls, every route has data every week)
    # But just in case, rolling(window=8, min_periods=1) on a shift(1) series gives the trailing up to 8.
    
    def get_trailing_avg(group):
        # shift(1) means the current row is ignored
        # rolling(8, min_periods=1) will average the up-to-8 previous non-null values
        return group['cost_per_tonne_km'].shift(1).rolling(window=8, min_periods=1).mean()
        
    df['past_8w_avg'] = df.groupby('route', group_keys=False).apply(get_trailing_avg)
    
    # Calculate % increase vs own history
    df['vs_own_history_pct'] = ((df['cost_per_tonne_km'] - df['past_8w_avg']) / df['past_8w_avg']) * 100
    
    # 2. vs similar routes (peer average excluding self)
    # For each week and route_type, we want the mean of OTHER routes.
    # We can calculate this by taking the sum of all routes in that type-week, subtracting the current route's cost,
    # and dividing by (count - 1). If count is 1, peer_avg is NaN.
    
    week_type_agg = df.groupby(['week_of', 'route_type']).agg(
        total_cost_sum=('cost_per_tonne_km', 'sum'),
        route_count=('route', 'count')
    ).reset_index()
    
    df = pd.merge(df, week_type_agg, on=['week_of', 'route_type'], how='left')
    
    # Calculate peer_avg
    df['peer_avg'] = np.where(
        df['route_count'] > 1,
        (df['total_cost_sum'] - df['cost_per_tonne_km']) / (df['route_count'] - 1),
        np.nan
    )
    
    # Calculate % vs similar routes
    df['vs_similar_routes_pct'] = ((df['cost_per_tonne_km'] - df['peer_avg']) / df['peer_avg']) * 100
    
    # Cleanup temp columns
    df = df.drop(columns=['total_cost_sum', 'route_count'])
    
    return df
