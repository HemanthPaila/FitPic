import tensorflow as tf
import numpy as np

model = tf.keras.Sequential([
    tf.keras.layers.Dense(64, activation='relu', input_shape=(8,)),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(2, activation='sigmoid')
])

model.compile(optimizer='adam', loss='binary_crossentropy')

X = np.random.rand(1000, 8)
y = np.random.randint(0, 2, (1000, 2))

model.fit(X, y, epochs=10)
model.save("fit_model.h5")
