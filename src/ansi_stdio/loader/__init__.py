from functools import lru_cache
from pathlib import Path

LOADERS = []


def load(path: Path):
    """
    Loads a buffer-like object from a file.
    """
    _load_cached(path.resolve())


@lru_cache
def _load_cached(absolute_path: Path):
    """
    Caches the load operation by absolute path.
    """
    for loader in LOADERS:
        try:
            return loader(absolute_path)
        except ValueError:
            pass
