---
name: scikit-learn-practical-reference-for-pre
description: 'Guide for correct sklearn API usage: scalers, PCA, regression, clustering, text vectorization, and common pitfalls.'
---

# scikit-learn — Practical Reference for Preprocessing, Regression, Clustering, and Vectorization

## Scalers: Shapes and Column Selection

`StandardScaler` and `MinMaxScaler` require 2D input and return a **2D numpy ndarray** of the same shape.

**Scale all columns in a DataFrame:**
```python
scaler = StandardScaler()
df[df.columns] = scaler.fit_transform(df[df.columns])
```

**Scale specific columns by name:**
```python
scaler = StandardScaler()
df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
```

**Scale a subset of columns specified by integer index** — use the index to look up the column name:
```python
scaler = StandardScaler()
for i in scale_cols:
    df[columns[i]] = scaler.fit_transform(df[[columns[i]]])
```

**Scale a single 1D array (must reshape to 2D column vector):**
```python
scaled = scaler.fit_transform(np.array(values).reshape(-1, 1)).flatten()
# .flatten() converts (n, 1) → (n,)
```

---

## Input Conversion: Dict or Array → DataFrame

When the function receives raw data (dict, list of tuples, 2D array), convert before sklearn operations:

```python
# dict of lists
df = pd.DataFrame(data)

# list of tuples — zip(*data) is the idiomatic unpacker
items, counts, weights = zip(*records)
scaler = MinMaxScaler()
weights_norm = scaler.fit_transform(np.array(weights).reshape(-1, 1)).flatten()

# 2D array with explicit columns
df = pd.DataFrame(array, columns=col_names)
```

---

## fit_transform vs fit + transform

`fit_transform(corpus)` builds the vocabulary from `corpus` and encodes it in one step. Calling `fit(A)` then `transform(B)` encodes `B` using the vocabulary learned from `A` — the two results differ because the vocabulary is different.

To include a new document in the learned vocabulary, pass it in the same call:

```python
vectorizer = CountVectorizer()
matrix = vectorizer.fit_transform([new_doc] + reference_sentences)
# matrix[0] is the new_doc row, encoded under the joint vocabulary
```

---

## Text Vectorization

### CountVectorizer — document-term matrix

```python
from sklearn.feature_extraction.text import CountVectorizer

vectorizer = CountVectorizer()
dtm = vectorizer.fit_transform(sentences)   # sparse matrix
df = pd.DataFrame(dtm.toarray(), columns=vectorizer.get_feature_names_out())
```

When the task says "vectorize a string against a fixed set of reference sentences", include the input string in the same `fit_transform` call so both share one vocabulary:

```python
X = vectorizer.fit_transform([s] + SENTENCES)
return X.toarray()[0]   # row 0 = the input string
```

### TF-IDF

```python
from sklearn.feature_extraction.text import TfidfVectorizer

vectorizer = TfidfVectorizer()
matrix = vectorizer.fit_transform(docs)
feature_names = list(vectorizer.get_feature_names_out())
```

### Text preprocessing before vectorization

When the task specifies removing numbers and punctuation, apply preprocessing **in-place on the column** before passing the column to the vectorizer. The vectorizer then receives the cleaned strings; do not re-add the preprocessed text as an extra column in the output:

```python
def clean(text):
    text = re.sub(r'\d+', '', text)          # remove numbers
    text = re.sub(r'\W+', ' ', text)         # remove punctuation
    return ' '.join(w for w in text.lower().split() if w not in STOPWORDS)

df[col] = df[col].apply(clean)
X = vectorizer.fit_transform(df[col])
return pd.DataFrame(X.toarray(), columns=vectorizer.get_feature_names_out())
```

---

## PCA

```python
from sklearn.decomposition import PCA

pca = PCA(n_components=2)
components = pca.fit_transform(X)   # shape (n_samples, 2); X is the raw array
# components is a plain ndarray — index directly, no pd.DataFrame wrapper needed
ax.scatter(components[:, 0], components[:, 1])
```

When the task specifies returning `ax`, create the figure first, then scatter:

```python
fig, ax = plt.subplots()
ax.scatter(components[:, 0], components[:, 1])
ax.set_xlabel('First Principal Component')
ax.set_ylabel('Second Principal Component')
ax.set_title('PCA Result')
return ax
```

