import tensorflow as tf
import cv2
import numpy as np
from concurrent.futures import ProcessPoolExecutor
import atexit
import threading
import io
from PIL import Image

from satelite_temperature_prediction.tile_api.application.repositories import IModelRepository
from satelite_temperature_prediction.tile_api.repositories.model import Unet


_WORKER_MODEL = None

def _init_worker(model_path: str):
    global _WORKER_MODEL
    _WORKER_MODEL = tf.keras.models.load_model(model_path, custom_objects={"Unet": Unet})


def _predict_chunk_worker(chunk_images):
    batch_data = []
    original_sizes = []
    for input_image in chunk_images:
        pil_image = Image.open(io.BytesIO(input_image))
        original_sizes.append(pil_image.size)
        batch_data.append(np.array(pil_image.convert('RGB')) / 255.0)

    if not batch_data:
        return []

    batch_tensor = tf.convert_to_tensor(np.stack(batch_data, axis=0), dtype=tf.float32)
    preds = _WORKER_MODEL.predict(batch_tensor)

    outputs = []
    for i, pred in enumerate(preds):
        mask = (pred > 0.5).astype(np.uint8) * 255
        mask = np.squeeze(mask, axis=-1) if mask.ndim == 3 and mask.shape[-1] == 1 else mask
        mask_resized = cv2.resize(mask, original_sizes[i], interpolation=cv2.INTER_NEAREST)

        result_image = Image.fromarray(mask_resized)
        bytes_io = io.BytesIO()
        result_image.save(bytes_io, format='PNG')
        outputs.append(bytes_io.getvalue())

    return outputs

class KerasModelRepository(IModelRepository):
    def __init__(self, model_path: str, workers=2):
        self.model_path = model_path
        self.executor = None
        self.max_workers = workers

        threading.Thread(target=self._ensure_executor, daemon=True).start()

        atexit.register(self._shutdown_executor)

    def _ensure_executor(self):
        if self.executor is not None:
            return
        try:
            self.executor = ProcessPoolExecutor(max_workers=self.max_workers, initializer=_init_worker, initargs=(self.model_path,))
        except Exception:
            self.executor = None

    def _shutdown_executor(self):
        if getattr(self, 'executor', None) is not None:
            try:
                self.executor.shutdown(wait=False)
            except Exception:
                pass

    def predict(self, input_image):
        return self.batch_predict([input_image])[0]

    def batch_predict(self, input_images):
        self.load_model()
        CHUNK_SIZE = 8
        outputs = []

        chunks = [
            input_images[start : start + CHUNK_SIZE]
            for start in range(0, len(input_images), CHUNK_SIZE)
        ]

        if not chunks:
            return outputs

        futures = [self.executor.submit(_predict_chunk_worker, chunk) for chunk in chunks]
        for fut in futures:
            res = fut.result()
            if res:
                outputs.extend(res)

        return outputs
