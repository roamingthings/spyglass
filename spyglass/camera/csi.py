import io
import libcamera

from picamera2.encoders import MJPEGEncoder
from picamera2.outputs import FileOutput
from threading import Condition

from . import camera
from ..server import StreamingHandler

class CSI(camera.Camera):
    def start_and_run_server(self,
            bind_address,
            port,
            stream_url='/stream',
            snapshot_url='/snapshot',
            orientation_exif=0):

        class StreamingOutput(io.BufferedIOBase):
            def __init__(self):
                self.frame = None
                self.condition = Condition()

            def write(self, buf):
                with self.condition:
                    self.frame = buf
                    self.condition.notify_all()
        output = StreamingOutput()
        def get_frame(self):
            with output.condition:
                output.condition.wait()
                return output.frame

        self.picam2.start_recording(MJPEGEncoder(), FileOutput(output))

        self._run_server(
            bind_address,
            port,
            StreamingHandler,
            get_frame,
            stream_url=stream_url,
            snapshot_url=snapshot_url,
            orientation_exif=orientation_exif
        )

    def stop(self):
        self.picam2.stop_recording()
