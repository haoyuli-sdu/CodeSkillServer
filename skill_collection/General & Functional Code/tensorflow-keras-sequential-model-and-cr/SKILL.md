---
name: tensorflow-keras-sequential-model-and-cr
description: 'Guide for tf.keras: Sequential model, training, cross-validation history, ROC/PR curves.'
---

# TensorFlow / Keras — Neural Network Training Patterns

TensorFlow exposes Keras via `tf.keras`. Follow the import path given in the code prompt exactly — `tf.keras.*` and standalone `keras.*` share the same API but are accessed differently.

```python
import tensorflow as tf
# tf.keras.models.Sequential, tf.keras.layers.Dense, tf.keras.optimizers.Adam

from tensorflow import keras
# keras.Sequential, keras.layers.Dense, keras.optimizers.SGD
```

## Building a Sequential Model

`Dense` with `input_dim` sets the number of input features (integer, not tuple). Use it on the first layer only:

```python
model = tf.keras.models.Sequential([
    tf.keras.layers.Dense(20, activation='relu'),
    tf.keras.layers.Dense(1, activation='sigmoid')
])
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
```

`input_dim=X.shape[1]` is the number of features. `X.shape[0]` is the number of samples — these are different.

## Training and Cross-Validation History

`model.fit()` returns a `History` object; append the **History object** itself (not `.history`) when collecting fold-level results:

```python
from sklearn.model_selection import KFold
from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)
kf = KFold(n_splits=5)
history = []

for train_idx, test_idx in kf.split(X_scaled):
    X_tr, X_te = X_scaled[train_idx], X_scaled[test_idx]
    y_tr, y_te = y[train_idx], y[test_idx]

    model = tf.keras.models.Sequential([
        tf.keras.layers.Dense(20, activation='relu'),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    hist = model.fit(X_tr, y_tr,
                     validation_data=(X_te, y_te),
                     batch_size=32, epochs=100, verbose=0)
    history.append(hist)   # History object, not hist.history dict

return history
```

## Prediction and Curve Plotting

`model.predict()` returns shape `(n_samples, output_units)`. Use `.ravel()` to flatten to 1D:

```python
Y_pred = model.predict(X_test, verbose=0).ravel()

# ROC curve
from sklearn.metrics import roc_curve, auc
fpr, tpr, _ = roc_curve(Y_test, Y_pred)
auc_score = auc(fpr, tpr)

fig, ax = plt.subplots()
ax.plot([0, 1], [0, 1], 'k--')
ax.plot(fpr, tpr, label=f'AUC = {auc_score:.3f}')
ax.set_xlabel('False positive rate')
ax.set_ylabel('True positive rate')
ax.legend(loc='best')
return model, ax
```

## Typical Defaults

| Parameter      | Common value          |
|----------------|-----------------------|
| `epochs`       | 200 (small datasets)  |
| `batch_size`   | 1 (SGD), 32 (Adam)    |
| `learning_rate`| 0.1 (SGD)             |
| `optimizer`    | `'adam'` or `SGD(lr)` |
| `verbose`      | 0 (suppress output)   |

## Data Preprocessing

```python
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)   # scales features to [0, 1]
```
