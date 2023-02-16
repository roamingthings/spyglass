import libcamera
import json
from picamera2 import Picamera2


def init_camera(
        width: int,
        height: int,
        fps: int,
        autofocus: str,
        lens_position: float,
        autofocus_speed: str,
        upsidedown=False,
        flip_horizontal=False,
        flip_vertical=False,
        control_string='{}'):

    picam2 = Picamera2()

    controls = {'FrameRate': fps}

    # preprocessing for json.loads
    control_string = control_string.replace('\'', '\"').replace('True', 'true').replace('False', 'false')

    c = process_control_string(picam2, control_string)
    controls.update(c)

    if 'AfMode' in picam2.camera_controls:
        controls['AfMode'] = autofocus
        controls['AfSpeed'] = autofocus_speed
        if autofocus == libcamera.controls.AfModeEnum.Manual:
            controls['LensPosition'] = lens_position
    else:
        print('Attached camera does not support autofocus')

    transform = libcamera.Transform(hflip=int(flip_horizontal or upsidedown), vflip=int(flip_vertical or upsidedown))

    picam2.configure(picam2.create_video_configuration(main={'size': (width, height)}, controls=controls, transform=transform))

    return picam2

def process_control_string(camera, control_string):
    controls_dict = camera.camera_controls
    try:
        string_dict = json.loads(control_string)
    except (TypeError, json.decoder.JSONDecodeError):
        return {}
    controls = {}
    for key in string_dict:
        for k in controls_dict:
            if key.lower() == k.lower():
                controls[k] = string_dict[key]

    return controls
