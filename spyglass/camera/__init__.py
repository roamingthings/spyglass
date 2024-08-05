from .camera import Camera
from .csi import CSI
from .usb import USB

from picamera2 import Picamera2

def init_camera(
        camera_num: int,
        tuning_filter=None,
        tuning_filter_dir=None
        ) -> Camera:
    tuning = None

    if tuning_filter:
        params = {'tuning_file': tuning_filter}
        if tuning_filter_dir:
            params['dir'] = tuning_filter_dir
        tuning = Picamera2.load_tuning_file(**params)

    picam2 = Picamera2(camera_num, tuning=tuning)
    if picam2._is_rpi_camera():
        cam = CSI(picam2)
    else:
        cam = USB(picam2)
    return cam
