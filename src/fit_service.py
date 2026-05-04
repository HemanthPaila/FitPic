import tensorflow as tf
import numpy as np

model = tf.keras.models.load_model("fit_model.h5")

def preprocess(data):
    data = np.array(data, dtype=np.float32)
    data[0:5] /= 200.0
    return data.reshape(1, -1)

def predict_fit(features):
    x = preprocess(features)

    fit_score, size_pred = model.predict(x)

    sizes = ["S", "M", "L", "XL"]

    return {
        "fit_score": float(fit_score[0][0]),
        "size": sizes[np.argmax(size_pred)]
    }
