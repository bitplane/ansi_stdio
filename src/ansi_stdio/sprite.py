from .buffer import Buffer


class Sprite:
    """
    An animated character buffer
    """

    def __init__(self):
        """
        Initialize the sprite.
        """
        pass

    def get_frame(self, t=None) -> Buffer:
        """
        Get the buffer for the given time in seconds
        """
        raise NotImplementedError

    def __len__(self):
        """
        Get the number of frames in the sprite.
        """
        return 1
