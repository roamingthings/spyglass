import argparse
import pytest
from unittest.mock import MagicMock, ANY, patch

AF_SPEED_ENUM_NORMAL = 1
AF_SPEED_ENUM_FAST = 2
AF_MODE_ENUM_CONTINUOUS = 2
AF_MODE_ENUM_MANUAL = 3

DEFAULT_HEIGHT = 480
DEFAULT_WIDTH = 640
DEFAULT_FLIP_VERTICALLY = False
DEFAULT_FLIP_HORIZONTALLY = False
DEFAULT_UPSIDE_DOWN = False
DEFAULT_LENS_POSITION = 0.0
DEFAULT_FPS = 15
DEFAULT_AF_SPEED = AF_SPEED_ENUM_NORMAL
DEFAULT_AUTOFOCUS_MODE = AF_MODE_ENUM_CONTINUOUS


@pytest.fixture(autouse=True)
def mock_libraries(mocker):
    mock_libcamera = MagicMock()
    mock_picamera2 = MagicMock()
    mock_picamera2_encoders = MagicMock()
    mock_picamera2_outputs = MagicMock()
    mocker.patch.dict('sys.modules', {
        'libcamera': mock_libcamera,
        'picamera2': mock_picamera2,
        'picamera2.encoders': mock_picamera2_encoders,
        'picamera2.outputs': mock_picamera2_outputs,
    })
    mocker.patch('libcamera.controls.AfModeEnum.Manual', AF_MODE_ENUM_MANUAL)
    mocker.patch('libcamera.controls.AfModeEnum.Continuous', AF_MODE_ENUM_CONTINUOUS)
    mocker.patch('libcamera.controls.AfSpeedEnum.Normal', AF_SPEED_ENUM_NORMAL)
    mocker.patch('libcamera.controls.AfSpeedEnum.Fast', AF_SPEED_ENUM_FAST)


def test_parse_bindaddress():
    from spyglass import cli
    args = cli.get_args(['-b', '1.2.3.4'])
    assert args.bindaddress == '1.2.3.4'


def test_parse_port():
    from spyglass import cli
    args = cli.get_args(['-p', '123'])
    assert args.port == 123


def test_parse_resolution():
    from spyglass import cli
    args = cli.get_args(['-r', '100x200'])
    assert args.resolution == '100x200'


def test_split_resolution():
    from spyglass import cli
    (width, height) = cli.split_resolution('100x200')
    assert width == 100
    assert height == 200


@patch("spyglass.server.run_server")
@patch("spyglass.camera.init_camera")
def test_init_camera_with_defaults(mock_spyglass_camera, mock_spyglass_server):
    from spyglass import cli
    import spyglass.camera
    cli.main(args=[])
    spyglass.camera.init_camera.assert_called_once_with(
        DEFAULT_WIDTH,
        DEFAULT_HEIGHT,
        DEFAULT_FPS,
        DEFAULT_AUTOFOCUS_MODE,
        DEFAULT_LENS_POSITION,
        DEFAULT_AF_SPEED,
        DEFAULT_UPSIDE_DOWN,
        DEFAULT_FLIP_HORIZONTALLY,
        DEFAULT_FLIP_VERTICALLY
    )


@patch("spyglass.server.run_server")
@patch("spyglass.camera.init_camera")
def test_init_camera_resolution(mock_spyglass_server, mock_spyglass_camera):
    from spyglass import cli
    import spyglass.camera
    cli.main(args=[
        '-r', '200x100'
    ])
    spyglass.camera.init_camera.assert_called_once_with(
        200,
        100,
        DEFAULT_FPS,
        DEFAULT_AUTOFOCUS_MODE,
        DEFAULT_LENS_POSITION,
        DEFAULT_AF_SPEED,
        DEFAULT_UPSIDE_DOWN,
        DEFAULT_FLIP_HORIZONTALLY,
        DEFAULT_FLIP_VERTICALLY
    )


def test_raise_error_when_width_greater_than_maximum():
    from spyglass import cli
    with pytest.raises(argparse.ArgumentTypeError):
        cli.main(args=[
            '-r', '1921x1920'
        ])


