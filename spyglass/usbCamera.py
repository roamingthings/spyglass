import libcamera
from picamera2 import Picamera2


def init_usb_camera(
        width: int,
        height: int,
        fps: int,
        autofocus: str,
        lens_position: float,
        autofocus_speed: str,
        camera_num: int):

    picam2 = Picamera2(camera_num)

    controls = {}

    if 'AfMode' in picam2.camera_controls:
        controls['AfMode'] = autofocus
        controls['AfSpeed'] = autofocus_speed
        if autofocus == libcamera.controls.AfModeEnum.Manual:
            controls['LensPosition'] = lens_position
    else:
        print('Attached camera does not support autofocus')

    picam2.configure(picam2.create_preview_configuration(main={'size': (width, height), 'format': 'MJPEG'}, controls=controls))

    return picam2
