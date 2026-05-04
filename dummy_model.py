import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np

# Example feature structure:
# [height, weight, chest, waist, hips, skin_tone, cloth_type, size]

def preprocess_data(X):
    X = np.array(X, dtype=np.float32)
    
    # Normalize body measurements
    X[:, 0:5] = X[:, 0:5] / 200.0   # scale values
    
    return X

def build_fit_model(input_dim=8):
    inputs = layers.Input(shape=(input_dim,))
    
    x = layers.Dense(64, activation='relu')(inputs)
    x = layers.BatchNormalization()(x)
    
    x = layers.Dense(128, activation='relu')(x)
    x = layers.Dropout(0.3)(x)
    
    x = layers.Dense(64, activation='relu')(x)
    
    # Output 1: Fit score (0–1)
    fit_output = layers.Dense(1, activation='sigmoid', name="fit_score")(x)
    
    # Output 2: Size classification (S, M, L, XL → 4 classes)
    size_output = layers.Dense(4, activation='softmax', name="size")(x)
    
    model = models.Model(inputs=inputs, outputs=[fit_output, size_output])
    
    model.compile(
        optimizer='adam',
        loss={
            "fit_score": "binary_crossentropy",
            "size": "categorical_crossentropy"
        },
        metrics={
            "fit_score": "accuracy",
            "size": "accuracy"
        }
    )
    
    return model

fit_model = build_fit_model()
fit_model.summary()


# Generate dummy dataset
X_train = np.random.rand(1000, 8)
X_train = preprocess_data(X_train)

y_fit = np.random.randint(0, 2, size=(1000, 1))
y_size = tf.keras.utils.to_categorical(np.random.randint(0, 4, 1000), num_classes=4)

fit_model.fit(
    X_train,
    {"fit_score": y_fit, "size": y_size},
    epochs=15,
    batch_size=32,
    validation_split=0.2
)



def predict_fit(model, user_data):
    user_data = preprocess_data([user_data])
    
    fit_score, size_pred = model.predict(user_data)
    
    size_labels = ["S", "M", "L", "XL"]
    size = size_labels[np.argmax(size_pred)]
    
    return {
        "fit_score": float(fit_score[0][0]),
        "recommended_size": size
    }

# Example usage
result = predict_fit(fit_model, [170, 65, 95, 80, 98, 2, 1, 3])
print(result)


def build_tryon_model():
    person_input = layers.Input(shape=(256, 256, 3))
    cloth_input = layers.Input(shape=(256, 256, 3))
    
    x = layers.Concatenate()([person_input, cloth_input])
    
    x = layers.Conv2D(64, 3, padding='same', activation='relu')(x)
    x = layers.MaxPooling2D()(x)
    
    x = layers.Conv2D(128, 3, padding='same', activation='relu')(x)
    x = layers.UpSampling2D()(x)
    
    x = layers.Conv2D(64, 3, padding='same', activation='relu')(x)
    
    output = layers.Conv2D(3, 1, activation='sigmoid')(x)
    
    model = models.Model(inputs=[person_input, cloth_input], outputs=output)
    
    model.compile(optimizer='adam', loss='mse')
    
    return model

tryon_model = build_tryon_model()
tryon_model.summary()


person_images = np.random.rand(100, 256, 256, 3)
cloth_images = np.random.rand(100, 256, 256, 3)
target_images = np.random.rand(100, 256, 256, 3)

tryon_model.fit(
    [person_images, cloth_images],
    target_images,
    epochs=5,
    batch_size=8
)


def full_pipeline(user_data, person_img, cloth_img):
    # Step 1: Fit prediction
    fit_result = predict_fit(fit_model, user_data)
    
    # Step 2: Try-on image
    person_img = np.expand_dims(person_img, axis=0)
    cloth_img = np.expand_dims(cloth_img, axis=0)
    
    generated_img = tryon_model.predict([person_img, cloth_img])[0]
    
    return {
        "fit": fit_result,
        "tryon_image": generated_img
    }


fit_model.save("fit_model.h5")
tryon_model.save("tryon_model.h5")

# Load later
fit_model = tf.keras.models.load_model("fit_model.h5")
tryon_model = tf.keras.models.load_model("tryon_model.h5")
