import tensorflow as tf
import numpy as np

model = tf.keras.models.load_model("tryon_model.h5")

def preprocess(img):
    img = np.array(img) / 255.0
    return np.expand_dims(img, axis=0)

def generate_tryon(person, cloth):
    p = preprocess(person)
    c = preprocess(cloth)

    result = model.predict([p, c])[0]

    return result
