import spidev
import RPi.GPIO as GPIO
import time

# SX1262 Pin Definitions
NSS_PIN = 8    # SPI Chip Select (CE0)
RESET_PIN = 25 # GPIO25 for Reset
BUSY_PIN = 24  # GPIO24 for Busy
DIO1_PIN = 23  # GPIO23 for Interrupt (optional)

# Initialize SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # bus 0, device 0 (CE0)
spi.max_speed_hz = 10000000  # 10 MHz

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(NSS_PIN, GPIO.OUT)
GPIO.setup(RESET_PIN, GPIO.OUT)
GPIO.setup(BUSY_PIN, GPIO.IN)
GPIO.setup(DIO1_PIN, GPIO.IN)

def reset_lora():
    GPIO.output(RESET_PIN, GPIO.LOW)
    time.sleep(0.1)
    GPIO.output(RESET_PIN, GPIO.HIGH)
    time.sleep(0.01)

def lora_busy_wait():
    while GPIO.input(BUSY_PIN):
        time.sleep(0.001)

def spi_write(cmd, data=None):
    GPIO.output(NSS_PIN, GPIO.LOW)
    spi.xfer([cmd])
    if data:
        spi.xfer(data)
    GPIO.output(NSS_PIN, GPIO.HIGH)
    lora_busy_wait()

def spi_read(cmd, length):
    GPIO.output(NSS_PIN, GPIO.LOW)
    spi.xfer([cmd])
    response = spi.readbytes(length)
    GPIO.output(NSS_PIN, GPIO.HIGH)
    lora_busy_wait()
    return response

def setup_lora():
    reset_lora()
    lora_busy_wait()

    # Set Standby mode (STDBY_RC)
    spi_write(0x80, [0x00])

    # Set Packet Type to LoRa
    spi_write(0x8A, [0x01])

    # Set Frequency (example: 868 MHz)
    freq = int((868000000 / (32e6)) * (2**25))
    spi_write(0x86, [(freq >> 24) & 0xFF, (freq >> 16) & 0xFF, (freq >> 8) & 0xFF, freq & 0xFF])

    # Set TX parameters (power 17 dBm, ramp time 40us)
    spi_write(0x8E, [0x11, 0x04])

def send_message(message):
    # Prepare buffer
    buffer = [ord(c) for c in message]

    # Set buffer base address
    spi_write(0x8F, [0x00, 0x00])

    # Write buffer
    spi_write(0x0E, buffer)

    # Set payload length
    spi_write(0x8B, [len(buffer)])

    # Set to transmit mode
    spi_write(0x83, [0x00, 0x00, 0x00])  # TX timeout = no timeout

    print(f"Sent: {message}")

try:
    setup_lora()
    while True:
        send_message("Hello from Raspberry Pi and SX1262!")
        time.sleep(5)  # Send every 5 seconds

except KeyboardInterrupt:
    print("Exiting...")
    spi.close()
    GPIO.cleanup()
