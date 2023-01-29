#!/usr/bin/python3

import io
import logging
import socketserver
from http import server
from threading import Condition
from . import logger


class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

class StreamingHandler(server.BaseHTTPRequestHandler):
    output = None
    stream_url = ''
    snapshot_url = ''

    def do_GET(self):
        if self.path == self.stream_url:
            self.start_streaming()
        elif self.path == self.snapshot_url:
            self.send_snapshot()
        else:
            self.send_error(404)
            self.end_headers()

    def start_streaming(self):
        try:
            self.send_response(200)
            self.send_default_headers()
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            while True:
                frame = self.get_frame()
                self.wfile.write(b'--FRAME\r\n')
                self.send_jpeg_content_headers(frame)
                self.end_headers()
                self.wfile.write(frame)
                self.wfile.write(b'\r\n')
        except Exception as e:
            logging.warning('Removed streaming client %s: %s', self.client_address, str(e))

    def send_snapshot(self):
        try:
            self.send_response(200)
            self.send_default_headers()
            frame = self.get_frame()
            self.send_jpeg_content_headers(frame)
            self.end_headers()
            self.wfile.write(frame)
        except Exception as e:
            logging.warning(
                'Removed client %s: %s',
                self.client_address, str(e))

    def send_default_headers(self):
        self.send_header('Age', 0)
        self.send_header('Cache-Control', 'no-cache, private')
        self.send_header('Pragma', 'no-cache')

    def send_jpeg_content_headers(self, frame):
        self.send_header('Content-Type', 'image/jpeg')
        self.send_header('Content-Length', len(frame))

    def get_frame(self):
        with self.output.condition:
            self.output.condition.wait()
            return self.output.frame

def run_server(bind_address, port, output, stream_url='/stream', snapshot_url='/snapshot'):
    logger.info('Server listening on %s:%d', bind_address, port)
    logger.info('Streaming endpoint: %s', stream_url)
    logger.info('Snapshot endpoint: %s', snapshot_url)
    address = (bind_address, port)
    streaming_handler = StreamingHandler
    streaming_handler.output = output
    streaming_handler.stream_url = stream_url
    streaming_handler.snapshot_url = snapshot_url
    current_server = StreamingServer(address, streaming_handler)
    current_server.serve_forever()
