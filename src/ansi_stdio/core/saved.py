import inspect
from dataclasses import dataclass
from typing import Any

__version__ = "0.1.0"


@dataclass(slots=True)
class Param:
    """
    Represents a parameter.
    """

    type: type
    default: Any = None


@dataclass(slots=True)
class Params:
    """
    Holds kwargs and constructor function for a class.
    """

    type: type
    params: dict[str, Param]


CLASSES: dict[str, Params] = {}


class Saved:
    """
    A class that can be serialized and deserialized.
    """

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.__name__ in CLASSES:
            raise ValueError(f"Duplicate Saved type: {cls.__name__}")

        sig = inspect.signature(cls.__init__)
        params: dict[str, Param] = {}
        for name, param in sig.parameters.items():
            if name == "self":
                continue
            # If no annotation is given, fall back to Any
            param_type = (
                param.annotation
                if param.annotation is not inspect.Parameter.empty
                else Any
            )
            default = (
                param.default if param.default is not inspect.Parameter.empty else None
            )
            params[name] = Param(type=param_type, default=default)

        CLASSES[cls.__name__] = Params(type=cls, params=params)

        # Set params to the __init__ signature
        cls.params = CLASSES[cls.__name__].params

    # def __json__(self) -> dict:
    #     """
    #     Convert the instance to a dictionary.
    #     """

    #     # get kargs from __init__ signature
    #     # and filter out any that start with "_"
    #     kwargs = self.__init__.__code__.

    #     if self.__class__ in (list, tuple, dict, set):

    # @classmethod
    # def from_dict(cls, data: dict) -> 'Saved':
    #     typename = data.pop("type")
    #     return TYPES[typename](**{
    #         k: Saved._maybe_recurse(v)
    #         for k, v in data.items()
    #     })
