import numpy as np
from typing import Dict

def compute_z_scores(all_features: Dict[str, dict]) -> Dict[str, dict]:
    """Compute Z-scores for each CSE across all CSEs in batch."""
    if not all_features:
        return {}
    
    cse_ids = list(all_features.keys())
    feature_names = list(next(iter(all_features.values())).keys())
    
    z_scores = {cse_id: {} for cse_id in cse_ids}
    
    for feat in feature_names:
        values = [all_features[cid].get(feat, 0.0) for cid in cse_ids]
        arr = np.array(values, dtype=float)
        mean = np.mean(arr)
        std = np.std(arr)
        if std < 1e-9:
            for cid in cse_ids:
                z_scores[cid][feat] = 0.0
        else:
            for i, cid in enumerate(cse_ids):
                z = (arr[i] - mean) / std
                z_scores[cid][feat] = float(np.clip(z, -3.0, 3.0))
    
    return z_scores


def compute_peer_ranks(all_features: Dict[str, dict], 
                       sector_map: Dict[str, str]) -> Dict[str, dict]:
    """Compute percentile rank of each CSE within its sector for key metrics."""
    peer_ranks = {cse_id: {} for cse_id in all_features}
    
    rank_features = [
        'escalation_rate', 'mean_closure_time_critical', 
        'critical_fast_closure_rate', 'critical_asset_telemetry_ratio',
        'alert_category_coverage'
    ]
    
    # Group by sector
    sectors = {}
    for cse_id, sector in sector_map.items():
        sectors.setdefault(sector, []).append(cse_id)
    
    # For CSEs not in any sector group, use all CSEs as peers
    all_cse_ids = list(all_features.keys())
    if len(all_cse_ids) == 1:
        # Only one CSE: use neutral ranks
        for cse_id in all_cse_ids:
            for feat in rank_features:
                peer_ranks[cse_id][feat] = 50.0
        return peer_ranks
    
    for sector, members in sectors.items():
        if len(members) < 2:
            # Not enough peers, use all CSEs as reference
            peer_group = all_cse_ids
        else:
            peer_group = members
        
        for feat in rank_features:
            vals = {cid: all_features[cid].get(feat, 0.0) for cid in peer_group}
            sorted_vals = sorted(vals.values())
            n = len(sorted_vals)
            
            for cse_id in members:
                if cse_id not in all_features:
                    continue
                val = all_features[cse_id].get(feat, 0.0)
                # Percentile: fraction of peers with lower value
                rank = sum(1 for v in sorted_vals if v < val) / n * 100
                peer_ranks[cse_id][feat] = float(rank)
    
    # Update peer feature placeholders
    for cse_id in all_features:
        peer_ranks[cse_id]['peer_escalation_percentile'] = peer_ranks[cse_id].get('escalation_rate', 50.0)
        peer_ranks[cse_id]['peer_closure_time_percentile'] = peer_ranks[cse_id].get('mean_closure_time_critical', 50.0)
    
    return peer_ranks
