Samsung photo frame control
---------------------------

A small Python application for controlling Samsung photo frames.

Based on:
* [Grace Woo's work](https://web.archive.org/web/20111006080636/http://web.media.mit.edu/~gracewoo/stuff/picframe/)
* [Gekkio's adaptation](https://github.com/Gekkio/samsung-photo-frame-ctrl/)
* [erictroebs changes](https://github.com/erictroebs/samsung-photo-frame-ctrl/)

Features
--------

* If a photo frame is in mass storage mode, the program will change it into mini display mode.
* If a photo frame is in mini display mode, the program will send the jpeg that was specified as the program argument to the photo frame. *The JPEG must be prescaled to the exactly correct size!*

Supported photo frames
----------------------

* SPF-72H (not tested)
* SPF-75H
* SPF-83H
* SPF-85H (not tested)
* SPF-87H
* SPF-107H (not tested)
* (In theory) Other similar Samsung photo frames should work once their product IDs are added into the code

[Thanks to MOA-2011 for listing various product IDs.](https://github.com/MOA-2011/3rdparty-plugins/blob/f11349bc643ac9664276734897c6ab9a4e1d58ba/LCD4linux/src/Photoframe.py).

Dependencies
------------

* [pyusb 1.0](http://github.com/pyusb/pyusb) - usb library for python.
* [imagemagick](https://imagemagick.org/) (Optional for scripts) - excellent tool for converting images on the cli.

Usage
-----

Show JPEG image with the exactly correct size in photo frame:

`sudo ./frame-ctrl.py my_correctly_scaled_image.jpg`

or

`cat my_correctly_scaled_image.jpg | sudo ./frame-ctrl.py`

Start a slideshow with images from a directory:

`python -m scripts.slideshow -i <image interval> <directory with images to show>

Capture a window from X11 and show on photoframe:

`python -m scripts.capture_winodow`

FAQ
---

### Can I use my photo frame as a mini monitor in Linux?

Nope. In theory it's possible but it would require an X driver that would repeatedly compress frames into JPEG format and send them to the photo frame. This is exactly what the Frame Manager software does in Windows.

### Why do I need to use sudo?

libusb needs direct access to the usb device and unless you have set up permissions explicitly, you won't have access to the raw usb devices.
