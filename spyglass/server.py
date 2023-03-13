import io
import logging
import socketserver
from http import server
from threading import Condition
from urllib.parse import urlparse, parse_qsl
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


def run_server(bind_address, port, output, stream_url='/stream', snapshot_url='/snapshot'):
    class StreamingHandler(server.BaseHTTPRequestHandler):        
        def do_GET(self):
            if self.check_urls_match(stream_url, self.path):
                self.start_streaming()
            elif self.check_urls_match(snapshot_url, self.path):
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
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
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
                with output.condition:
                    output.condition.wait()
                    frame = output.frame
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
            
        def check_paths_match(self, expected_url, incoming_url):
            
            # Assign paths from URL into list
            exp_paths = urlparse(expected_url.strip("/")).path.split("/")
            inc_paths = urlparse(incoming_url.strip("/")).path.split("/")
            
            # Drop ip/hostname if present in path
            if '.' in exp_paths[0]: exp_paths.pop(0)
            if '.' in inc_paths[0]: inc_paths.pop(0)
            
            # Determine if match
            if len(exp_paths)==len(inc_paths):
                return all([exp == inc for exp, inc in zip(exp_paths, inc_paths)])
            
            return False
        
        def check_params_match(self, expected_url, incoming_url):
            
            # Check URL params
            exp_params = parse_qsl(urlparse(expected_url).query)
            inc_params = parse_qsl(urlparse(incoming_url).query)
            
            # Create list of matching params
            matching_params = list(set(exp_params) & set(inc_params))
            
            # Update list order for expected params
            exp_params = list(set(exp_params))
            
            if matching_params and exp_params:
                return matching_params==exp_params
            
            return False
        
        def check_urls_match(self, expected_url, incoming_url):
            
            # Check URL paths
            paths_match = self.check_paths_match(expected_url, incoming_url)
            
            # Check URL params
            params_match = self.check_params_match(expected_url, incoming_url)
            
            return paths_match and params_match

    logger.info('Server listening on %s:%d', bind_address, port)
    logger.info('Streaming endpoint: %s', stream_url)
    logger.info('Snapshot endpoint: %s', snapshot_url)
    address = (bind_address, port)
    current_server = StreamingServer(address, StreamingHandler)
    current_server.serve_forever()
