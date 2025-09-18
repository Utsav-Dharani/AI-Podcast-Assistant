import re
from typing import List

_STOPWORDS = set("""
a about above after again against all am an and any are aren't as at be because been before
being below between both but by can't cannot could couldn't did didn't do does doesn't doing
don't down during each few for from further had hadn't has hasn't have haven't having he he'd
he'll he's her here here's hers herself him himself his how how's i i'd i'll i'm i've if in
into is isn't it it's its itself let's me more most mustn't my myself no nor not of off on
once only or other ought our ours ourselves out over own same shan't she she'd she'll she's
should shouldn't so some such than that that's the their theirs them themselves then there
there's these they they'd they'll they're they've this those through to too under until up
very was wasn't we we'd we'll we're we've were weren't what what's when when's where where's
which while who who's whom why why's with won't would wouldn't you you'd you'll you're you've
your yours yourself yourselves
""".split())

def sent_tokenize(text: str) -> List[str]:
    sents = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sents if s.strip()]

def word_tokenize(text: str) -> List[str]:
    text = re.sub(r"[^A-Za-z0-9\s]", " ", text.lower())
    return [w for w in text.split() if w and w not in _STOPWORDS]

def top_keywords(text: str, k: int = 8) -> List[str]:
    words = word_tokenize(text)
    freq: dict[str,int] = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    return [w for w, _ in sorted(freq.items(), key=lambda x: x[1], reverse=True)[:k]]

def summarize_text(text: str, max_sentences: int = 6) -> str:
    sents = sent_tokenize(text)
    if len(sents) <= max_sentences:
        return " ".join(sents)
    # simple frequency-based extractive summary
    vocab_freq: dict[str,int] = {}
    for w in word_tokenize(text):
        vocab_freq[w] = vocab_freq.get(w, 0) + 1
    scored = []
    for s in sents:
        score = sum(vocab_freq.get(w, 0) for w in word_tokenize(s))
        scored.append((score, s))
    top = set(s for _, s in sorted(scored, key=lambda x: x[0], reverse=True)[:max_sentences])
    ordered = [s for s in sents if s in top][:max_sentences]
    return " ".join(ordered)