---

## Linear and Logistic Regression Patterns

### Train on DataFrame features, return score (float)

```python
X = df.drop(columns=[target])
y = df[target]
model = LinearRegression()
model.fit(X, y)
return model.score(X, y)   # R² as a plain float
```

### Train/test split, return model and predictions

```python
X = df.drop(columns=[target])
y = df[target]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = LinearRegression()
model.fit(X_train, y_train)
predictions = model.predict(X_test)
return model, predictions
```

### 1D feature Series → must reshape before fit

```python
X_train_2d = X_train.values.reshape(-1, 1)
X_test_2d  = X_test.values.reshape(-1, 1)
model.fit(X_train_2d, y_train)
y_pred = model.predict(X_test_2d)
```

### coef_ shape depends on y dimensionality

```python
y_1d = np.array(df['value'])                # 1D → coef_ shape (1,), intercept_ float
y_2d = np.array(df['value']).reshape(-1, 1) # 2D → coef_ shape (1,1), intercept_ (1,)
```

---

## Random Seed Placement

Set the seed **before** generating any random data:

```python
if random_seed is not None:
    np.random.seed(random_seed)

X = np.random.rand(num_samples, 1)          # uses the seed
y = 2 * X.squeeze() + 1 + np.random.randn(num_samples) * noise
```

---

## LabelEncoder

`LabelEncoder.fit_transform` accepts a 1D array-like (list of strings, Series) and returns integer-encoded labels:

```python
from sklearn.preprocessing import LabelEncoder

le = LabelEncoder()
df[col] = le.fit_transform(df[col])   # replaces string values with integers
```

When the task involves **only categorical encoding** (not numerical standardization), use LabelEncoder alone — do not add a StandardScaler pass unless the task specification explicitly asks for it.

---

## KMeans Clustering

```python
from sklearn.cluster import KMeans

kmeans = KMeans(n_clusters=k, n_init=10, random_state=42)
labels = kmeans.fit_predict(X)   # same as .fit(X).labels_
centroids = kmeans.cluster_centers_    # shape (k, n_features)
```

When two DataFrames share a common key column, use **`pd.merge`** to join them before clustering:

```python
df = pd.merge(df1, df2, on='id')
X = df[[col1, col2]]
kmeans.fit(X)
```

---

## NMF for Topic Extraction

```python
from sklearn.decomposition import NMF

nmf = NMF(n_components=n_topics, random_state=0)
W = nmf.fit_transform(tfidf_matrix)   # document-topic matrix
H = nmf.components_                   # topic-word matrix, shape (n_topics, vocab)

for row in H:
    top_idx = row.argsort()[-n_top_words:][::-1]   # descending
    topics.append([feature_names[i] for i in top_idx])
```

---

## RandomForestClassifier and Feature Importance

```python
from sklearn.ensemble import RandomForestClassifier

clf = RandomForestClassifier(random_state=42)
clf.fit(X_train, y_train)
importances = pd.Series(clf.feature_importances_, index=X.columns).sort_values(ascending=False)
```

---

## SelectKBest

```python
from sklearn.feature_selection import SelectKBest, f_classif

selector = SelectKBest(f_classif, k=2)
X_new = selector.fit_transform(X, y)
selected = [col for col, keep in zip(X.columns, selector.get_support()) if keep]
```

---

## Return Type Quick Reference

| Operation | Return type |
|---|---|
| `StandardScaler().fit_transform(X)` | `np.ndarray`, same shape as X |
| `MinMaxScaler().fit_transform(X)` | `np.ndarray`, same shape as X |
| `PCA(k).fit_transform(X)` | `np.ndarray`, shape (n_samples, k) |
| `LabelEncoder().fit_transform(y)` | `np.ndarray` 1D, int-encoded |
| `LinearRegression().score(X, y)` | plain `float` (R²) |
| `KMeans().fit_predict(X)` | `np.ndarray` 1D, int cluster labels |
| `CountVectorizer().fit_transform(docs)` | sparse matrix → `.toarray()` for ndarray |
| `CountVectorizer().get_feature_names_out()` | `np.ndarray` of strings |
