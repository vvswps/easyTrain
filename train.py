import tensorflow as tf
import tensorflow_hub as hub

IMAGE_SIZE = 224  # Adjust based on the pre-trained model
BATCH_SIZE = 32  # Adjust based on your resources

def get_data_directory(data_dir):
    # Later you'll modify this to load from Cloud Storage
    return tf.keras.utils.image_dataset_from_directory(
        data_dir, 
        labels='inferred', 
        image_size=(IMAGE_SIZE, IMAGE_SIZE), 
        batch_size=BATCH_SIZE
    )

def build_model(num_classes):
    # Load pre-trained model (example, adjust based on your choice!)
    base_model = hub.KerasLayer("https://tfhub.dev/google/imagenet/mobilenet_v2_100_224/feature_vector/5", trainable=True) 

    model = tf.keras.Sequential([
        base_model,
        tf.keras.layers.Dense(num_classes)  # New classification layer
    ])

    model.compile(
        optimizer='adam',
        loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True),
        metrics=['accuracy']
    )
    return model

if __name__ == '__main__':
    try:   
        data_dir = 'uploads'  # Placeholder, change this for cloud storage
        train_ds = get_data_directory(data_dir)
        val_ds = get_data_directory(data_dir)  # Placeholder, add validation set later

        num_classes = len(train_ds.class_names)  # Infer from data
        model = build_model(num_classes)

        model.fit(train_ds, epochs=5, validation_data=val_ds) 
    
    # Placeholder save, update this for Cloud Storage
        model.save('my_image_classifier.h5')

    except Exception as e:  # Catch potential errors
        error_message = str(e)
        # Optionally, add more structured logging here
        print("Training Error:", error_message) 
        # We'll return this error to the Flask app
        
