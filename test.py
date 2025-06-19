import spidev
import RPi.GPIO as GPIO
import time

# === GPIO Pin Setup ===
PIN_CS    = 8     # GPIO8  - NSS (CS)
PIN_BUSY  = 24    # GPIO24 - BUSY
PIN_RESET = 25    # GPIO25 - RESET
PIN_DIO1  = 23    # GPIO23 - DIO1 (optional for interrupt)

# === GPIO Init ===
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(PIN_CS, GPIO.OUT)
GPIO.setup(PIN_RESET, GPIO.OUT)
GPIO.setup(PIN_BUSY, GPIO.IN)

# === SPI Init ===
spi = spidev.SpiDev()
spi.open(0, 0)  # (bus 0, device 0 = CE0 = GPIO8)
spi.max_speed_hz = 1000000  # 1 MHz (safe for SX1262)
spi.mode = 0b00

# === Functions ===

def wait_until_ready():
    while GPIO.input(PIN_BUSY) == GPIO.HIGH:
        time.sleep(0.001)

def reset_sx1262():
    print("[RESET] Pulsing RESET pin...")
    GPIO.output(PIN_RESET, GPIO.LOW)
    time.sleep(0.01)
    GPIO.output(PIN_RESET, GPIO.HIGH)
    time.sleep(0.01)
    wait_until_ready()
    print("[RESET] Done.")

def get_status():
    wait_until_ready()
    GPIO.output(PIN_CS, GPIO.LOW)
    response = spi.xfer2([0xC0, 0x00])  # GetStatus command
    GPIO.output(PIN_CS, GPIO.HIGH)
    wait_until_ready()
    print(f"[STATUS] SX1262 Response: {response}")

# === Run Test ===
if __name__ == "__main__":
    print("🔧 Testing SX1262 LoRa Node (HF)...")
    reset_sx1262()
    get_status()
