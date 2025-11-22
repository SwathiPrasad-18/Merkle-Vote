from pyfingerprint.pyfingerprint import PyFingerprint
import time
import sys

# --- Configuration ---
# Make sure this is the correct COM port for your USB-to-UART adapter
SERIAL_PORT = 'COM5' 
# --- End Configuration ---

# List of baud rates to try
baud_rates = [57600, 9600, 19200, 38400, 115200]

print(f"--- Fingerprint Sensor Test ---")
print(f"Trying to find sensor on {SERIAL_PORT}...")

found_sensor = False
for baud in baud_rates:
    try:
        print(f"\nTrying at {baud} baud...")
        f = PyFingerprint(SERIAL_PORT, baud, 0xFFFFFFFF, 0x00000000)
        
        # The .verifyPassword() has its own default timeout
        if f.verifyPassword():
            print(f"✅ Sensor connected successfully at baud {baud}!")
            found_sensor = True
            break
        else:
            print("❌ Wrong password or bad header (likely wrong baud).")
            
    except Exception as e:
        # Catch errors like "Permission denied" or "Packet does not begin with valid header"
        print(f"❌ Failed at {baud}: {e}")
        time.sleep(0.5)

if not found_sensor:
    print("\n--- Test Complete ---")
    print("❌ FAILED: Could not find sensor on any baud rate.")
    print("Please check your wiring (TX/RX) and COM port.")