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

serialport = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=3.0)

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

    def send_to_uart(self, post_data):
        led_r, brightness_r = post_data.split('&')
        led_index = int(led_r.split('=')[1])
        brightness = int(brightness_r.split('=')[1])
        self.log_message("POST data: led_index = %s, brightness = %s",
                        led_index, brightness)

        b = bytearray()
        # add header
        b.extend([0x56, 0x12, 0x54])
        # set lightning number
        b.extend([0x00, 0x00, led_index])
        # command - set brightness
        b.append(0x01)
        # brightness value
        b.append(brightness)
        # lenght + crc32 (4bytes)
        package_length = len(b) + 4
        b.insert(0, package_length)
        # insert crc32 sum
        crc32_str_h = hex(binascii.crc32(b))
        crc32_hex_b = int(crc32_str_h, 16).to_bytes(4, byteorder='big', signed=False)
        b.extend(crc32_hex_b)

        pretty_hex = "0x" + " 0x".join("{:02x}".format(x) for x in b)
        self.log_message("UART: data: %s", pretty_hex)
        k = serialport.write(b)
        self.log_message("UART: sended %s bytes!", k)

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
