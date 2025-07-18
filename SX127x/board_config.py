""" Defines the BOARD class that contains the board pin mappings and RF module HF/LF info. """

# -*- coding: utf-8 -*-

# Copyright 2015-2022 Mayer Analytics Ltd.
#
# This file is part of pySX127x.
#
# pySX127x is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public
# License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# pySX127x is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
# details.
#
# You can be released from the requirements of the license by obtaining a commercial license. Such a license is
# mandatory as soon as you develop commercial activities involving pySX127x without disclosing the source code of your
# own applications, or shipping pySX127x with a closed source product.
#
# You should have received a copy of the GNU General Public License along with pySX127.  If not, see
# <http://www.gnu.org/licenses/>.


from gpiozero import LED, DigitalInputDevice, DigitalOutputDevice
import spidev

import time


class BOARD:
    """Board initialisation/teardown and pin configuration is kept here.
    Also, information about the RF module is kept here.
    This is the Raspberry Pi board with one LED and a Ra-02 Lora.
    """

    # Note that the BCOM numbering for the GPIOs is used.
    DIO0 = 22  # RaspPi GPIO 22
    DIO1 = 23  # RaspPi GPIO 23
    DIO2 = 24  # RaspPi GPIO 24
    DIO3 = 25  # RaspPi GPIO 25
    RST_PIN = 27  # RaspPi GPIO 27
    LED_PIN = 13  # RaspPi GPIO 13 connects to the LED and a resistor (1kohm or 330ohm)

    # The spi object is kept here
    spi = None
    SPI_BUS = 0
    SPI_CS = 0

    # tell pySX127x here whether the attached RF module uses low-band (RF*_LF pins) or high-band (RF*_HF pins).
    # low band (called band 1&2) are 137-175 and 410-525
    # high band (called band 3) is 862-1020
    low_band = True

    # gpiozero devices
    led = None
    rst = None
    dio_pins = {}
    dio_callbacks = {}

    @staticmethod
    def setup():
        """Configure the Raspberry GPIOs
        :rtype : None
        """
        # LED
        BOARD.led = LED(BOARD.LED_PIN)
        BOARD.rst = DigitalOutputDevice(BOARD.RST_PIN, initial_value=True)
        # DIOx
        for pin in [BOARD.DIO0, BOARD.DIO1, BOARD.DIO2, BOARD.DIO3]:
            BOARD.dio_pins[pin] = DigitalInputDevice(pin, pull_up=False)
        # blink 2 times to signal the board is set up
        BOARD.blink(0.1, 2)

    @staticmethod
    def teardown():
        """Cleanup SpiDev"""
        if BOARD.spi:
            BOARD.spi.close()

    @staticmethod
    def SpiDev():
        """Init and return the SpiDev object
        :return: SpiDev object
        :param spi_bus: The RPi SPI bus to use: 0 or 1
        :param spi_cs: The RPi SPI chip select to use: 0 or 1
        :rtype: SpiDev
        """
        spi_bus = BOARD.SPI_BUS
        spi_cs = BOARD.SPI_CS
        BOARD.spi = spidev.SpiDev()
        BOARD.spi.open(spi_bus, spi_cs)
        BOARD.spi.max_speed_hz = (
            5000000  # SX127x can go up to 10MHz, pick half that to be safe
        )

        return BOARD.spi

    @staticmethod
    def add_event_detect(dio_number, callback):
        """Wraps around the GPIO.add_event_detect function
        :param dio_number: DIO pin 0...5
        :param callback: The function to call when the DIO triggers an IRQ.
        :return: None
        """
        BOARD.dio_pins[dio_number].when_activated = callback
        BOARD.dio_callbacks[dio_number] = callback

    @staticmethod
    def add_events(cb_dio0, cb_dio1, cb_dio2, cb_dio3, cb_dio4, cb_dio5):
        BOARD.add_event_detect(BOARD.DIO0, callback=cb_dio0)
        BOARD.add_event_detect(BOARD.DIO1, callback=cb_dio1)
        BOARD.add_event_detect(BOARD.DIO2, callback=cb_dio2)
        BOARD.add_event_detect(BOARD.DIO3, callback=cb_dio3)
        # the modtronix inAir9B does not expose DIO4 and DIO5

    @staticmethod
    def led_on(value=1):
        """Switch the proto shields LED
        :param value: 0/1 for off/on. Default is 1.
        :return: value
        :rtype : int
        """
        if value:
            BOARD.led.on()
        else:
            BOARD.led.off()
        return value

    @staticmethod
    def led_off():
        """Switch LED off
        :return: 0
        """
        BOARD.led.off()
        return 0

    @staticmethod
    def reset():
        """manual reset
        :return: 0
        """
        BOARD.rst.off()
        time.sleep(0.01)
        BOARD.rst.on()
        time.sleep(0.01)
        return 0

    @staticmethod
    def blink(time_sec, n_blink):
        if n_blink == 0:
            return
        BOARD.led.on()
        for i in range(n_blink):
            time.sleep(time_sec)
            BOARD.led.off()
            time.sleep(time_sec)
            BOARD.led.on()
        BOARD.led.off()
