from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sqlalchemy.orm import Session
from ..models.orm import CaseRecord

def compute_text_similarity(cse_id: str, batch_id: str, db: Session) -> float:
    cases = db.query(CaseRecord).filter(
        CaseRecord.batch_id == batch_id,
        CaseRecord.cse_id == cse_id,
        CaseRecord.investigation_text.isnot(None)
    ).all()
    
    texts = [c.investigation_text.strip() for c in cases 
             if c.investigation_text and len(c.investigation_text.strip()) > 5]
    
    if len(texts) < 3:
        return 0.0
    
    try:
        # Check exact and near-duplicate ratio
        vectorizer = TfidfVectorizer(min_df=1, stop_words='english', token_pattern=r'(?u)\b\w+\b')
        tfidf_matrix = vectorizer.fit_transform(texts)
        sim_matrix = cosine_similarity(tfidf_matrix)
        
        n = len(texts)
        # For each case, find max similarity with any other case
        np.fill_diagonal(sim_matrix, 0.0)
        max_sims = np.max(sim_matrix, axis=1)
        
        # High similarity ratio: fraction of cases with >0.85 similarity to another case
        high_sim_ratio = float(np.mean(max_sims >= 0.85))
        
        # Upper triangle mean
        upper_tri = [sim_matrix[i][j] for i in range(n) for j in range(i+1, n)]
        mean_sim = float(np.mean(upper_tri)) if upper_tri else 0.0
        
        # Return composite similarity signal: weighted combination of high similarity ratio and mean
        return max(high_sim_ratio, mean_sim)
    except Exception:
        return 0.0
