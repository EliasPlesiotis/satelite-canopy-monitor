from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed

class IWorkerPool(ABC):
    @abstractmethod
    def fetch_images_parallel(self, tiles, fetch_func, max_workers: int, max_failures: int):
        raise NotImplementedError

class WorkerPool(IWorkerPool):
    def _handle_failures(self, failures: int, max_failures: int, futures: dict):
        failures += 1
        if failures >= max_failures:
            for pending_future in futures:
                if not pending_future.done():
                    pending_future.cancel()
            return failures, True
        return failures, False

    def fetch_images_parallel(self, tiles, fetch_func, max_workers: int, max_failures: int):
        images = [None] * len(tiles)
        failures = 0

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(fetch_func, tile.x, tile.y, tile.zoom): index
                for index, tile in enumerate(tiles)
            }
            for future in as_completed(futures):
                index = futures[future]
                try:
                    images[index] = future.result()
                except Exception:
                    failures, should_break = self._handle_failures(failures, max_failures, futures)
                    if should_break:
                        break
        
        return images
