# from .buffer import Buffer


# class Frame:
#     """
#     Represents a single frame of animation
#     """

#     def __init__(self, duration: float = 0.1):
#         self.duration = duration
#         self.is_key_frame = False


# class KeyFrame(Frame):
#     """
#     Represents a key frame of an animation. Contains delta frames
#     """

#     def __init__(self, buffer: Buffer, duration: float = 0):
#         super().__init__(buffer, duration)
#         self.is_key_frame = True
#         self.deltas : list[Frame] = []


# class Animation:
#     """
#     Represents an animated buffer.

#     """
#     def __init__(self):
#         self.frames = []
#         self

#     def render(self, time: float, start_time: float=0, buffer: Buffer = None):
#         """
#         Renders the animation at the given time.
#         :param time: The current time in seconds
#         :param start_time: The time at which the animation started
#         """
