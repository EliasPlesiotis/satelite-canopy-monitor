import tensorflow as tf

@tf.keras.utils.register_keras_serializable(package="Custom", name="Unet")
class Unet(tf.keras.Model):
    def __init__(self, **kwargs):
        super(Unet, self).__init__(**kwargs)

        # First encoder layer
        self.enc1_1 = tf.keras.layers.Conv2D(16, 3, activation='relu', padding='same')
        self.enc1_2 = tf.keras.layers.Conv2D(16, 3, activation='relu', padding='same')
        self.pool1  = tf.keras.layers.MaxPool2D(pool_size=(2, 2), strides=2)

        # Second encoder layer
        self.enc2_1 = tf.keras.layers.Conv2D(32, 3, activation='relu', padding='same')
        self.enc2_2 = tf.keras.layers.Conv2D(32, 3, activation='relu', padding='same')
        self.pool2  = tf.keras.layers.MaxPool2D(pool_size=(2, 2), strides=2)

        # Third encoder layer
        self.enc3_1 = tf.keras.layers.Conv2D(64, 3, activation='relu', padding='same')
        self.enc3_2 = tf.keras.layers.Conv2D(64, 3, activation='relu', padding='same')
        self.pool3  = tf.keras.layers.MaxPool2D(pool_size=(2, 2), strides=2)

        # Bottleneck
        self.bottl1 = tf.keras.layers.Conv2D(128, 3, padding='same', activation='relu')
        self.bottl2 = tf.keras.layers.Conv2D(128, 3, padding='same', activation='relu')

        # First decoder layer
        self.dec1_transpose = tf.keras.layers.Conv2DTranspose(64, (2, 2), strides=2, padding='same')
        self.dec1_1         = tf.keras.layers.Conv2D(64, 3, activation='relu', padding='same')
        self.dec1_2         = tf.keras.layers.Conv2D(64, 3, activation='relu', padding='same')

        # Second decoder layer
        self.dec2_transpose = tf.keras.layers.Conv2DTranspose(32, (2, 2), strides=2, padding='same')
        self.dec2_1         = tf.keras.layers.Conv2D(32, 3, activation='relu', padding='same')
        self.dec2_2         = tf.keras.layers.Conv2D(32, 3, activation='relu', padding='same')

        # Third decoder layer
        self.dec3_transpose = tf.keras.layers.Conv2DTranspose(16, (2, 2), strides=2, padding='same')
        self.dec3_1         = tf.keras.layers.Conv2D(16, 3, activation='relu', padding='same')
        self.dec3_2         = tf.keras.layers.Conv2D(16, 3, activation='relu', padding='same')

        self.final = tf.keras.layers.Conv2D(1, 1, padding='same', activation='sigmoid')

        self.concat = tf.keras.layers.Concatenate(axis=-1)

    def call(self, inputs):
        # Encoder 1
        x = self.enc1_1(inputs)
        x = self.enc1_2(x)
        enc1_out = self.pool1(x)

        # Encoder 2
        x = self.enc2_1(enc1_out)
        x = self.enc2_2(x)
        enc2_out = self.pool2(x)

        # Encoder 3
        x = self.enc3_1(enc2_out)
        x = self.enc3_2(x)
        enc3_out = self.pool3(x)

        # Bottleneck
        x = self.bottl1(enc3_out)
        bottl1_out = self.bottl2(x)

        # Decoder 1
        x = self.dec1_transpose(bottl1_out)
        skip_features = tf.keras.layers.Resizing(x.shape[1], x.shape[2])(enc3_out)
        x = tf.keras.layers.Concatenate()([x, skip_features])

        x = self.dec1_1(x)
        dec1_out = self.dec1_2(x)

        # Decoder 2
        x = self.dec2_transpose(dec1_out)
        skip_features = tf.keras.layers.Resizing(x.shape[1], x.shape[2])(enc2_out)
        x = tf.keras.layers.Concatenate()([x, skip_features])

        x = self.dec2_1(x)
        dec2_out = self.dec2_2(x)

        # Decoder 3
        x = self.dec3_transpose(dec2_out)
        skip_features = tf.keras.layers.Resizing(x.shape[1], x.shape[2])(enc1_out)
        x = tf.keras.layers.Concatenate()([x, skip_features])

        x = self.dec3_1(x)
        dec3_out = self.dec3_2(x)

        output = self.final(dec3_out)

        return output

    def get_config(self):
        base_config = super(Unet, self).get_config()
        return base_config
