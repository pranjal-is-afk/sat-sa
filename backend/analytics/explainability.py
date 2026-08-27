from typing import List, Dict

def compute_attribution(features: dict, score_breakdown: dict) -> List[dict]:
    """Compute deterministic feature attributions based on score contributions."""
    
    # Map features to score components and their contribution directions
    feature_contributions = [
        # (feature_name, display_name, component, direction, weight_within_component)
        ('critical_fast_closure_rate', 'Fast Critical Closure Rate', 'rules', 'positive', 0.3),
        ('escalation_rate', 'Escalation Rate', 'peer', 'negative', 0.35),  # low = risky
        ('mean_closure_time_critical', 'Mean Critical Closure Time', 'statistical', 'negative', 0.25),
        ('investigation_text_similarity', 'Investigation Text Similarity', 'rules', 'positive', 0.2),
        ('case_linkage_rate', 'Case Linkage Rate', 'rules', 'negative', 0.15),
        ('alert_category_coverage', 'Alert Category Coverage', 'negative_space', 'negative', 0.2),
        ('critical_asset_telemetry_ratio', 'Critical Asset Telemetry', 'negative_space', 'negative', 0.3),
        ('low_activity_window_count', 'Low Activity Windows', 'statistical', 'positive', 0.15),
        ('closure_time_cv', 'Closure Time Uniformity', 'rules', 'negative', 0.15),
        ('peer_escalation_percentile', 'Escalation Peer Rank', 'peer', 'negative', 0.35),
        ('peer_closure_time_percentile', 'Closure Time Peer Rank', 'peer', '3', 0.3),
    ]
    
    result = []
    for feat_name, display, component, direction, weight in feature_contributions:
        comp_score = score_breakdown.get(component, 0.0)
        feat_val = features.get(feat_name, 0.0)
        
        # Contribution = component_score * weight * direction_multiplier
        direction_mult = 1.0 if direction == 'positive' else -1.0
        contribution = comp_score * weight * direction_mult
        
        result.append({
            'feature': display,
            'value': round(float(feat_val), 4),
            'contribution': round(contribution, 2)
        })
    
    # Sort by absolute contribution descending
    result.sort(key=lambda x: abs(x['contribution']), reverse=True)
    return result[:8]  # top 8
