#!/usr/bin/python3

import logging
import socketserver
from http import server
import io
import logging
import socketserver
from http import server
from threading import Condition
from spyglass.url_parsing import check_urls_match, get_url_params
from spyglass.exif import create_exif_header
from spyglass.camera_options import parse_dictionary_to_html_page, process_controls

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

class StreamingHandler(server.BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.picam2 = None
        self.exif_header = None
        self.stream_url = None
        self.snapshot_url = None
        self.get_frame = None

    def do_GET(self):
        if check_urls_match(self.stream_url, self.path):
            self.start_streaming()
        elif check_urls_match(self.snapshot_url, self.path):
            self.send_snapshot()
        elif check_urls_match('/controls', self.path):
            parsed_controls = get_url_params(self.path)
            parsed_controls = parsed_controls if parsed_controls else None
            processed_controls = process_controls(self.picam2, parsed_controls)
            self.picam2.set_controls(processed_controls)
            content = parse_dictionary_to_html_page(self.picam2, parsed_controls, processed_controls).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
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
                if self.exif_header is None:
                    self.send_jpeg_content_headers(frame)
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
                else:
                    self.send_jpeg_content_headers(frame, len(self.exif_header) - 2)
                    self.end_headers()
                    self.wfile.write(self.exif_header)
                    self.wfile.write(frame[2:])
                    self.wfile.write(b'\r\n')
        except Exception as e:
            logging.warning('Removed streaming client %s: %s', self.client_address, str(e))

    def send_snapshot(self):
        try:
            self.send_response(200)
            self.send_default_headers()
            frame = self.get_frame()
            if self.exif_header is None:
                self.send_jpeg_content_headers(frame)
                self.end_headers()
                self.wfile.write(frame)
            else:
                self.send_jpeg_content_headers(frame, len(self.exif_header) - 2)
                self.end_headers()
                self.wfile.write(self.exif_header)
                self.wfile.write(frame[2:])
        except Exception as e:
            logging.warning(
                'Removed client %s: %s',
                self.client_address, str(e))

    def send_default_headers(self):
        self.send_header('Age', 0)
        self.send_header('Cache-Control', 'no-cache, private')
        self.send_header('Pragma', 'no-cache')

    def send_jpeg_content_headers(self, frame, extra_len=0):
        self.send_header('Content-Type', 'image/jpeg')
        self.send_header('Content-Length', str(len(frame) + extra_len))
