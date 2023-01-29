#!/usr/bin/python3

from spyglass.server import StreamingHandler, StreamingServer
from . import logger

class StreamingHandlerUSB(StreamingHandler):
    def get_frame(self):
        #TODO: Cuts framerate in 1/n with n streams open, add some kind of buffer
        return self.output.capture_buffer()
    
    
def run_usb_server(bind_address, port, cam, stream_url='/stream', snapshot_url='/snapshot'):
    logger.info('Server listening on %s:%d', bind_address, port)
    logger.info('Streaming endpoint: %s', stream_url)
    logger.info('Snapshot endpoint: %s', snapshot_url)
    address = (bind_address, port)
    streaming_handler = StreamingHandlerUSB
    streaming_handler.output = cam
    streaming_handler.stream_url = stream_url
    streaming_handler.snapshot_url = snapshot_url
    current_server = StreamingServer(address, streaming_handler)
    current_server.serve_forever()