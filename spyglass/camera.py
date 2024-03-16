import libcamera
from spyglass.camera_options import process_controls
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
        control_list: list[list[str]]=[],
        tuning_filter=None,
        tuning_filter_dir=None):

    tuning = None

    if tuning_filter:
        params = {'tuning_file': tuning_filter}
        if tuning_filter_dir:
            params['dir'] = tuning_filter_dir
        tuning = Picamera2.load_tuning_file(**params)

    picam2 = Picamera2(tuning=tuning)
    controls = {'FrameRate': fps}

    c = process_controls(picam2, [tuple(ctrl) for ctrl in control_list])
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
