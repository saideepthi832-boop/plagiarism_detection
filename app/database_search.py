import requests
import re
from difflib import SequenceMatcher

CROSSREF_API = "https://api.crossref.org/works"

def get_key_sentences(text, count=3):
    """Extract longest/most meaningful sentences"""
    sentences = [s.strip() for s in re.split(r'[.!?]', text) if len(s.strip()) > 40]
    sentences = sorted(sentences, key=len, reverse=True)
    return sentences[:count]

def get_keywords(text, count=6):
    """Extract important keywords from text"""
    stopwords = {
        'the','a','an','and','or','but','in','on','at','to','for',
        'of','with','by','from','is','are','was','were','be','been',
        'has','have','had','this','that','these','those','it','its',
        'we','our','they','their','you','your','i','my','as','not',
        'can','will','would','could','should','may','might','also',
        'than','then','when','which','who','what','how','there'
    }
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    freq = {}
    for w in words:
        if w not in stopwords:
            freq[w] = freq.get(w, 0) + 1
    sorted_words = sorted(freq, key=freq.get, reverse=True)
    return sorted_words[:count]

def search_crossref_by_query(query, rows=5):
    """Search CrossRef with a text query"""
    try:
        response = requests.get(
            CROSSREF_API,
            params={
                "query": query,
                "rows": rows,
                "select": "title,author,DOI,abstract,published,container-title"
            },
            headers={"User-Agent": "PlagiarismDetector/1.0"},
            timeout=10
        )
        if response.status_code == 200:
            items = response.json().get('message', {}).get('items', [])
            results = []
            for item in items:
                title = item.get('title', [''])[0] if item.get('title') else ''
                authors = item.get('author', [])
                author_names = ', '.join(
                    f"{a.get('given','')} {a.get('family','')}".strip()
                    for a in authors[:3]
                )
                doi = item.get('DOI', '')
                abstract = item.get('abstract', '')
                # Clean HTML tags from abstract
                abstract = re.sub(r'<[^>]+>', '', abstract)
                journal = item.get('container-title', [''])[0] if item.get('container-title') else ''
                published = item.get('published', {}).get('date-parts', [['']])[0][0]

                if title:
                    results.append({
                        'title': title,
                        'authors': author_names or 'Unknown',
                        'doi': doi,
                        'url': f"https://doi.org/{doi}" if doi else '',
                        'abstract': abstract[:400] + '...' if len(abstract) > 400 else abstract,
                        'journal': journal,
                        'year': published
                    })
            return results
    except Exception as e:
        print(f"CrossRef error: {e}")
    return []

def calculate_similarity(text1, text2):
    """Calculate text similarity percentage"""
    if not text1 or not text2:
        return 0
    return round(SequenceMatcher(None, text1.lower(), text2.lower()).ratio() * 100, 2)

def search_academic_databases(text):
    """
    Main function - searches CrossRef using:
    1. Key sentences from text
    2. Keywords from text
    Returns ranked list of matching papers
    """
    if not text or len(text.split()) < 20:
        return []

    all_results = {}

    # Search by key sentences
    sentences = get_key_sentences(text, count=2)
    for sentence in sentences:
        results = search_crossref_by_query(sentence[:200], rows=3)
        for r in results:
            key = r['doi'] or r['title']
            if key and key not in all_results:
                # Calculate similarity with abstract
                sim = calculate_similarity(
                    sentence,
                    r['abstract']
                )
                r['similarity'] = sim
                r['matched_by'] = 'sentence'
                all_results[key] = r

    # Search by keywords
    keywords = get_keywords(text, count=6)
    keyword_query = ' '.join(keywords)
    if keyword_query:
        results = search_crossref_by_query(keyword_query, rows=4)
        for r in results:
            key = r['doi'] or r['title']
            if key and key not in all_results:
                sim = calculate_similarity(
                    text[:500],
                    r['abstract']
                )
                r['similarity'] = sim
                r['matched_by'] = 'keywords'
                all_results[key] = r

    # Sort by similarity and return top 5
    sorted_results = sorted(
        all_results.values(),
        key=lambda x: x['similarity'],
        reverse=True
    )
    return sorted_results[:5]