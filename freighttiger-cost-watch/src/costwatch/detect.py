import pandas as pd

def flag_anomalies(df: pd.DataFrame, 
                   spike_threshold: float = 15.0, 
                   drift_threshold: float = 10.0,
                   peer_gap_increase_threshold: float = 5.0) -> pd.DataFrame:
    """
    Flags routes that have an unexplained cost rise.
    Returns the dataframe with a 'flagged_candidate' boolean column.
    
    A route is flagged if:
    1. It has a sharp spike (vs_own_history_pct > spike_threshold)
    OR
    2. It has slow drift (long-term cost vs recent cost) AND its peer gap has widened.
    """
    df = df.copy()
    
    # 1. Spike signal
    spike_signal = df['vs_own_history_pct'] > spike_threshold
    
    # 2. Drift signal
    # Calculate a long-term (e.g., 26-week) trailing average for drift detection
    def get_long_term_avg(group):
        return group['cost_per_tonne_km'].shift(1).rolling(window=26, min_periods=4).mean()
        
    df['past_26w_avg'] = df.groupby('route', group_keys=False).apply(get_long_term_avg)
    df['vs_long_term_pct'] = ((df['cost_per_tonne_km'] - df['past_26w_avg']) / df['past_26w_avg']) * 100
    
    # We also need to check if peer gap is increasing to avoid flagging a systemic market shift
    # peer gap = cost_per_tonne_km - peer_avg
    # Let's compute a long-term peer gap average
    df['peer_gap'] = df['cost_per_tonne_km'] - df['peer_avg']
    
    def get_long_term_peer_gap(group):
        return group['peer_gap'].shift(1).rolling(window=26, min_periods=4).mean()
        
    df['past_26w_peer_gap'] = df.groupby('route', group_keys=False).apply(get_long_term_peer_gap)
    
    # gap increase in absolute terms (or percentage relative to peer_avg)
    # If a route's cost goes up 10% but peers also go up 10%, the gap relative to peer might stay similar.
    # Let's say gap increase is significant if current gap > past gap by peer_gap_increase_threshold % of peer_avg
    # Or just simpler: vs_similar_routes_pct > peer_gap_increase_threshold (it's significantly above peers)
    # The prompt hints: "Mumbai-Pune is structurally about 12% above Delhi-Jaipur every week... raw peer threshold would flag it forever"
    # So we need to compare current vs_similar_routes_pct against historical vs_similar_routes_pct
    
    def get_long_term_similar_pct(group):
        return group['vs_similar_routes_pct'].shift(1).rolling(window=26, min_periods=4).mean()
        
    df['past_26w_similar_pct'] = df.groupby('route', group_keys=False).apply(get_long_term_similar_pct)
    
    # Drift signal is true if long term cost increased significantly AND the gap vs peers also widened
    drift_signal = (df['vs_long_term_pct'] > drift_threshold) & \
                   ((df['vs_similar_routes_pct'] - df['past_26w_similar_pct']) > peer_gap_increase_threshold)
                   
    # Ensure they are boolean
    spike_signal = spike_signal.fillna(False)
    drift_signal = drift_signal.fillna(False)
    
    df['flagged_candidate'] = spike_signal | drift_signal
    
    # Clean up temp columns
    df = df.drop(columns=['past_26w_avg', 'vs_long_term_pct', 'peer_gap', 'past_26w_peer_gap', 'past_26w_similar_pct'])
    
    return df
