import tensorflow as tf
import os
from sklearn.model_selection import train_test_split
import shutil


IMAGE_SIZE = 224  # Adjust based on the pre-trained model
BATCH_SIZE = 32  # Adjust based on your resources


def get_data_directory(data_dir):
    # modify this to load from Cloud Storage later

    return tf.keras.utils.image_dataset_from_directory(
        data_dir,
        labels="inferred",
        image_size=(IMAGE_SIZE, IMAGE_SIZE),
        batch_size=BATCH_SIZE,
    )


def split_data_into_train_and_val(data_dir, train_dir, val_dir, test_size=0.2):
    # Get the class names
    class_names = os.listdir(data_dir)
    print("Class names: ", class_names)

    for class_name in class_names:
        # Get all the image filenames for this class
        image_filenames = os.listdir(os.path.join(data_dir, class_name))
        print(f"Class: {class_name}, number of images: {len(image_filenames)}")

        # Split the filenames into training and validation sets
        train_filenames, val_filenames = train_test_split(
            image_filenames, test_size=test_size
        )

        # Create the training and validation directories for this class
        os.makedirs(os.path.join(train_dir, class_name), exist_ok=True)
        os.makedirs(os.path.join(val_dir, class_name), exist_ok=True)

        # Move the training images to the training directory
        for filename in train_filenames:
            shutil.move(
                os.path.join(data_dir, class_name, filename),
                os.path.join(train_dir, class_name, filename),
            )

        # Move the validation images to the validation directory
        for filename in val_filenames:
            shutil.move(
                os.path.join(data_dir, class_name, filename),
                os.path.join(val_dir, class_name, filename),
            )


def build_model(num_classes):
    inputs = tf.keras.Input(shape=(IMAGE_SIZE, IMAGE_SIZE, 3))
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(224, 224, 3), include_top=False, weights="imagenet"
    )(inputs)

    # Add a global average pooling layer to reduce the dimensionality of the output
    x = tf.keras.layers.GlobalAveragePooling2D()(base_model)

    # Add a dense layer for the final classification
    outputs = tf.keras.layers.Dense(num_classes)(x)

    # Create the model
    model = tf.keras.Model(inputs=inputs, outputs=outputs)
    tf.keras.backend.clear_session()

    model.compile(
        optimizer="adam",
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=["accuracy"],
    )

    return model


def start_training(data_dir, classNames):
    try:
        print("Training model")

        split_data_into_train_and_val("uploads", "uploads/train", "uploads/val")

        train_ds = get_data_directory("uploads/train")
        val_ds = get_data_directory("uploads/val")

        # le = LabelEncoder()
        # train_ds = train_ds.map(lambda x, y: (x, le.fit_transform(y)))
        # val_ds = val_ds.map(lambda x, y: (x, le.transform(y)))

        num_classes = len(train_ds.class_names)
        model = build_model(num_classes)

        model.fit(train_ds, epochs=5, validation_data=val_ds)

        model.save(f"predict_{'_'.join(train_ds.class_names)}.keras")

    except Exception as e:
        error_message = str(e)
        print("Training Error:", error_message)
        raise e
