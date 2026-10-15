---
name: gensim-topic-modelling-and-word-embeddin
description: 'Guide for gensim: Word2Vec training, empty input handling, text preprocessing pipeline, LDA with corpora.Dictionary, similarity queries.'
---

# gensim — Topic Modelling and Word Embeddings

## Word2Vec

```python
from gensim.models import Word2Vec

# sentences: list of lists of strings (tokenized documents)
sentences = [
    ["the", "quick", "brown", "fox"],
    ["the", "fox", "jumped", "over"],
]

model = Word2Vec(
    sentences=sentences,
    vector_size=100,   # embedding dimensions
    window=5,          # context window
    min_count=1,       # include words appearing at least once
    workers=4,
)
```

`Word2Vec(sentences=sentences, ...)` builds vocabulary and trains in one call.

## Handling Empty Input

Passing an empty list to `Word2Vec(sentences=[], ...)` raises `RuntimeError: you must first build vocabulary before training`. Return an untrained instance instead:

```python
if not tokenized_sentences:
    return Word2Vec(vector_size=100)   # no sentences= arg — safe, no error
```

## Text Preprocessing Pipeline

```python
import re
import nltk
from gensim.models import Word2Vec

ALPHANUMERIC = re.compile(r'[\W_]+')

def train_word_vectors(texts, stopwords=None):
    if stopwords is None:
        stopwords = nltk.corpus.stopwords.words('english')

    tokenized = [
        [w for w in ALPHANUMERIC.sub(' ', text).lower().split()
         if w not in stopwords]
        for text in texts
    ]

    if not tokenized:
        return Word2Vec(vector_size=100)

    return Word2Vec(sentences=tokenized, vector_size=100, window=5, min_count=1, workers=4)
```

Steps: substitute non-alphanumeric characters with space → lowercase → split on whitespace → filter stopwords.

## Accessing Word Vectors

```python
vector  = model.wv['fox']                         # numpy array shape (vector_size,)
similar = model.wv.most_similar('fox', topn=5)    # [(word, cosine_score), ...]
vocab   = list(model.wv.key_to_index.keys())      # all trained vocabulary words
```

## LDA Topic Model

```python
from gensim import corpora
from gensim.models import LdaModel

dictionary = corpora.Dictionary(tokenized_docs)
corpus = [dictionary.doc2bow(doc) for doc in tokenized_docs]

lda = LdaModel(corpus=corpus, id2word=dictionary, num_topics=5, passes=10)
topics = lda.print_topics(num_words=10)
```

`doc2bow(doc)` converts a token list to a bag-of-words list of `(word_id, count)` tuples. `print_topics()` returns a list of `(topic_id, topic_string)` pairs.

## Similarity Queries

```python
from gensim.similarities import MatrixSimilarity

index = MatrixSimilarity(lda[corpus])
query_bow = dictionary.doc2bow(query_tokens)
sims = index[lda[query_bow]]   # cosine similarity scores for all docs
```
