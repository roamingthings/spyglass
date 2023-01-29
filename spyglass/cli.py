"""cli entry point for hellocli.

Parse command line arguments in, invoke hello.
"""
import argparse
import sys
import libcamera
import re
from spyglass.camera import init_camera
from spyglass.usbCamera import init_usb_camera
from spyglass.server import StreamingOutput
from spyglass.server import run_server
from spyglass.usbServer import run_usb_server
from picamera2.encoders import MJPEGEncoder
from picamera2.outputs import FileOutput


def main(args=None):
    """Entry point for hello cli.

    The setup_py entry_point wraps this in sys.exit already so this effectively
    becomes sys.exit(main()).
    The __main__ entry point similarly wraps sys.exit().
    """
    if args is None:
        args = sys.argv[1:]

    parsed_args = get_args(args)

    bind_address = parsed_args.bindaddress
    port = parsed_args.port
    width, height = split_resolution(parsed_args.resolution)
    stream_url = parsed_args.stream_url
    snapshot_url = parsed_args.snapshot_url
    is_usbcam = parsed_args.is_usbcam

    if is_usbcam:
        picam2 = init_usb_camera(
                        width,
                        height,
                        parsed_args.fps,
                        parse_autofocus(parsed_args.autofocus),
                        parsed_args.lensposition,
                        parse_autofocus_speed(parsed_args.autofocusspeed),
                        parsed_args.camera_num)
        try:
            picam2.start()
            run_usb_server(bind_address, port, picam2, stream_url, snapshot_url)
        finally:
            picam2.stop()
    else:
        picam2 = init_camera(
                        width,
                        height,
                        parsed_args.fps,
                        parse_autofocus(parsed_args.autofocus),
                        parsed_args.lensposition,
                        parse_autofocus_speed(parsed_args.autofocusspeed),
                        parsed_args.camera_num)
        try:
            output = StreamingOutput()
            picam2.start_recording(MJPEGEncoder(), FileOutput(output))
            run_server(bind_address, port, output, stream_url, snapshot_url)
        finally:
            picam2.stop_recording()


# region args parsers


def resolution_type(arg_value, pat=re.compile(r"^\d+x\d+$")):
    if not pat.match(arg_value):
        raise argparse.ArgumentTypeError("invalid value: <width>x<height> expected.")
    return arg_value


def parse_autofocus(arg_value):
    if arg_value == 'manual':
        return libcamera.controls.AfModeEnum.Manual
    elif arg_value == 'continuous':
        return libcamera.controls.AfModeEnum.Continuous
    raise argparse.ArgumentTypeError("invalid value: manual or continuous expected.")


def parse_autofocus_speed(arg_value):
    if arg_value == 'normal':
        return libcamera.controls.AfSpeedEnum.Normal
    elif arg_value == 'fast':
        return libcamera.controls.AfSpeedEnum.Fast
    raise argparse.ArgumentTypeError("invalid value: normal or fast expected.")


def split_resolution(res):
    parts = res.split('x')
    w = int(parts[0])
    h = int(parts[1])
    return w, h


# endregion args parsers


# region cli args


def get_args(args):
    """Parse arguments passed in from shell."""
    return get_parser().parse_args(args)


def get_parser():
    """Return ArgumentParser for hello cli."""
    parser = argparse.ArgumentParser(
        allow_abbrev=True,
        prog='spyglass',
        description='Start a webserver for Picamera2 videostreams.',
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-b', '--bindaddress', type=str, default='0.0.0.0', help='Bind to address for incoming '
                                                                                 'connections')
    parser.add_argument('-p', '--port', type=int, default=8080, help='Bind to port for incoming connections')
    parser.add_argument('-r', '--resolution', type=resolution_type, default='640x480',
                        help='Resolution of the images width x height')
    parser.add_argument('-f', '--fps', type=int, default=15, help='Frames per second to capture')
    parser.add_argument('-st', '--stream_url', type=str, default='/stream',
                        help='Sets the URL for the mjpeg stream')
    parser.add_argument('-sn', '--snapshot_url', type=str, default='/snapshot',
                        help='Sets the URL for snapshots (single frame of stream)')
    parser.add_argument('-af', '--autofocus', type=str, default='continuous', choices=['manual', 'continuous'],
                        help='Autofocus mode')
    parser.add_argument('-l', '--lensposition', type=float, default=0.0,
                        help='Set focal distance. 0 for infinite focus, 0.5 for approximate 50cm. '
                             'Only used with Autofocus manual')
    parser.add_argument('-s', '--autofocusspeed', type=str, default='normal', choices=['normal', 'fast'],
                        help='Autofocus speed. Only used with Autofocus continuous')
    parser.add_argument('-n', '--camera_num', type=int, default=0, help='Camera number to be used')
    parser.add_argument('-u', '--is_usbcam', action='store_true', help='Make MJPEG USB-Cams usable. Only use if normal method doesn\'t work')
    return parser

# endregion cli args
