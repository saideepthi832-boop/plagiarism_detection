import re
import math
from collections import Counter

MODEL_LOADED = False
ai_classifier = None


def get_sentences(text):
    return [s.strip() for s in re.split(r'[.!?]', text) if len(s.strip()) > 10]


def check_chatgpt_phrases(text):
    """Phrases commonly used by ChatGPT"""
    chatgpt_phrases = [
        # Structural phrases
        'in conclusion', 'to summarize', 'in summary', 'overall',
        'it is important to note', 'it is worth noting',
        'it should be noted', 'as mentioned earlier',
        'as previously stated', 'in other words',

        # Formal connectors ChatGPT overuses
        'furthermore', 'moreover', 'additionally', 'consequently',
        'therefore', 'thus', 'hence', 'nevertheless', 'nonetheless',

        # ChatGPT filler words
        'delve', 'delving', 'leverage', 'leveraging', 'utilize',
        'utilizing', 'facilitate', 'facilitating', 'paradigm',
        'multifaceted', 'nuanced', 'comprehensive', 'robust',
        'streamline', 'underscore', 'pivotal', 'paramount',
        'imperative', 'groundbreaking', 'revolutionary',

        # ChatGPT sentence starters
        'certainly', 'absolutely', 'of course', 'great question',
        'it is essential', 'it is crucial', 'plays a crucial role',
        'plays a vital role', 'in today\'s world', 'in the modern era',
        'in the realm of', 'in the context of', 'it can be seen that',
        'this essay will', 'this paper will', 'we will explore',
        'let us explore', 'let\'s dive into',

        # ChatGPT conclusions
        'in the final analysis', 'all things considered',
        'taking everything into account', 'on the whole',
        'by and large', 'for the most part'
    ]
    text_lower = text.lower()
    found = [p for p in chatgpt_phrases if p in text_lower]
    return len(found), found


def check_sentence_uniformity(text):
    sentences = get_sentences(text)
    if len(sentences) < 3:
        return 100
    lengths = [len(s.split()) for s in sentences]
    avg = sum(lengths) / len(lengths)
    variance = sum((l - avg) ** 2 for l in lengths) / len(lengths)
    return round(variance, 2)


def check_paragraph_structure(text):
    """ChatGPT always writes in perfect structured paragraphs"""
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    if len(paragraphs) >= 3:
        return True
    return False


def detect_ai_content(text, api_key=None):
    if not text or len(text.split()) < 20:
        return {
            "ai_probability": 0,
            "verdict": "Too short to analyze",
            "is_chatgpt": False,
            "method": "none",
            "signals": {
                "perplexity": 0,
                "avg_sentence_length": 0,
                "vocabulary_richness": 0,
                "chatgpt_phrases_found": 0,
                "sentence_variance": 0
            },
            "found_phrases": []
        }

    words = text.lower().split()
    total = len(words)
    word_counts = Counter(words)
    log_prob = sum(math.log(word_counts[w] / total) for w in words)
    perplexity = round(math.exp(-log_prob / total), 2)

    sentences = get_sentences(text)
    avg_len = round(sum(len(s.split()) for s in sentences) / len(sentences), 2) if sentences else 0
    richness = round(len(set(words)) / total, 2)
    phrase_count, found_phrases = check_chatgpt_phrases(text)
    variance = check_sentence_uniformity(text)
    structured = check_paragraph_structure(text)

    method = "local"
    score = 0

    # Use RoBERTa model if loaded
    if MODEL_LOADED:
        try:
            sample = text[:1000]
            result = ai_classifier(sample)[0]
            label = result['label'].upper()
            confidence = round(result['score'] * 100, 2)

            if 'FAKE' in label or label == 'LABEL_1':
                score = confidence
            else:
                score = 100 - confidence

            method = "RoBERTa Classifier"

            # Boost with ChatGPT-specific signals
            if phrase_count >= 5:
                score = min(score + 20, 99)
            elif phrase_count >= 3:
                score = min(score + 12, 99)
            elif phrase_count >= 1:
                score = min(score + 5, 99)

            if variance < 20:
                score = min(score + 8, 99)
            if structured:
                score = min(score + 5, 99)

        except Exception as e:
            print(f"Classifier error: {e}")
            score = _local_score(phrase_count, variance, perplexity, richness, structured)
    else:
        score = _local_score(phrase_count, variance, perplexity, richness, structured)

    score = round(score, 2)
    is_chatgpt = score >= 65

    if score >= 65:
        verdict = "🤖 Likely ChatGPT Generated"
    elif score >= 35:
        verdict = "🤔 Possibly AI Assisted"
    else:
        verdict = "✅ Likely Human Written"

    return {
        "ai_probability": score,
        "verdict": verdict,
        "is_chatgpt": is_chatgpt,
        "method": method,
        "signals": {
            "perplexity": perplexity,
            "avg_sentence_length": avg_len,
            "vocabulary_richness": richness,
            "chatgpt_phrases_found": phrase_count,
            "sentence_variance": variance
        },
        "found_phrases": found_phrases[:5]
    }


def _local_score(phrase_count, variance, perplexity, richness, structured):
    score = 0
    if phrase_count >= 5: score += 40
    elif phrase_count >= 3: score += 28
    elif phrase_count >= 1: score += 14
    if variance < 20: score += 20
    elif variance < 40: score += 10
    if perplexity < 10: score += 15
    elif perplexity < 20: score += 8
    if richness > 0.75: score += 12
    if structured: score += 13
    return min(score, 95)
