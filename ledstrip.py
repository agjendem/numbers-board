#!/usr/bin/env python3
import time
from rpi_ws281x import PixelStrip, Color


class LedStrip:
    def __init__(self, brightness=255):
        # LED strip configuration:
        self.LED_COUNT      = 58      # Number of LED pixels.
        self.LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
        self.LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
        self.LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
        self.LED_BRIGHTNESS = brightness     # Set to 0 for darkest and 255 for brightest
        self.LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
        self.LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

        self.strip = PixelStrip(self.LED_COUNT,
                                self.LED_PIN,
                                self.LED_FREQ_HZ,
                                self.LED_DMA,
                                self.LED_INVERT,
                                self.LED_BRIGHTNESS,
                                self.LED_CHANNEL)
        self.strip.begin()

    def _color(self, color, wait_ms=50):
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color)
            self.strip.show()
            time.sleep(wait_ms/1000.0)

    def color(self, r: int, g: int, b: int, w: int, wait_ms=50):
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, Color(r, g, b, w))
            self.strip.show()
            time.sleep(wait_ms/1000.0)

    def all_red(self):
        self._color(Color(255, 0, 0))

    def all_green(self):
        self._color(Color(0, 255, 0))

    def all_blue(self):
        self._color(Color(0, 0, 255))

    def all_white(self):
        self._color(Color(0, 0, 0, 255))

    def all_off(self):
        self._color(Color(0, 0, 0, 0))