def test_raise_error_when_height_greater_than_maximum():
    from spyglass import cli
    with pytest.raises(argparse.ArgumentTypeError):
        cli.main(args=[
            '-r', '1920x1921'
        ])


@patch("spyglass.server.run_server")
@patch("spyglass.camera.init_camera")
def test_init_camera_fps(mock_spyglass_server, mock_spyglass_camera):
    from spyglass import cli
    import spyglass.camera
    cli.main(args=[
        '-f', '20'
    ])
    spyglass.camera.init_camera.assert_called_once_with(
        DEFAULT_WIDTH,
        DEFAULT_HEIGHT,
        20,
        DEFAULT_AUTOFOCUS_MODE,
        DEFAULT_LENS_POSITION,
        DEFAULT_AF_SPEED,
        DEFAULT_UPSIDE_DOWN,
        DEFAULT_FLIP_HORIZONTALLY,
        DEFAULT_FLIP_VERTICALLY
    )


@patch("spyglass.server.run_server")
@patch("spyglass.camera.init_camera")
def test_init_camera_af_manual(mock_spyglass_server, mock_spyglass_camera):
    from spyglass import cli
    import spyglass.camera
    cli.main(args=[
        '-af', 'manual'
    ])
    spyglass.camera.init_camera.assert_called_once_with(
        DEFAULT_WIDTH,
        DEFAULT_HEIGHT,
        DEFAULT_FPS,
        AF_MODE_ENUM_MANUAL,
        DEFAULT_LENS_POSITION,
        DEFAULT_AF_SPEED,
        DEFAULT_UPSIDE_DOWN,
        DEFAULT_FLIP_HORIZONTALLY,
        DEFAULT_FLIP_VERTICALLY
    )


@patch("spyglass.server.run_server")
@patch("spyglass.camera.init_camera")
def test_init_camera_af_continuous(mock_spyglass_server, mock_spyglass_camera):
    from spyglass import cli
    import spyglass.camera
    cli.main(args=[
        '-af', 'continuous'
    ])
    spyglass.camera.init_camera.assert_called_once_with(
        DEFAULT_WIDTH,
        DEFAULT_HEIGHT,
        DEFAULT_FPS,
        AF_MODE_ENUM_CONTINUOUS,
        DEFAULT_LENS_POSITION,
        DEFAULT_AF_SPEED,
        DEFAULT_UPSIDE_DOWN,
        DEFAULT_FLIP_HORIZONTALLY,
        DEFAULT_FLIP_VERTICALLY
    )


@patch("spyglass.server.run_server")
@patch("spyglass.camera.init_camera")
def test_init_camera_lens_position(mock_spyglass_server, mock_spyglass_camera):
    from spyglass import cli
    import spyglass.camera
    cli.main(args=[
        '-l', '1.0'
    ])
    spyglass.camera.init_camera.assert_called_once_with(
        DEFAULT_WIDTH,
        DEFAULT_HEIGHT,
        DEFAULT_FPS,
        DEFAULT_AUTOFOCUS_MODE,
        1.0,
        DEFAULT_AF_SPEED,
        DEFAULT_UPSIDE_DOWN,
        DEFAULT_FLIP_HORIZONTALLY,
        DEFAULT_FLIP_VERTICALLY
    )


@patch("spyglass.server.run_server")
@patch("spyglass.camera.init_camera")
def test_init_camera_af_speed_normal(mock_spyglass_server, mock_spyglass_camera):
    from spyglass import cli
    import spyglass.camera
    cli.main(args=[
        '-s', 'normal'
    ])
    spyglass.camera.init_camera.assert_called_once_with(
        DEFAULT_WIDTH,
        DEFAULT_HEIGHT,
        DEFAULT_FPS,
        DEFAULT_AUTOFOCUS_MODE,
        DEFAULT_LENS_POSITION,
        AF_SPEED_ENUM_NORMAL,
        DEFAULT_UPSIDE_DOWN,
        DEFAULT_FLIP_HORIZONTALLY,
        DEFAULT_FLIP_VERTICALLY
    )


