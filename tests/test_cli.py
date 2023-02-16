import pytest
from unittest.mock import MagicMock, ANY

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
DEFAULT_CONTROLS = '{}'


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
    mocker.patch('spyglass.camera.init_camera')
    mocker.patch('spyglass.server.run_server')


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


def test_init_camera_with_defaults():
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
        DEFAULT_FLIP_VERTICALLY,
        DEFAULT_CONTROLS
    )


def test_init_camera_resolution():
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
        DEFAULT_FLIP_VERTICALLY,
        DEFAULT_CONTROLS
    )


def test_init_camera_fps():
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
        DEFAULT_FLIP_VERTICALLY,
        DEFAULT_CONTROLS
    )


def test_init_camera_af_manual():
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
        DEFAULT_FLIP_VERTICALLY,
        DEFAULT_CONTROLS
    )


def test_init_camera_af_continuous():
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
        DEFAULT_FLIP_VERTICALLY,
        DEFAULT_CONTROLS
    )


def test_init_camera_lens_position():
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
        DEFAULT_FLIP_VERTICALLY,
        DEFAULT_CONTROLS
    )


def test_init_camera_af_speed_normal():
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
        DEFAULT_FLIP_VERTICALLY,
        DEFAULT_CONTROLS
    )


def test_init_camera_af_speed_fast():
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
        DEFAULT_FLIP_VERTICALLY,
        DEFAULT_CONTROLS
    )


def test_init_camera_upside_down():
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
        DEFAULT_FLIP_VERTICALLY,
        DEFAULT_CONTROLS
    )


def test_init_camera_flip_horizontal():
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
        DEFAULT_FLIP_VERTICALLY,
        DEFAULT_CONTROLS
    )


def test_init_camera_flip_vertical():
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
        True,
        DEFAULT_CONTROLS
    )


def test_init_camera_controls():
    from spyglass import cli
    import spyglass.camera
    cli.main(args=[
        '-c', '{"brightness": -0.4}'
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
        DEFAULT_FLIP_VERTICALLY,
        '{"brightness": -0.4}'
    )


def test_run_server_with_configuration_from_arguments():
    from spyglass import cli
    import spyglass.server
    cli.main(args=[
        '-b', '1.2.3.4',
        '-p', '1234',
        '-st', 'streaming-url',
        '-sn', 'snapshot-url'
    ])
    spyglass.server.run_server.assert_called_once_with('1.2.3.4', 1234, ANY, ANY, 'streaming-url', 'snapshot-url')
