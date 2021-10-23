#!/usr/bin/env python

import os
import struct
import sys
import time
import usb.core
from usb.util import CTRL_TYPE_STANDARD, CTRL_TYPE_VENDOR, CTRL_IN, CTRL_RECIPIENT_DEVICE

VENDOR_ID= 0x04e8
MODELS = {
    'SPF-72H': {
        'product_id': (0x200a, 0x200b),
        'geometry': '800x480',
    },
    'SPF-75H': {
        'product_id': (0x200e, 0x200f),
        'geometry': '800x480',
    },
    'SPF-83H': {
        'product_id': (0x200c, 0x200d),
        'geometry': '800x480',
    },
    'SPF-85H': {
        'product_id': (0x2012, 0x2013),
        'geometry': '800x480',
    },
    'SPF-87H': {
        'product_id': (0x2033, 0x2034),
        'geometry': '800x480',
    },
    'SPF-87H (old firmware)': {
        'product_id': (0x2025, 0x2026),
        'geometry': '800x480',
    },
    'SPF-107H': {
        'product_id': (0x2035, 0x2036),
        'geometry': '800x480',
    },
    'SPF-107H (old firmware)': {
        'product_id': (0x2027, 0x2028),
        'geometry': '800x480',
    },
}

CHUNK_SIZE = 0x4000
BUFFER_SIZE = 0x20000

def expect(result, expected):
    results = result.tolist()
    if results != expected:
        print("Warning: Expected " + str(expected) + " but got " + str(results), file=sys.stderr)

class FrameController():
    def __init__(self):
        for model, info in MODELS.items():
            self.dev = usb.core.find(idVendor=VENDOR_ID, idProduct=info['product_id'][0])
            if self.dev:
                print("Found " + model + " in storage mode")
                self.change_mode()
                time.sleep(1)
                self.dev = usb.core.find(idVendor=VENDOR_ID, idProduct=info['product_id'][1])
            else:
                self.dev = usb.core.find(idVendor=VENDOR_ID, idProduct=info['product_id'][1])

            if self.dev:
                print("Found " + model + " in display mode")
                self.current_model = model
                self.dev.set_configuration()
                self.display_mode_setup()
                return

        print("No supported devices found", file=sys.stderr)
        sys.exit(-1)

    def change_mode(self):
        print("Setting device to display mode")
        try:
            self.dev.ctrl_transfer(CTRL_TYPE_STANDARD | CTRL_IN | CTRL_RECIPIENT_DEVICE, 0x06, 0xfe, 0xfe, 254)
            print(self.dev)
        except usb.core.USBError as e:
            # Ignore Input/Output Error since the device will now be disconnected
            if e.errno != 5:
                raise e

    def display_mode_setup(self):
        print("Sending setup commands to device")
        if self.current_model in ('SPF-72H', 'SPF-83H', 'SPF-85H', 'SPF-87H', 'SPF-107H'):
            result = self.dev.ctrl_transfer(CTRL_TYPE_VENDOR | CTRL_IN | CTRL_RECIPIENT_DEVICE, 0x04, 0x00, 0x00, 1)
            expect(result, [ 0x03 ])
        elif self.current_model in ('SPF-75H'):
            result = self.dev.ctrl_transfer(CTRL_TYPE_VENDOR | CTRL_IN | CTRL_RECIPIENT_DEVICE, 0x01, 0x00, 0x00, 2)
            expect(result, [ 0x09, 0x04 ])
        else:
            result = self.dev.ctrl_transfer(CTRL_TYPE_VENDOR | CTRL_IN | CTRL_RECIPIENT_DEVICE, 0x02, 0x00, 0x00, 1)
            expect(result, [ 0x46 ])

    def padded_bytes(self, buf, size):
        diff = size - len(buf)
        return buf + bytes(b'\x00') * diff

    def chunky_write(self, buf):
        pos = 0
        while pos < BUFFER_SIZE:
            self.dev.write(0x02, buf[pos:pos+CHUNK_SIZE])
            pos += CHUNK_SIZE

    def write_image(self, content):
#        result = self.dev.ctrl_transfer(CTRL_TYPE_STANDARD | CTRL_IN | CTRL_RECIPIENT_DEVICE, 0x06, 0x0300, 0x00, 255)
#        expect(result, [ 0x04, 0x03, 0x09, 0x04 ])

        if self.current_model in ('SPF-75H'):
            result = self.dev.ctrl_transfer(CTRL_TYPE_STANDARD | CTRL_IN | CTRL_RECIPIENT_DEVICE, 0x06, 0x0301, 0x0409, 255)

        size = struct.pack('I', len(content))
        header = b'\xa5\x5a\x09\x04' + size + b'\x46\x00\x00\x00'

        content = header + content

        pos = 0
        while pos < len(content):
            buf = self.padded_bytes(content[pos:pos+BUFFER_SIZE], BUFFER_SIZE)
            self.chunky_write(buf)
            pos += BUFFER_SIZE

#        result = self.dev.ctrl_transfer(CTRL_TYPE_VENDOR | CTRL_IN | CTRL_RECIPIENT_DEVICE, 0x06, 0x00, 0x00, 2)
#        expect(result, [ 0x00, 0x00 ])

    def write_image_from_file(self, filename):
        with open(filename, "rb") as f:
            self.write_image(f.read())

    def get_display_geometry(self):
        return MODELS[self.current_model]['geometry']

if __name__ == '__main__':
    frame_ctrl = FrameController()

    if len(sys.argv) < 2 or sys.argv[1] == "-":
        print("Reading file from stdin")
        content = sys.stdin.buffer.read()
        frame_ctrl.write_image(content)
    else:
        print("Reading from file " + sys.argv[1])
        frame_ctrl.write_image_from_file(sys.argv[1])
