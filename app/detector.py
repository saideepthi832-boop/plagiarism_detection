from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

def get_sentences(text):
    return [s.strip() for s in text.split('.') if len(s.strip()) > 20]

def compare_documents(new_text, existing_docs):
    new_sentences = get_sentences(new_text)
    if not new_sentences:
        return []
    
    new_embeddings = model.encode(new_sentences)
    results = []

    for doc in existing_docs:
        existing_sentences = get_sentences(doc["text"])
        if not existing_sentences:
            continue
        existing_embeddings = model.encode(existing_sentences)
        sim_matrix = cosine_similarity(new_embeddings, existing_embeddings)
        max_scores = sim_matrix.max(axis=1)

        matches = []
        for i, score in enumerate(max_scores):
            if score > 0.80:
                j = sim_matrix[i].argmax()
                matches.append({
                    "new_sentence": new_sentences[i],
                    "matched_sentence": existing_sentences[j],
                    "score": round(float(score) * 100, 2)
                })

        overall = round(float(np.mean(max_scores)) * 100, 2)
        results.append({
            "source": doc["title"],
            "overall_similarity": overall,
            "matches": matches
        })

    return results