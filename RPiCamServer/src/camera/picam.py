
from camera_interface import CameraInterface
from PiCamera import PiCamera
from time import sleep

class PiCam(CameraInterface):
    """
    Wrapper for picamera module
    """
    
    def __init__(self):
        camera = PiCamera()
        camera.start_preview()
        sleep(2)
        self._camera = camera
    
    def capture(self) -> BytesIO:
        stream = BytesIO()
        self._camera.capture(stream, format='jpeg')
        stream.seek(0)
        return stream