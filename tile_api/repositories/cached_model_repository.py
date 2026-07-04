import hashlib
from pathlib import Path

from tile_api.application.repositories import IModelRepository


class CachedModelRepository(IModelRepository):
    def __init__(self, repository: IModelRepository, cache_dir: Path):
        self.repository = repository
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def predict(self, input_data):
        return self.batch_predict([input_data])[0]

    def batch_predict(self, input_images):
        outputs = [None] * len(input_images)
        missing_inputs = []
        missing_indexes = []

        for index, input_image in enumerate(input_images):
            if input_image is None:
                outputs[index] = None
                continue

            cache_key = hashlib.sha256(input_image).hexdigest()
            cache_path = self.cache_dir / f"{cache_key}.png"
            if cache_path.exists():
                outputs[index] = cache_path.read_bytes()
            else:
                missing_inputs.append(input_image)
                missing_indexes.append(index)

        if missing_inputs:
            predictions = self.repository.batch_predict(missing_inputs)
            for missing_input, index, prediction in zip(missing_inputs, missing_indexes, predictions):
                outputs[index] = prediction
                if prediction is not None:
                    cache_key = hashlib.sha256(missing_input).hexdigest()
                    cache_path = self.cache_dir / f"{cache_key}.png"
                    cache_path.write_bytes(prediction)

        return outputs
