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

    params: Params = None

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

    def arguments(self) -> dict[str, Any]:
        """
        Get the arguments needed to construct this object.
        Filters out any arguments that are the same as the default value.
        """
        out = {}
        for name, param in self.params.items():
            value = getattr(self, name)
            if value != param.default:
                out[name] = value
        return out

    def save(self) -> dict:
        """
        Convert the instance to a dictionary.
        """
        return {"class": self.__class__.__name__} | {
            k: v.save() if hasattr(v, "save") else v
            for k, v in self.arguments().items()
        }

    @classmethod
    def load(data: dict[str, Any]) -> "Saved":
        cls = CLASSES[data["class"]].type
        args = {
            k: Saved.load(v) if Saved.is_loadable(v) else v
            for k, v in data["args"].items()
        }
        return cls(**args)

    @staticmethod
    def is_loadable(val: Any) -> bool:
        return isinstance(val, dict) and "class" in val and val["class"] in CLASSES
