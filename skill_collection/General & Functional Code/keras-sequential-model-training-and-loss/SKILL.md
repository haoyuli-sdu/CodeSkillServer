---
name: keras-sequential-model-training-and-loss
description: 'Guide for keras: Sequential model, Dense layers, training history, validation loss plotting.'
---

# Keras — Sequential Model, Training, and Visualisation

Keras is available as a standalone package (`keras`) or through TensorFlow (`tensorflow.keras`). Follow the import path given in the code prompt exactly.

```python
# Standalone keras package
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import SGD

# TensorFlow-bundled
from tensorflow import keras
# keras.Sequential, keras.layers.Dense, keras.optimizers.SGD
```

## Building and Compiling a Model

`Dense` with `input_dim` specifies the number of input features (an integer). Use it on the first layer:

```python
model = Sequential([
    Dense(input_dim=4, units=8, activation='relu'),
    Dense(units=1, activation='sigmoid')
])
model.compile(
    loss='binary_crossentropy',
    optimizer=SGD(learning_rate=0.1)
)
```

## Training with Train/Validation Split

```python
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.25)

model = Sequential([
    Dense(input_dim=X_train.shape[1], units=1, activation='sigmoid')
])
model.compile(loss='binary_crossentropy', optimizer=SGD(learning_rate=0.1))

history = model.fit(X_train, Y_train,
                    epochs=200, batch_size=1, verbose=0,
                    validation_data=(X_test, Y_test))

fig, ax = plt.subplots()
ax.plot(history.history['loss'], label='Train Loss')
ax.plot(history.history['val_loss'], label='Validation Loss')
ax.set_title('Model loss')
ax.set_ylabel('Loss')
ax.set_xlabel('Epoch')
ax.legend(['Train', 'Test'], loc='upper left')

return model, ax
```

`history.history` is a dict. Keys present after training:
- `'loss'`, `'val_loss'` — always present when `validation_data` is provided
- `'accuracy'`, `'val_accuracy'` — only if `metrics=['accuracy']` is in `compile()`

## Key API Contracts

```
model.fit(...)         → History object; access history.history for loss dict
model.predict(X)       → ndarray shape (n_samples, output_units); use .ravel() for 1D
model.evaluate(X, y)   → [loss, metric1, ...]
```

Functions typically return `(model, ax)` where `ax` is from `plt.subplots()`.
