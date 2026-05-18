from machine import Pin, UART
import utime

uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))

def send_band_uart(band):
    packet = bytearray([0xAA, 0x01, band, 0xFF])
    uart.write(packet)
    print("Sent band:", band)

while True:
    send_band_uart(1)
    utime.sleep(2)

    send_band_uart(2)
    utime.sleep(2)

    send_band_uart(3)
    utime.sleep(2)