

from io import BytesIO
import abc

class CameraInterface(metaclass=abc.ABCMeta):
    """
    Interface for camera module
    """
    @abc.abstractmethod
    def capture(self) -> BytesIO:
        pass