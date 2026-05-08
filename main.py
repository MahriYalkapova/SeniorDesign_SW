from machine import Pin
import utime
from machine import freq

freq(250_000_000)   # 250 MHz
print(freq())

# WIRING
# GP2 -> SER1 / DATA of shift register 1
# GP3 -> SER2 / DATA of shift register 2
# GP4 -> CLK / SRCLK of both shift registers
# GP5 -> LATCH / RCLK of both shift registers
# GP15 -> button pin for debugging

# hardware
LED_PIN = 25
DATA_PIN1 = 2
DATA_PIN2 = 3
CLOCK_PIN = 4
LATCH_PIN = 5
BUTTON_PIN = 15

# Frequency Band Variable
BANDS = 8

# sleep times
shift_period = 1  # seconds
shift_period_half = shift_period / 2

#clock delay in microseconds
CLOCK_DELAY_US = 2

# PIN SETUP
SER1 = Pin(DATA_PIN1, Pin.OUT)
SER2 = Pin(DATA_PIN2, Pin.OUT)
CLK = Pin(CLOCK_PIN, Pin.OUT)
LATCH = Pin(LATCH_PIN, Pin.OUT)
LED = Pin(LED_PIN, Pin.OUT)
BUTTON = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)

# Initial states
SER1.value(0)
SER2.value(0)
CLK.value(0)
LATCH.value(1)
LED.value(0)

# Put latch into default LOW state after startup
utime.sleep_us(CLOCK_DELAY_US)
LATCH.value(0)

# BAND TABLE (15-BIT, first bit becomes 0 when treated as 16-bit)
# B1 = 920 MHz  -> 00011100 00011000
# B2 = 978 MHz  -> 001100000011000
# B3 = 1090 MHz -> 000110000001000
# B4 = 1.15 GHz -> 000100000001000
# B5 = 1.30 GHz -> 001010000010000
# B6 = 1.40 GHz -> 001000000010000
# B7 = 1.80 GHz -> 000010000000000
# B8 = 2.40 GHz -> 000000000000000

table_bands = {
    1: 0b001110000011000,
    2: 0b001100000011000,
    3: 0b000110000001000,
    4: 0b000100000001000,
    5: 0b001010000010000,
    6: 0b001000000010000,
    7: 0b000010000000000,
    8: 0b000000000000000,
    9: 0b1111111111111110
}

band_freqs = {
    1: "920 MHz",
    2: "978 MHz",
    3: "1090 MHz",
    4: "1.15 GHz",
    5: "1.30 GHz",
    6: "1.40 GHz",
    7: "1.80 GHz",
    8: "2.40 GHz"
}


# Functions
def wait_button():
    while BUTTON.value() == 1:
        pass
    utime.sleep_us(CLOCK_DELAY_US)
    while BUTTON.value() == 0:
        pass
    utime.sleep_us(CLOCK_DELAY_US)

def clock_pulse():
    CLK.value(1)
    utime.sleep_us(CLOCK_DELAY_US)
    CLK.value(0)
    utime.sleep_us(CLOCK_DELAY_US)

def latch_pulse():
    LATCH.value(1)
    utime.sleep_us(CLOCK_DELAY_US)
    LATCH.value(0)

# Test functions
def test_clock():
    print("Testing CLOCK pin...")
    SER1.value(0)
    SER2.value(0)

    while True:
        wait_button()
        CLK.value(1)
        LED.value(1)
        print("CLOCK HIGH")
        utime.sleep_us(CLOCK_DELAY_US)

        CLK.value(0)
        LED.value(0)
        print("CLOCK LOW")
        utime.sleep_us(CLOCK_DELAY_US)

def test_latch():
    print("Testing LATCH pin...")

    # Initial HIGH
    LATCH.value(1)
    LED.value(1)
    print("LATCH INITIAL HIGH")
    utime.sleep_us(CLOCK_DELAY_US)

    # Default LOW
    LATCH.value(0)
    LED.value(0)
    print("LATCH DEFAULT LOW")
    utime.sleep_us(CLOCK_DELAY_US)

    while True:
        wait_button()
        LATCH.value(1)
        LED.value(1)
        print("LATCH HIGH")
        utime.sleep_us(CLOCK_DELAY_US)

        LATCH.value(0)
        LED.value(0)
        print("LATCH LOW")
        utime.sleep_us(CLOCK_DELAY_US)

def test_data():
    print("Testing DATA pin...")
    CLK.value(0)

    while True:
        wait_button()
        SER1.value(0)
        SER2.value(1)
        LED.value(1)
        print("DATA1 LOW / DATA2 HIGH")

        wait_button()
        SER1.value(1)
        SER2.value(0)
        LED.value(0)
        print("DATA1 HIGH / DATA2 LOW")


# Shift register functions

def shift_out(data):  # 16-bit pattern split into two parallel 8-bit sends
    data1 = (data >> 8) & 0xFF   # upper 8 bits -> SER1
    data2 = data & 0xFF          # lower 8 bits -> SER2

    print(f"SER1 byte: {data1:08b}")
    print(f"SER2 byte: {data2:08b}")

    for i in range(0, 8):
        bit1 = (data1 >> i) & 1
        bit2 = (data2 >> i) & 1

        SER1.value(bit1)
        SER2.value(bit2)

        LED.value(bit1 or bit2)

        print(f"Sent bit {8 - i}: SER1={bit1}, SER2={bit2}")
        clock_pulse()

    latch_pulse()
    print(f"Latched data: {data:016b}")

def send_band(usr_inp):
    if usr_inp not in table_bands:
        print("Invalid band. Choose 1 to 8.")
        return

    tBaud = table_bands[usr_inp]
    shift_out(tBaud)

    print("Band:", usr_inp)
    print("Frequency:", band_freqs[usr_inp])
    print(f"Pattern: {tBaud:016b}")

def test_all_bands():
    i = 1
    while i <= 8:
        send_band(i)
        utime.sleep_us(CLOCK_DELAY_US)
        i = i + 1

def main():
    # test_clock()
    # test_data()
    # test_latch()

    band = int(input("Enter band number (1-8): "))
    send_band(band)

    # test_all_bands()

if __name__ == "__main__":
    main()