@patch("spyglass.server.run_server")
@patch("spyglass.camera.init_camera")
def test_init_camera_af_speed_fast(mock_spyglass_server, mock_spyglass_camera):
    from spyglass import cli
    import spyglass.camera
    cli.main(args=[
        '-s', 'fast'
    ])
    spyglass.camera.init_camera.assert_called_once_with(
        DEFAULT_WIDTH,
        DEFAULT_HEIGHT,
        DEFAULT_FPS,
        DEFAULT_AUTOFOCUS_MODE,
        DEFAULT_LENS_POSITION,
        AF_SPEED_ENUM_FAST,
        DEFAULT_UPSIDE_DOWN,
        DEFAULT_FLIP_HORIZONTALLY,
        DEFAULT_FLIP_VERTICALLY
    )


@patch("spyglass.server.run_server")
@patch("spyglass.camera.init_camera")
def test_init_camera_upside_down(mock_spyglass_server, mock_spyglass_camera):
    from spyglass import cli
    import spyglass.camera
    cli.main(args=[
        '-ud'
    ])
    spyglass.camera.init_camera.assert_called_once_with(
        DEFAULT_WIDTH,
        DEFAULT_HEIGHT,
        DEFAULT_FPS,
        DEFAULT_AUTOFOCUS_MODE,
        DEFAULT_LENS_POSITION,
        DEFAULT_AF_SPEED,
        True,
        DEFAULT_FLIP_HORIZONTALLY,
        DEFAULT_FLIP_VERTICALLY
    )


@patch("spyglass.server.run_server")
@patch("spyglass.camera.init_camera")
def test_init_camera_flip_horizontal(mock_spyglass_server, mock_spyglass_camera):
    from spyglass import cli
    import spyglass.camera
    cli.main(args=[
        '-fh'
    ])
    spyglass.camera.init_camera.assert_called_once_with(
        DEFAULT_WIDTH,
        DEFAULT_HEIGHT,
        DEFAULT_FPS,
        DEFAULT_AUTOFOCUS_MODE,
        DEFAULT_LENS_POSITION,
        DEFAULT_AF_SPEED,
        DEFAULT_UPSIDE_DOWN,
        True,
        DEFAULT_FLIP_VERTICALLY
    )


@patch("spyglass.server.run_server")
@patch("spyglass.camera.init_camera")
def test_init_camera_flip_vertical(mock_spyglass_server, mock_spyglass_camera):
    from spyglass import cli
    import spyglass.camera
    cli.main(args=[
        '-fv'
    ])
    spyglass.camera.init_camera.assert_called_once_with(
        DEFAULT_WIDTH,
        DEFAULT_HEIGHT,
        DEFAULT_FPS,
        DEFAULT_AUTOFOCUS_MODE,
        DEFAULT_LENS_POSITION,
        DEFAULT_AF_SPEED,
        DEFAULT_UPSIDE_DOWN,
        DEFAULT_FLIP_HORIZONTALLY,
        True
    )


@patch("spyglass.server.run_server")
@patch("spyglass.camera.init_camera")
def test_run_server_with_configuration_from_arguments(mock_spyglass_server, mock_spyglass_camera):
    from spyglass import cli
    import spyglass.server
    cli.main(args=[
        '-b', '1.2.3.4',
        '-p', '1234',
        '-st', 'streaming-url',
        '-sn', 'snapshot-url',
        '-or', 'h'
    ])
    spyglass.server.run_server.assert_called_once_with('1.2.3.4', 1234, ANY, 'streaming-url', 'snapshot-url', 1)


@patch("spyglass.server.run_server")
@patch("spyglass.camera.init_camera")
@pytest.mark.parametrize("input_value, expected_output", [
    ('h', 1),
    ('mh', 2),
    ('r180', 3),
    ('mv', 4),
    ('mhr270', 5),
    ('r90', 6),
    ('mhr90', 7),
    ('r270', 8),
])
def test_run_server_with_orientation(mock_spyglass_server, mock_spyglass_camera, input_value, expected_output):
    from spyglass import cli
    import spyglass.server
    cli.main(args=[
        '-b', '1.2.3.4',
        '-p', '1234',
        '-st', 'streaming-url',
        '-sn', 'snapshot-url',
        '-or', input_value
    ])
    spyglass.server.run_server.assert_called_once_with(
        '1.2.3.4',
        1234,
        ANY,
        'streaming-url',
        'snapshot-url',
        expected_output
    )
