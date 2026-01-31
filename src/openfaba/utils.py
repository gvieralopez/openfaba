from contextlib import contextmanager
from typing import Iterator

from mutagen.id3._util import BitPaddedInt


@contextmanager
def allow_invalid_synchsafe_in_mutagen() -> Iterator[None]:
    """
    Temporarily disable synchsafe integer validation.
    Intended only for ID3 deletion paths.
    """
    orig = BitPaddedInt.has_valid_padding
    BitPaddedInt.has_valid_padding = lambda *_: True  # type: ignore[method-assign]
    try:
        yield
    finally:
        BitPaddedInt.has_valid_padding = orig  # type: ignore[method-assign]
