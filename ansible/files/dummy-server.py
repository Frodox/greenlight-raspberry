#!/usr/bin/python3 -u

"""
Very simple HTTP server in python.

Usage::
    ./dummy-server.py [<port>]

Send a GET request::
    curl http://localhost

Send a HEAD request::
    curl -I http://localhost

Send a POST request::
    curl -d "foo=bar&bin=baz" http://localhost

"""

from http.server import BaseHTTPRequestHandler, HTTPServer
from sys import argv
#import SocketServer
#import simplejson
import serial
import binascii
import threading
import time

SERIALPORT = serial.Serial(
    "/dev/ttyAMA0",
    baudrate=9600,
    parity=serial.PARITY_EVEN,
    stopbits=serial.STOPBITS_TWO,
    bytesize=serial.EIGHTBITS,
    timeout=3.0,
)
SEND_THREAD = None
LED_INDEX = None
LED_BRIGHTNESS = None


class S(BaseHTTPRequestHandler):
    buffer = 1
    log_file_path = '/var/log/greenlight/greenligh-server.log'
    log_file = open(log_file_path, 'a', buffer)

    def _set_headers(self, code=200):
        self.send_response(code)
        self.send_header('Content-type', 'text/html')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def log_message(self, formatt, *args):
        log = "{} - - [{}] {}\n".format(
                            self.client_address[0],
                            self.log_date_time_string(),
                            formatt % args,
        )
        self.log_file.write(log)
        print(log, end='')
        #print(formatt)
        #print(args)

    def send_to_serial(self):
        global LED_INDEX
        global LED_BRIGHTNESS
        global SERIALPORT

        if LED_INDEX is None or LED_BRIGHTNESS is None:
            self.log_message("LED_INDEX or LED_BRIGHTNESS is None")
            raise Exception("LED_INDEX or LED_BRIGHTNESS is None")

        # TODO: need to sync/Lock with main thread where we change data
        while True:
            if LED_INDEX > 256 or LED_BRIGHTNESS > 256:
                self.log_message("LED_INDEX > 256 or LED_BRIGHTNESS > 256")
                raise Exception("LED_INDEX > 256 or LED_BRIGHTNESS > 256")

            b = bytearray()
            # add header
            b.extend([0x56, 0x12, 0x54])
            # set lightning number
            b.extend([0x00, 0x00, LED_INDEX])
            # command - set brightness
            b.append(0x01)
            # brightness value
            b.append(LED_BRIGHTNESS)
            # lenght + crc32 (4bytes)
            package_length = len(b) + 4
            b.insert(0, package_length)
            # insert crc32 sum
            crc32_str_h = hex(binascii.crc32(b))
            crc32_hex_b = int(crc32_str_h, 16).to_bytes(4, byteorder='big', signed=False)
            b.extend(crc32_hex_b)

            pretty_hex = "0x" + " 0x".join("{:02x}".format(x) for x in b)

            self.log_message("UART: data: %s", pretty_hex)
            k = SERIALPORT.write(b)
            self.log_message("UART: sended %s bytes!", k)
            time.sleep(5)

    def send_to_uart(self, post_data):
        global LED_INDEX
        global LED_BRIGHTNESS
        global SEND_THREAD

        led_r, brightness_r = post_data.split('&')
        LED_INDEX = abs(int(led_r.split('=')[1]))
        LED_BRIGHTNESS = abs(int(brightness_r.split('=')[1]))
        self.log_message("POST data: led_index = %s, brightness = %s",
                        LED_INDEX, LED_BRIGHTNESS)

        if SEND_THREAD is None or not SEND_THREAD.is_alive():
            SEND_THREAD = threading.Thread(target=self.send_to_serial)
            SEND_THREAD.start()

    def show_logs(self):
        self.wfile.write(b"Gotcha logs!\n")

        with open(self.log_file_path, 'r') as content:
            logs = content.read()

        parts = logs.split('\n')
        logs = '<br>\n'.join(list(reversed(parts)))
        #logs = logs.replace('\n', '<br>\n')
        self.wfile.write(b"<br><code>")
        self.wfile.write(logs.encode("utf-8"))
        self.wfile.write(b"</code>")


    def do_GET(self):

        parts = self.requestline.split(' ')
        request_url = parts[1]
        if request_url == "/logs":
            self._set_headers()
            self.show_logs()
        else:
            self._set_headers(404)
            self.wfile.write(b"Ok. But nothing interesting here")

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        # Doesn't do anything with posted data

        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length).decode("utf-8")  # <--- Gets the data itself

        parts = self.requestline.split(' ')
        request_url = parts[1]
        print("Request:", request_url)
        if request_url == "/greenlight":
            self._set_headers()
            l = "Gotcha: {}".format(post_data)
            self.wfile.write(l.encode('utf-8'))
            self.log_message("- - - - - - - - - - - - - - -")
            self.log_message("POST data(raw): %s", post_data)
            self.send_to_uart(post_data)
        else:
            self._set_headers(404)
            self.wfile.write(b"POST only allowed for /greenlight")
            return


def run(server_class=HTTPServer, handler_class=S, port=80):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting httpd at {}...'.format(port))
    httpd.serve_forever()

if __name__ == "__main__":

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
