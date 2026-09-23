from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict

class NoteRetriever:
    def __init__(self, notes_text: Dict[str, str]):
        self.notes_text = notes_text
        self.note_ids = list(notes_text.keys())
        self.texts = list(notes_text.values())
        
        self.vectorizer = TfidfVectorizer(stop_words='english')
        if self.texts:
            self.tfidf_matrix = self.vectorizer.fit_transform(self.texts)
            
    def rank_notes(self, query: str, candidate_ids: List[str]) -> List[str]:
        """
        Ranks candidate_ids based on similarity to query.
        """
        if not candidate_ids:
            return []
            
        query_vec = self.vectorizer.transform([query])
        
        # Get indices of candidates in self.note_ids
        candidate_indices = [self.note_ids.index(nid) for nid in candidate_ids]
        
        # Calculate similarity between query and candidates
        candidate_matrix = self.tfidf_matrix[candidate_indices]  # type: ignore
        similarities = cosine_similarity(query_vec, candidate_matrix).flatten()
        
        # Sort by similarity descending
        ranked_pairs = sorted(zip(candidate_ids, similarities), key=lambda x: x[1], reverse=True)
        return [pair[0] for pair in ranked_pairs]
